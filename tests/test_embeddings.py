"""Embedding contracts are tested without launching a model or network service."""

from dataclasses import FrozenInstanceError
import io
import json
import math
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from versionlens import embeddings
from versionlens.embeddings import (
    EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, MAX_INPUT_BYTES, MAX_RESPONSE_BYTES,
    EmbeddingIdentity, LocalEmbeddingClient, LocalEmbeddingConfig, LocalEmbeddingError,
)
from versionlens.local_model import LocalModelError


DIGEST = "a" * 64


def inventory(digest=DIGEST):
    return {"models": [{"name": EMBEDDING_MODEL, "model": EMBEDDING_MODEL, "digest": digest}]}


def embedding_payload(count=1, vector=None):
    vector = [3.0, 4.0] + [0.0] * (EMBEDDING_DIMENSIONS - 2) if vector is None else vector
    return {
        "model": EMBEDDING_MODEL, "embeddings": [vector[:] for _ in range(count)],
        "prompt_eval_count": 7 * count, "total_duration": 123,
    }


class FakeOpener:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append((request, timeout))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        raw = response if isinstance(response, bytes) else json.dumps(response).encode("utf-8")
        return io.BytesIO(raw)


def fake_client(*responses):
    client = LocalEmbeddingClient()
    client._opener = FakeOpener(*responses)
    return client


class LocalEmbeddingConfigTests(unittest.TestCase):
    def test_only_fixed_local_model_context_and_dimensions_are_allowed(self):
        self.assertEqual(LocalEmbeddingConfig(base_url="http://[::1]:11435").dimensions, 768)
        for changes in (
            {"base_url": "https://api.nomic.ai"}, {"base_url": "http://localhost:11435"},
            {"base_url": "http://127.0.0.1:11434"}, {"base_url": "http://127.0.0.1:11435/"},
            {"base_url": "http://user@127.0.0.1:11435"},
            {"base_url": "http://127.0.0.1:11435?x=1"},
            {"base_url": "http://127.0.0.1:11435#x"},
            {"model": "nomic-embed-text:latest"}, {"model": "qwen3:1.7b"},
            {"dimensions": 512}, {"dimensions": True}, {"num_ctx": 4096},
            {"timeout_seconds": 0}, {"timeout_seconds": float("inf")},
            {"timeout_seconds": float("nan")}, {"timeout_seconds": True},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                LocalEmbeddingConfig(**changes)
        config = LocalEmbeddingConfig()
        object.__setattr__(config, "base_url", "http://remote.invalid:11435")
        with self.assertRaises(LocalEmbeddingError):
            LocalEmbeddingClient(config)
        self.assertTrue(issubclass(LocalEmbeddingError, LocalModelError))

    def test_http_client_disables_proxy_inheritance_and_redirects(self):
        with patch.object(embeddings, "build_opener") as build:
            LocalEmbeddingClient()
        proxy_handler, redirect_handler = build.call_args.args
        self.assertEqual(proxy_handler.proxies, {})
        self.assertIsNone(redirect_handler.redirect_request(None, None, 302, "", {}, "https://remote.invalid"))


class LocalEmbeddingClientTests(unittest.TestCase):
    def test_document_prefixes_preserve_full_inputs_and_expose_stable_identity(self):
        texts = ["  API troubleshooting\nfull original text  ", "ö" * (MAX_INPUT_BYTES // 2)]
        client = fake_client(inventory(), embedding_payload(2), inventory())
        batch = client.embed_documents(texts)
        self.assertEqual(batch.identity, EmbeddingIdentity(EMBEDDING_MODEL, DIGEST, 768))
        self.assertIsInstance(batch.vectors, tuple)
        self.assertIsInstance(batch.vectors[0], tuple)
        self.assertAlmostEqual(batch.vectors[0][0], 0.6)
        self.assertAlmostEqual(batch.vectors[0][1], 0.8)
        self.assertAlmostEqual(math.hypot(*batch.vectors[0]), 1.0)
        self.assertEqual((batch.prompt_tokens, batch.total_duration_ns), (14, 123))
        with self.assertRaises(FrozenInstanceError):
            batch.identity = None
        self.assertEqual([request.full_url for request, _ in client._opener.requests], [
            "http://127.0.0.1:11435/api/tags", "http://127.0.0.1:11435/api/embed",
            "http://127.0.0.1:11435/api/tags",
        ])
        request, timeout = client._opener.requests[1]
        payload = json.loads(request.data)
        self.assertEqual(payload["input"], ["search_document: " + text for text in texts])
        self.assertIs(payload["truncate"], False)
        self.assertEqual(payload["dimensions"], 768)
        self.assertEqual(payload["options"], {"num_ctx": 8192})
        self.assertEqual(timeout, 120)

    def test_query_prefix_and_numerically_stable_unit_normalization(self):
        for scale in (1.0, 1e308, 1e-300):
            vector = [scale, scale] + [0.0] * 766
            client = fake_client(inventory(), embedding_payload(vector=vector), inventory())
            batch = client.embed_query("Why did proxies stop working?")
            self.assertAlmostEqual(math.hypot(*batch.vectors[0]), 1.0)
            self.assertTrue(all(math.isfinite(value) for value in batch.vectors[0]))
            payload = json.loads(client._opener.requests[1][0].data)
            self.assertEqual(payload["input"], ["search_query: Why did proxies stop working?"])

    def test_invalid_inputs_fail_before_any_model_or_inventory_request(self):
        for texts in (
            [], ["x"] * 17, ("x",), [""], [" \n"], [None], ["\ud800"],
            ["x" * (MAX_INPUT_BYTES + 1)], ["€" * 4001],
        ):
            client = fake_client()
            with self.subTest(texts_type=type(texts).__name__), self.assertRaises(LocalEmbeddingError):
                client.embed_documents(texts)
            self.assertEqual(client._opener.requests, [])

    def test_inventory_rejects_missing_duplicate_remote_and_invalid_digest_entries(self):
        valid = inventory()["models"][0]
        for response in (
            {"models": []}, {"models": [valid, valid]}, {"models": "invalid"},
            inventory("short"), inventory("A" * 64), inventory("sha256:" + DIGEST),
            {"models": [{**valid, "model": "other"}]},
            {"models": [{**valid, "remote_host": "https://ollama.com"}]},
        ):
            with self.subTest(response=response), self.assertRaises(LocalEmbeddingError):
                fake_client(response).identity()

    def test_model_digest_change_during_embedding_is_rejected(self):
        client = fake_client(inventory(), embedding_payload(), inventory("b" * 64))
        with self.assertRaisesRegex(LocalEmbeddingError, "changed"):
            client.embed_query("question")

    def test_invalid_vector_batch_model_and_usage_are_rejected(self):
        bad_vectors = (
            [0.0] * 768, [1.0] * 767, [1.0] * 769,
            [True] + [0.0] * 767, ["1"] + [0.0] * 767,
            [float("inf")] + [0.0] * 767, [float("nan")] + [0.0] * 767,
        )
        invalid_payloads = [embedding_payload(vector=vector) for vector in bad_vectors]
        invalid_payloads.extend([
            {**embedding_payload(), "embeddings": []},
            {**embedding_payload(), "model": "other"},
            {**embedding_payload(), "prompt_eval_count": True},
            {**embedding_payload(), "total_duration": -1},
        ])
        for payload in invalid_payloads:
            client = fake_client(inventory(), payload)
            with self.subTest(payload_keys=list(payload)), self.assertRaises(LocalEmbeddingError):
                client.embed_query("question")

    def test_bounded_json_and_sanitized_failures(self):
        error_body = io.BytesIO(b"private upstream response")
        failures = (
            b"{not-json", b"[]", b"x" * (MAX_RESPONSE_BYTES + 1),
            {"error": "private upstream response"},
            URLError("private upstream response"),
            HTTPError("http://private.invalid", 503, "private upstream response", {}, error_body),
        )
        for failure in failures:
            client = fake_client(failure)
            with self.subTest(failure_type=type(failure).__name__), self.assertRaises(LocalEmbeddingError) as caught:
                client.identity()
            self.assertNotIn("private", str(caught.exception))
        self.assertTrue(error_body.closed)


if __name__ == "__main__":
    unittest.main()
