"""Bounded loopback HTTP transport for the local VersionLens demo.

This server is a local workstation tool, not an authenticated public deployment.
It serves only three bundled assets and the explicit, read-only application API.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import socket
from threading import BoundedSemaphore, Lock
from urllib.parse import parse_qs, urlsplit

from .api import ApiNotFound, ApiService
from .local_model import LocalModelError
from .models import ValidationError


WEB_ROOT = Path(__file__).with_name("web")
MAX_BODY_BYTES = 16_384
MAX_CONNECTIONS = 8
CONNECTION_TIMEOUT_SECONDS = 5
SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}
STATIC_FILES = {"/": ("index.html", "text/html; charset=utf-8"),
                "/style.css": ("style.css", "text/css; charset=utf-8"),
                "/app.js": ("app.js", "text/javascript; charset=utf-8")}


class HttpInputError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message


def _strict_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("Duplicate JSON key")
        result[name] = value
    return result


def _reject_constant(value):
    raise ValueError("Nonstandard JSON number")


class VersionLensHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False
    allow_reuse_address = True
    request_queue_size = 16

    def __init__(self, address, service):
        self.service = service
        self.work_lock = Lock()
        self.connection_slots = BoundedSemaphore(MAX_CONNECTIONS)
        super().__init__(address, VersionLensHandler)

    def get_request(self):
        request, address = super().get_request()
        request.settimeout(CONNECTION_TIMEOUT_SECONDS)
        return request, address

    def process_request(self, request, client_address):
        if not self.connection_slots.acquire(blocking=False):
            headers = "\r\n".join(f"{key}: {value}" for key, value in SECURITY_HEADERS.items())
            body = json.dumps({"error": {"code": "busy", "message": "Local connection capacity reached. Please try again shortly."}}).encode("utf-8")
            raw = f"HTTP/1.0 503 Service Unavailable\r\n{headers}\r\nConnection: close\r\nContent-Type: application/json; charset=utf-8\r\nContent-Length: {len(body)}\r\n\r\n"
            try:
                request.sendall(raw.encode("ascii") + body)
            except OSError:
                pass
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.connection_slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.connection_slots.release()

    def handle_error(self, request, client_address):
        # Error responses and local diagnostics never log source text or secrets.
        pass


class VersionLensHandler(BaseHTTPRequestHandler):
    server_version = "VersionLens"
    sys_version = ""
    protocol_version = "HTTP/1.0"

    def log_message(self, format, *args):
        pass

    def _respond(self, status: int, body: bytes, content_type: str):
        self.close_connection = True
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        for key, value in SECURITY_HEADERS.items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, status: int, payload: dict):
        raw = json.dumps(payload, ensure_ascii=True, allow_nan=False).encode("utf-8")
        self._respond(status, raw, "application/json; charset=utf-8")

    def _error(self, status: int, code: str, message: str):
        self._json(status, {"error": {"code": code, "message": message}})

    def send_error(self, code, message=None, explain=None):
        if code == 501:
            self._error(405, "method_not_allowed", "This HTTP method is not supported.")
        else:
            self._error(code, "invalid_http_request", "The HTTP request could not be processed.")

    def _guard(self):
        origin = f"http://127.0.0.1:{self.server.server_port}"
        hosts = self.headers.get_all("Host", [])
        if hosts != [f"127.0.0.1:{self.server.server_port}"]:
            raise HttpInputError(400, "invalid_host", "Use the exact local address shown at startup.")
        origins = self.headers.get_all("Origin", [])
        if len(origins) > 1 or origins and origins != [origin]:
            raise HttpInputError(403, "origin_rejected", "Requests from another origin are not allowed.")
        fetch_sites = self.headers.get_all("Sec-Fetch-Site", [])
        if len(fetch_sites) > 1 or fetch_sites and fetch_sites[0] not in {"same-origin", "none"}:
            raise HttpInputError(403, "origin_rejected", "Requests from another site are not allowed.")
        try:
            parsed = urlsplit(self.path)
        except ValueError:
            raise HttpInputError(400, "invalid_target", "Use a valid local relative request path.") from None
        if parsed.scheme or parsed.netloc or parsed.fragment or not self.path.startswith("/"):
            raise HttpInputError(400, "invalid_target", "Use a local relative request path.")
        return parsed

    def _payload(self):
        if self.headers.get_all("Transfer-Encoding", []):
            raise HttpInputError(400, "invalid_body", "Transfer encodings are not supported.")
        content_types = self.headers.get_all("Content-Type", [])
        if (len(content_types) != 1 or content_types[0].lower() not in
                {"application/json", "application/json; charset=utf-8"}):
            raise HttpInputError(415, "json_required", "Send Content-Type: application/json.")
        lengths = self.headers.get_all("Content-Length", [])
        if len(lengths) != 1 or not re.fullmatch(r"[0-9]{1,8}", lengths[0]):
            raise HttpInputError(400, "invalid_body", "A single bounded Content-Length is required.")
        length = int(lengths[0])
        if length > MAX_BODY_BYTES:
            raise HttpInputError(413, "body_too_large", "The request body exceeds 16 KiB.")
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise HttpInputError(400, "invalid_body", "The request body is incomplete.")
        try:
            payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_object,
                                 parse_constant=_reject_constant)
            if not isinstance(payload, dict):
                raise ValueError("JSON object required")
            return payload
        except (ValueError, UnicodeError, RecursionError):
            raise HttpInputError(400, "invalid_json", "Send one valid UTF-8 JSON object.") from None

    def _dispatch(self):
        parsed = self._guard()
        if self.command in {"GET", "HEAD"}:
            if parsed.path in STATIC_FILES and not parsed.query:
                filename, content_type = STATIC_FILES[parsed.path]
                self._respond(200, (WEB_ROOT / filename).read_bytes(), content_type)
                return
            if self.command == "HEAD":
                raise HttpInputError(405, "method_not_allowed", "HEAD is supported only for bundled assets.")
            if parsed.path == "/api/catalog" and not parsed.query:
                self._json(200, self.server.service.catalog())
                return
            if parsed.path.startswith("/api/chunks/"):
                try:
                    query = parse_qs(parsed.query, strict_parsing=True, keep_blank_values=True, max_num_fields=2)
                except ValueError:
                    raise HttpInputError(400, "invalid_query", "Supply one exact version parameter.") from None
                if set(query) != {"version"} or len(query["version"]) != 1:
                    raise HttpInputError(400, "invalid_query", "Supply one exact version parameter.")
                chunk_id = parsed.path.removeprefix("/api/chunks/")
                self._json(200, self.server.service.chunk(chunk_id, query["version"][0]))
                return
            raise HttpInputError(404, "not_found", "The requested route was not found.")
        if self.command != "POST":
            raise HttpInputError(405, "method_not_allowed", "Use GET or POST for these routes.")
        if parsed.path not in {"/api/search", "/api/ask"} or parsed.query:
            raise HttpInputError(404, "not_found", "The requested route was not found.")
        payload = self._payload()
        if not self.server.work_lock.acquire(blocking=False):
            raise HttpInputError(503, "busy", "Another query is running. Please try again shortly.")
        try:
            method = self.server.service.search if parsed.path == "/api/search" else self.server.service.ask
            result = method(payload)
        finally:
            self.server.work_lock.release()
        if result.get("status") == "error":
            raise HttpInputError(503, "local_model_unavailable", "The local model could not complete the request. Check its server and try again.")
        self._json(200, result)

    def _handle(self):
        try:
            self._dispatch()
        except HttpInputError as exc:
            self._error(exc.status, exc.code, exc.message)
        except ApiNotFound:
            self._error(404, "not_found", "The requested source excerpt was not found in this version.")
        except ValidationError as exc:
            self._error(400, "invalid_request", str(exc))
        except LocalModelError:
            self._error(503, "local_model_unavailable", "The local model or vector index is unavailable. Check local setup and try again.")
        except (TimeoutError, socket.timeout):
            self._error(408, "request_timeout", "The request timed out.")
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True
        except Exception:
            self._error(500, "internal_error", "The local service could not complete the request.")

    do_GET = _handle
    do_HEAD = _handle
    do_POST = _handle


def create_server(service: ApiService, host: str = "127.0.0.1", port: int = 8765) -> VersionLensHTTPServer:
    if host != "127.0.0.1":
        raise ValidationError("The web service binds only to 127.0.0.1.")
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValidationError("The local port must be an integer from 0 to 65535.")
    return VersionLensHTTPServer((host, port), service)


def serve(index_path: Path, vector_path: Path, port: int = 8765) -> int:
    if type(port) is not int or not 1024 <= port <= 65535:
        raise ValidationError("Choose an unprivileged local port from 1024 to 65535.")
    with create_server(ApiService(index_path, vector_path), port=port) as server:
        print(f"VersionLens local UI: http://127.0.0.1:{server.server_port}", flush=True)
        print("Local workstation demo. Start the separate model server for draft answers.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            return 0
    return 0
