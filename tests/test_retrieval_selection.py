from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from test_models import example_source
from versionlens.answering import answer
from versionlens.cli import main
from versionlens.ingest import Corpus, chunk_markdown
from versionlens.models import SearchRequest, ValidationError
from versionlens.retrieval import SearchHit
from versionlens.search_service import retrieve
from versionlens.store import replace_corpus


class RetrievalSelectionTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        text = "# Timeout\nRequests time out after five seconds of network inactivity.\n"
        source = example_source(text=text)
        chunks = chunk_markdown(source, text)
        self.index = self.root / "data/versionlens.sqlite3"
        self.vectors = self.root / "data/versionlens-vectors.sqlite3"
        replace_corpus(self.index, Corpus((source,), chunks))
        self.hit = SearchHit(chunks[0], .9)
        self.request = SearchRequest("timeout", "0.28.1")

    def test_default_keyword_search_never_constructs_an_embedding_client(self):
        with patch("versionlens.embeddings.LocalEmbeddingClient") as client:
            hits = retrieve(self.index, self.request)
        self.assertEqual(hits[0].chunk.chunk_id, self.hit.chunk.chunk_id)
        client.assert_not_called()

    def test_explicit_vector_route_preserves_caller_paths_and_client(self):
        client = object()
        with patch("versionlens.vector_store.vector_search", return_value=(self.hit,)) as vector:
            hits = retrieve(self.index, self.request, method="vector", vector_path=self.vectors, client=client)
        self.assertEqual(hits, (self.hit,))
        vector.assert_called_once_with(self.index, self.vectors, self.request, client)

    def test_invalid_method_or_missing_vector_cache_never_falls_back(self):
        for method, path in (("cloud", self.vectors), ("vector", None), ("hybrid", None)):
            with self.subTest(method=method), self.assertRaises(ValidationError):
                retrieve(self.index, self.request, method=method, vector_path=path)

    def test_search_cli_exposes_method_but_no_generated_answer(self):
        output = io.StringIO()
        with patch("versionlens.vector_store.vector_search", return_value=(self.hit,)), redirect_stdout(output):
            status = main(["--root", str(self.root), "search", "timeout", "--version", "0.28.1",
                           "--retriever", "vector"])
        result = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(result["mode"], "vector_retrieval_only")
        self.assertIsNone(result["answer"])
        self.assertEqual(result["hits"][0]["version"], "0.28.1")

    def test_vector_setup_error_is_reported_without_keyword_fallback(self):
        output, errors = io.StringIO(), io.StringIO()
        with patch("versionlens.vector_store.vector_search", side_effect=ValidationError("Rebuild vector index")), \
                redirect_stdout(output), redirect_stderr(errors):
            status = main(["--root", str(self.root), "search", "timeout", "--version", "0.28.1",
                           "--retriever", "vector"])
        self.assertEqual(status, 2)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(json.loads(errors.getvalue())["error"], "Rebuild vector index")

    def test_answer_checks_version_even_with_a_different_retrieval_engine(self):
        old = example_source("0.27.2", "Wrong version evidence.")
        old_hit = SearchHit(chunk_markdown(old, "Wrong version evidence.")[0], .9)
        with patch("versionlens.vector_store.vector_search", return_value=(old_hit,)), self.assertRaises(ValidationError):
            answer(self.index, self.request, retrieval_method="vector", vector_path=self.vectors)

    def test_empty_explicit_retrieval_keeps_generation_off(self):
        with patch("versionlens.hybrid.hybrid_search", return_value=()), \
                patch("versionlens.local_model.LocalModelClient.generate") as generate:
            result = answer(self.index, self.request, retrieval_method="hybrid", vector_path=self.vectors)
        generate.assert_not_called()
        self.assertEqual(result["retrieval_method"], "hybrid")
        self.assertEqual(result["reason"], "no_matching_evidence")
