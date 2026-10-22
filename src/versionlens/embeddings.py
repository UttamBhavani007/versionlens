"""Bounded local Nomic embeddings with explicit task prefixes and model identity."""

from dataclasses import dataclass
from http.client import HTTPException
import json
import math
import re
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from .local_model import LocalModelError

EMBEDDING_MODEL = "nomic-embed-text:v1.5"
EMBEDDING_DIMENSIONS = 768
PREPROCESSING_REVISION = "nomic-search-prefix-v1"
MAX_INPUT_BYTES = 12_000
MAX_BATCH_SIZE = 16
MAX_BATCH_BYTES = MAX_INPUT_BYTES * MAX_BATCH_SIZE
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class LocalEmbeddingError(LocalModelError):
    """The selected local model could not produce a validated embedding batch."""


@dataclass(frozen=True)
class LocalEmbeddingConfig:
    base_url: str = "http://127.0.0.1:11435"
    model: str = EMBEDDING_MODEL
    timeout_seconds: float = 120.0
    dimensions: int = EMBEDDING_DIMENSIONS
    num_ctx: int = 8192

    def __post_init__(self) -> None:
        if not isinstance(self.base_url, str) or self.base_url not in {
            "http://127.0.0.1:11435", "http://[::1]:11435",
        }:
            raise ValueError("Embedding endpoint must be HTTP literal loopback on port 11435")
        if self.model != EMBEDDING_MODEL:
            raise ValueError("Only the approved local Nomic embedding model is allowed")
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not 0 < self.timeout_seconds <= 300
            or not math.isfinite(self.timeout_seconds)
        ):
            raise ValueError("Embedding timeout must be finite and in (0, 300] seconds")
        if type(self.dimensions) is not int or self.dimensions != EMBEDDING_DIMENSIONS:
            raise ValueError("Embedding dimensions must be exactly 768")
        if type(self.num_ctx) is not int or self.num_ctx != 8192:
            raise ValueError("Embedding context must be exactly 8192 tokens")


@dataclass(frozen=True)
class EmbeddingIdentity:
    model: str
    digest: str
    dimensions: int

    def __post_init__(self) -> None:
        if self.model != EMBEDDING_MODEL:
            raise ValueError("Embedding identity must name the approved model")
        if not isinstance(self.digest, str) or re.fullmatch(r"[0-9a-f]{64}", self.digest) is None:
            raise ValueError("Embedding identity digest must be full lowercase SHA-256 hex")
        if type(self.dimensions) is not int or self.dimensions != EMBEDDING_DIMENSIONS:
            raise ValueError("Embedding identity must have exactly 768 dimensions")


@dataclass(frozen=True)
class EmbeddingBatch:
    vectors: tuple[tuple[float, ...], ...]
    identity: EmbeddingIdentity
    prompt_tokens: int
    total_duration_ns: int


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def _reject_json_constant(value):
    raise ValueError("Non-finite JSON value")


def _usage_integer(payload: dict, name: str) -> int:
    value = payload.get(name)
    if type(value) is not int or not 0 <= value <= 2**63 - 1:
        raise LocalEmbeddingError("Local embedding service returned invalid usage metadata.")
    return value


def _normalized_vector(vector: object) -> tuple[float, ...]:
    if not isinstance(vector, list) or len(vector) != EMBEDDING_DIMENSIONS:
        raise LocalEmbeddingError("Local embedding service returned an invalid vector shape.")
    values = []
    for value in vector:
        if type(value) not in (int, float):
            raise LocalEmbeddingError("Local embedding service returned a nonnumeric vector.")
        try:
            number = float(value)
        except (ValueError, OverflowError):
            raise LocalEmbeddingError("Local embedding service returned an invalid vector.") from None
        if not math.isfinite(number):
            raise LocalEmbeddingError("Local embedding service returned a non-finite vector.")
        values.append(number)
    scale = max(abs(value) for value in values)
    if scale == 0:
        raise LocalEmbeddingError("Local embedding service returned a zero vector.")
    # Scaling first avoids overflow for large finite values and underflow for
    # tiny ones. The model's full 768 dimensions remain intact.
    scaled = tuple(value / scale for value in values)
    norm = math.sqrt(math.fsum(value * value for value in scaled))
    return tuple(value / norm for value in scaled)


class LocalEmbeddingClient:
    def __init__(self, config: LocalEmbeddingConfig = LocalEmbeddingConfig()):
        try:
            self.config = LocalEmbeddingConfig(
                base_url=config.base_url, model=config.model,
                timeout_seconds=config.timeout_seconds,
                dimensions=config.dimensions, num_ctx=config.num_ctx,
            )
        except (AttributeError, TypeError, ValueError):
            raise LocalEmbeddingError("Local embedding configuration is invalid.") from None
        self._opener = build_opener(ProxyHandler({}), _RejectRedirects())

    def _request(self, endpoint: str, payload: dict | None = None) -> dict:
        if endpoint not in {"/api/tags", "/api/embed"}:
            raise LocalEmbeddingError("Local embedding endpoint is invalid.")
        try:
            body = None if payload is None else json.dumps(
                payload, ensure_ascii=False, allow_nan=False,
            ).encode("utf-8")
        except (TypeError, ValueError, UnicodeError, RecursionError):
            raise LocalEmbeddingError("Local embedding request is invalid.") from None
        request = Request(
            self.config.base_url + endpoint, data=body,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="GET" if body is None else "POST",
        )
        try:
            with self._opener.open(request, timeout=self.config.timeout_seconds) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            status = exc.code
            exc.close()
            raise LocalEmbeddingError(f"Local embedding request failed (HTTP {status}).") from None
        except (URLError, OSError, HTTPException):
            raise LocalEmbeddingError("Local embedding service is unavailable or timed out.") from None
        if len(raw) > MAX_RESPONSE_BYTES:
            raise LocalEmbeddingError("Local embedding response exceeds the size limit.")
        try:
            result = json.loads(raw.decode("utf-8"), parse_constant=_reject_json_constant)
        except (UnicodeError, ValueError, RecursionError):
            raise LocalEmbeddingError("Local embedding service returned invalid JSON.") from None
        if not isinstance(result, dict):
            raise LocalEmbeddingError("Local embedding service returned an invalid response object.")
        if "error" in result:
            raise LocalEmbeddingError("Local embedding service reported an error.")
        return result

    def identity(self) -> EmbeddingIdentity:
        """Validate the exact approved local inventory entry and full model digest."""
        models = self._request("/api/tags").get("models")
        if not isinstance(models, list):
            raise LocalEmbeddingError("Local embedding model inventory is invalid.")
        matches = [entry for entry in models if (
            isinstance(entry, dict) and entry.get("name") == self.config.model
        )]
        if len(matches) != 1:
            raise LocalEmbeddingError("Selected embedding model is not available locally.")
        selected = matches[0]
        if (
            selected.get("model", self.config.model) != self.config.model
            or selected.get("remote_host") or selected.get("remote_model")
        ):
            raise LocalEmbeddingError("Embedding inventory does not match the selected local model.")
        try:
            return EmbeddingIdentity(
                model=self.config.model, digest=selected.get("digest"),
                dimensions=self.config.dimensions,
            )
        except (TypeError, ValueError):
            raise LocalEmbeddingError("Local embedding model digest is invalid.") from None

    def _embed(self, texts: list[str], prefix: str) -> EmbeddingBatch:
        if not isinstance(texts, list) or not 1 <= len(texts) <= MAX_BATCH_SIZE:
            raise LocalEmbeddingError("Embedding batches must contain 1 to 16 texts.")
        texts = list(texts)
        byte_count = 0
        for text in texts:
            if not isinstance(text, str) or not text.strip():
                raise LocalEmbeddingError("Embedding inputs must be nonempty text.")
            try:
                size = len(text.encode("utf-8"))
            except UnicodeError:
                raise LocalEmbeddingError("Embedding inputs must be valid UTF-8 text.") from None
            if size > MAX_INPUT_BYTES:
                raise LocalEmbeddingError("Embedding input exceeds the UTF-8 byte limit.")
            byte_count += size
        if byte_count > MAX_BATCH_BYTES:
            raise LocalEmbeddingError("Embedding batch exceeds the UTF-8 byte limit.")
        before = self.identity()
        payload = self._request("/api/embed", {
            "model": self.config.model,
            "input": [prefix + text for text in texts],
            "truncate": False,
            "dimensions": self.config.dimensions,
            "options": {"num_ctx": self.config.num_ctx},
            "keep_alive": "5m",
        })
        if payload.get("model") != self.config.model:
            raise LocalEmbeddingError("Embedding response does not match the selected model.")
        vectors = payload.get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise LocalEmbeddingError("Local embedding service returned an invalid batch shape.")
        normalized = tuple(_normalized_vector(vector) for vector in vectors)
        prompt_tokens = _usage_integer(payload, "prompt_eval_count")
        total_duration = _usage_integer(payload, "total_duration")
        if self.identity() != before:
            raise LocalEmbeddingError("Local embedding model changed during the request.")
        return EmbeddingBatch(
            vectors=normalized, identity=before, prompt_tokens=prompt_tokens,
            total_duration_ns=total_duration,
        )

    def embed_documents(self, texts: list[str]) -> EmbeddingBatch:
        return self._embed(texts, "search_document: ")

    def embed_query(self, text: str) -> EmbeddingBatch:
        return self._embed([text], "search_query: ")
