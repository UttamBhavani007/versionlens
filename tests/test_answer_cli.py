from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from test_models import example_source
from versionlens.cli import main
from versionlens.ingest import Corpus, chunk_markdown
from versionlens.local_model import LocalModelError, ModelResponse
from versionlens.store import replace_corpus


class LocalAnswerCliTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.text = "The proxies argument has been removed."
        source = example_source(text=self.text)
        replace_corpus(self.root / "data/versionlens.sqlite3",
                       Corpus((source,), chunk_markdown(source, self.text)))

    def invoke(self, *args):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = main(["--root", str(self.root), *args])
        return code, output.getvalue(), errors.getvalue()

    def test_missing_evidence_abstains_offline_without_model_call(self):
        with patch("versionlens.local_model.LocalModelClient.generate") as generate:
            code, output, _ = self.invoke("ask", "quantumgiraffeunsupported", "--version", "0.28.1")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["reason"], "no_matching_evidence")
        generate.assert_not_called()

    def test_runtime_failure_is_a_nonzero_operational_error(self):
        with patch("versionlens.local_model.LocalModelClient.generate", side_effect=LocalModelError("unavailable")):
            code, output, _ = self.invoke("ask", "proxies", "--version", "0.28.1")
        self.assertEqual(code, 2)
        result = json.loads(output)
        self.assertEqual(result["status"], "error")
        self.assertIsNone(result["answer"])

    def test_cited_local_draft_is_returned_as_structured_json(self):
        response = {"decision": "answer", "claims": [{"text": self.text,
                    "citations": [{"evidence_id": "E1", "quote_id": "Q1"}]}]}
        model_response = ModelResponse(json.dumps(response), "qwen3:1.7b", 30, 20, 1000)
        with patch("versionlens.local_model.LocalModelClient.generate", return_value=model_response):
            code, output, _ = self.invoke("ask", "proxies", "--version", "0.28.1")
        result = json.loads(output)
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "answered")
        self.assertFalse(result["semantic_support_verified"])
        self.assertEqual(result["claims"][0]["citations"][0]["version"], "0.28.1")

    def test_doctor_does_not_require_an_index_and_sanitizes_runtime_errors(self):
        with TemporaryDirectory() as empty:
            output = io.StringIO()
            with patch("versionlens.local_model.LocalModelClient.health", return_value={"name": "qwen3:1.7b"}), redirect_stdout(output):
                code = main(["--root", empty, "doctor"])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.getvalue())["mode"], "local_only")
            self.assertEqual(list(Path(empty).iterdir()), [])
        with patch("versionlens.local_model.LocalModelClient.health", side_effect=LocalModelError("Local model unavailable")):
            code, _, error = self.invoke("doctor")
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(error)["error"], "Local model unavailable")
