#!/usr/bin/env python3
"""Add confidence intervals and paired comparisons to a recorded development run."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from versionlens.models import ValidationError
from versionlens.uncertainty import summarize_run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "reports/day6-development-evaluation.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/day8-development-uncertainty.json")
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValidationError("Output already exists; choose a new path.")
        summary = summarize_run(json.loads(args.report.read_text(encoding="utf-8")))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as output:
            json.dump(summary, output, indent=2, allow_nan=False, ensure_ascii=False)
            output.write("\n")
        print(json.dumps({"output": str(args.output), "methods": {
            name: {k: v for k, v in data.items() if k in ("known_anchor_hits_at_5", "hit_at_5_wilson_95",
                                                           "known_anchor_mrr_at_5", "mrr_at_5_bootstrap_95",
                                                           "missed_case_ids")}
            for name, data in summary["methods"].items()}, "comparisons": summary["comparisons"]}, indent=2))
    except (OSError, ValueError) as error:
        print(f"Summary failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
