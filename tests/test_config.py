"""Protect the no-paid-provider boundary and bounded local model settings."""

from dataclasses import FrozenInstanceError
import unittest

from versionlens.config import LocalModelConfig


class LocalModelConfigTests(unittest.TestCase):
    def test_defaults_and_literal_ipv6_loopback(self):
        config = LocalModelConfig()
        self.assertEqual(config.base_url, "http://127.0.0.1:11435")
        self.assertEqual(config.model, "qwen3:1.7b")
        self.assertEqual(config.num_ctx, 8192)
        self.assertEqual(config.max_output_tokens, 600)
        self.assertEqual(LocalModelConfig(base_url="http://[::1]:11435").timeout_seconds, 120)
        with self.assertRaises(FrozenInstanceError):
            config.model = "another-model"

    def test_rejects_nonlocal_or_ambiguous_endpoints(self):
        for endpoint in (
            "https://ollama.com", "http://localhost:11435", "http://0.0.0.0:11435",
            "http://127.0.0.1:11434", "https://127.0.0.1:11435",
            "http://127.0.0.1:11435/", "http://127.0.0.1:11435/api",
            "http://user:pass@127.0.0.1:11435", "http://127.0.0.1:11435?x=1",
            "http://127.0.0.1:11435#fragment", "http://127.0.0.1.evil:11435",
            "http://2130706433:11435", None,
        ):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                LocalModelConfig(base_url=endpoint)

    def test_rejects_unapproved_models_and_unbounded_values(self):
        for model in ("qwen3:1.7b-cloud", "qwen3:latest", "gpt-4", "", None):
            with self.subTest(model=model), self.assertRaises(ValueError):
                LocalModelConfig(model=model)
        for timeout in (0, -1, float("inf"), float("nan"), 301, True, "120"):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                LocalModelConfig(timeout_seconds=timeout)
        for context in (0, 511, 8193, True, 8192.0):
            with self.subTest(context=context), self.assertRaises(ValueError):
                LocalModelConfig(num_ctx=context)
        for output in (0, 601, True, 600.0):
            with self.subTest(output=output), self.assertRaises(ValueError):
                LocalModelConfig(max_output_tokens=output)


if __name__ == "__main__":
    unittest.main()
