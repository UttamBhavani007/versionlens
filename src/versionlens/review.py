"""Draft question validation and digest-bound, human-attested holdout release.

This module checks review records, not a reviewer's identity or the quality of
human judgments. It never executes retrieval/generation and never approves a
question. Test review records are explicitly fictional unit-test fixtures.
"""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata

from .models import Chunk, SearchRequest, ValidationError
from .vector_store import corpus_fingerprint


MAX_INPUT_BYTES = 4_000_000
ROOT_FIELDS = {"schema_version", "kind", "review_status", "label_origin", "protocol", "corpus_fingerprint", "cases"}
CASE_FIELDS = {"case_id", "group_id", "split", "question", "version", "access_profile", "category",
               "expected_decision", "anchors", "reference_answer", "review_notes", "prior_development_overlap"}
ANCHOR_FIELDS = {"source_id", "source_sha256", "section_contains", "text_contains"}
REVIEW_FIELDS = {"schema_version", "kind", "dataset_sha256", "corpus_fingerprint", "records"}
RECORD_FIELDS = {"case_id", "case_sha256", "status", "reviewer_type", "reviewer", "reviewed_at", "notes"}
LOCK_FIELDS = {"schema_version", "kind", "dataset_sha256", "review_sha256", "corpus_fingerprint", "case_ids", "case_sha256"}
CATEGORIES = {"answerable", "missing_evidence", "wrong_version_trap", "conflicting_evidence", "permission_denied"}
PROTOCOL = {"top_k": 5, "candidate_pool": 20, "rrf_constant": 60}


def _canonical(value) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                          allow_nan=False).encode("utf-8", errors="strict")
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise ValidationError("Evaluation metadata is not valid finite UTF-8 JSON.") from None


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("Evaluation JSON contains a duplicate key.")
        result[key] = value
    return result


def _constant(value):
    raise ValidationError("Evaluation JSON contains a nonfinite number.")


def _read(path: Path):
    try:
        with Path(path).open("rb") as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise ValidationError("Evaluation input exceeds the size limit.")
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_object, parse_constant=_constant)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        if isinstance(exc, ValidationError):
            raise
        raise ValidationError("Evaluation input is unreadable or invalid UTF-8 JSON.") from None
    return data, sha256(raw).hexdigest()


def _fields(value, fields, label):
    if not isinstance(value, dict) or set(value) != fields:
        raise ValidationError(f"{label} has unexpected or missing fields.")


def _string(value, label, *, empty=False, limit=20_000):
    if not isinstance(value, str) or len(value) > limit or not empty and not value.strip():
        raise ValidationError(f"{label} must be a bounded string.")
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        raise ValidationError(f"{label} must contain valid Unicode.") from None
    return value


def _digest(value, label):
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValidationError(f"{label} must be a SHA-256 digest.")
    return value


def _validate_dataset(data, chunks=None):
    _fields(data, ROOT_FIELDS, "Candidate dataset")
    if (type(data["schema_version"]) is not int or data["schema_version"] != 2
            or data["kind"] != "question_review_candidates" or data["review_status"] != "draft"):
        raise ValidationError("Expected an explicitly draft question-candidate dataset.")
    _string(data["label_origin"], "Label origin", limit=2000)
    _digest(data["corpus_fingerprint"], "Corpus fingerprint")
    protocol = data["protocol"]
    if (not isinstance(protocol, dict) or protocol != PROTOCOL
            or any(type(value) is not int for value in protocol.values())):
        raise ValidationError("The evaluation protocol must remain top-5, pool-20, RRF-60.")
    if chunks is not None:
        if (not isinstance(chunks, (tuple, list)) or not chunks
                or any(not isinstance(chunk, Chunk) for chunk in chunks)):
            raise ValidationError("Candidate validation requires a nonempty validated corpus.")
        if corpus_fingerprint(tuple(chunks)) != data["corpus_fingerprint"]:
            raise ValidationError("Candidate corpus fingerprint is stale.")
    cases = data["cases"]
    if not isinstance(cases, list) or not 1 <= len(cases) <= 200:
        raise ValidationError("Candidate dataset needs 1–200 questions.")
    ids, questions, groups = set(), set(), {}
    for case in cases:
        _fields(case, CASE_FIELDS, "Candidate case")
        case_id = _string(case["case_id"], "Case ID", limit=200)
        group = _string(case["group_id"], "Group ID", limit=200)
        if case_id in ids:
            raise ValidationError("Candidate case IDs must be unique.")
        ids.add(case_id)
        split = case["split"]
        if not isinstance(split, str) or split not in {"development", "candidate_holdout"}:
            raise ValidationError("Candidate split is unsupported.")
        if group in groups and groups[group] != split:
            raise ValidationError("A topic group cannot cross development and candidate holdout.")
        groups[group] = split
        request = SearchRequest(case["question"], case["version"], 5, case["access_profile"])
        normalized = " ".join(unicodedata.normalize("NFKC", request.question).casefold().split())
        key = (normalized, request.version, request.access_profile)
        if key in questions:
            raise ValidationError("Duplicate normalized question/version/profile combination.")
        questions.add(key)
        category = case["category"]
        if not isinstance(category, str) or category not in CATEGORIES:
            raise ValidationError("Candidate category is unsupported.")
        expected = "answer" if category == "answerable" else "abstain"
        if case["expected_decision"] != expected:
            raise ValidationError("Candidate decision does not match its category.")
        _string(case["reference_answer"], "Reference answer", empty=expected == "abstain")
        _string(case["review_notes"], "Review notes", empty=True)
        overlap = case["prior_development_overlap"]
        if not isinstance(overlap, list) or len(overlap) > 100:
            raise ValidationError("Prior development overlap must be a bounded list.")
        for prior in overlap:
            _string(prior, "Prior development ID", limit=200)
        if len(set(overlap)) != len(overlap) or overlap and split != "development":
            raise ValidationError("Previously used development cases cannot enter the holdout.")
        anchors = case["anchors"]
        if not isinstance(anchors, list) or len(anchors) > 20:
            raise ValidationError("Case anchors must be a bounded list.")
        if category == "answerable" and not anchors:
            raise ValidationError("Answerable questions require evidence anchors.")
        if category not in {"answerable", "conflicting_evidence"} and anchors:
            raise ValidationError("Abstention probes cannot carry positive answer anchors.")
        anchor_ids, seen_anchors = set(), set()
        for anchor in anchors:
            _fields(anchor, ANCHOR_FIELDS, "Evidence anchor")
            _string(anchor["source_id"], "Anchor source ID", limit=1000)
            _digest(anchor["source_sha256"], "Anchor source digest")
            _string(anchor["section_contains"], "Anchor section")
            _string(anchor["text_contains"], "Anchor text")
            identity = _canonical(anchor)
            if identity in seen_anchors:
                raise ValidationError("Duplicate evidence anchors are not allowed.")
            seen_anchors.add(identity)
            anchor_ids.add(anchor["source_id"])
            if chunks is not None and not any(
                chunk.source.source_id == anchor["source_id"]
                and chunk.source.sha256 == anchor["source_sha256"]
                and chunk.source.version == request.version and request.allows(chunk.source)
                and anchor["section_contains"] in chunk.section and anchor["text_contains"] in chunk.text
                for chunk in chunks
            ):
                raise ValidationError(f"Anchor is absent, inaccessible or from another snapshot: {case_id}")
        if category == "conflicting_evidence" and len(anchor_ids) < 2:
            raise ValidationError("Conflict questions need anchors from at least two accessible sources.")
    return data


def load_candidates(path: Path, chunks: tuple) -> dict:
    """Validate drafts against actual corpus identity without running any question."""
    data, _ = _read(path)
    return _validate_dataset(data, chunks)


def case_digest(case: dict) -> str:
    """Bind all question, split, policy, anchor, rubric and contamination fields."""
    if not isinstance(case, dict):
        raise ValidationError("Case digest requires a case object.")
    return sha256(_canonical(case)).hexdigest()


def make_review_template(data: dict, dataset_sha256: str) -> dict:
    """Create pending records only; this function never approves human review."""
    _validate_dataset(data)
    _digest(dataset_sha256, "Dataset digest")
    return {"schema_version": 1, "kind": "human_question_review", "dataset_sha256": dataset_sha256,
            "corpus_fingerprint": data["corpus_fingerprint"],
            "records": [{"case_id": case["case_id"], "case_sha256": case_digest(case), "status": "pending",
                         "reviewer_type": None, "reviewer": None, "reviewed_at": None, "notes": ""}
                        for case in data["cases"]]}


def _reviewed_metadata(dataset_path, review_path, chunks):
    data, dataset_sha = _read(dataset_path)
    _validate_dataset(data, chunks)
    review, review_sha = _read(review_path)
    _fields(review, REVIEW_FIELDS, "Human review")
    if (type(review["schema_version"]) is not int or review["schema_version"] != 1
            or review["kind"] != "human_question_review"
            or review["dataset_sha256"] != dataset_sha
            or review["corpus_fingerprint"] != data["corpus_fingerprint"]):
        raise ValidationError("Review metadata is stale or does not bind this exact dataset and corpus.")
    records = review["records"]
    if not isinstance(records, list) or len(records) != len(data["cases"]):
        raise ValidationError("Review records must cover every dataset case exactly once.")
    cases = {case["case_id"]: case for case in data["cases"]}
    seen = set()
    for record in records:
        _fields(record, RECORD_FIELDS, "Human review record")
        case_id = record["case_id"]
        if not isinstance(case_id, str) or case_id not in cases or case_id in seen:
            raise ValidationError("Review records contain unknown or duplicate case IDs.")
        seen.add(case_id)
        if record["case_sha256"] != case_digest(cases[case_id]):
            raise ValidationError("A review record refers to a stale question or label.")
        _string(record["notes"], "Human review notes", empty=True)
        status = record["status"]
        if not isinstance(status, str) or status not in {"pending", "approved", "rejected"}:
            raise ValidationError("Review record status is unsupported.")
        if status == "pending":
            if any(record[key] is not None for key in ("reviewer_type", "reviewer", "reviewed_at")):
                raise ValidationError("Pending records must not claim completed human review.")
        else:
            if record["reviewer_type"] != "human":
                raise ValidationError("Completed review records need an explicit human attestation.")
            _string(record["reviewer"], "Human reviewer", limit=500)
            _string(record["reviewed_at"], "Review timestamp", limit=100)
            try:
                timestamp = datetime.fromisoformat(record["reviewed_at"])
            except ValueError:
                raise ValidationError("Review timestamp must be timezone-aware ISO format.") from None
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValidationError("Review timestamp must include its timezone.")
            if timestamp > datetime.now(timezone.utc) + timedelta(minutes=1):
                raise ValidationError("Review timestamp cannot be in the future.")
        if cases[case_id]["split"] == "candidate_holdout" and status != "approved":
            raise ValidationError("Every candidate holdout question needs approved human review before release.")
    holdout = sorted(case_id for case_id, case in cases.items() if case["split"] == "candidate_holdout")
    if not holdout:
        raise ValidationError("There are no candidate holdout questions to release.")
    return {"schema_version": 1, "kind": "reviewed_holdout_lock", "dataset_sha256": dataset_sha,
            "review_sha256": review_sha, "corpus_fingerprint": data["corpus_fingerprint"],
            "case_ids": holdout, "case_sha256": {case_id: case_digest(cases[case_id]) for case_id in holdout}}


def _assert_inputs_unchanged(dataset_path, review_path, metadata):
    if (_read(dataset_path)[1] != metadata["dataset_sha256"]
            or _read(review_path)[1] != metadata["review_sha256"]):
        raise ValidationError("Dataset or review changed during holdout validation.")


def freeze_holdout(dataset_path: Path, review_path: Path, chunks: tuple, output_path: Path) -> dict:
    """Write a new lock only after every held-out draft has human-attested approval.

    Development review may remain pending. No identity verification or semantic
    quality certification is implied by a structurally valid human attestation.
    """
    metadata = _reviewed_metadata(dataset_path, review_path, chunks)
    _assert_inputs_unchanged(dataset_path, review_path, metadata)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("x", encoding="utf-8") as handle:
            json.dump(metadata, handle, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write("\n")
    except FileExistsError:
        raise ValidationError("Holdout lock output already exists; previous releases are preserved.") from None
    return metadata


def validate_holdout_lock(lock_path: Path, dataset_path: Path, review_path: Path, chunks: tuple) -> dict:
    """Recheck exact live inputs and the complete released case membership."""
    expected = _reviewed_metadata(dataset_path, review_path, chunks)
    actual, _ = _read(lock_path)
    _fields(actual, LOCK_FIELDS, "Holdout lock")
    if type(actual["schema_version"]) is not int or actual != expected:
        raise ValidationError("Holdout lock does not match the reviewed dataset, corpus and case membership.")
    _assert_inputs_unchanged(dataset_path, review_path, expected)
    return actual
