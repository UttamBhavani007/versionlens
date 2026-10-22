from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from versionlens.embeddings import EmbeddingBatch, EmbeddingIdentity
from versionlens.ingest import Corpus, chunk_markdown
from versionlens.models import SearchRequest
from versionlens.store import connect, replace_corpus
from versionlens.vector_store import (
    VectorIndexError, build_vector_index, corpus_fingerprint, load_chunks, vector_search,
)

from test_models import example_source


def unit_vector(axis=0, direction=1.0):
    vector = [0.0] * 768
    vector[axis] = direction
    return tuple(vector)


class FakeEmbeddingClient:
    def __init__(self, vectors=None):
        self.current_identity = EmbeddingIdentity("nomic-embed-text:v1.5", "a" * 64, 768)
        self.document_vectors = vectors or {}
        self.query_vector = unit_vector()
        self.document_calls = []
        self.query_calls = []
        self.identity_calls = 0
        self.on_documents = None
        self.on_query = None
        self.on_identity = None

    def identity(self):
        self.identity_calls += 1
        if self.on_identity:
            self.on_identity(self)
        return self.current_identity

    def embed_documents(self, texts):
        self.document_calls.append(texts)
        if self.on_documents:
            self.on_documents(self)
        vectors = tuple(self.document_vectors.get(text, unit_vector()) for text in texts)
        return EmbeddingBatch(vectors, self.current_identity, len(texts) * 2, len(texts) * 100)

    def embed_query(self, question):
        self.query_calls.append(question)
        batch = EmbeddingBatch((self.query_vector,), self.current_identity, 3, 100)
        if self.on_query:
            self.on_query(self)
        return batch


class VectorStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.index = self.root / "source.sqlite3"
        self.vectors = self.root / "vectors.sqlite3"
        self.client = FakeEmbeddingClient()
        self.write_corpus(("0.28.1", "# Guide\nCurrent version documentation.\n"))

    def write_corpus(self, *documents):
        sources = []
        chunks = []
        for version, text in documents:
            source = example_source(version=version, text=text)
            sources.append(source)
            chunks.extend(chunk_markdown(source, text))
        corpus = Corpus(tuple(sources), tuple(chunks))
        replace_corpus(self.index, corpus)
        return corpus

    def build(self, client=None):
        return build_vector_index(self.index, self.vectors, client or self.client)

    def search(self, version="0.28.1", limit=5, client=None):
        return vector_search(
            self.index, self.vectors, SearchRequest("How does it work?", version, limit),
            client or self.client,
        )

    def snapshot(self):
        with sqlite3.connect(self.vectors) as connection:
            return (
                connection.execute("SELECT * FROM vector_metadata ORDER BY key").fetchall(),
                connection.execute("SELECT * FROM vectors ORDER BY chunk_id").fetchall(),
            )

    def test_build_records_full_identity_and_keeps_provenance_in_hits(self):
        stats = self.build()
        chunks = load_chunks(self.index)

        self.assertEqual(stats["chunks"], 1)
        self.assertEqual(stats["dimensions"], 768)
        self.assertEqual(stats["model_digest"], "a" * 64)
        self.assertEqual(stats["model"], "nomic-embed-text:v1.5")
        self.assertEqual(stats["corpus_fingerprint"], corpus_fingerprint(chunks))
        self.assertEqual(stats["prompt_tokens"], 2)
        self.assertEqual(stats["total_duration_ns"], 100)
        self.assertEqual(stats["versions"], ["0.28.1"])
        hit = self.search()[0]
        self.assertEqual(hit.chunk, chunks[0])
        self.assertEqual(hit.score, 1.0)
        self.assertEqual(hit.to_dict()["citation_url"], chunks[0].citation_url)

    def test_build_bounds_document_batches_at_sixteen(self):
        self.write_corpus(("0.28.1", "\n".join(f"# Heading {number}\nContent {number}." for number in range(35))))

        stats = self.build()

        self.assertEqual([len(batch) for batch in self.client.document_calls], [16, 16, 3])
        self.assertEqual(stats["chunks"], 35)
        self.assertEqual(stats["batches"], 3)

    def test_version_is_filtered_before_scoring_or_limiting(self):
        corpus = self.write_corpus(
            ("0.27.2", "# Old\nObsolete higher-scoring answer.\n"),
            ("0.28.1", "# New\nCurrent lower-scoring answer.\n"),
        )
        self.client.document_vectors = {
            chunk.text: unit_vector(0 if chunk.source.version == "0.27.2" else 1)
            for chunk in corpus.chunks
        }
        self.build()

        hits = self.search(limit=1)

        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].chunk.source.version, "0.28.1")
        self.assertEqual(hits[0].score, 0.0)

    def test_equal_scores_have_stable_chunk_id_order(self):
        self.write_corpus(("0.28.1", "# A\nFirst.\n# B\nSecond.\n# C\nThird.\n"))
        self.build()
        hits = self.search()
        self.assertEqual([hit.chunk.chunk_id for hit in hits], sorted(hit.chunk.chunk_id for hit in hits))

    def test_cosine_scores_are_sorted_without_a_confidence_threshold(self):
        corpus = self.write_corpus(("0.28.1", "# Positive\nOne.\n# Orthogonal\nTwo.\n# Negative\nThree.\n"))
        self.client.document_vectors = dict(zip(
            (chunk.text for chunk in corpus.chunks),
            (unit_vector(), unit_vector(1), unit_vector(0, -1.0)),
        ))
        self.build()
        self.assertEqual([hit.score for hit in self.search()], [1.0, 0.0, -1.0])

    def test_missing_cache_does_not_create_a_file_or_embed_query(self):
        with self.assertRaisesRegex(VectorIndexError, "not found"):
            self.search()
        self.assertFalse(self.vectors.exists())
        self.assertEqual(self.client.query_calls, [])

    def test_text_change_is_detected_even_with_an_unchanged_chunk_id(self):
        self.build()
        with connect(self.index) as connection:
            connection.execute("UPDATE chunks SET text='Changed text with the same identity'")
            connection.commit()

        with self.assertRaisesRegex(VectorIndexError, "stale"):
            self.search()
        self.assertEqual(self.client.query_calls, [])

    def test_source_metadata_change_is_detected(self):
        self.build()
        chunks = load_chunks(self.index)
        source = replace(chunks[0].source, title="New source title")
        changed = replace(chunks[0], source=source)
        replace_corpus(self.index, Corpus((source,), (changed,)))

        with self.assertRaisesRegex(VectorIndexError, "stale"):
            self.search()

    def test_version_reingest_invalidates_the_cache(self):
        self.build()
        self.write_corpus(("0.27.2", "# Guide\nCurrent version documentation.\n"))
        with self.assertRaisesRegex(VectorIndexError, "stale"):
            self.search(version="0.27.2")

    def test_digest_and_preprocessing_changes_invalidate_cache(self):
        self.build()
        other_client = FakeEmbeddingClient()
        other_client.current_identity = replace(other_client.current_identity, digest="b" * 64)
        with self.assertRaisesRegex(VectorIndexError, "stale"):
            self.search(client=other_client)
        with patch("versionlens.vector_store.PREPROCESSING_REVISION", "changed-revision"):
            with self.assertRaisesRegex(VectorIndexError, "stale"):
                self.search()

    def test_incomplete_or_wrong_version_vector_rows_are_rejected(self):
        self.build()
        with sqlite3.connect(self.vectors) as connection:
            connection.execute("UPDATE vectors SET version='0.27.2'")
        with self.assertRaisesRegex(VectorIndexError, "version metadata"):
            self.search()
        with sqlite3.connect(self.vectors) as connection:
            connection.execute("DELETE FROM vectors")
        with self.assertRaisesRegex(VectorIndexError, "incomplete"):
            self.search()

    def test_corrupt_cached_vectors_fail_before_query_embedding(self):
        self.build()
        invalid = ("not-json", json.dumps([1.0]), json.dumps([0.0] * 768),
                   json.dumps([float("nan")] + [0.0] * 767))
        for serialized in invalid:
            with self.subTest(vector=serialized[:30]):
                with sqlite3.connect(self.vectors) as connection:
                    connection.execute("UPDATE vectors SET vector_json=?", (serialized,))
                with self.assertRaises(VectorIndexError):
                    self.search()
        self.assertEqual(self.client.query_calls, [])

    def test_invalid_embedding_vectors_never_replace_a_previous_cache(self):
        self.build()
        previous = self.snapshot()
        text = load_chunks(self.index)[0].text
        for vector in (
            (1.0,), tuple([0.0] * 768), tuple([float("nan")] + [0.0] * 767),
            tuple([float("inf")] + [0.0] * 767), tuple([True] + [0.0] * 767),
            tuple([10 ** 1000] + [0.0] * 767),
        ):
            self.client.document_vectors = {text: vector}
            with self.subTest(vector_length=len(vector)), self.assertRaises(VectorIndexError):
                self.build()
            self.assertEqual(self.snapshot(), previous)

    def test_invalid_batches_never_publish_a_new_cache(self):
        identity = self.client.current_identity
        batches = (
            EmbeddingBatch((), identity, 1, 1),
            EmbeddingBatch((unit_vector(),), replace(identity, digest="b" * 64), 1, 1),
            EmbeddingBatch((unit_vector(),), identity, True, 1),
            EmbeddingBatch((unit_vector(),), identity, 1, -1),
        )
        for batch in batches:
            with self.subTest(batch=batch.identity.digest):
                with patch.object(self.client, "embed_documents", return_value=batch):
                    with self.assertRaises(VectorIndexError):
                        self.build()
                self.assertFalse(self.vectors.exists())

    def test_failed_embedding_preserves_previous_cache(self):
        self.build()
        previous = self.snapshot()
        with patch.object(self.client, "embed_documents", side_effect=RuntimeError("Local service failed")):
            with self.assertRaises(RuntimeError):
                self.build()
        self.assertEqual(self.snapshot(), previous)

    def test_source_change_during_build_prevents_publication(self):
        self.build()
        previous = self.snapshot()
        self.client.on_documents = lambda client: self.write_corpus(("0.28.1", "# Changed\nNew corpus.\n"))
        with self.assertRaisesRegex(VectorIndexError, "changed during embedding"):
            self.build()
        self.assertEqual(self.snapshot(), previous)

    def test_model_change_before_publication_preserves_cache(self):
        self.build()
        previous = self.snapshot()
        fresh_client = FakeEmbeddingClient()

        def change_on_recheck(client):
            if client.identity_calls == 2:
                client.current_identity = replace(client.current_identity, digest="b" * 64)

        fresh_client.on_identity = change_on_recheck
        with self.assertRaisesRegex(VectorIndexError, "changed before vector publication"):
            self.build(fresh_client)
        self.assertEqual(self.snapshot(), previous)

    def test_sqlite_failure_rolls_back_deletes_and_metadata_replacement(self):
        self.build()
        previous = self.snapshot()
        with sqlite3.connect(self.vectors) as connection:
            connection.execute(
                "CREATE TRIGGER reject_replacement BEFORE INSERT ON vectors "
                "BEGIN SELECT RAISE(ABORT, 'test rejection'); END"
            )
        with self.assertRaisesRegex(VectorIndexError, "previous index was preserved"):
            self.build()
        self.assertEqual(self.snapshot(), previous)

    def test_source_or_model_change_during_query_fails_closed(self):
        self.build()
        self.client.on_query = lambda client: setattr(
            client, "current_identity", replace(client.current_identity, digest="b" * 64)
        )
        with self.assertRaisesRegex(VectorIndexError, "changed while searching"):
            self.search()
        self.client = FakeEmbeddingClient()
        self.client.on_query = lambda client: self.write_corpus(("0.28.1", "# Updated\nChanged after query.\n"))
        with self.assertRaisesRegex(VectorIndexError, "changed during retrieval"):
            self.search()

    def test_invalid_model_dimensions_and_query_vectors_are_rejected(self):
        self.build()
        bad_client = FakeEmbeddingClient()
        object.__setattr__(bad_client.current_identity, "dimensions", 767)
        with self.assertRaisesRegex(VectorIndexError, "identity or dimensions"):
            self.search(client=bad_client)
        self.client.query_vector = unit_vector()[:-1]
        with self.assertRaisesRegex(VectorIndexError, "dimensions"):
            self.search()

    def test_same_database_cannot_be_used_for_source_and_sidecar(self):
        original = self.index.read_bytes()
        with self.assertRaisesRegex(VectorIndexError, "separate"):
            build_vector_index(self.index, self.index, self.client)
        with self.assertRaisesRegex(VectorIndexError, "separate"):
            vector_search(self.index, self.index, SearchRequest("Question", "0.28.1"), self.client)
        self.assertEqual(self.index.read_bytes(), original)

    def test_empty_corpus_and_unknown_sidecar_schema_are_not_overwritten(self):
        with sqlite3.connect(self.vectors) as connection:
            connection.execute("CREATE TABLE unrelated (value TEXT)")
            connection.execute("INSERT INTO unrelated VALUES ('keep')")
        with self.assertRaisesRegex(VectorIndexError, "Unknown vector sidecar schema"):
            self.build()
        with sqlite3.connect(self.vectors) as connection:
            self.assertEqual(connection.execute("SELECT value FROM unrelated").fetchall(), [("keep",)])
        with connect(self.index) as connection:
            connection.execute("DELETE FROM chunks")
            connection.commit()
        with self.assertRaisesRegex(VectorIndexError, "empty source index"):
            self.build()

    def test_rebuilding_is_idempotent_and_does_not_accumulate_vectors(self):
        first = self.build()
        before = self.snapshot()
        second = self.build()
        self.assertEqual(first, second)
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
