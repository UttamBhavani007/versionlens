"""Access-policy regressions with synthetic content and model-free adapters.

These tests exercise confidentiality boundaries. They do not establish model
faithfulness or production authentication for the local demonstration profiles.
"""

from contextlib import closing
from dataclasses import FrozenInstanceError, asdict, replace
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from test_answering import FakeGenerator
from test_models import example_source
from test_vector_store import FakeEmbeddingClient, unit_vector
from versionlens.api import ApiNotFound, ApiService
from versionlens.answering import answer, select_evidence
from versionlens.hybrid import hybrid_search
from versionlens.ingest import Corpus, chunk_markdown
from versionlens.models import SearchRequest, Source, ValidationError
from versionlens.retrieval import SearchHit, search
from versionlens.search_service import retrieve
from versionlens.store import connect, index_stats, replace_corpus
from versionlens.updates import delete_snapshot
from versionlens.vector_store import VectorIndexError, build_vector_index, vector_search


VERSION = "0.28.1"
PREVIOUS = "0.27.2"
PUBLIC_TEXT = "# Public guide\n\nThe public timeout guidance remains available to all profiles.\n"
RESTRICTED_TEXT = (
    "# SYNTHETIC DEMO: Orion escalation\n\n"
    "The orion timeout escalation code is AMBER-NINE for the current snapshot.\n"
)
OLD_RESTRICTED_TEXT = (
    "# SYNTHETIC DEMO: Orion escalation\n\n"
    "The orion timeout escalation code is BLUE-THREE for the previous snapshot.\n"
)
ABSTAIN = {"decision": "insufficient_evidence", "claims": []}


def synthetic_source(text=RESTRICTED_TEXT, *, version=VERSION, access="support", filename="orion.md"):
    digest = sha256(text.encode("utf-8")).hexdigest()
    return Source(
        source_id=f"synthetic:httpx:{version}:{filename}", product="httpx", version=version,
        path=f"data/synthetic/httpx/{version}/{filename}", upstream_path=filename,
        commit=digest, sha256=digest,
        url=f"versionlens://synthetic/httpx/{version}/{filename}?sha256={digest}",
        title="SYNTHETIC DEMO: Orion escalation", source_kind="synthetic", access=access,
    )


class PermissionPolicyTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.index = self.root / "sources.sqlite3"
        self.vectors = self.root / "vectors.sqlite3"
        self.public = example_source(VERSION, PUBLIC_TEXT)
        self.restricted = synthetic_source()
        self.previous = synthetic_source(OLD_RESTRICTED_TEXT, version=PREVIOUS)
        sources = (self.public, self.restricted, self.previous)
        texts = (PUBLIC_TEXT, RESTRICTED_TEXT, OLD_RESTRICTED_TEXT)
        self.chunks = tuple(chunk for source, text in zip(sources, texts)
                            for chunk in chunk_markdown(source, text))
        self.corpus = Corpus(sources, self.chunks)
        replace_corpus(self.index, self.corpus)
        self.embedding = FakeEmbeddingClient({
            chunk.text: unit_vector(axis=1 if chunk.source.access == "public" else 0)
            for chunk in self.chunks
        })
        build_vector_index(self.index, self.vectors, self.embedding)
        self.public_chunk = next(chunk for chunk in self.chunks if chunk.source == self.public)
        self.restricted_chunk = next(chunk for chunk in self.chunks if chunk.source == self.restricted)
        self.public_api = ApiService(self.index, self.vectors, access_profile="public")
        self.support_api = ApiService(self.index, self.vectors, access_profile="support")

    def request(self, question="orion", *, profile="public", version=VERSION, limit=5):
        return SearchRequest(question, version, limit, access_profile=profile)

    def assert_public_only(self, hits):
        self.assertTrue(hits, "Public candidates must remain available before the result limit")
        self.assertTrue(all(hit.chunk.source.access == "public" for hit in hits))
        self.assertTrue(all(hit.chunk.source.version == VERSION for hit in hits))
        self.assertNotIn("AMBER-NINE", json.dumps([hit.to_dict() for hit in hits]))
        self.assertNotIn("BLUE-THREE", json.dumps([hit.to_dict() for hit in hits]))

    def test_default_profile_is_public_and_request_is_immutable(self):
        request = SearchRequest("orion", VERSION)
        self.assertEqual(request.access_profile, "public")
        self.assertTrue(request.allows(self.public))
        self.assertFalse(request.allows(self.restricted))
        with self.assertRaises(FrozenInstanceError):
            request.access_profile = "support"

    def test_unknown_profiles_are_rejected_before_retrieval(self):
        for profile in ("admin", "SUPPORT", "", None, [], {}, True):
            with self.subTest(profile=profile), self.assertRaises(ValidationError):
                self.request(profile=profile)
            with self.subTest(api_profile=profile), self.assertRaises(ValidationError):
                ApiService(self.index, self.vectors, access_profile=profile)

    def test_unknown_acl_and_provenance_kind_fail_closed(self):
        for access in ("admin", "PUBLIC", "", None, [], True):
            with self.subTest(access=access), self.assertRaises(ValidationError):
                replace(self.restricted, access=access)
        for kind in ("internal", "", None, [], True):
            with self.subTest(source_kind=kind), self.assertRaises(ValidationError):
                replace(self.restricted, source_kind=kind)

    def test_upstream_document_cannot_be_relabelled_as_private_synthetic_evidence(self):
        for change in ({"access": "support"}, {"source_kind": "synthetic"}):
            with self.subTest(change=change), self.assertRaises(ValidationError):
                replace(self.public, **change)

    def test_synthetic_provenance_cannot_impersonate_github_sources(self):
        for change in (
            {"url": self.public.url}, {"commit": self.public.commit},
            {"source_id": self.public.source_id}, {"path": self.public.path},
            {"title": "Official HTTPX support instructions"},
            {"upstream_path": "../orion.md"},
        ):
            with self.subTest(change=change), self.assertRaises(ValidationError):
                replace(self.restricted, **change)
        self.assertEqual(self.restricted.commit, self.restricted.sha256)
        self.assertEqual(self.restricted_chunk.citation_url,
                         f"/api/chunks/{self.restricted_chunk.chunk_id}?version={VERSION}")

    def test_public_synthetic_documents_are_allowed_by_both_profiles(self):
        public_synthetic = replace(self.restricted, access="public")
        self.assertTrue(self.request().allows(public_synthetic))
        self.assertTrue(self.request(profile="support").allows(public_synthetic))
        self.assertTrue(self.request(profile="support").allows(self.restricted))

    def test_keyword_does_not_return_restricted_only_matches_to_public(self):
        self.assertEqual(search(self.index, self.request()), ())
        self.assertNotEqual(search(self.index, self.request(profile="support")), ())

    def test_keyword_permission_filter_precedes_result_limit(self):
        hits = search(self.index, self.request("timeout orion", limit=1))
        self.assert_public_only(hits)
        self.assertEqual(hits[0].chunk.chunk_id, self.public_chunk.chunk_id)

    def test_vector_permission_filter_precedes_cosine_limit(self):
        # The restricted chunks have cosine 1, the public chunk cosine 0.
        # Filtering only the already-selected nearest hit would lose the public hit.
        hits = vector_search(self.index, self.vectors, self.request(limit=1), self.embedding)
        self.assert_public_only(hits)
        self.assertEqual(hits[0].chunk.chunk_id, self.public_chunk.chunk_id)
        support_hits = vector_search(self.index, self.vectors,
                                     self.request(profile="support", limit=1), self.embedding)
        self.assertEqual(support_hits[0].chunk.chunk_id, self.restricted_chunk.chunk_id)

    def test_hybrid_keeps_public_candidates_when_restricted_neighbors_dominate(self):
        hits = hybrid_search(self.index, self.vectors, self.request(limit=1), self.embedding)
        self.assert_public_only(hits)
        self.assertEqual(hits[0].chunk.chunk_id, self.public_chunk.chunk_id)

    def test_all_retrievers_preserve_profile_and_exact_version(self):
        for method in ("keyword", "vector", "hybrid"):
            for profile in ("public", "support"):
                request = self.request("timeout orion", profile=profile)
                with self.subTest(method=method, profile=profile):
                    hits = retrieve(self.index, request, method=method,
                                    vector_path=self.vectors, client=self.embedding)
                    self.assertTrue(hits)
                    self.assertTrue(all(hit.chunk.source.version == VERSION for hit in hits))
                    self.assertTrue(all(request.allows(hit.chunk.source) for hit in hits))
                    self.assertNotIn("BLUE-THREE", json.dumps([hit.to_dict() for hit in hits]))

    def test_public_source_inspection_hides_existing_restricted_ids(self):
        for chunk_id in (self.restricted_chunk.chunk_id, "0" * 24):
            with self.subTest(chunk_id=chunk_id), self.assertRaises(ApiNotFound) as error:
                self.public_api.chunk(chunk_id, VERSION)
            self.assertEqual(str(error.exception), "Source excerpt not found.")
        allowed = self.public_api.chunk(self.public_chunk.chunk_id, VERSION)
        self.assertEqual(allowed["text"], self.public_chunk.text)

    def test_support_inspector_keeps_synthetic_provenance_and_version(self):
        result = self.support_api.chunk(self.restricted_chunk.chunk_id, VERSION)
        self.assertEqual(result["source_kind"], "synthetic")
        self.assertEqual(result["access"], "support")
        self.assertEqual(result["source_sha256"], self.restricted.sha256)
        self.assertEqual(result["text"], self.restricted_chunk.text)
        with self.assertRaises(ApiNotFound):
            self.support_api.chunk(self.restricted_chunk.chunk_id, PREVIOUS)

    def test_catalog_does_not_expose_restricted_document_counts_or_versions(self):
        catalog = self.public_api.catalog()
        self.assertEqual(catalog["access_profile"], "public")
        self.assertIs(catalog["permission_demo"], True)
        self.assertEqual(catalog["index"]["sources"], 1)
        self.assertEqual(catalog["index"]["chunks"], 1)
        self.assertEqual(catalog["versions"], [VERSION])
        self.assertNotIn(PREVIOUS, json.dumps(catalog))
        self.assertNotIn(self.restricted.source_id, json.dumps(catalog))
        support_catalog = self.support_api.catalog()
        self.assertEqual(support_catalog["index"]["sources"], 3)
        self.assertEqual(support_catalog["versions"], [PREVIOUS, VERSION])

    def test_browser_cannot_promote_itself_in_search_or_ask_payload(self):
        original = {"question": "orion", "version": VERSION}
        for field in ("role", "roles", "access", "profile", "access_profile"):
            for method in ("search", "ask"):
                with self.subTest(field=field, method=method), \
                     patch("versionlens.api.retrieve") as retrieval, \
                     patch("versionlens.api.answer") as generation:
                    with self.assertRaises(ValidationError):
                        getattr(self.public_api, method)({**original, field: "support"})
                    retrieval.assert_not_called()
                    generation.assert_not_called()

    def test_api_uses_trusted_profile_for_retrieval_and_answering(self):
        query = {"question": "orion", "version": VERSION}
        self.assertEqual(self.public_api.search(query)["hits"], [])
        support_result = self.support_api.search(query)
        self.assertEqual(support_result["hits"][0]["source_id"], self.restricted.source_id)
        with patch("versionlens.api.answer", return_value={"status": "abstained"}) as generation:
            self.support_api.ask(query)
        request = generation.call_args.args[1]
        self.assertEqual(request.access_profile, "support")

    def test_keyword_answer_without_authorized_matches_skips_generation(self):
        generator = FakeGenerator(ABSTAIN)
        result = answer(self.index, self.request(), generator)
        self.assertEqual(result["status"], "abstained")
        self.assertEqual(result["reason"], "no_matching_evidence")
        self.assertFalse(result["model_called"])
        self.assertIsNone(result["answer"])
        self.assertEqual(generator.calls, [])
        self.assertNotIn("AMBER-NINE", json.dumps(result))

    def test_experimental_lexical_gate_ignores_restricted_matches(self):
        for method in ("vector", "hybrid"):
            generator = FakeGenerator(ABSTAIN)
            with self.subTest(method=method), patch("versionlens.search_service.retrieve") as retrieval:
                result = answer(self.index, self.request(), generator,
                                retrieval_method=method, vector_path=self.vectors,
                                embedding_client=self.embedding)
                self.assertEqual(result["reason"], "no_lexical_support_for_experimental_retrieval")
                self.assertFalse(result["model_called"])
                retrieval.assert_not_called()
                self.assertEqual(generator.calls, [])
        self.assertEqual(self.embedding.query_calls, [])

    def test_public_generation_context_contains_no_restricted_text(self):
        for method in ("keyword", "vector", "hybrid"):
            generator = FakeGenerator(ABSTAIN)
            with self.subTest(method=method):
                result = answer(self.index, self.request("timeout"), generator,
                                retrieval_method=method, vector_path=self.vectors,
                                embedding_client=self.embedding)
                self.assertTrue(result["model_called"])
                prompt = json.dumps(generator.calls[0][1])
                self.assertIn("public timeout guidance", prompt)
                self.assertNotIn("AMBER-NINE", prompt)
                self.assertNotIn("BLUE-THREE", prompt)
                self.assertFalse(result["semantic_support_verified"])

    def test_support_generation_context_uses_requested_snapshot_only(self):
        for method in ("keyword", "vector", "hybrid"):
            generator = FakeGenerator(ABSTAIN)
            with self.subTest(method=method):
                result = answer(self.index, self.request(profile="support"), generator,
                                retrieval_method=method, vector_path=self.vectors,
                                embedding_client=self.embedding)
                self.assertTrue(result["model_called"])
                prompt = json.dumps(generator.calls[0][1])
                self.assertIn("AMBER-NINE", prompt)
                self.assertNotIn("BLUE-THREE", prompt)

    def test_evidence_selection_rejects_forged_unauthorized_hits(self):
        forbidden = SearchHit(self.restricted_chunk, 100.0)
        with self.assertRaises(ValidationError):
            select_evidence((forbidden,), VERSION, access_profile="public")
        support = select_evidence((forbidden,), VERSION, access_profile="support")
        self.assertEqual(support[0].hit.chunk, self.restricted_chunk)

    def test_answer_defense_rejects_unauthorized_retriever_output_before_model(self):
        generator = FakeGenerator(ABSTAIN)
        with patch("versionlens.answering.search", return_value=(SearchHit(self.restricted_chunk, 100.0),)):
            with self.assertRaises(ValidationError):
                answer(self.index, self.request(), generator)
        self.assertEqual(generator.calls, [])

    def test_hybrid_defense_rejects_unauthorized_engine_candidates(self):
        forbidden = SearchHit(self.restricted_chunk, 100.0)
        for keyword_hits, vector_hits in (((forbidden,), ()), ((), (forbidden,))):
            with self.subTest(keyword=bool(keyword_hits)), \
                 patch("versionlens.hybrid.search", return_value=keyword_hits), \
                 patch("versionlens.hybrid.vector_search", return_value=vector_hits):
                with self.assertRaises(ValidationError):
                    hybrid_search(self.index, self.vectors, self.request(), self.embedding)

    def test_permission_change_rechecks_existing_chunk_id_and_invalidates_vectors(self):
        public_source = replace(self.restricted, access="public")
        sources = tuple(public_source if source == self.restricted else source
                        for source in self.corpus.sources)
        chunks = tuple(replace(chunk, source=public_source) if chunk.source == self.restricted else chunk
                       for chunk in self.corpus.chunks)
        replace_corpus(self.index, Corpus(sources, chunks))
        inspected = self.public_api.chunk(self.restricted_chunk.chunk_id, VERSION)
        self.assertEqual(inspected["access"], "public")
        self.assertIn("AMBER-NINE", inspected["text"])
        with self.assertRaises(VectorIndexError):
            vector_search(self.index, self.vectors, self.request(), self.embedding)
        replace_corpus(self.index, self.corpus)
        with self.assertRaises(ApiNotFound):
            self.public_api.chunk(self.restricted_chunk.chunk_id, VERSION)

    def test_permission_revocation_during_generation_suppresses_the_entire_draft(self):
        public_source = replace(self.restricted, access="public")
        sources = tuple(public_source if source == self.restricted else source
                        for source in self.corpus.sources)
        chunks = tuple(replace(chunk, source=public_source) if chunk.source == self.restricted else chunk
                       for chunk in self.corpus.chunks)
        replace_corpus(self.index, Corpus(sources, chunks))
        owner = self

        class RevokingGenerator(FakeGenerator):
            def generate(self, system, prompt, schema):
                response = super().generate(system, prompt, schema)
                replace_corpus(owner.index, owner.corpus)
                return response

        generator = RevokingGenerator({"decision": "answer", "claims": [{
            "text": "The orion timeout escalation code is AMBER-NINE.",
            "citations": [{"evidence_id": "E1", "quote_id": "Q1"}],
        }]})
        result = answer(self.index, self.request(), generator)
        self.assertEqual(len(generator.calls), 1)
        self.assertIn("AMBER-NINE", json.dumps(generator.calls[0][1]))
        self.assertEqual(result["status"], "abstained")
        self.assertEqual(result["reason"], "evidence_changed")
        self.assertEqual(result["claims"], [])
        self.assertEqual(result["evidence_ids"], [])
        self.assertIsNone(result["answer"])
        self.assertFalse(result["citation_identity_and_quotes_checked"])
        self.assertNotIn("AMBER-NINE", json.dumps(result))
        with self.assertRaises(ApiNotFound):
            self.public_api.chunk(self.restricted_chunk.chunk_id, VERSION)

    def test_deleting_the_only_snapshot_during_generation_withholds_stale_output(self):
        replace_corpus(self.index, Corpus((self.public,), (self.public_chunk,)))
        owner = self

        class DeletingGenerator(FakeGenerator):
            def generate(self, system, prompt, schema):
                response = super().generate(system, prompt, schema)
                delete_snapshot(owner.index, VERSION)
                return response

        generator = DeletingGenerator({"decision": "answer", "claims": [{
            "text": "The public timeout guidance is available.",
            "citations": [{"evidence_id": "E1", "quote_id": "Q1"}],
        }]})
        result = answer(self.index, self.request("timeout"), generator)
        self.assertEqual(len(generator.calls), 1)
        self.assertTrue(result["model_called"])
        self.assertEqual(index_stats(self.index)["sources"], 0)
        self.assertEqual(index_stats(self.index)["chunks"], 0)
        self.assertEqual(result["status"], "abstained")
        self.assertEqual(result["reason"], "evidence_changed")
        self.assertEqual(result["claims"], [])
        self.assertEqual(result["evidence_ids"], [])
        self.assertIsNone(result["answer"])
        self.assertFalse(result["citation_identity_and_quotes_checked"])
        self.assertNotIn("The public timeout guidance is available.", json.dumps(result))

    def test_explicit_reingestion_migrates_legacy_public_index_without_publishing_restricted_rows(self):
        legacy = self.root / "legacy.sqlite3"
        # This is the actual previous storage contract: source metadata had no
        # dedicated access/kind columns. A real file tests ALTER/FTS behavior.
        legacy_schema = """
        CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE sources (
            source_id TEXT PRIMARY KEY, version TEXT NOT NULL, metadata_json TEXT NOT NULL
        );
        CREATE TABLE chunks (
            rowid INTEGER PRIMARY KEY, chunk_id TEXT NOT NULL UNIQUE,
            source_id TEXT NOT NULL REFERENCES sources(source_id) ON DELETE CASCADE,
            version TEXT NOT NULL, section TEXT NOT NULL, start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL, text TEXT NOT NULL
        );
        CREATE INDEX chunks_version ON chunks(version);
        CREATE VIRTUAL TABLE chunk_fts USING fts5(
            section, text, content='chunks', content_rowid='rowid',
            tokenize='unicode61 remove_diacritics 2'
        );
        CREATE TRIGGER chunks_ai AFTER INSERT ON chunks BEGIN
            INSERT INTO chunk_fts(rowid, section, text) VALUES(new.rowid, new.section, new.text);
        END;
        CREATE TRIGGER chunks_ad AFTER DELETE ON chunks BEGIN
            INSERT INTO chunk_fts(chunk_fts,rowid,section,text)
                VALUES('delete',old.rowid,old.section,old.text);
        END;
        """
        with closing(sqlite3.connect(legacy)) as connection, connection:
            connection.executescript(legacy_schema)
            connection.execute("INSERT INTO metadata VALUES ('schema_version','1')")
            metadata = asdict(self.public)
            metadata.pop("access")
            metadata.pop("source_kind")
            connection.execute("INSERT INTO sources VALUES (?,?,?)", (
                self.public.source_id, VERSION, json.dumps(metadata, sort_keys=True),
            ))
            chunk = self.public_chunk
            connection.execute(
                "INSERT INTO chunks(chunk_id,source_id,version,section,start_line,end_line,text) "
                "VALUES(?,?,?,?,?,?,?)", (chunk.chunk_id, chunk.source.source_id, VERSION,
                    chunk.section, chunk.start_line, chunk.end_line, chunk.text),
            )
        with self.assertRaises(ValidationError):
            index_stats(legacy)
        stats = replace_corpus(legacy, self.corpus)
        self.assertEqual(stats["schema_version"], "2")
        self.assertEqual(stats["sources"], 3)
        public_api = ApiService(legacy, self.vectors, access_profile="public")
        self.assertEqual(public_api.catalog()["index"]["sources"], 1)
        self.assertEqual(public_api.search({"question": "orion", "version": VERSION})["hits"], [])
        self.assertEqual(public_api.chunk(self.public_chunk.chunk_id, VERSION)["text"],
                         self.public_chunk.text)
        with self.assertRaises(ApiNotFound):
            public_api.chunk(self.restricted_chunk.chunk_id, VERSION)

    def test_inconsistent_permission_column_cannot_release_restricted_source_text(self):
        with connect(self.index) as connection:
            connection.execute("UPDATE sources SET access='public' WHERE source_id=?",
                               (self.restricted.source_id,))
            connection.commit()
        with self.assertRaises(ValidationError):
            search(self.index, self.request())


if __name__ == "__main__":
    unittest.main()
