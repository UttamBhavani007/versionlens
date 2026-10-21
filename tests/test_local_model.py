from dataclasses import FrozenInstanceError
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request as RealRequest
from urllib.error import URLError

from versionlens.config import LocalModelConfig
from versionlens import local_model
from versionlens.local_model import LocalModelClient, LocalModelError, MAX_RESPONSE_BYTES


class StubHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.respond()

    def do_POST(self):
        self.respond()

    def respond(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        self.server.requests.append((self.command, self.path, body))
        status, headers, response = self.server.reply
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        pass


class LocalModelClientTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), StubHandler)
        self.server.daemon_threads = True
        self.server.requests = []
        self.thread = threading.Thread(
            target=self.server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
        )
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.approved_requests = []
        server_url = f"http://127.0.0.1:{self.server.server_port}"

        def request_to_fixture(url, *args, **kwargs):
            # Keep the production config pinned to port 11435, while routing test
            # transport to an ephemeral port that cannot compete with Ollama.
            self.approved_requests.append(url)
            prefix = "http://127.0.0.1:11435"
            if not url.startswith(prefix + "/api/"):
                raise AssertionError("Adapter attempted an unapproved endpoint")
            return RealRequest(server_url + url[len(prefix):], *args, **kwargs)

        self.request_patch = patch.object(local_model, "Request", request_to_fixture)
        self.request_patch.start()
        self.addCleanup(self.request_patch.stop)
        self.client = LocalModelClient()

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def reply_json(self, payload, status=200):
        self.server.reply = (
            status, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8")
        )

    @staticmethod
    def generated(**overrides):
        payload = {
            "model": "qwen3:1.7b",
            "done": True,
            "response": '{"answer":"Local answer"}',
            "prompt_eval_count": 42,
            "eval_count": 7,
            "total_duration": 123456,
        }
        payload.update(overrides)
        return payload

    def generate(self):
        return self.client.generate(
            "Use supplied evidence only.",
            "Private prompt content.",
            {"type": "object", "properties": {"answer": {"type": "string"}}},
        )

    def test_generate_sends_nonstreaming_local_request_and_returns_usage(self):
        self.reply_json(self.generated())
        self.client = LocalModelClient(LocalModelConfig(num_ctx=2048, max_output_tokens=256))

        result = self.generate()

        self.assertEqual(result.response, '{"answer":"Local answer"}')
        self.assertEqual(result.model, "qwen3:1.7b")
        self.assertEqual((result.prompt_tokens, result.output_tokens, result.total_duration_ns),
                         (42, 7, 123456))
        with self.assertRaises(FrozenInstanceError):
            result.response = "changed"
        method, path, body = self.server.requests[0]
        self.assertEqual((method, path), ("POST", "/api/generate"))
        payload = json.loads(body)
        self.assertEqual(payload, {
            "model": "qwen3:1.7b",
            "system": "Use supplied evidence only.",
            "prompt": "Private prompt content.",
            "format": {"type": "object", "properties": {"answer": {"type": "string"}}},
            "stream": False,
            "think": False,
            "options": {"num_ctx": 2048, "num_predict": 256, "temperature": 0},
            "keep_alive": "5m",
        })
        self.assertEqual(self.approved_requests, ["http://127.0.0.1:11435/api/generate"])

    def test_optional_duration_defaults_to_zero(self):
        payload = self.generated()
        del payload["total_duration"]
        self.reply_json(payload)
        self.assertEqual(self.generate().total_duration_ns, 0)

    def test_health_returns_only_exact_selected_model(self):
        selected = {"name": "qwen3:1.7b", "model": "qwen3:1.7b", "size": 123}
        self.reply_json({"models": [
            {"name": "qwen3:1.7b-cloud"}, selected, {"name": "another-model"},
        ]})

        self.assertEqual(self.client.health(), selected)
        self.assertEqual(self.server.requests, [("GET", "/api/tags", b"")])

    def test_health_rejects_missing_ambiguous_or_mismatched_model(self):
        for models in (
            [], [{"name": "qwen3:1.7b-cloud"}],
            [{"name": "qwen3:1.7b"}, {"name": "qwen3:1.7b"}],
            [{"name": "qwen3:1.7b", "model": "other"}],
        ):
            with self.subTest(models=models):
                self.reply_json({"models": models})
                with self.assertRaises(LocalModelError):
                    self.client.health()

    def test_invalid_inventory_is_rejected(self):
        for inventory in ({}, {"models": {}}, {"models": None}, []):
            with self.subTest(inventory=inventory):
                self.reply_json(inventory)
                with self.assertRaises(LocalModelError):
                    self.client.health()

    def test_redirects_are_never_followed(self):
        for status in (301, 302, 303, 307, 308):
            with self.subTest(status=status):
                self.server.requests.clear()
                self.server.reply = (status, {"Location": "/redirect-target"}, b"")
                with self.assertRaisesRegex(LocalModelError, f"HTTP {status}"):
                    self.generate()
                self.assertEqual(len(self.server.requests), 1)
                self.assertEqual(self.server.requests[0][1], "/api/generate")

    def test_remote_redirect_does_not_make_a_second_request(self):
        self.server.reply = (302, {"Location": "https://example.com/sign-in"}, b"")
        with self.assertRaises(LocalModelError):
            self.generate()
        self.assertEqual(len(self.server.requests), 1)

    def test_proxy_environment_is_ignored(self):
        self.reply_json(self.generated())
        poison = "http://127.0.0.1:1"
        with patch.dict(os.environ, {
            "HTTP_PROXY": poison, "HTTPS_PROXY": poison, "ALL_PROXY": poison,
            "http_proxy": poison, "https_proxy": poison, "all_proxy": poison,
            "NO_PROXY": "", "no_proxy": "",
        }), patch("urllib.request.proxy_bypass", return_value=False):
            self.client = LocalModelClient()
            self.assertEqual(self.generate().model, "qwen3:1.7b")

    def test_oversized_response_is_rejected(self):
        self.server.reply = (200, {"Content-Type": "application/json"}, b"x" * (MAX_RESPONSE_BYTES + 1))
        with self.assertRaisesRegex(LocalModelError, "size limit"):
            self.generate()

    def test_non_json_nonfinite_and_non_utf8_responses_are_rejected(self):
        for body in (b"not json", b"\xff", b"[]", b'{"total_duration": NaN}', b'{"x": Infinity}'):
            with self.subTest(body=body):
                self.server.reply = (200, {}, body)
                with self.assertRaises(LocalModelError):
                    self.generate()

    def test_http_errors_hide_response_body_and_never_auto_pull(self):
        for status in (400, 401, 403, 404, 429, 500, 503):
            with self.subTest(status=status):
                self.server.requests.clear()
                self.server.reply = (status, {}, b"Private prompt content. SECRET SERVER ERROR")
                with self.assertRaises(LocalModelError) as caught:
                    self.generate()
                self.assertNotIn("Private", str(caught.exception))
                self.assertNotIn("SECRET", str(caught.exception))
                self.assertIn(str(status), str(caught.exception))
                self.assertEqual([request[1] for request in self.server.requests], ["/api/generate"])

    def test_json_error_field_is_sanitized(self):
        self.reply_json({"error": "Private prompt content. SECRET SERVER ERROR"})
        with self.assertRaises(LocalModelError) as caught:
            self.generate()
        self.assertEqual(str(caught.exception), "Local model service reported an error.")

    def test_wrong_model_and_unfinished_generation_are_rejected(self):
        for overrides in (
            {"model": "other"}, {"model": None}, {"done": False}, {"done": 1},
            {"done_reason": "length"}, {"done_reason": "unknown"},
        ):
            with self.subTest(overrides=overrides):
                self.reply_json(self.generated(**overrides))
                with self.assertRaises(LocalModelError):
                    self.generate()

    def test_natural_stop_reason_is_accepted(self):
        self.reply_json(self.generated(done_reason="stop"))
        self.assertEqual(self.generate().output_tokens, 7)

    def test_empty_missing_or_nontext_answer_is_rejected(self):
        for response in ("", "  \n", None, 17, {}):
            with self.subTest(response=response):
                self.reply_json(self.generated(response=response))
                with self.assertRaises(LocalModelError):
                    self.generate()

    def test_usage_requires_nonnegative_integers_without_booleans(self):
        for field in ("prompt_eval_count", "eval_count", "total_duration"):
            for value in (-1, 1.5, True, "2", None):
                with self.subTest(field=field, value=value):
                    self.reply_json(self.generated(**{field: value}))
                    with self.assertRaisesRegex(LocalModelError, "usage metadata"):
                        self.generate()
        for field in ("prompt_eval_count", "eval_count"):
            payload = self.generated()
            del payload[field]
            self.reply_json(payload)
            with self.subTest(missing=field), self.assertRaises(LocalModelError):
                self.generate()

    def test_invalid_inputs_never_reach_the_server(self):
        for system, prompt, schema in (
            ("", "prompt", {}), ("system", " ", {}),
            ("system", "prompt", []), ("system", "prompt", {"bad": object()}),
        ):
            with self.subTest(system=system, prompt=prompt):
                with self.assertRaises(LocalModelError):
                    self.client.generate(system, prompt, schema)
        self.assertEqual(self.server.requests, [])

    def test_modified_config_is_revalidated_before_network_access(self):
        config = LocalModelConfig()
        object.__setattr__(config, "base_url", "https://example.com")
        with self.assertRaisesRegex(LocalModelError, "configuration is invalid"):
            LocalModelClient(config)
        self.assertEqual(self.server.requests, [])

    def test_transport_errors_are_sanitized(self):
        for error in (URLError("Private prompt content."), TimeoutError("Private prompt content.")):
            with self.subTest(error=type(error).__name__):
                with patch.object(self.client._opener, "open", side_effect=error):
                    with self.assertRaises(LocalModelError) as caught:
                        self.generate()
                self.assertEqual(
                    str(caught.exception), "Local model service is unavailable or timed out."
                )
        self.assertEqual(self.server.requests, [])


if __name__ == "__main__":
    unittest.main()
