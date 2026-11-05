#!/usr/bin/env python3
"""Review draft questions yourself, one at a time, in a terminal. Never run from a pipe or script."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from versionlens.evaluation_corpus import load_evaluation_corpus
from versionlens.models import ValidationError
from versionlens.review_session import open_review, progress, queue, record_decision, render_case, save_review

RULE = "-" * 78


def ask(prompt: str) -> str:
    return input(prompt).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=ROOT / "data/evaluation/review-candidates.json")
    parser.add_argument("--review", type=Path, default=ROOT / "reports/local/question-review/review.json")
    parser.add_argument("--split", choices=("candidate_holdout", "development", "all"), default="candidate_holdout")
    parser.add_argument("--status", action="store_true", help="print progress only; no decisions")
    args = parser.parse_args()
    try:
        chunks = load_evaluation_corpus(ROOT).chunks
        data, review = open_review(args.dataset, args.review, chunks)
        if args.status:
            print(json.dumps(progress(data, review), indent=2))
            return 0
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
            raise ValidationError("Decisions must be typed by a person at a terminal; refusing piped or scripted input.")
        print("You are recording your own judgment. Nothing is pre-filled or suggested.")
        reviewer = ask("Your full name (stored as the human reviewer): ")
        if not reviewer:
            raise ValidationError("A reviewer name is required.")
        todo = queue(data, review, args.split)
        print(f"{len(todo)} pending in '{args.split}'. Commands: approve | reject | skip | quit\n")
        for number, case in enumerate(todo, 1):
            print(RULE + f"\n[{number}/{len(todo)}] " + render_case(case, chunks, ROOT) + "\n" + RULE)
            while True:
                choice = ask("approve / reject / skip / quit > ").lower()
                if choice == "quit":
                    break
                if choice == "skip":
                    break
                if choice in ("approve", "reject"):
                    notes = ask("What did you check? (required) > ")
                    if not notes:
                        print("A note is required."); continue
                    status = "approved" if choice == "approve" else "rejected"
                    review = record_decision(review, case["case_id"], status, reviewer, notes)
                    save_review(review, args.review)
                    print(f"Saved {case['case_id']}: {status}.")
                    break
                print("Type the full word: approve, reject, skip or quit.")
            if choice == "quit":
                break
        print(json.dumps(progress(data, review), indent=2))
        print(f"Review file: {args.review}\nWhen holdout_ready_to_freeze is true, freeze with scripts/review_questions.py freeze.")
    except (OSError, ValueError, EOFError, KeyboardInterrupt) as error:
        print(f"Review stopped: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
