from dataclasses import asdict
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from versionlens.ingest import Corpus, chunk_markdown, load_corpus
from versionlens.models import ValidationError
from versionlens.store import connect, index_stats, replace_corpus

from test_models import example_source


class TemporaryCorpusTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write_fixture(self, text="# Test\nVerified original document.\n"):
        source = example_source(text=text)
        source_path = self.root / source.path
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(text, encoding="utf-8")
        self.write_manifest([asdict(source)])
        return source

    def write_manifest(self, entries):
        manifest_path = self.root / "data/sources.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps({"schema_version": 1, "sources": entries}), encoding="utf-8"
        )

    def test_checksum_tampering_rejects_the_entire_corpus(self):
        source = self.write_fixture()
        (self.root / source.path).write_text("# Test\nModified after approval.\n", encoding="utf-8")

        with self.assertRaisesRegex(ValidationError, "Checksum mismatch"):
            load_corpus(self.root)

    def test_manifest_path_rejects_absolute_traversal_and_backslashes(self):
        self.write_fixture()
        invalid_paths = (
            str(self.root / "data/sources.json"),
            "../sources.json",
            "data/../sources.json",
            "./data/sources.json",
            "data//sources.json",
            "data\\sources.json",
        )
        for manifest_path in invalid_paths:
            with self.subTest(path=manifest_path), self.assertRaises(ValidationError):
                load_corpus(self.root, manifest_path)

    def test_manifest_source_paths_cannot_escape_the_snapshot(self):
        source = self.write_fixture()
        for path in ("../outside.md", "/tmp/outside.md", "data/corpus/httpx/other.md"):
            entry = asdict(source)
            entry["path"] = path
            self.write_manifest([entry])
            with self.subTest(path=path), self.assertRaises(ValidationError):
                load_corpus(self.root)

    def test_duplicate_manifest_source_is_rejected(self):
        source = self.write_fixture()
        self.write_manifest([asdict(source), asdict(source)])

        with self.assertRaisesRegex(ValidationError, "Duplicate source ID"):
            load_corpus(self.root)

    def test_source_file_symlink_is_rejected_even_with_matching_bytes(self):
        source = self.write_fixture()
        source_path = self.root / source.path
        target = self.root / "approved-content.md"
        source_path.rename(target)
        source_path.symlink_to(target)

        with self.assertRaisesRegex(ValidationError, "symlinks are not allowed"):
            load_corpus(self.root)

    def test_source_ancestor_symlink_is_rejected(self):
        source = self.write_fixture()
        directory = (self.root / source.path).parent
        target = self.root / "linked-docs"
        directory.rename(target)
        directory.symlink_to(target, target_is_directory=True)

        with self.assertRaisesRegex(ValidationError, "symlinks are not allowed"):
            load_corpus(self.root)

    def test_manifest_symlink_is_rejected(self):
        self.write_fixture()
        manifest_path = self.root / "data/sources.json"
        target = self.root / "manifest-copy.json"
        manifest_path.rename(target)
        manifest_path.symlink_to(target)

        with self.assertRaisesRegex(ValidationError, "symlinks are not allowed"):
            load_corpus(self.root)

    def test_missing_readonly_index_does_not_create_database_or_directory(self):
        index_path = self.root / "not-created" / "index.sqlite3"

        with self.assertRaisesRegex(ValidationError, "Index not found"):
            index_stats(index_path)

        self.assertFalse(index_path.exists())
        self.assertFalse(index_path.parent.exists())

    def test_failed_replacement_preserves_previous_rows_and_search_index(self):
        self.write_fixture("# Original\nOriginalneedle remains searchable.\n")
        original = load_corpus(self.root)
        index_path = self.root / "index.sqlite3"
        expected_stats = replace_corpus(index_path, original)
        before = self.snapshot(index_path)

        self.write_fixture("# Replacement\nReplacementneedle should be rolled back.\n")
        replacement = load_corpus(self.root)
        duplicate_chunks = Corpus(
            replacement.sources, replacement.chunks + (replacement.chunks[0],)
        )

        with self.assertRaises(sqlite3.IntegrityError):
            replace_corpus(index_path, duplicate_chunks)

        self.assertEqual(index_stats(index_path), expected_stats)
        self.assertEqual(self.snapshot(index_path), before)
        with connect(index_path, readonly=True) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT count(*) FROM chunk_fts WHERE chunk_fts MATCH ?",
                    ("Originalneedle",),
                ).fetchone()[0],
                1,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT count(*) FROM chunk_fts WHERE chunk_fts MATCH ?",
                    ("Replacementneedle",),
                ).fetchone()[0],
                0,
            )

    def test_reingesting_same_corpus_is_idempotent(self):
        self.write_fixture("# First\nSearchneedle one.\n\n## Second\nSearchneedle two.\n")
        corpus = load_corpus(self.root)
        index_path = self.root / "index.sqlite3"
        first_stats = replace_corpus(index_path, corpus)
        first_snapshot = self.snapshot(index_path)

        for _ in range(3):
            self.assertEqual(replace_corpus(index_path, corpus), first_stats)
            self.assertEqual(self.snapshot(index_path), first_snapshot)

        self.assertEqual(first_stats["sources"], 1)
        self.assertEqual(first_stats["chunks"], 2)
        with connect(index_path, readonly=True) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT count(*) FROM chunk_fts WHERE chunk_fts MATCH ?", ("Searchneedle",)
                ).fetchone()[0],
                2,
            )
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    @staticmethod
    def snapshot(index_path):
        with connect(index_path, readonly=True) as connection:
            return {
                "sources": [tuple(row) for row in connection.execute(
                    "SELECT * FROM sources ORDER BY source_id"
                )],
                "chunks": [tuple(row) for row in connection.execute(
                    "SELECT * FROM chunks ORDER BY chunk_id"
                )],
                "metadata": [tuple(row) for row in connection.execute(
                    "SELECT * FROM metadata ORDER BY key"
                )],
            }


class MarkdownChunkTests(unittest.TestCase):
    def test_exact_line_spans_and_heading_hierarchy_ignore_fenced_headings(self):
        lines = [
            "Intro before a heading.",
            "",
            "# Guide",
            "Opening text.",
            "```python",
            "# This is code, not a heading",
            "value = 1",
            "```",
            "## Usage",
            "~~~markdown",
            "### Also code",
            "~~~",
            "Usage details.",
            "# Other",
            "Other details.",
        ]
        content = "\n".join(lines) + "\n"
        source = example_source(text=content)

        chunks = chunk_markdown(source, content)

        self.assertEqual(
            [(chunk.start_line, chunk.end_line, chunk.section) for chunk in chunks],
            [(1, 2, "Test"), (3, 8, "Guide"), (9, 13, "Guide > Usage"), (14, 15, "Other")],
        )
        for chunk in chunks:
            with self.subTest(start=chunk.start_line, end=chunk.end_line):
                self.assertEqual(chunk.text, "\n".join(lines[chunk.start_line - 1:chunk.end_line]))
                self.assertEqual(
                    chunk.citation_url,
                    f"{source.url}?plain=1#L{chunk.start_line}-L{chunk.end_line}",
                )

    def test_size_split_preserves_every_line_and_keeps_long_line_intact(self):
        lines = ["# Sized", "a" * 120, "b" * 120, "c" * 240, "tail"]
        content = "\n".join(lines) + "\n"

        chunks = chunk_markdown(example_source(text=content), content, max_chars=200)

        self.assertEqual(
            [(chunk.start_line, chunk.end_line) for chunk in chunks],
            [(1, 2), (3, 3), (4, 4), (5, 5)],
        )
        self.assertEqual("\n".join(chunk.text for chunk in chunks), "\n".join(lines))
        self.assertEqual([chunk.section for chunk in chunks], ["Sized"] * 4)


if __name__ == "__main__":
    unittest.main()
