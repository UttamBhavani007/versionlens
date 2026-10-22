import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from test_models import example_source
from versionlens.evaluation import load_development_set, matches_anchor, summarize
from versionlens.ingest import chunk_markdown
from versionlens.models import ValidationError


class DevelopmentEvaluationTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "cases.json"
        text = "# Timeout\nFive seconds of network inactivity.\n"
        self.chunks = chunk_markdown(example_source(text=text), text)
        self.anchor = {"upstream_path": "docs/example.md", "section_contains": "Timeout",
                       "text_contains": "Five seconds"}
        self.anchor["upstream_path"] = self.chunks[0].source.upstream_path
        self.data = {"schema_version": 1, "split": "development", "human_reviewed": False,
                     "protocol": {"top_k": 5, "candidate_pool": 20, "rrf_constant": 60},
                     "cases": [{"case_id": "D01", "question": "default timeout", "version": "0.28.1",
                                "category": "answerable", "expected": [self.anchor]}]}

    def load(self):
        self.path.write_text(json.dumps(self.data), encoding="utf-8")
        return load_development_set(self.path, self.chunks)

    def test_anchor_requires_path_section_and_text_in_same_chunk(self):
        self.assertTrue(matches_anchor(self.chunks[0], self.anchor))
        for field in self.anchor:
            changed = {**self.anchor, field: "absent"}
            self.assertFalse(matches_anchor(self.chunks[0], changed))

    def test_wrong_version_or_fabricated_anchor_stops_the_comparison(self):
        self.assertEqual(len(self.load()["cases"]), 1)
        self.data["cases"][0]["version"] = "0.27.2"
        with self.assertRaises(ValidationError):
            self.load()
        self.data["cases"][0]["version"] = "0.28.1"
        self.anchor["text_contains"] = "Invented source sentence"
        with self.assertRaises(ValidationError):
            self.load()

    def test_reviewed_or_holdout_files_cannot_be_used_as_unreviewed_development(self):
        for field, value in (("human_reviewed", True), ("split", "held_out")):
            original = self.data[field]
            self.data[field] = value
            with self.assertRaises(ValidationError):
                self.load()
            self.data[field] = original

    def test_duplicate_cases_and_qualitative_positive_labels_are_rejected(self):
        self.data["cases"].append(dict(self.data["cases"][0]))
        with self.assertRaises(ValidationError):
            self.load()
        self.data["cases"].pop()
        self.data["cases"][0]["category"] = "missing_evidence"
        with self.assertRaises(ValidationError):
            self.load()

    def test_qualitative_probes_are_excluded_from_known_anchor_metrics(self):
        rows = [{"method": "keyword", "category": "answerable", "latency_ms": 10,
                 "first_known_evidence_rank": 2},
                {"method": "keyword", "category": "answerable", "latency_ms": 20,
                 "first_known_evidence_rank": None},
                {"method": "keyword", "category": "missing_evidence", "latency_ms": 999,
                 "first_known_evidence_rank": None}]
        result = summarize(rows, "keyword")
        self.assertEqual(result["answerable_cases"], 2)
        self.assertEqual(result["known_evidence_hit_at_5"], .5)
        self.assertEqual(result["known_evidence_mrr_at_5"], .25)
        self.assertEqual(result["latency_ms_median"], 15)
        self.assertEqual(result["latency_ms_p95_nearest_rank"], 20)

    def test_malformed_categories_boolean_versions_and_float_protocols_are_rejected(self):
        self.data["cases"][0]["category"] = []
        with self.assertRaises(ValidationError):
            self.load()
        self.data["cases"][0]["category"] = "answerable"
        self.data["schema_version"] = True
        with self.assertRaises(ValidationError):
            self.load()
        self.data["schema_version"] = 1
        self.data["protocol"]["top_k"] = 5.0
        with self.assertRaises(ValidationError):
            self.load()
