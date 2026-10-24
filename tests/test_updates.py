"""Exercise real SQLite snapshot changes, isolation and rollback without models."""

from copy import copy
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import sqlite3
import tempfile
import unittest

from versionlens.ingest import Corpus, chunk_markdown
from versionlens.models import Chunk, SearchRequest, Source, UPSTREAM_COMMITS, ValidationError
from versionlens.store import connect, index_stats, replace_corpus
from versionlens.updates import delete_snapshot, sync_snapshot


def document(version, name, text, *, title=None):
    path = f"docs/{name}.md"
    commit = UPSTREAM_COMMITS[version]
    source = Source(
        source_id=f"httpx:{version}:{path}", product="httpx", version=version,
        path=f"data/corpus/httpx/{version}/{path}", upstream_path=path, commit=commit,
        sha256=sha256(text.encode()).hexdigest(),
        url=f"https://github.com/encode/httpx/blob/{commit}/{path}", title=title or name,
    )
    return Corpus((source,), chunk_markdown(source, text))


def combined(*corpora):
    return Corpus(tuple(source for corpus in corpora for source in corpus.sources),
                  tuple(chunk for corpus in corpora for chunk in corpus.chunks))


class SnapshotUpdateTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.index = self.root / "source.sqlite3"
        self.legacy = document("0.27.2", "legacy", "# Legacy\nLegacyneedle remains unchanged.\n")
        self.stable = document("0.28.1", "stable", "# Stable\nStableneedle remains unchanged.\n")
        self.original = document("0.28.1", "change", "# Change\nOldneedle is the original content.\n")
        self.removable = document("0.28.1", "remove", "# Remove\nDeleteneedle should disappear.\n")
        self.changed = document("0.28.1", "change", "# Change\nNewneedle is the new content.\n")
        self.added = document("0.28.1", "added", "# Added\nAddedneedle is new.\n")
        replace_corpus(self.index, combined(self.legacy, self.stable, self.original, self.removable))

    def snapshot(self):
        with connect(self.index, readonly=True) as connection:
            return {
                "metadata": [tuple(row) for row in connection.execute("SELECT * FROM metadata ORDER BY key")],
                "sources": [tuple(row) for row in connection.execute("SELECT rowid,* FROM sources ORDER BY source_id")],
                "chunks": [tuple(row) for row in connection.execute("SELECT * FROM chunks ORDER BY chunk_id")],
            }

    def chunk_rows(self, corpus):
        ids = {chunk.chunk_id for chunk in corpus.chunks}
        with connect(self.index, readonly=True) as connection:
            return [tuple(row) for row in connection.execute("SELECT * FROM chunks ORDER BY chunk_id")
                    if row["chunk_id"] in ids]

    def count_term(self, term):
        with connect(self.index, readonly=True) as connection:
            return connection.execute("SELECT COUNT(*) FROM chunk_fts WHERE chunk_fts MATCH ?", (term,)).fetchone()[0]

    def test_add_change_and_remove_are_atomic_and_preserve_other_snapshot_and_unchanged_rowids(self):
        stable_before = self.chunk_rows(self.stable)
        legacy_before = self.chunk_rows(self.legacy)
        result = sync_snapshot(self.index, combined(self.stable, self.changed, self.added), "0.28.1")

        self.assertEqual({key: result[key] for key in ("added", "updated", "deleted", "unchanged")},
                         {"added": 1, "updated": 1, "deleted": 1, "unchanged": 1})
        self.assertEqual(result["index"], index_stats(self.index))
        self.assertEqual(result["index"]["sources"], 4)
        self.assertEqual(result["index"]["chunks"], 4)
        self.assertEqual(result["index"]["versions"], ["0.27.2", "0.28.1"])
        self.assertEqual(self.chunk_rows(self.stable), stable_before)
        self.assertEqual(self.chunk_rows(self.legacy), legacy_before)
        self.assertEqual(self.count_term("Oldneedle"), 0)
        self.assertEqual(self.count_term("Deleteneedle"), 0)
        self.assertEqual(self.count_term("Newneedle"), 1)
        self.assertEqual(self.count_term("Addedneedle"), 1)
        self.assertEqual(self.count_term("Legacyneedle"), 1)

    def test_repeated_sync_is_a_true_noop_including_source_and_chunk_rowids(self):
        desired = combined(self.stable, self.changed, self.added)
        sync_snapshot(self.index, desired, "0.28.1")
        before = self.snapshot()
        for _ in range(2):
            result = sync_snapshot(self.index, desired, "0.28.1")
            self.assertEqual((result["added"], result["updated"], result["deleted"], result["unchanged"]), (0, 0, 0, 3))
            self.assertEqual(self.snapshot(), before)

    def test_metadata_only_change_is_updated_even_with_identical_checksum_and_chunk_id(self):
        source = replace(self.stable.sources[0], title="Revised source title")
        revised = Corpus((source,), tuple(replace(chunk, source=source) for chunk in self.stable.chunks))
        desired = combined(revised, self.original, self.removable)
        result = sync_snapshot(self.index, desired, "0.28.1")
        self.assertEqual((result["added"], result["updated"], result["deleted"], result["unchanged"]), (0, 1, 0, 2))
        self.assertEqual(revised.chunks[0].chunk_id, self.stable.chunks[0].chunk_id)
        with connect(self.index, readonly=True) as connection:
            metadata = connection.execute("SELECT metadata_json FROM sources WHERE source_id=?", (source.source_id,)).fetchone()[0]
        self.assertIn("Revised source title", metadata)
        self.assertEqual(self.count_term("Stableneedle"), 1)

    def test_acl_only_change_updates_policy_columns_without_changing_content_identity(self):
        text = "# Synthetic demo\nDemoonlyneedle is labelled synthetic evidence.\n"
        digest = sha256(text.encode()).hexdigest()
        source = Source(
            source_id="synthetic:httpx:0.28.1:demo-policy.md", product="httpx", version="0.28.1",
            path="data/synthetic/httpx/0.28.1/demo-policy.md", upstream_path="demo-policy.md",
            commit=digest, sha256=digest,
            url=f"versionlens://synthetic/httpx/0.28.1/demo-policy.md?sha256={digest}",
            title="SYNTHETIC DEMO: Policy", source_kind="synthetic", access="public",
        )
        public = Corpus((source,), chunk_markdown(source, text))
        replace_corpus(self.index, combined(self.legacy, self.stable, self.original, self.removable, public))
        restricted_source = replace(source, access="support")
        restricted = Corpus((restricted_source,), tuple(replace(chunk, source=restricted_source) for chunk in public.chunks))
        result = sync_snapshot(self.index, combined(self.stable, self.original, self.removable, restricted), "0.28.1")
        self.assertEqual((result["added"], result["updated"], result["deleted"], result["unchanged"]), (0, 1, 0, 3))
        self.assertEqual(public.chunks[0].chunk_id, restricted.chunks[0].chunk_id)
        self.assertEqual(index_stats(self.index, access_profile="public")["sources"], 4)
        self.assertEqual(index_stats(self.index, access_profile="support")["sources"], 5)
        with connect(self.index, readonly=True) as connection:
            row = connection.execute("SELECT access,source_kind,metadata_json FROM sources WHERE source_id=?", (source.source_id,)).fetchone()
        self.assertEqual((row["access"], row["source_kind"]), ("support", "synthetic"))
        self.assertIn('"access": "support"', row["metadata_json"])

    def test_invalid_or_incomplete_input_never_changes_the_database(self):
        source = self.stable.sources[0]
        chunk = self.stable.chunks[0]
        bad_source = copy(source)
        object.__setattr__(bad_source, "sha256", "invalid-checksum")
        bad_id = replace(chunk, chunk_id="0" * 24)
        overlap = Chunk.create(source, "Overlap", 1, 1, "Overlapping content.")
        invalid = (
            None, Corpus((), ()), Corpus(self.stable.sources, ()),
            Corpus(list(self.stable.sources), self.stable.chunks),
            Corpus(self.stable.sources * 2, self.stable.chunks),
            Corpus(self.stable.sources, self.stable.chunks * 2),
            Corpus((bad_source,), self.stable.chunks),
            Corpus((replace(source, title="Invalid" + chr(0xD800)),), self.stable.chunks),
            Corpus(self.stable.sources, (bad_id,)),
            Corpus(self.stable.sources, (replace(chunk, section=None),)),
            Corpus(self.stable.sources, (replace(chunk, start_line=True),)),
            Corpus(self.stable.sources, (replace(chunk, end_line=0),)),
            Corpus(self.stable.sources, (replace(chunk, text="invalid" + chr(0xD800)),)),
            Corpus(self.stable.sources, (replace(chunk, text="One line in a two-line span."),)),
            Corpus(self.stable.sources, (replace(chunk, source={}),)),
            Corpus(self.stable.sources, self.original.chunks),
            Corpus(self.stable.sources, (replace(chunk, source=replace(source, title="Mismatched metadata")),)),
            Corpus(self.stable.sources + self.added.sources, self.stable.chunks),
            Corpus(self.stable.sources, self.stable.chunks + (overlap,)),
            self.legacy, combined(self.stable, self.legacy),
        )
        before = self.snapshot()
        for number, desired in enumerate(invalid):
            with self.subTest(case=number), self.assertRaises(ValidationError):
                sync_snapshot(self.index, desired, "0.28.1")
            self.assertEqual(self.snapshot(), before)

    def test_unknown_versions_and_missing_index_do_not_create_a_database(self):
        before = self.snapshot()
        for version in ("latest", "0.28", "", None, True, []):
            for operation in (lambda: sync_snapshot(self.index, self.stable, version),
                              lambda: delete_snapshot(self.index, version)):
                with self.subTest(version=version), self.assertRaises(ValidationError):
                    operation()
        self.assertEqual(self.snapshot(), before)
        missing = self.root / "not-created" / "new.sqlite3"
        for operation in (lambda: sync_snapshot(missing, self.stable, "0.28.1"),
                          lambda: delete_snapshot(missing, "0.28.1")):
            with self.assertRaisesRegex(ValidationError, "Index not found"):
                operation()
        self.assertFalse(missing.parent.exists())

    def test_sql_failure_rolls_back_added_changed_deleted_rows_and_fts(self):
        with connect(self.index) as connection:
            connection.execute("CREATE TRIGGER force_sync_failure BEFORE INSERT ON chunks "
                               "WHEN NEW.text LIKE '%Newneedle%' BEGIN SELECT RAISE(ABORT, 'forced fixture failure'); END")
            connection.commit()
        before = self.snapshot()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "forced fixture failure"):
            sync_snapshot(self.index, combined(self.stable, self.changed, self.added), "0.28.1")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.count_term("Oldneedle"), 1)
        self.assertEqual(self.count_term("Deleteneedle"), 1)
        self.assertEqual(self.count_term("Newneedle"), 0)
        self.assertEqual(self.count_term("Addedneedle"), 0)

    def test_delete_snapshot_removes_fts_and_preserves_the_other_version(self):
        before = self.chunk_rows(self.legacy)
        result = delete_snapshot(self.index, "0.28.1")
        self.assertEqual(result["deleted"], 3)
        self.assertEqual(result["index"], index_stats(self.index))
        self.assertEqual(result["index"]["versions"], ["0.27.2"])
        self.assertEqual(self.chunk_rows(self.legacy), before)
        self.assertEqual(self.count_term("Stableneedle"), 0)
        self.assertEqual(self.count_term("Legacyneedle"), 1)
        result = delete_snapshot(self.index, "0.28.1")
        self.assertEqual(result["deleted"], 0)
        self.assertEqual(self.chunk_rows(self.legacy), before)

    def test_explicit_deletion_can_remove_the_final_snapshot(self):
        delete_snapshot(self.index, "0.28.1")
        result = delete_snapshot(self.index, "0.27.2")
        self.assertEqual(result["deleted"], 1)
        self.assertEqual(result["index"]["sources"], 0)
        self.assertEqual(result["index"]["chunks"], 0)
        self.assertEqual(result["index"]["versions"], [])

    def test_sync_can_reintroduce_a_deleted_snapshot_without_rewriting_other_version(self):
        before = self.chunk_rows(self.legacy)
        delete_snapshot(self.index, "0.28.1")
        result = sync_snapshot(self.index, self.stable, "0.28.1")
        self.assertEqual((result["added"], result["updated"], result["deleted"], result["unchanged"]), (1, 0, 0, 0))
        self.assertEqual(self.chunk_rows(self.legacy), before)
        self.assertEqual(self.count_term("Stableneedle"), 1)

    def test_delete_failure_rolls_back_chunk_deletes_and_fts(self):
        with connect(self.index) as connection:
            connection.execute("CREATE TRIGGER force_delete_failure BEFORE DELETE ON sources "
                               "WHEN OLD.version='0.28.1' BEGIN SELECT RAISE(ABORT, 'forced fixture failure'); END")
            connection.commit()
        before = self.snapshot()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "forced fixture failure"):
            delete_snapshot(self.index, "0.28.1")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.count_term("Stableneedle"), 1)
        self.assertEqual(self.count_term("Oldneedle"), 1)

    def test_corrupt_indexed_metadata_fails_before_modifying_the_selected_snapshot(self):
        with connect(self.index) as connection:
            connection.execute("UPDATE sources SET metadata_json='{}' WHERE source_id=?", (self.original.sources[0].source_id,))
            connection.commit()
        before = self.snapshot()
        for operation in (lambda: sync_snapshot(self.index, self.stable, "0.28.1"),
                          lambda: delete_snapshot(self.index, "0.28.1")):
            with self.assertRaises(ValidationError):
                operation()
            self.assertEqual(self.snapshot(), before)

    def test_acl_columns_cannot_disagree_with_indexed_source_metadata(self):
        with connect(self.index) as connection:
            connection.execute("UPDATE sources SET access='support' WHERE source_id=?", (self.original.sources[0].source_id,))
            connection.commit()
        before = self.snapshot()
        with self.assertRaisesRegex(ValidationError, "disagree"):
            sync_snapshot(self.index, self.stable, "0.28.1")
        self.assertEqual(self.snapshot(), before)

    def test_changed_version_column_in_indexed_chunks_is_not_silently_ignored(self):
        with connect(self.index) as connection:
            connection.execute("UPDATE chunks SET version='0.27.2' WHERE source_id=?", (self.original.sources[0].source_id,))
            connection.commit()
        before = self.snapshot()
        with self.assertRaisesRegex(ValidationError, "inconsistent"):
            sync_snapshot(self.index, self.stable, "0.28.1")
        self.assertEqual(self.snapshot(), before)

    def test_updates_invalidate_vector_cache_without_rebuilding_or_calling_query_embedding(self):
        from test_vector_store import FakeEmbeddingClient
        from versionlens.vector_store import VectorIndexError, build_vector_index, vector_search
        client = FakeEmbeddingClient()
        vectors = self.root / "vectors.sqlite3"
        build_vector_index(self.index, vectors, client)
        sync_snapshot(self.index, combined(self.stable, self.changed, self.added), "0.28.1")
        with self.assertRaisesRegex(VectorIndexError, "stale"):
            vector_search(self.index, vectors, SearchRequest("Newneedle", "0.28.1"), client)
        self.assertEqual(client.query_calls, [])


if __name__ == "__main__":
    unittest.main()
