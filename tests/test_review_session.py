"""Review-session helpers, tested only with fictional fixtures and fictional reviewer names."""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import unittest

import test_review
from versionlens.models import ValidationError
from versionlens.review import freeze_holdout
from versionlens.review_session import (check_review, open_review, progress, queue, record_decision, render_case,
                                        save_review)

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


class ReviewSessionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_review.ReviewReleaseTests("test_pending_template_cannot_freeze_or_claim_human_review")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.data, self.chunks = self.fixture.data, self.fixture.chunks
        self.dataset_path = self.fixture.dataset_path
        self.review_path = self.fixture.root / "session" / "review.json"

    def open(self):
        return open_review(self.dataset_path, self.review_path, self.chunks)

    def test_new_review_is_all_pending_and_never_overwritten(self):
        _, review = self.open()
        self.assertTrue(all(r["status"] == "pending" and r["reviewer"] is None for r in review["records"]))
        data, again = self.open()
        self.assertEqual(review, again)
        with self.assertRaises(ValidationError):
            save_review(review, self.review_path, create=True)

    def test_decision_needs_reviewer_note_and_a_real_verdict(self):
        _, review = self.open()
        for args in (("approved", "", "checked"), ("approved", "Fictional A", " "), ("pending", "Fictional A", "x"),
                     ("approved", "Fictional A", None)):
            with self.assertRaises(ValidationError):
                record_decision(review, "C001", *args)
        with self.assertRaises(ValidationError):
            record_decision(review, "NOPE", "approved", "Fictional A", "checked")
        with self.assertRaises(ValidationError):
            record_decision(review, "C001", "approved", "Fictional A", "checked", now=datetime(2026, 1, 1))

    def test_recorded_decision_is_a_valid_human_attestation_and_input_is_not_mutated(self):
        data, review = self.open()
        updated = record_decision(review, "C001", "approved", "Fictional A", " checked source ", now=NOW)
        self.assertEqual(review["records"][0]["status"], "pending")
        record = updated["records"][0]
        self.assertEqual((record["status"], record["reviewer_type"], record["notes"]),
                         ("approved", "human", "checked source"))
        check_review(updated, data, updated["dataset_sha256"])
        self.assertEqual(progress(data, updated)["by_split"]["candidate_holdout"], {"approved": 1})
        self.assertEqual(progress(data, review)["holdout_ready_to_freeze"], False)
        self.assertEqual(progress(data, updated)["holdout_ready_to_freeze"], True)

    def test_saved_review_reloads_and_releases_the_same_way_as_the_existing_gate(self):
        data, review = self.open()
        review = record_decision(review, "C001", "approved", "Fictional A", "checked", now=NOW)
        save_review(review, self.review_path)
        self.assertEqual(self.open()[1], review)
        lock = freeze_holdout(self.dataset_path, self.review_path, self.chunks, self.fixture.root / "lock.json")
        self.assertEqual(lock["case_ids"], ["C001"])

    def test_rejected_holdout_still_blocks_release(self):
        _, review = self.open()
        review = record_decision(review, "C001", "rejected", "Fictional A", "ambiguous", now=NOW)
        save_review(review, self.review_path)
        with self.assertRaises(ValidationError):
            freeze_holdout(self.dataset_path, self.review_path, self.chunks, self.fixture.root / "lock.json")

    def test_stale_dataset_or_forged_pending_claims_are_refused(self):
        data, review = self.open()
        self.fixture.data["cases"][0]["question"] = "Changed question?"
        self.fixture.save_dataset()
        with self.assertRaises(ValidationError):
            self.open()
        self.fixture.data["cases"][0]["question"] = "What is the network inactivity timeout?"
        self.fixture.save_dataset()
        review["records"][0]["reviewer"] = "Someone"
        with self.assertRaises(ValidationError):
            check_review(review, data, review["dataset_sha256"])

    def test_queue_filters_split_and_skips_decided_cases(self):
        data, review = self.open()
        self.assertEqual([c["case_id"] for c in queue(data, review, "candidate_holdout")], ["C001"])
        self.assertEqual([c["case_id"] for c in queue(data, review, "development")], ["D001"])
        self.assertEqual(len(queue(data, review, "all")), 2)
        review = record_decision(review, "C001", "approved", "Fictional A", "checked", now=NOW)
        self.assertEqual([c["case_id"] for c in queue(data, review, "all")], ["D001"])

    def test_render_shows_question_draft_labels_and_source_text(self):
        text = render_case(self.data["cases"][0], self.chunks, ROOT)
        for expected in ("What is the network inactivity timeout?", "DRAFT REFERENCE", "five seconds"):
            self.assertIn(expected, text)

    def test_interactive_script_refuses_piped_input_and_leaves_review_pending(self):
        review = self.fixture.root / "piped.json"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/review_session.py"), "--review", str(review)],
                                input="Fictional A\napprove\nchecked\n", capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 2)
        self.assertIn("terminal", result.stderr)
        if review.exists():
            records = json.loads(review.read_text())["records"]
            self.assertTrue(all(r["status"] == "pending" for r in records))


if __name__ == "__main__":
    unittest.main()
