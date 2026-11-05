"""Support for a person recording question reviews one decision at a time.

Nothing here decides, suggests or pre-fills a verdict. Every decision is a single
explicit call carrying a reviewer name and the reviewer's own note, and the
interactive script refuses to run without a terminal. Like the rest of the review
workflow, this records attestations; it cannot verify identity or judgment quality.
"""

from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from .models import ValidationError
from .review import (RECORD_FIELDS, REVIEW_FIELDS, _fields, _read, _string, _validate_dataset, case_digest,
                     make_review_template)

DECISIONS = {"approved", "rejected"}


def save_review(review: dict, path: Path, *, create: bool = False) -> None:
    """Write atomically; with create=True an existing file is never replaced."""
    path = Path(path)
    if create and path.exists():
        raise ValidationError("Review file already exists; existing work is preserved.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=".review-", suffix=".tmp",
                            delete=False) as handle:
        json.dump(review, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
        temporary = Path(handle.name)
    try:
        if create and path.exists():
            raise ValidationError("Review file already exists; existing work is preserved.")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def check_review(review: dict, data: dict, dataset_sha256: str) -> None:
    """Validate a possibly partial review against the exact dataset; pending records are allowed."""
    _fields(review, REVIEW_FIELDS, "Human review")
    if (review["schema_version"] != 1 or review["kind"] != "human_question_review"
            or review["dataset_sha256"] != dataset_sha256 or review["corpus_fingerprint"] != data["corpus_fingerprint"]):
        raise ValidationError("Review file is stale or belongs to another dataset or corpus.")
    cases = [case["case_id"] for case in data["cases"]]
    records = review["records"]
    if not isinstance(records, list) or [r.get("case_id") if isinstance(r, dict) else None for r in records] != cases:
        raise ValidationError("Review records must cover every dataset case once, in dataset order.")
    digests = {case["case_id"]: case_digest(case) for case in data["cases"]}
    for record in records:
        _fields(record, RECORD_FIELDS, "Human review record")
        if record["case_sha256"] != digests[record["case_id"]]:
            raise ValidationError("A review record refers to a stale question or label.")
        status = record["status"]
        if status not in {"pending"} | DECISIONS:
            raise ValidationError("Review record status is unsupported.")
        _string(record["notes"], "Review notes", empty=True)
        if status == "pending":
            if any(record[key] is not None for key in ("reviewer_type", "reviewer", "reviewed_at")):
                raise ValidationError("Pending records must not claim completed human review.")
            continue
        if record["reviewer_type"] != "human" or not record["notes"].strip():
            raise ValidationError("Completed records need a human attestation and the reviewer's note.")
        _string(record["reviewer"], "Reviewer", limit=500)
        stamp = datetime.fromisoformat(_string(record["reviewed_at"], "Review timestamp", limit=100))
        if stamp.tzinfo is None or stamp > datetime.now(timezone.utc) + timedelta(minutes=1):
            raise ValidationError("Review timestamps must be timezone-aware and not in the future.")


def open_review(dataset_path: Path, review_path: Path, chunks: tuple) -> tuple[dict, dict]:
    """Load or create the review file; a new file contains only pending records."""
    data, dataset_sha256 = _read(dataset_path)
    _validate_dataset(data, chunks)
    review_path = Path(review_path)
    if review_path.exists():
        review, _ = _read(review_path)
        check_review(review, data, dataset_sha256)
    else:
        review = make_review_template(data, dataset_sha256)
        save_review(review, review_path, create=True)
    return data, review


def record_decision(review: dict, case_id: str, status: str, reviewer: str, notes: str, *, now=None) -> dict:
    """Return a copy with one decision recorded; refuses empty identity or notes."""
    if status not in DECISIONS:
        raise ValidationError("A decision is either approved or rejected.")
    _string(reviewer, "Reviewer", limit=500)
    _string(notes, "Review notes", limit=5000)
    now = now or datetime.now(timezone.utc).astimezone()
    if now.tzinfo is None:
        raise ValidationError("Review timestamp must include its timezone.")
    updated = deepcopy(review)
    matches = [record for record in updated["records"] if record["case_id"] == case_id]
    if len(matches) != 1:
        raise ValidationError("Unknown case ID.")
    matches[0].update(status=status, reviewer_type="human", reviewer=reviewer.strip(),
                      reviewed_at=now.isoformat(timespec="seconds"), notes=notes.strip())
    return updated


def progress(data: dict, review: dict) -> dict:
    split = {case["case_id"]: case["split"] for case in data["cases"]}
    counts = {name: Counter() for name in sorted(set(split.values()))}
    for record in review["records"]:
        counts[split[record["case_id"]]][record["status"]] += 1
    holdout = counts.get("candidate_holdout", Counter())
    return {"by_split": {name: dict(counter) for name, counter in counts.items()},
            "holdout_ready_to_freeze": bool(holdout) and set(holdout) == {"approved"}}


def queue(data: dict, review: dict, split: str) -> list[dict]:
    status = {record["case_id"]: record["status"] for record in review["records"]}
    return [case for case in data["cases"]
            if status[case["case_id"]] == "pending" and split in ("all", case["split"])]


def render_case(case: dict, chunks: tuple, root: Path) -> str:
    lines = [f'{case["case_id"]}  [{case["split"]}]  group: {case["group_id"]}',
             f'HTTPX {case["version"]} · profile: {case["access_profile"]} · category: {case["category"]}'
             f' · draft decision: {case["expected_decision"].upper()}', "",
             f'QUESTION: {case["question"]}', "",
             f'DRAFT REFERENCE / RUBRIC: {case["reference_answer"] or "(abstention expected)"}',
             f'DRAFT NOTES: {case["review_notes"] or "(none)"}',
             "PRIOR DEVELOPMENT OVERLAP: " + (", ".join(case["prior_development_overlap"]) or "none declared; check yourself")]
    for anchor in case["anchors"]:
        chunk = next((c for c in chunks if c.source.source_id == anchor["source_id"]
                      and c.source.sha256 == anchor["source_sha256"] and anchor["section_contains"] in c.section
                      and anchor["text_contains"] in c.text), None)
        if chunk is None:
            raise ValidationError("Anchor source context is unavailable.")
        lines += ["", f'SOURCE {anchor["source_id"]}', f"  section: {chunk.section} · lines {chunk.start_line}-{chunk.end_line}",
                  f"  file: {root / chunk.source.path}", f"  pinned: {chunk.citation_url}",
                  *["  | " + line for line in chunk.text.splitlines()]]
    if not case["anchors"]:
        lines += ["", "No positive anchor: check the stated absence, snapshot or permission boundary yourself."]
    return "\n".join(lines)
