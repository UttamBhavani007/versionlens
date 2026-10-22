#!/usr/bin/env python3
"""Record actual local answer behavior across retrieval modes on development probes."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from versionlens.answering import answer
from versionlens.embeddings import LocalEmbeddingClient
from versionlens.local_model import LocalModelClient, LocalModelError
from versionlens.models import SearchRequest, ValidationError
from versionlens.search_service import RETRIEVERS
from versionlens.vector_store import corpus_fingerprint, load_chunks

PROBES = (
    ("upgrade", "Why did the proxies argument stop working after upgrading?", "0.28.1"),
    ("old_version", "Is the proxies argument deprecated?", "0.27.2"),
    ("missing_evidence", "quantumgiraffeunsupported", "0.28.1"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/local/day3-answer-smoke.json")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists. Choose another filename to preserve earlier observations.")
    generation, embeddings = LocalModelClient(), LocalEmbeddingClient()
    index, vectors = ROOT / "data/versionlens.sqlite3", ROOT / "data/versionlens-vectors.sqlite3"
    try:
        generation_identity = generation.health()
        embedding_identity = embeddings.identity()
        fingerprint = corpus_fingerprint(load_chunks(index))
        results = []
        for case_id, question, version in PROBES:
            for method in RETRIEVERS:
                result = answer(index, SearchRequest(question, version), generation,
                                retrieval_method=method, vector_path=vectors, embedding_client=embeddings)
                results.append({"case_id": case_id, **result})
                print(json.dumps({"case_id": case_id, "retrieval_method": method,
                                  "status": result["status"], "reason": result["reason"],
                                  "latency_ms": result["latency_ms"]}), flush=True)
        if (embeddings.identity() != embedding_identity
                or generation.health().get("digest") != generation_identity.get("digest")
                or corpus_fingerprint(load_chunks(index)) != fingerprint):
            raise ValidationError("A model or corpus changed during the smoke run.")
        report = {
            "schema_version": 1, "kind": "local_retriever_answer_development_smoke",
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "not_a_held_out_benchmark": True, "human_reviewed": False,
            "semantic_support_verified": False, "api_fee_usd": 0,
            "corpus_fingerprint": fingerprint, "generation_model_inventory": generation_identity,
            "embedding_model": asdict(embedding_identity),
            "limitations": ["Repeated development probes; no answer-accuracy or entailment score.",
                            "Fixed request order and model swapping affect end-to-end latency.",
                            "Dense neighbors do not establish answerability; abstention requires evaluation."],
            "implementation_sha256": {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
                                      for path in sorted((ROOT / "src/versionlens").glob("*.py"))},
            "results": results,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, LocalModelError, ValidationError) as exc:
        print(f"Local retriever smoke failed: {exc}", file=sys.stderr)
        return 2
    return 2 if any(result["status"] == "error" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
