"""Source-anchor development checks, deliberately separate from a held-out benchmark."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import median
from time import perf_counter

from .models import SearchRequest, ValidationError
from .search_service import RETRIEVERS, retrieve


def matches_anchor(chunk, anchor: dict) -> bool:
    return (chunk.source.upstream_path == anchor["upstream_path"]
            and anchor["section_contains"] in chunk.section
            and anchor["text_contains"] in chunk.text)


def load_development_set(path: Path, chunks: tuple) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or type(data.get("schema_version")) is not int or data.get("schema_version") != 1
            or data.get("split") != "development" or data.get("human_reviewed") is not False):
        raise ValidationError("Expected an explicitly unreviewed development set, not a holdout.")
    protocol = data.get("protocol")
    if (not isinstance(protocol, dict)
            or protocol != {"top_k": 5, "candidate_pool": 20, "rrf_constant": 60}
            or any(type(value) is not int for value in protocol.values())):
        raise ValidationError("Development protocol must use top-5, pool-20, RRF-60 without tuning.")
    cases = data.get("cases")
    if not isinstance(cases, list) or not 1 <= len(cases) <= 200:
        raise ValidationError("Development set needs 1–200 cases.")
    seen = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValidationError("Development cases must be objects.")
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValidationError("Development case IDs must be unique nonempty strings.")
        seen.add(case_id)
        request = SearchRequest(case.get("question"), case.get("version"), 5)
        category, expected = case.get("category"), case.get("expected")
        if (not isinstance(category, str)
                or category not in {"answerable", "missing_evidence", "wrong_version_trap"}
                or not isinstance(expected, list)):
            raise ValidationError("Development case has an unsupported category or anchors.")
        if (category == "answerable") != bool(expected):
            raise ValidationError("Only answerable cases have known positive evidence anchors.")
        for anchor in expected:
            if (not isinstance(anchor, dict)
                    or set(anchor) != {"upstream_path", "section_contains", "text_contains"}
                    or any(not isinstance(value, str) or not value for value in anchor.values())):
                raise ValidationError("Evidence anchors need exact path, section, and source text.")
            if not any(chunk.source.version == request.version and matches_anchor(chunk, anchor)
                       for chunk in chunks):
                raise ValidationError(f"Development anchor is absent from its pinned snapshot: {case_id}")
    return data


def summarize(results: list[dict], method: str) -> dict:
    rows = [row for row in results if row["method"] == method and row["category"] == "answerable"]
    if not rows:
        raise ValidationError("At least one answerable development case is required.")
    latencies = sorted(row["latency_ms"] for row in rows)
    ranks = [row["first_known_evidence_rank"] for row in rows]
    return {
        "answerable_cases": len(rows),
        "known_evidence_hit_at_5": sum(rank is not None for rank in ranks) / len(rows),
        "known_evidence_mrr_at_5": sum(1 / rank for rank in ranks if rank is not None) / len(rows),
        "latency_ms_median": median(latencies),
        "latency_ms_p95_nearest_rank": latencies[math.ceil(.95 * len(latencies)) - 1],
        "api_fee_usd": 0,
    }


def compare_retrieval(index_path: Path, vector_path: Path, development_path: Path, *, client=None) -> dict:
    from .embeddings import LocalEmbeddingClient
    from .vector_store import corpus_fingerprint, load_chunks
    client = client or LocalEmbeddingClient()
    chunks = load_chunks(index_path)
    development_digest = sha256(development_path.read_bytes()).hexdigest()
    data = load_development_set(development_path, chunks)
    identity = client.identity()
    results = []
    for case in data["cases"]:
        request = SearchRequest(case["question"], case["version"], 5)
        for method in RETRIEVERS:
            started = perf_counter()
            hits = retrieve(index_path, request, method=method, vector_path=vector_path, client=client)
            elapsed = round((perf_counter() - started) * 1000, 3)
            if any(hit.chunk.source.version != request.version for hit in hits):
                raise ValidationError("Retrieval leaked another version during development checks.")
            ranks = [rank for rank, hit in enumerate(hits, 1)
                     if any(matches_anchor(hit.chunk, anchor) for anchor in case["expected"])]
            results.append({
                "case_id": case["case_id"], "question": request.question, "version": request.version,
                "category": case["category"], "method": method,
                "first_known_evidence_rank": min(ranks) if ranks else None,
                "latency_ms": elapsed, "returned_count": len(hits),
                "hits": [hit.to_dict() for hit in hits],
            })
    if client.identity() != identity or corpus_fingerprint(load_chunks(index_path)) != corpus_fingerprint(chunks):
        raise ValidationError("Corpus or embedding model changed during development comparison.")
    if sha256(development_path.read_bytes()).hexdigest() != development_digest:
        raise ValidationError("Development questions or labels changed during comparison.")
    return {
        "schema_version": 1, "kind": "retrieval_development_comparison",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "not_a_held_out_benchmark": True, "human_reviewed": False,
        "development_set_sha256": development_digest,
        "corpus_fingerprint": corpus_fingerprint(chunks),
        "embedding_model": {"model": identity.model, "digest": identity.digest, "dimensions": identity.dimensions},
        "protocol": {"top_k": 5, "rrf_constant": 60, "candidate_pool": 20,
                     "execution_order": list(RETRIEVERS), "api_fee_usd": 0,
                     "reranker": None, "keyword_remains_default": True},
        "limitations": [
            "AI-authored, source-checked, nonexhaustive positive anchors; not independent human review.",
            "Hit and reciprocal-rank scores refer to these known anchors, not complete relevance labels.",
            "Missing-evidence and wrong-version probes are qualitative and excluded from aggregates.",
            "No answer generation, citation entailment, or unsupported-answer rate is evaluated here.",
            "One fixed-order local run; model warming and caching affect latency. No speed guarantee.",
            "Dense retrieval returns neighbors for unsupported questions; scores are not calibrated confidence.",
        ],
        "summary": {method: summarize(results, method) for method in RETRIEVERS},
        "results": results,
    }
