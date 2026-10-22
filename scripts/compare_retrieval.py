#!/usr/bin/env python3
"""Compare retrieval on labelled development probes using only local embeddings."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from versionlens.evaluation import compare_retrieval
from versionlens.local_model import LocalModelError
from versionlens.models import ValidationError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/local/day3-retrieval.json")
    parser.add_argument("--development-set", type=Path, default=ROOT / "data/evaluation/development-retrieval.json")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists. Choose a new filename to preserve the previous run.")
    try:
        report = compare_retrieval(ROOT / "data/versionlens.sqlite3", ROOT / "data/versionlens-vectors.sqlite3",
                                   args.development_set)
        report["implementation_sha256"] = {
            str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
            for path in sorted((ROOT / "src/versionlens").glob("*.py"))
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, sqlite3.Error, LocalModelError, ValidationError) as exc:
        print(f"Local retrieval comparison failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"report": str(args.output), "summary": report["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
