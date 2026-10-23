"""Exercise the loopback HTTP boundary with sockets and a model-free service."""

import concurrent.futures
from http import client as http_client
import json
import socket
import threading
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from versionlens.api import ApiNotFound
from versionlens.local_model import LocalModelError
from versionlens.models import ValidationError
from versionlens.server import create_server


CHUNK_ID = "a" * 24
VERSION = "0.28.1"
SEARCH = {"question": "How do I configure a proxy?", "version": VERSION, "retriever": "keyword"}


class RecordingService:
    """A deterministic API substitute; no runtime, index, or model is involved."""

    def __init__(self):
        self.lock = threading.Lock()
        self.release = threading.Event()
        self.entered = threading.Event()
        self.condition = threading.Condition(self.lock)
        self.reset()

    def reset(self):
        with self.lock:
            self.calls = []
            self.failure = None
            self.ask_result = {"status": "draft", "answer": "A cited fixture answer."}
            self.block_method = None
            self.blocked_count = 0
            self.release.clear()
            self.entered.clear()

    def _record(self, method, *arguments):
        with self.condition:
            self.calls.append((method, arguments))
            blocked = self.block_method == method
            if blocked:
                self.blocked_count += 1
                self.entered.set()
                self.condition.notify_all()
            failure = self.failure
        if blocked and not self.release.wait(10):
            raise RuntimeError("Fixture was not released")
        if failure:
            raise failure

    def catalog(self):
        self._record("catalog")
        return {"product": "httpx", "versions": ["0.27.2", VERSION]}

    def search(self, payload):
        self._record("search", payload)
        return {"status": "ok", "results": [], "question": payload.get("question")}

    def ask(self, payload):
        self._record("ask", payload)
        return self.ask_result

    def chunk(self, chunk_id, version):
        self._record("chunk", chunk_id, version)
        if version not in {"0.27.2", VERSION}:
            raise ValidationError("Unsupported version")
        if chunk_id != CHUNK_ID or version != VERSION:
            raise ApiNotFound("Source excerpt not found.")
        return {"chunk_id": chunk_id, "version": version, "text": "Full source excerpt."}


class HTTPBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets = TemporaryDirectory()
        for name, body in {"index.html": "<h1>Fixture</h1>", "style.css": "body{}", "app.js": "void 0;"}.items():
            (Path(cls.assets.name) / name).write_text(body)
        cls.asset_patch = patch("versionlens.server.WEB_ROOT", Path(cls.assets.name))
        cls.asset_patch.start()
        cls.service = RecordingService()
        cls.server = create_server(cls.service, host="127.0.0.1", port=0)
        cls.port = cls.server.server_address[1]
        cls.host = f"127.0.0.1:{cls.port}"
        cls.origin = f"http://{cls.host}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.service.release.set()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)
        cls.asset_patch.stop()
        cls.assets.cleanup()
        if cls.thread.is_alive():
            raise AssertionError("HTTP fixture server did not stop")

    def setUp(self):
        self.service.reset()

    def request(self, method, path, body=None, headers=None):
        fields = {"Connection": "close"}
        fields.update(headers or {})
        connection = http_client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        try:
            connection.request(method, path, body=body, headers=fields)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read(1024 * 1024)
        finally:
            connection.close()

    def post(self, path="/api/search", payload=None, headers=None):
        fields = {"Content-Type": "application/json"}
        fields.update(headers or {})
        body = json.dumps(SEARCH if payload is None else payload).encode("utf-8")
        return self.request("POST", path, body, fields)

    def raw_request(self, method="POST", path="/api/search", headers=(), body=b"", include_host=True):
        lines = [f"{method} {path} HTTP/1.1", "Connection: close"]
        if include_host:
            lines.append(f"Host: {self.host}")
        lines.extend(f"{name}: {value}" for name, value in headers)
        data = ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1") + body
        with socket.create_connection(("127.0.0.1", self.port), timeout=3) as connection:
            connection.sendall(data)
            response = http_client.HTTPResponse(connection)
            response.begin()
            return response.status, dict(response.getheaders()), response.read(1024 * 1024)

    def assert_error(self, result, status):
        actual, headers, body = result
        self.assertIn(actual, status if isinstance(status, tuple) else (status,))
        self.assertTrue(headers.get("Content-Type", "").startswith("application/json"))
        error = json.loads(body)["error"]
        self.assertIsInstance(error.get("code"), str)
        self.assertTrue(error["code"])
        self.assertIsInstance(error.get("message"), str)
        self.assertTrue(error["message"])
        return error

    def assert_security_headers(self, headers):
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(headers.get("X-Frame-Options"), "DENY")
        self.assertIn("no-store", headers.get("Cache-Control", ""))
        policy = headers.get("Content-Security-Policy", "")
        self.assertIn("default-src 'none'", policy)
        for directive in ("script-src", "style-src", "connect-src"):
            self.assertIn(f"{directive} 'self'", policy)
        self.assertNotIn("https:", policy)
        self.assertNotIn("'unsafe-eval'", policy)
        for name in headers:
            self.assertFalse(name.lower().startswith("access-control-"))

    def test_factory_rejects_any_host_except_exact_ipv4_loopback(self):
        for host in ("0.0.0.0", "localhost", "127.0.0.2", "::1", "example.com", ""):
            with self.subTest(host=host), self.assertRaises(ValueError):
                create_server(self.service, host=host, port=0)
        self.assertEqual(self.server.server_address[0], "127.0.0.1")
        self.assertGreater(self.port, 0)

    def test_catalog_accepts_direct_local_clients_without_origin(self):
        status, headers, body = self.request("GET", "/api/catalog")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["product"], "httpx")
        self.assertEqual(self.service.calls, [("catalog", ())])
        self.assert_security_headers(headers)

    def test_same_origin_json_search_preserves_payload(self):
        payload = {**SEARCH, "question": "How does HTTPS work with für proxies?"}
        status, headers, body = self.post(payload=payload, headers={
            "Origin": self.origin, "Sec-Fetch-Site": "same-origin",
            "Content-Type": "application/json; charset=utf-8",
        })
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["question"], payload["question"])
        self.assertEqual(self.service.calls, [("search", (payload,))])
        self.assert_security_headers(headers)

    def test_ask_route_returns_service_draft_without_a_real_model(self):
        status, _, body = self.post("/api/ask", headers={"Origin": self.origin})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), self.service.ask_result)
        self.assertEqual(self.service.calls[0][0], "ask")

    def test_source_excerpt_route_keeps_exact_chunk_and_version(self):
        status, _, body = self.request("GET", f"/api/chunks/{CHUNK_ID}?version={VERSION}")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["text"], "Full source excerpt.")
        self.assertEqual(self.service.calls, [("chunk", (CHUNK_ID, VERSION))])

    def test_missing_or_wrong_version_source_returns_json_404(self):
        for chunk_id, version in (("b" * 24, VERSION), (CHUNK_ID, "0.27.2")):
            with self.subTest(chunk_id=chunk_id, version=version):
                result = self.request("GET", f"/api/chunks/{chunk_id}?version={version}")
                self.assert_error(result, 404)
                self.assert_security_headers(result[1])

    def test_static_allowlist_uses_local_assets_and_head_has_no_body(self):
        for path, content_types in (("/", ("text/html",)), ("/style.css", ("text/css",)), ("/app.js", ("application/javascript", "text/javascript"))):
            with self.subTest(path=path):
                status, headers, body = self.request("GET", path)
                self.assertEqual(status, 200)
                self.assertTrue(headers.get("Content-Type", "").startswith(content_types))
                self.assertTrue(body)
                self.assert_security_headers(headers)
                head_status, head_headers, head_body = self.request("HEAD", path)
                self.assertEqual(head_status, 200)
                self.assertEqual(head_body, b"")
                self.assertEqual(int(head_headers["Content-Length"]), len(body))

    def test_queries_traversal_percent_encoding_and_unknown_static_paths_are_blocked(self):
        for path in (
            "/../pyproject.toml", "/%2e%2e/pyproject.toml", "/%61pp.js", "/app.js?cache=1",
            "/index.html", "/data/sources.json",
        ):
            with self.subTest(path=path):
                result = self.request("GET", path)
                self.assert_error(result, 404)
                self.assert_security_headers(result[1])
        for target in ("http://example.com/app.js", "http://[bad/"):
            self.assert_error(self.raw_request("GET", target), 400)
        self.assertEqual(self.request("GET", "/style.css?")[0], 200)
        self.assertEqual(self.service.calls, [])

    def test_unknown_api_and_post_targets_return_json_404(self):
        self.assert_error(self.request("GET", "/api/unknown"), 404)
        self.assert_error(self.post("/api/unknown"), 404)
        self.assertEqual(self.service.calls, [])

    def test_unsupported_methods_return_405_without_cors_or_service_calls(self):
        for method in ("PUT", "DELETE", "OPTIONS", "PATCH"):
            with self.subTest(method=method):
                result = self.request(method, "/api/search")
                self.assert_error(result, 405)
                self.assert_security_headers(result[1])
        self.assertEqual(self.service.calls, [])

    def test_host_header_must_match_the_bound_ip_and_port(self):
        for host in (f"localhost:{self.port}", "127.0.0.1", f"evil.invalid:{self.port}", "127.0.0.1:1"):
            with self.subTest(host=host):
                self.assert_error(self.request("GET", "/api/catalog", headers={"Host": host}), 400)
        self.assertEqual(self.service.calls, [])

    def test_missing_or_duplicate_host_is_rejected(self):
        self.assert_error(self.raw_request("GET", "/api/catalog", include_host=False), 400)
        self.assert_error(self.raw_request("GET", "/api/catalog", headers=(("Host", self.host),)), 400)
        self.assertEqual(self.service.calls, [])

    def test_request_header_names_are_case_insensitive(self):
        body = json.dumps(SEARCH).encode()
        result = self.raw_request(headers=(
            ("hOsT", self.host), ("oRiGiN", self.origin),
            ("cOnTeNt-TyPe", "application/json"), ("cOnTeNt-LeNgTh", len(body)),
        ), body=body, include_host=False)
        self.assertEqual(result[0], 200)
        self.assertEqual(self.service.calls, [("search", (SEARCH,))])

    def test_cross_origin_or_cross_site_browser_requests_never_reach_service(self):
        for headers in (
            {"Origin": "https://evil.invalid"}, {"Origin": "null"},
            {"Origin": f"http://localhost:{self.port}"},
            {"Origin": self.origin, "Sec-Fetch-Site": "cross-site"},
        ):
            with self.subTest(headers=headers):
                self.assert_error(self.post(headers=headers), 403)
        self.assertEqual(self.service.calls, [])

    def test_duplicate_origin_is_rejected_even_when_values_match(self):
        body = json.dumps(SEARCH).encode()
        result = self.raw_request(headers=(
            ("Origin", self.origin), ("Origin", self.origin),
            ("Content-Type", "application/json"), ("Content-Length", len(body)),
        ), body=body)
        self.assert_error(result, (400, 403))
        self.assertEqual(self.service.calls, [])

    def test_post_requires_json_content_type(self):
        self.assert_error(self.request("POST", "/api/search", b"{}"), 415)
        for content_type in ("text/plain", "application/x-www-form-urlencoded", "application/jsonp"):
            with self.subTest(content_type=content_type):
                self.assert_error(self.post(headers={"Content-Type": content_type}), 415)
        self.assertEqual(self.service.calls, [])

    def test_post_requires_one_ascii_decimal_content_length(self):
        common = (("Content-Type", "application/json"),)
        self.assert_error(self.raw_request(headers=common), 400)
        for length in ("-1", "+2", "2,2", "two", "²"):
            with self.subTest(length=length):
                self.assert_error(self.raw_request(headers=common + (("Content-Length", length),)), 400)
        self.assert_error(self.raw_request(headers=common + (
            ("Content-Length", "2"), ("Content-Length", "2"),
        ), body=b"{}"), 400)
        self.assertEqual(self.service.calls, [])

    def test_transfer_encoding_is_rejected_with_or_without_content_length(self):
        for headers in (
            (("Transfer-Encoding", "chunked"),),
            (("Transfer-Encoding", "identity"), ("Content-Length", "2")),
        ):
            with self.subTest(headers=headers):
                self.assert_error(self.raw_request(headers=(("Content-Type", "application/json"),) + headers), 400)
        self.assertEqual(self.service.calls, [])

    def test_oversized_body_is_rejected_before_waiting_for_the_body(self):
        result = self.raw_request(headers=(
            ("Content-Type", "application/json"), ("Content-Length", "16385"),
        ))
        self.assert_error(result, 413)
        self.assertEqual(self.service.calls, [])

    def test_invalid_utf8_json_constants_and_nonobject_bodies_are_rejected(self):
        for body in (b"{bad", b"\xff", b"[]", b"null", b'{"question":NaN}', b'{"question":Infinity}'):
            with self.subTest(body=body):
                self.assert_error(self.request("POST", "/api/search", body, {"Content-Type": "application/json"}), 400)
        self.assertEqual(self.service.calls, [])

    def test_service_validation_errors_become_json_400(self):
        self.service.failure = ValidationError("Invalid question")
        result = self.post()
        self.assert_error(result, 400)
        self.assert_security_headers(result[1])

    def test_internal_and_runtime_errors_do_not_expose_private_details(self):
        for failure, status in (
            (RuntimeError("private /secret/path and token fixture"), 500),
            (LocalModelError("private upstream response and token fixture"), 503),
        ):
            self.service.failure = failure
            with self.subTest(failure=type(failure).__name__):
                result = self.post("/api/ask")
                self.assert_error(result, status)
                self.assertNotIn(b"private", result[2])
                self.assertNotIn(b"token fixture", result[2])
                self.assertNotIn(b"Traceback", result[2])
                self.assert_security_headers(result[1])

    def test_answer_runtime_error_result_becomes_sanitized_503(self):
        self.service.ask_result = {"status": "error", "reason": "local_model_error", "answer": "private runtime body"}
        result = self.post("/api/ask")
        self.assert_error(result, 503)
        self.assertNotIn(b"private", result[2])

    def test_concurrent_post_is_busy_while_catalog_remains_available(self):
        self.service.block_method = "search"
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            first = pool.submit(self.post)
            try:
                self.assertTrue(self.service.entered.wait(2), "First request never reached the fake service")
                self.assert_error(self.post("/api/ask"), 503)
                self.assertEqual(self.request("GET", "/api/catalog")[0], 200)
                self.assertEqual([name for name, _ in self.service.calls], ["search", "catalog"])
            finally:
                self.service.release.set()
            self.assertEqual(first.result(timeout=3)[0], 200)

    def test_eight_blocked_handlers_do_not_allow_unbounded_service_threads(self):
        self.service.block_method = "catalog"
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            requests = [pool.submit(self.request, "GET", "/api/catalog") for _ in range(8)]
            try:
                with self.service.condition:
                    complete = self.service.condition.wait_for(lambda: self.service.blocked_count == 8, timeout=2)
                self.assertTrue(complete, "Eight concurrent fixture requests were not accepted")
                self.assert_error(self.request("GET", "/api/catalog"), 503)
                self.assertEqual(self.service.blocked_count, 8)
            finally:
                self.service.release.set()
            self.assertTrue(all(request.result(timeout=3)[0] == 200 for request in requests))

    def test_stalled_partial_body_is_closed_within_the_request_timeout(self):
        data = (
            f"POST /api/search HTTP/1.1\r\nHost: {self.host}\r\n"
            "Content-Type: application/json\r\nContent-Length: 2\r\nConnection: close\r\n\r\n{"
        ).encode()
        started = time.monotonic()
        with socket.create_connection(("127.0.0.1", self.port), timeout=7) as connection:
            connection.sendall(data)
            response = http_client.HTTPResponse(connection)
            try:
                response.begin()
            except http_client.RemoteDisconnected:
                pass
            else:
                self.assertIn(response.status, (400, 408))
                response.read(1024 * 1024)
        self.assertLess(time.monotonic() - started, 7)
        self.assertEqual(self.service.calls, [])


if __name__ == "__main__":
    unittest.main()
