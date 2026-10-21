"""Verify runtime policy without downloading or launching external software."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


_spec = importlib.util.spec_from_file_location(
    "versionlens_runtime_for_tests",
    Path(__file__).resolve().parents[1] / "scripts" / "local_runtime.py",
)
runtime = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runtime)


class LocalRuntimePolicyTests(unittest.TestCase):
    def test_symlinked_cli_cannot_pass_runtime_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            installed = root / ".tools" / "ollama"
            installed.mkdir(parents=True)
            other_cli = root / "another-ollama"
            other_cli.write_bytes(b"test executable bytes")
            (installed / "ollama").symlink_to(other_cli)
            (installed / ".release.json").write_text(json.dumps({
                "release": runtime.RELEASE,
                "archive_sha256": runtime.ARCHIVE_SHA256,
                "files": {"ollama": hashlib.sha256(other_cli.read_bytes()).hexdigest()},
            }))
            with patch.multiple(runtime, ROOT=root, RUNTIME=installed):
                with self.assertRaisesRegex(runtime.RuntimeSetupError, "symlinks"):
                    runtime.require_runtime()

    def test_environment_forces_local_cloud_off_and_drops_tokens_and_proxies(self):
        inherited = {
            "OPENAI_API_KEY": "test-only-token",
            "AWS_SECRET_ACCESS_KEY": "test-only-token",
            "OLLAMA_NO_CLOUD": "0",
            "OLLAMA_HOST": "https://ollama.com",
            "OLLAMA_MODELS": "/unapproved/models",
            "OLLAMA_CONTEXT_LENGTH": "1000000",
            "OLLAMA_DEBUG_LOG_REQUESTS": "1",
            "OLLAMA_REMOTES": "unapproved.invalid",
            "HTTP_PROXY": "https://proxy.invalid",
            "HTTPS_PROXY": "https://proxy.invalid",
            "http_proxy": "https://proxy.invalid",
        }
        with patch.dict(os.environ, inherited):
            environment = runtime.runtime_environment()
        self.assertEqual(environment["OLLAMA_HOST"], "http://127.0.0.1:11435")
        self.assertEqual(environment["OLLAMA_NO_CLOUD"], "1")
        self.assertEqual(environment["OLLAMA_MODELS"], str(runtime.MODELS))
        self.assertEqual(environment["OLLAMA_CONTEXT_LENGTH"], "8192")
        self.assertEqual(environment["OLLAMA_MAX_LOADED_MODELS"], "1")
        self.assertEqual(environment["OLLAMA_NUM_PARALLEL"], "1")
        self.assertEqual(environment["OLLAMA_DEBUG_LOG_REQUESTS"], "0")
        for forbidden in (
            "OPENAI_API_KEY", "AWS_SECRET_ACCESS_KEY", "OLLAMA_REMOTES",
            "HTTP_PROXY", "HTTPS_PROXY", "http_proxy",
        ):
            self.assertNotIn(forbidden, environment)
        self.assertEqual(environment["NO_PROXY"], "127.0.0.1,::1,localhost")

    def test_corrupt_or_partial_cached_archive_fails_before_extraction(self):
        for invalid_content in (b"ab", b"bad"):
            with self.subTest(content=invalid_content), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                tools = root / ".tools"
                tools.mkdir()
                archive = tools / "cached.tgz"
                archive.write_bytes(invalid_content)
                with (
                    patch.multiple(
                        runtime,
                        ROOT=root,
                        RUNTIME=tools / "ollama",
                        ARCHIVE=archive,
                        ARCHIVE_SIZE=3,
                        ARCHIVE_SHA256=hashlib.sha256(b"abc").hexdigest(),
                    ),
                    patch.object(runtime.platform, "system", return_value="Darwin"),
                    patch.object(runtime.platform, "machine", return_value="arm64"),
                    patch.object(runtime.urllib.request, "build_opener") as network,
                    patch.object(runtime.tarfile, "open") as extract,
                ):
                    with self.assertRaises(runtime.RuntimeSetupError):
                        runtime.install()
                    network.assert_not_called()
                    extract.assert_not_called()
                self.assertFalse((tools / "ollama").exists())
                self.assertEqual(list(tools.iterdir()), [archive])


if __name__ == "__main__":
    unittest.main()
