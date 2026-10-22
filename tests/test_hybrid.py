from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from test_models import example_source
from versionlens.hybrid import CANDIDATE_POOL, RRF_CONSTANT, hybrid_search
from versionlens.ingest import Corpus
from versionlens.models import Chunk, SearchRequest, ValidationError
from versionlens.retrieval import SearchHit
from versionlens.store import replace_corpus


def hit(text, *, version="0.28.1", score=1.0):
    source = example_source(version, text)
    return SearchHit(Chunk.create(source, "Test", 1, 1, text), score)


class HybridRetrievalTests(unittest.TestCase):
    def run_search(self, keyword_hits, vector_hits, *, limit=5, client=None):
        with patch("versionlens.hybrid.search", return_value=keyword_hits) as keyword, \
             patch("versionlens.hybrid.vector_search", return_value=vector_hits) as vector, \
             patch("versionlens.hybrid.load_chunks", return_value=()):
            results = hybrid_search(Path("index.sqlite3"), Path("vectors.json"),
                                    SearchRequest("How do proxies work?", "0.28.1", limit),
                                    client=client)
        return results, keyword, vector

    def test_agreement_across_engines_outweighs_a_single_first_place(self):
        lexical_first, shared, vector_first = hit("Lexical only"), hit("Shared evidence"), hit("Vector only")
        results, _, _ = self.run_search((lexical_first, shared), (vector_first, shared))
        self.assertEqual(results[0].chunk, shared.chunk)
        self.assertAlmostEqual(results[0].score, 2.0 / (RRF_CONSTANT + 2))
        self.assertEqual(len(results), 3)

    def test_pool_size_and_exact_version_are_passed_to_both_engines(self):
        client = object()
        _, keyword, vector = self.run_search((), (), limit=1, client=client)
        expected = SearchRequest("How do proxies work?", "0.28.1", CANDIDATE_POOL)
        keyword.assert_called_once_with(Path("index.sqlite3"), expected)
        vector.assert_called_once_with(Path("index.sqlite3"), Path("vectors.json"), expected, client=client)

    def test_raw_score_magnitudes_do_not_affect_fusion(self):
        one, two = hit("One", score=1e30), hit("Two", score=-1e30)
        original, _, _ = self.run_search((one, two), (two, one))
        changed, _, _ = self.run_search((replace(one, score=-123.0), replace(two, score=999.0)),
                                       (replace(two, score=0.001), replace(one, score=0.9)))
        self.assertEqual(original, changed)

    def test_equal_rank_scores_have_stable_chunk_id_order_and_limit(self):
        one, two = hit("One"), hit("Two")
        results, _, _ = self.run_search((one, two), (two, one), limit=1)
        self.assertEqual(results[0].chunk.chunk_id, min(one.chunk.chunk_id, two.chunk.chunk_id))

    def test_empty_lexical_results_keep_vector_candidates_without_a_threshold(self):
        candidate = hit("Nearest candidate", score=-0.25)
        results, _, _ = self.run_search((), (candidate,))
        self.assertEqual(results[0].chunk, candidate.chunk)
        self.assertAlmostEqual(results[0].score, 1.0 / (RRF_CONSTANT + 1))
        self.assertEqual(self.run_search((), ())[0], ())

    def test_either_engine_returning_wrong_version_fails_closed(self):
        wrong = hit("Wrong version", version="0.27.2")
        for keyword_hits, vector_hits in (((wrong,), ()), ((), (wrong,))):
            with self.subTest(keyword=bool(keyword_hits)), self.assertRaisesRegex(ValidationError, "another version"):
                self.run_search(keyword_hits, vector_hits)

    def test_duplicate_within_one_engine_cannot_inflate_fused_scores(self):
        candidate = hit("Duplicate candidate")
        with self.assertRaisesRegex(ValidationError, "duplicate chunk IDs"):
            self.run_search((candidate, candidate), ())

    def test_same_chunk_id_cannot_substitute_different_provenance(self):
        candidate = hit("Original candidate")
        forged = SearchHit(replace(candidate.chunk, text="Unrelated forged text"), 0.8)
        with self.assertRaisesRegex(ValidationError, "inconsistent source provenance"):
            self.run_search((candidate,), (forged,))

    def test_vector_failure_is_not_silently_replaced_by_keyword_results(self):
        with patch("versionlens.hybrid.search", return_value=(hit("Keyword candidate"),)), \
             patch("versionlens.hybrid.vector_search", side_effect=ValidationError("Stale vector index")), \
             patch("versionlens.hybrid.load_chunks", return_value=()):
            with self.assertRaisesRegex(ValidationError, "Stale vector index"):
                hybrid_search(Path("index.sqlite3"), Path("vectors.json"), SearchRequest("proxies", "0.28.1"))

    def test_corpus_change_between_engines_rejects_distinct_old_and_new_chunks(self):
        old = hit("The original proxies documentation.")
        new = hit("The replacement proxies documentation.")
        self.assertNotEqual(old.chunk.chunk_id, new.chunk.chunk_id)
        with TemporaryDirectory() as temporary:
            index = Path(temporary) / "source.sqlite3"
            replace_corpus(index, Corpus((old.chunk.source,), (old.chunk,)))

            def replace_before_vector(*args, **kwargs):
                replace_corpus(index, Corpus((new.chunk.source,), (new.chunk,)))
                return (new,)

            with patch("versionlens.hybrid.vector_search", side_effect=replace_before_vector):
                with self.assertRaisesRegex(ValidationError, "changed during hybrid retrieval"):
                    hybrid_search(index, Path(temporary) / "vectors.sqlite3",
                                  SearchRequest("proxies", "0.28.1"))


if __name__ == "__main__":
    unittest.main()
