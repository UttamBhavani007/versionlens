"""Uncertainty summary for a recorded development run; it never executes retrieval or a model."""

from math import ceil, comb, sqrt
from random import Random
from statistics import median

from .models import ValidationError

METHODS = ("keyword", "vector", "hybrid")
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20261025


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if type(successes) is not int or type(total) is not int or total < 1 or not 0 <= successes <= total:
        raise ValidationError("Wilson interval needs 0 <= successes <= total and total >= 1.")
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return max(0.0, centre - margin), min(1.0, centre + margin)


def exact_sign_test(only_first: int, only_second: int) -> float:
    """Two-sided exact binomial p-value for discordant pairs (McNemar exact)."""
    discordant = only_first + only_second
    if discordant == 0:
        return 1.0
    tail = sum(comb(discordant, k) for k in range(min(only_first, only_second) + 1)) / 2 ** discordant
    return min(1.0, 2 * tail)


def _reciprocal(rank):
    return 0.0 if rank is None else 1 / rank


def bootstrap_mean_interval(values: list[float], *, resamples: int = BOOTSTRAP_RESAMPLES,
                            seed: int = BOOTSTRAP_SEED) -> tuple[float, float]:
    if not values:
        raise ValidationError("Bootstrap needs at least one paired value.")
    rng = Random(seed)
    count = len(values)
    means = sorted(sum(values[rng.randrange(count)] for _ in range(count)) / count for _ in range(resamples))
    return means[int(.025 * resamples)], means[ceil(.975 * resamples) - 1]


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[ceil(fraction * len(ordered)) - 1]


def summarize_run(report: dict) -> dict:
    if (not isinstance(report, dict) or report.get("kind") != "support_evaluation_observations"
            or report.get("split") != "development" or report.get("held_out_benchmark") is not False
            or not isinstance(report.get("results"), list)):
        raise ValidationError("Expected a recorded development run, not a holdout or another report kind.")
    rows = {method: [row for row in report["results"] if row.get("method") == method] for method in METHODS}
    if any(not rows[method] for method in METHODS):
        raise ValidationError("The report must contain all three methods.")
    answerable = {method: {row["case_id"]: row for row in rows[method] if row["category"] == "answerable"}
                  for method in METHODS}
    case_ids = sorted(answerable["keyword"])
    if not case_ids or any(sorted(answerable[method]) != case_ids for method in METHODS):
        raise ValidationError("Every method needs the same nonempty answerable cases.")

    def rank(method, case_id):
        row = answerable[method][case_id]
        return None if row.get("error") else row["first_known_anchor_rank"]

    methods = {}
    for method in METHODS:
        ranks = [rank(method, case_id) for case_id in case_ids]
        hits = sum(value is not None for value in ranks)
        reciprocal = [_reciprocal(value) for value in ranks]
        latencies = [row["retrieval_latency_ms"] for row in rows[method] if row.get("retrieval_latency_ms") is not None]
        statuses = {}
        for row in rows[method]:
            status = (row.get("answer") or {}).get("status", "error")
            bucket = statuses.setdefault(row["category"], {})
            bucket[status] = bucket.get(status, 0) + 1
        answered_answerable = statuses.get("answerable", {}).get("answered", 0)
        low, high = wilson_interval(hits, len(case_ids))
        mrr_low, mrr_high = bootstrap_mean_interval(reciprocal)
        a_low, a_high = wilson_interval(answered_answerable, len(case_ids))
        methods[method] = {
            "answerable_cases": len(case_ids),
            "known_anchor_hits_at_5": hits,
            "known_anchor_hit_at_5": hits / len(case_ids),
            "hit_at_5_wilson_95": [low, high],
            "known_anchor_mrr_at_5": sum(reciprocal) / len(reciprocal),
            "mrr_at_5_bootstrap_95": [mrr_low, mrr_high],
            "missed_case_ids": [case_id for case_id, value in zip(case_ids, ranks) if value is None],
            "rank_distribution": {str(k): ranks.count(k) for k in range(1, 6)} | {"miss": ranks.count(None)},
            "retrieval_latency_ms": {"count": len(latencies), "median": median(latencies),
                                      "p95_nearest_rank": _percentile(latencies, .95)},
            "answer_status_by_category": statuses,
            "answered_on_answerable": {"answered": answered_answerable, "of": len(case_ids),
                                        "wilson_95": [a_low, a_high]},
        }

    comparisons = {}
    for first, second in (("keyword", "vector"), ("keyword", "hybrid"), ("vector", "hybrid")):
        hit_a = {c: rank(first, c) is not None for c in case_ids}
        hit_b = {c: rank(second, c) is not None for c in case_ids}
        only_first = sum(hit_a[c] and not hit_b[c] for c in case_ids)
        only_second = sum(hit_b[c] and not hit_a[c] for c in case_ids)
        differences = [_reciprocal(rank(second, c)) - _reciprocal(rank(first, c)) for c in case_ids]
        low, high = bootstrap_mean_interval(differences)
        comparisons[f"{second}_minus_{first}"] = {
            "hit_only_in_first": only_first, "hit_only_in_second": only_second,
            "exact_sign_test_p": exact_sign_test(only_first, only_second),
            "mrr_difference": sum(differences) / len(differences),
            "mrr_difference_bootstrap_95": [low, high],
        }

    return {
        "schema_version": 1, "kind": "development_uncertainty_summary",
        "source_report_dataset_sha256": report.get("dataset_sha256"),
        "source_report_corpus_fingerprint": report.get("corpus_fingerprint"),
        "source_report_recorded_at_utc": report.get("recorded_at_utc"),
        "development_only": True, "human_reviewed": False, "held_out_benchmark": False,
        "method": {"hit_interval": "Wilson score, 95%",
                   "mrr_interval": f"percentile bootstrap, {BOOTSTRAP_RESAMPLES} resamples, seed {BOOTSTRAP_SEED}",
                   "paired_hit_test": "exact two-sided sign test on discordant cases",
                   "errors": "retrieval errors count as misses, as in the source report"},
        "methods": methods, "comparisons": comparisons,
        "limitations": [
            "Computed only from a recorded run; no retrieval or model was executed.",
            "Questions and anchors are AI-authored, source-checked and not human-reviewed.",
            "Small samples give wide intervals; paired p-values are not corrected for multiple comparisons.",
            "Hit and MRR refer to known nonexhaustive anchors, not answer accuracy or semantic citation correctness.",
        ],
    }
