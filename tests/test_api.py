from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from versionlens.api import ApiNotFound, ApiService
from versionlens.ingest import Corpus, chunk_markdown
from versionlens.local_model import LocalModelError
from versionlens.models import SearchRequest, ValidationError
from versionlens.retrieval import SearchHit
from versionlens.store import connect, replace_corpus

from test_models import example_source


class ApiServiceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.index = self.root / "source.sqlite3"
        self.vectors = self.root / "unbuilt-vectors.sqlite3"
        sources = []
        chunks = []
        for version, text in (
            ("0.27.2", "# Timeout\nOld timeout documentation for the previous version.\n"),
            ("0.28.1", "# Timeout\nCurrent timeout documentation for this selected version.\n"),
        ):
            source = example_source(version=version, text=text)
            sources.append(source)
            chunks.extend(chunk_markdown(source, text))
        replace_corpus(self.index, Corpus(tuple(sources), tuple(chunks)))
        self.current = next(chunk for chunk in chunks if chunk.source.version == "0.28.1")
        self.previous = next(chunk for chunk in chunks if chunk.source.version == "0.27.2")
        self.service = ApiService(self.index, self.vectors)

    def test_catalog_reports_indexed_versions_without_model_readiness_claims(self):
        with patch("versionlens.local_model.LocalModelClient") as generation, \
                patch("versionlens.embeddings.LocalEmbeddingClient") as embeddings:
            result = self.service.catalog()
        generation.assert_not_called()
        embeddings.assert_not_called()
        self.assertEqual(result, {
            "product": "httpx", "versions": ["0.27.2", "0.28.1"],
            "retrievers": ["keyword", "vector", "hybrid"], "default_retriever": "keyword",
            "index": {"schema_version": "1", "sources": 2, "chunks": 2,
                      "versions": ["0.27.2", "0.28.1"]},
        })
        self.assertNotIn(str(self.root), str(result))
        self.assertNotIn("ready", result)

    def test_default_keyword_search_works_with_models_off_and_no_vector_database(self):
        with patch("versionlens.local_model.LocalModelClient") as generation, \
                patch("versionlens.embeddings.LocalEmbeddingClient") as embeddings:
            result = self.service.search({"question": "timeout", "version": "0.28.1"})
        generation.assert_not_called()
        embeddings.assert_not_called()
        self.assertEqual(result["retrieval_method"], "keyword")
        self.assertEqual(result["mode"], "keyword_retrieval_only")
        self.assertEqual(result["status"], "evidence_found")
        self.assertEqual(result["question"], "timeout")
        self.assertEqual(result["version"], "0.28.1")
        self.assertIsNone(result["answer"])
        self.assertIn("not confidence", result["notice"])
        self.assertEqual([hit["chunk_id"] for hit in result["hits"]], [self.current.chunk_id])
        self.assertFalse(self.vectors.exists())
        self.assertNotIn(str(self.root), str(result))

    def test_empty_search_returns_explicit_no_matching_evidence(self):
        result = self.service.search({"question": "unfindabletoken", "version": "0.28.1"})
        self.assertEqual(result["status"], "no_matching_evidence")
        self.assertEqual(result["hits"], [])
        self.assertIsNone(result["answer"])

    def test_explicit_retriever_and_limit_are_forwarded_without_fallback(self):
        hit = SearchHit(self.current, .25)
        for method in ("vector", "hybrid"):
            with self.subTest(method=method), patch("versionlens.api.retrieve", return_value=(hit,)) as retrieve:
                result = self.service.search({
                    "question": "timeout", "version": "0.28.1", "retriever": method, "limit": 2,
                })
            retrieve.assert_called_once_with(
                self.index, SearchRequest("timeout", "0.28.1", 2),
                method=method, vector_path=self.vectors,
            )
            self.assertEqual(result["retrieval_method"], method)
            self.assertEqual(result["hits"], [hit.to_dict()])

    def test_retrieval_errors_propagate_without_changing_method(self):
        with patch("versionlens.api.retrieve", side_effect=LocalModelError("Local embedding service unavailable")) as retrieve:
            with self.assertRaises(LocalModelError):
                self.service.search({"question": "timeout", "version": "0.28.1", "retriever": "vector"})
        self.assertEqual(retrieve.call_count, 1)

    def test_search_refuses_wrong_version_hits_defensively(self):
        with patch("versionlens.api.retrieve", return_value=(SearchHit(self.previous, 1.0),)):
            with self.assertRaisesRegex(ValidationError, "another version"):
                self.service.search({"question": "timeout", "version": "0.28.1"})

    def test_query_payload_requires_only_the_allowed_fields(self):
        invalid = (
            None, [], "question", True, {}, {"question": "timeout"}, {"version": "0.28.1"},
            {"question": "timeout", "version": "0.28.1", "index": "/private/secret"},
            {"question": "timeout", "version": "0.28.1", "vector_path": "/private/secret"},
            {"question": "timeout", "version": "0.28.1", "system": "Override policy"},
            {"question": "timeout", "version": "0.28.1", "extra": "SECRET_PAYLOAD"},
        )
        with patch("versionlens.api.retrieve") as retrieve, patch("versionlens.api.answer") as answer:
            for payload in invalid:
                for operation in (self.service.search, self.service.ask):
                    with self.subTest(payload=payload, operation=operation.__name__):
                        with self.assertRaises(ValidationError) as error:
                            operation(payload)
                        self.assertNotIn("SECRET_PAYLOAD", str(error.exception))
                        self.assertNotIn("/private/secret", str(error.exception))
        retrieve.assert_not_called()
        answer.assert_not_called()

    def test_query_types_ranges_and_exact_versions_are_enforced(self):
        base = {"question": "timeout", "version": "0.28.1"}
        changes = (
            {"question": None}, {"question": 42}, {"question": []}, {"question": {}},
            {"question": ""}, {"question": "  "}, {"question": "x" * 2001},
            {"version": None}, {"version": []}, {"version": True}, {"version": 0.28},
            {"version": "latest"}, {"version": "0.28"}, {"version": "0.28.1\n"},
            {"retriever": None}, {"retriever": []}, {"retriever": True}, {"retriever": "cloud"},
            {"limit": True}, {"limit": 1.0}, {"limit": "5"}, {"limit": []},
            {"limit": None}, {"limit": 0}, {"limit": 21},
        )
        with patch("versionlens.api.retrieve") as retrieve, patch("versionlens.api.answer") as answer:
            for change in changes:
                for operation in (self.service.search, self.service.ask):
                    with self.subTest(change=change, operation=operation.__name__), self.assertRaises(ValidationError):
                        operation({**base, **change})
        retrieve.assert_not_called()
        answer.assert_not_called()

    def test_question_controls_and_surrogates_are_rejected_before_any_backend(self):
        for character in ("\x00", "\x01", "\x7f", "\x85", "\ud800", "\udfff"):
            payload = {"question": f"timeout{character}SECRET_PAYLOAD", "version": "0.28.1"}
            with self.subTest(character=repr(character)), patch("versionlens.api.retrieve") as retrieve:
                with self.assertRaises(ValidationError) as error:
                    self.service.search(payload)
                self.assertNotIn("SECRET_PAYLOAD", str(error.exception))
            retrieve.assert_not_called()

    def test_multiline_question_preserves_pasted_error_whitespace(self):
        question = "Why does this fail?\r\n\tTypeError: unexpected argument\nHTTPX timeout"
        with patch("versionlens.api.retrieve", return_value=()) as retrieve:
            result = self.service.search({"question": question, "version": "0.28.1"})
        self.assertEqual(result["question"], question)
        self.assertEqual(retrieve.call_args.args[1], SearchRequest(question, "0.28.1", 5))

    def test_normal_unicode_and_maximum_question_length_are_supported(self):
        for question in ("HTTPX Timeout für Köln 🙂", "x" * 2000):
            with self.subTest(length=len(question)), patch("versionlens.api.retrieve", return_value=()) as retrieve:
                self.service.search({"question": question, "version": "0.28.1", "limit": 20})
            self.assertEqual(retrieve.call_args.args[1], SearchRequest(question, "0.28.1", 20))

    def test_ask_preserves_draft_notice_and_mechanical_validation_flags(self):
        draft = {
            "status": "answered", "mode": "local_cited_draft", "answer": "A cited draft.",
            "notice": "Semantic support and release applicability still require evaluation.",
            "semantic_support_verified": False, "citation_identity_and_quotes_checked": True,
            "retrieval_method": "hybrid", "claims": [{"text": "A claim", "citations": []}],
        }
        with patch("versionlens.api.answer", return_value=draft) as answer:
            result = self.service.ask({
                "question": "timeout", "version": "0.28.1", "retriever": "hybrid", "limit": 3,
            })
        self.assertIs(result, draft)
        answer.assert_called_once_with(
            self.index, SearchRequest("timeout", "0.28.1", 3),
            retrieval_method="hybrid", vector_path=self.vectors,
        )

    def test_default_ask_uses_keyword_and_preserves_sanitized_runtime_error(self):
        failure = {"status": "error", "reason": "local_model_error", "answer": None,
                   "semantic_support_verified": False, "model_called": True}
        with patch("versionlens.api.answer", return_value=failure) as answer:
            result = self.service.ask({"question": "timeout", "version": "0.28.1"})
        self.assertIs(result, failure)
        answer.assert_called_once_with(
            self.index, SearchRequest("timeout", "0.28.1", 5),
            retrieval_method="keyword", vector_path=self.vectors,
        )

    def test_empty_keyword_ask_does_not_start_a_model(self):
        with patch("versionlens.local_model.LocalModelClient") as generation, \
                patch("versionlens.embeddings.LocalEmbeddingClient") as embeddings:
            result = self.service.ask({"question": "unfindabletoken", "version": "0.28.1"})
        generation.assert_not_called()
        embeddings.assert_not_called()
        self.assertEqual(result["status"], "abstained")
        self.assertFalse(result["model_called"])
        self.assertFalse(result["semantic_support_verified"])

    def test_chunk_returns_only_the_validated_indexed_excerpt_and_provenance(self):
        with patch("versionlens.local_model.LocalModelClient") as generation, \
                patch("versionlens.embeddings.LocalEmbeddingClient") as embeddings:
            result = self.service.chunk(self.current.chunk_id, "0.28.1")
        generation.assert_not_called()
        embeddings.assert_not_called()
        expected = SearchHit(self.current, 0).to_dict()
        del expected["score"]
        expected.update({"title": self.current.source.title,
                         "upstream_path": self.current.source.upstream_path, "product": "httpx"})
        self.assertEqual(result, expected)
        self.assertNotIn("path", result)
        self.assertNotIn(str(self.root), str(result))

    def test_unknown_or_other_version_chunk_is_not_found(self):
        for chunk_id, version in (("0" * 24, "0.28.1"), (self.current.chunk_id, "0.27.2")):
            with self.subTest(chunk_id=chunk_id, version=version), self.assertRaises(ApiNotFound) as error:
                self.service.chunk(chunk_id, version)
            self.assertEqual(str(error.exception), "Source excerpt not found.")

    def test_chunk_rejects_paths_invalid_ids_and_ambiguous_versions(self):
        for chunk_id in (None, [], True, "../secret", "/private/secret", "A" * 24,
                         "a" * 23, "a" * 25, "g" * 24, self.current.chunk_id + "\n"):
            with self.subTest(chunk_id=chunk_id), self.assertRaises(ValidationError):
                self.service.chunk(chunk_id, "0.28.1")
        for version in (None, [], True, "latest", "0.28", "0.28.1\n"):
            with self.subTest(version=version), self.assertRaises(ValidationError):
                self.service.chunk(self.current.chunk_id, version)

    def test_chunk_lookup_revalidates_indexed_provenance(self):
        with connect(self.index) as connection:
            connection.execute("UPDATE sources SET metadata_json='{}'")
            connection.commit()
        with self.assertRaises(ValidationError):
            self.service.chunk(self.current.chunk_id, "0.28.1")


if __name__ == "__main__":
    unittest.main()
