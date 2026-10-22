"""Verify runtime policy without downloading or launching external software."""

import hashlib
import importlib.util
import io
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
    def test_pull_selects_only_explicit_approved_generation_or_embedding_model(self):
        for arguments, expected_model in (
            (["pull"], "qwen3:1.7b"),
            (["pull", "--embedding"], "nomic-embed-text:v1.5"),
        ):
            with self.subTest(arguments=arguments), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                executable = root / ".tools" / "ollama" / "ollama"
                with (
                    patch.multiple(runtime, ROOT=root, MODELS=root / ".ollama" / "models"),
                    patch.object(runtime.sys, "argv", ["local_runtime.py", *arguments]),
                    patch.object(runtime, "require_runtime", return_value=executable),
                    patch.object(runtime.subprocess, "run") as run,
                    patch("sys.stdout", new_callable=io.StringIO),
                ):
                    run.return_value.returncode = 0
                    self.assertEqual(runtime.main(), 0)
                    self.assertEqual(run.call_args.args[0], [str(executable), "pull", expected_model])
                    self.assertEqual(run.call_args.kwargs["env"]["OLLAMA_NO_CLOUD"], "1")
                    self.assertEqual(run.call_args.kwargs["env"]["OLLAMA_HOST"], "http://127.0.0.1:11435")

    def test_embedding_flag_rejects_other_runtime_commands_before_execution(self):
        with (
            patch.object(runtime.sys, "argv", ["local_runtime.py", "serve", "--embedding"]),
            patch.object(runtime, "require_runtime") as verify,
            patch.object(runtime.subprocess, "run") as run,
            patch("sys.stderr", new_callable=io.StringIO),
        ):
            with self.assertRaises(SystemExit) as caught:
                runtime.main()
            self.assertEqual(caught.exception.code, 2)
            verify.assert_not_called()
            run.assert_not_called()

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
