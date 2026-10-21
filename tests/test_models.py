from dataclasses import replace
from hashlib import sha256
import unittest

from versionlens.models import Chunk, SearchRequest, Source, UPSTREAM_COMMITS, ValidationError


def example_source(version="0.28.1", text="# Test\nA source document.\n"):
    path = "docs/test.md"
    commit = UPSTREAM_COMMITS[version]
    return Source(
        source_id=f"httpx:{version}:{path}", product="httpx", version=version,
        path=f"data/corpus/httpx/{version}/{path}", upstream_path=path, commit=commit,
        sha256=sha256(text.encode()).hexdigest(),
        url=f"https://github.com/encode/httpx/blob/{commit}/{path}", title="Test",
    )


class VersionContractTests(unittest.TestCase):
    def test_missing_latest_and_unsupported_versions_fail_closed(self):
        for version in ("", "latest", "0.28", "0.29.0", None):
            with self.subTest(version=version), self.assertRaises(ValidationError):
                SearchRequest("How do proxies work?", version)

    def test_empty_and_oversized_questions_and_limits_are_rejected(self):
        for question, limit in ((" ", 5), ("x" * 2001, 5), ("hello", 0), ("hi", True)):
            with self.subTest(question=question[:8], limit=limit), self.assertRaises(ValidationError):
                SearchRequest(question, "0.28.1", limit)

    def test_invalid_unicode_question_is_rejected_before_building_a_prompt(self):
        with self.assertRaises(ValidationError):
            SearchRequest("question " + chr(0xd800), "0.28.1")

    def test_source_cannot_misrepresent_its_version_or_upstream(self):
        source = example_source()
        for fields in (
            {"version": "0.27.2"}, {"url": "https://example.com/doc"},
            {"sha256": "missing"}, {"source_id": "unrelated"},
            {"upstream_path": "../secret"}, {"path": "/tmp/secret"},
            {"path": "data/../secret"}, {"path": "data\\secret"},
            {"path": "data/secret\x00.md"},
            {"commit": "main"}, {"title": ""},
        ):
            with self.subTest(fields=fields), self.assertRaises(ValidationError):
                replace(source, **fields)

    def test_chunk_identity_is_deterministic_and_tracks_content(self):
        source = example_source()
        one = Chunk.create(source, "Test", 1, 2, "# Test\nA source document.")
        again = Chunk.create(source, "Test", 1, 2, one.text)
        changed = Chunk.create(example_source(text="changed"), "Test", 1, 2, "changed")
        self.assertEqual(one.chunk_id, again.chunk_id)
        self.assertNotEqual(one.chunk_id, changed.chunk_id)
        self.assertEqual(one.citation_url, source.url + "?plain=1#L1-L2")

    def test_invalid_chunk_ranges_are_rejected(self):
        for start, end, text in ((0, 1, "text"), (2, 1, "text"), (1, 1, " ")):
            with self.subTest(start=start, end=end), self.assertRaises(ValidationError):
                Chunk.create(example_source(), "Test", start, end, text)
