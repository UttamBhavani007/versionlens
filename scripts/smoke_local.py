#!/usr/bin/env python3
"""Run explicit local development probes; this is not an accuracy benchmark."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from versionlens.answering import answer
from versionlens.config import LocalModelConfig
from versionlens.local_model import LocalModelClient, LocalModelError
from versionlens.models import SearchRequest
from versionlens.store import index_stats


PROBES = (
    ("timeout", "What is the default timeout in HTTPX?", "0.28.1"),
    ("upgrade", "Why did the proxies argument stop working after upgrading?", "0.28.1"),
    ("old_version", "Is the proxies argument deprecated?", "0.27.2"),
    ("missing_evidence", "quantumgiraffeunsupported", "0.28.1"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/local/day2-smoke.json")
    args = parser.parse_args()
    client = LocalModelClient()
    try:
        inventory = client.health()
        stats = index_stats(ROOT / "data/versionlens.sqlite3")
    except (LocalModelError, OSError, ValueError) as exc:
        print(f"Local smoke prerequisites failed: {exc}", file=sys.stderr)
        return 2
    results = []
    for case_id, question, version in PROBES:
        result = answer(ROOT / "data/versionlens.sqlite3", SearchRequest(question, version), client)
        results.append({"case_id": case_id, **result})
        print(json.dumps({"case_id": case_id, "status": result["status"],
                          "reason": result["reason"], "latency_ms": result["latency_ms"]}), flush=True)
    report = {"schema_version": 1, "kind": "local_development_smoke",
              "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
              "not_a_held_out_benchmark": True, "human_reviewed": False,
              "base_url": LocalModelConfig().base_url, "model_inventory": inventory,
              "index": stats, "results": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved development evidence: {args.output}")
    return 2 if any(result["status"] == "error" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
