from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from test_models import example_source
from versionlens.cli import main
from versionlens.ingest import Corpus, chunk_markdown
from versionlens.models import SearchRequest
from versionlens.retrieval import query_terms, search
from versionlens.store import replace_corpus


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.index = self.root / "data" / "versionlens.sqlite3"
        old_text = "# Proxies\nThe proxies argument is deprecated but still accepted.\n"
        new_text = "# Proxies\nThe proxies argument has been removed. Canarynewonly.\n"
        self.old = example_source("0.27.2", old_text)
        self.new = example_source("0.28.1", new_text)
        self.corpus = Corpus((self.old, self.new), (
            *chunk_markdown(self.old, old_text), *chunk_markdown(self.new, new_text),
        ))
        replace_corpus(self.index, self.corpus)

    def test_new_version_only_canary_never_leaks_to_old_version(self):
        self.assertEqual(search(self.index, SearchRequest("Canarynewonly", "0.27.2")), ())
        hits = search(self.index, SearchRequest("Canarynewonly", "0.28.1"))
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].chunk.source.version, "0.28.1")

    def test_same_question_returns_only_selected_snapshot(self):
        for version, expected in (("0.27.2", "still accepted"), ("0.28.1", "removed")):
            hits = search(self.index, SearchRequest("proxies argument", version))
            self.assertEqual(len(hits), 1)
            self.assertIn(expected, hits[0].chunk.text)
            self.assertEqual(hits[0].chunk.source.version, version)
            self.assertTrue(hits[0].chunk.citation_url.startswith(hits[0].chunk.source.url))

    def test_missing_terms_and_stopwords_have_no_results(self):
        for question in ("quantumgiraffe", "the and is", '" OR * NEAR(( -'):
            with self.subTest(question=question):
                self.assertEqual(search(self.index, SearchRequest(question, "0.28.1")), ())

    def test_fts_and_sql_punctuation_is_literal_and_cannot_drop_tables(self):
        search(self.index, SearchRequest('proxies"; DROP TABLE chunks; -- OR *', "0.28.1"))
        self.assertEqual(len(search(self.index, SearchRequest("proxies", "0.28.1"))), 1)
        self.assertEqual(query_terms("httpx.Client(proxies=proxy_config)"), ("httpx", "client", "proxies", "proxy", "config"))

    def test_cli_uses_json_and_does_not_claim_to_generate_answers(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--root", str(self.root), "search", "proxies", "--version", "0.28.1"])
        data = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(data["mode"], "keyword_retrieval_only")
        self.assertIsNone(data["answer"])
        self.assertEqual(data["hits"][0]["version"], "0.28.1")

    def test_cli_ingest_failure_preserves_working_index(self):
        sources = []
        for source, chunk in zip(self.corpus.sources, self.corpus.chunks):
            path = self.root / source.path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(chunk.text + "TAMPERED", encoding="utf-8")
            sources.append(asdict(source))
        (self.root / "data/sources.json").write_text(json.dumps({"schema_version": 1, "sources": sources}))
        error = io.StringIO()
        with redirect_stderr(error):
            code = main(["--root", str(self.root), "ingest"])
        self.assertEqual(code, 2)
        self.assertIn("Checksum mismatch", error.getvalue())
        self.assertEqual(len(search(self.index, SearchRequest("proxies", "0.27.2"))), 1)

    def test_cli_rejects_missing_version_and_bad_limit(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            main(["--root", str(self.root), "search", "proxies"])
        self.assertEqual(raised.exception.code, 2)
        with redirect_stderr(io.StringIO()):
            code = main(["--root", str(self.root), "search", "proxies", "--version", "0.28.1", "--limit", "0"])
        self.assertEqual(code, 2)
