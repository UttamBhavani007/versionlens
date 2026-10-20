from pathlib import Path
import unittest

from versionlens.ingest import load_corpus
from versionlens.models import SUPPORTED_VERSIONS


class ShippedCorpusTests(unittest.TestCase):
    def test_checked_in_sources_are_valid_and_cover_both_snapshots(self):
        root = Path(__file__).resolve().parents[1]
        corpus = load_corpus(root)
        self.assertEqual({source.version for source in corpus.sources}, set(SUPPORTED_VERSIONS))
        for version in SUPPORTED_VERSIONS:
            self.assertTrue(any(source.version == version and source.upstream_path == "LICENSE.md"
                                for source in corpus.sources))
            self.assertTrue(any(source.version == version and source.upstream_path == "CHANGELOG.md"
                                for source in corpus.sources))

    def test_every_shipped_chunk_matches_its_exact_upstream_line_span(self):
        root = Path(__file__).resolve().parents[1]
        corpus = load_corpus(root)
        lines = {source.source_id: (root / source.path).read_text(encoding="utf-8").splitlines()
                 for source in corpus.sources}
        for chunk in corpus.chunks:
            with self.subTest(chunk_id=chunk.chunk_id):
                expected = "\n".join(lines[chunk.source.source_id][chunk.start_line-1:chunk.end_line])
                self.assertEqual(chunk.text, expected)
                self.assertIn("?plain=1#L", chunk.citation_url)
