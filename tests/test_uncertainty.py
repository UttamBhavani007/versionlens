import unittest

from versionlens.models import ValidationError
from versionlens.uncertainty import (METHODS, bootstrap_mean_interval, exact_sign_test, summarize_run,
                                     wilson_interval)


def row(case_id, method, rank, category="answerable", status="answered", error=None):
    return {"case_id": case_id, "method": method, "category": category, "first_known_anchor_rank": rank,
            "retrieval_latency_ms": 1.0 + len(case_id), "error": error, "answer": {"status": status}}


def report(ranks_by_method):
    results = [row(f"C{i:02d}", method, rank) for method, ranks in ranks_by_method.items()
               for i, rank in enumerate(ranks, 1)]
    results.append(row("Z01", "keyword", None, "missing_evidence", "abstained"))
    return {"kind": "support_evaluation_observations", "split": "development", "held_out_benchmark": False,
            "results": results, "dataset_sha256": "d", "corpus_fingerprint": "c", "recorded_at_utc": "t"}


class IntervalTests(unittest.TestCase):
    def test_wilson_matches_hand_computed_value_for_17_of_19(self):
        low, high = wilson_interval(17, 19)
        self.assertAlmostEqual(low, 0.6860, places=3)
        self.assertAlmostEqual(high, 0.9706, places=3)

    def test_wilson_stays_inside_zero_and_one_and_rejects_bad_counts(self):
        self.assertEqual(wilson_interval(0, 5)[0], 0.0)
        self.assertEqual(wilson_interval(5, 5)[1], 1.0)
        for args in ((6, 5), (-1, 5), (1, 0), (True, 5)):
            with self.assertRaises(ValidationError):
                wilson_interval(*args)

    def test_exact_sign_test(self):
        self.assertEqual(exact_sign_test(0, 0), 1.0)
        self.assertEqual(exact_sign_test(1, 0), 1.0)
        self.assertAlmostEqual(exact_sign_test(5, 0), 0.0625)
        self.assertAlmostEqual(exact_sign_test(2, 2), 1.0)

    def test_bootstrap_is_deterministic_and_brackets_the_mean(self):
        values = [1.0, 0.5, 0.0, 1.0, 0.25]
        first = bootstrap_mean_interval(values, resamples=500)
        self.assertEqual(first, bootstrap_mean_interval(values, resamples=500))
        self.assertLessEqual(first[0], sum(values) / 5)
        self.assertGreaterEqual(first[1], sum(values) / 5)
        with self.assertRaises(ValidationError):
            bootstrap_mean_interval([])


class SummarizeRunTests(unittest.TestCase):
    def setUp(self):
        self.ranks = {"keyword": [1, 2, None, 1], "vector": [1, 1, None, 3], "hybrid": [1, 2, 4, 1]}

    def test_hits_mrr_misses_and_pairs(self):
        summary = summarize_run(report(self.ranks))
        keyword = summary["methods"]["keyword"]
        self.assertEqual(keyword["known_anchor_hits_at_5"], 3)
        self.assertAlmostEqual(keyword["known_anchor_mrr_at_5"], (1 + .5 + 0 + 1) / 4)
        self.assertEqual(keyword["missed_case_ids"], ["C03"])
        self.assertEqual(keyword["rank_distribution"]["miss"], 1)
        pair = summary["comparisons"]["hybrid_minus_keyword"]
        self.assertEqual((pair["hit_only_in_first"], pair["hit_only_in_second"]), (0, 1))
        self.assertEqual(pair["exact_sign_test_p"], 1.0)
        self.assertEqual(set(summary["methods"]), set(METHODS))

    def test_qualitative_categories_are_excluded_from_aggregates(self):
        summary = summarize_run(report(self.ranks))
        self.assertEqual(summary["methods"]["keyword"]["answerable_cases"], 4)
        self.assertEqual(summary["methods"]["keyword"]["answer_status_by_category"]["missing_evidence"],
                         {"abstained": 1})

    def test_retrieval_errors_count_as_misses(self):
        data = report(self.ranks)
        target = next(r for r in data["results"] if r["method"] == "hybrid" and r["case_id"] == "C01")
        target["error"] = "boom"
        self.assertEqual(summarize_run(data)["methods"]["hybrid"]["known_anchor_hits_at_5"], 3)

    def test_output_is_labelled_unreviewed_development(self):
        summary = summarize_run(report(self.ranks))
        self.assertTrue(summary["development_only"])
        self.assertFalse(summary["human_reviewed"])
        self.assertFalse(summary["held_out_benchmark"])

    def test_holdout_other_kinds_and_mismatched_cases_are_rejected(self):
        for field, value in (("split", "holdout"), ("kind", "other"), ("held_out_benchmark", True)):
            data = report(self.ranks)
            data[field] = value
            with self.assertRaises(ValidationError):
                summarize_run(data)
        data = report(self.ranks)
        data["results"] = [r for r in data["results"] if not (r["method"] == "vector" and r["case_id"] == "C04")]
        with self.assertRaises(ValidationError):
            summarize_run(data)


if __name__ == "__main__":
    unittest.main()
