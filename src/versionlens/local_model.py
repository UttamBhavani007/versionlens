"""Bounded, proxy-free HTTP access to the approved local Ollama service."""

from dataclasses import dataclass
from http.client import HTTPException
import json
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from .config import LocalModelConfig


MAX_RESPONSE_BYTES = 128 * 1024


class LocalModelError(RuntimeError):
    """The local service could not produce a complete, validated response."""


@dataclass(frozen=True)
class ModelResponse:
    response: str
    model: str
    prompt_tokens: int
    output_tokens: int
    total_duration_ns: int


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def _reject_json_constant(value):
    raise ValueError("Non-finite JSON value")


def _usage_integer(payload: dict, name: str, *, optional: bool = False) -> int:
    value = payload.get(name, 0 if optional else None)
    if type(value) is not int or value < 0:
        raise LocalModelError("Local model returned invalid usage metadata.")
    return value


class LocalModelClient:
    def __init__(self, config: LocalModelConfig = LocalModelConfig()):
        try:
            # Revalidate even a dataclass modified outside its frozen contract.
            self.config = LocalModelConfig(
                base_url=config.base_url,
                model=config.model,
                timeout_seconds=config.timeout_seconds,
                num_ctx=config.num_ctx,
                max_output_tokens=config.max_output_tokens,
            )
        except (AttributeError, TypeError, ValueError):
            raise LocalModelError("Local model configuration is invalid.") from None
        self._opener = build_opener(ProxyHandler({}), _RejectRedirects())

    def _request(self, endpoint: str, payload: dict | None = None) -> dict:
        try:
            body = None if payload is None else json.dumps(payload, allow_nan=False).encode("utf-8")
        except (TypeError, ValueError, UnicodeError, RecursionError):
            raise LocalModelError("Local model request is not valid JSON.") from None
        request = Request(
            self.config.base_url + endpoint,
            data=body,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="GET" if body is None else "POST",
        )
        try:
            with self._opener.open(request, timeout=self.config.timeout_seconds) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            status = exc.code
            exc.close()
            raise LocalModelError(f"Local model request failed (HTTP {status}).") from None
        except (URLError, OSError, HTTPException):
            raise LocalModelError("Local model service is unavailable or timed out.") from None
        if len(raw) > MAX_RESPONSE_BYTES:
            raise LocalModelError("Local model response exceeds the size limit.")
        try:
            result = json.loads(raw.decode("utf-8"), parse_constant=_reject_json_constant)
        except (UnicodeError, ValueError, RecursionError):
            raise LocalModelError("Local model returned invalid JSON.") from None
        if not isinstance(result, dict):
            raise LocalModelError("Local model returned an invalid response object.")
        if "error" in result:
            raise LocalModelError("Local model service reported an error.")
        return result

    def health(self) -> dict:
        """Return only the exact approved model's local inventory entry."""
        payload = self._request("/api/tags")
        models = payload.get("models")
        if not isinstance(models, list):
            raise LocalModelError("Local model inventory is invalid.")
        matches = [
            entry for entry in models
            if isinstance(entry, dict) and entry.get("name") == self.config.model
        ]
        if len(matches) != 1:
            raise LocalModelError("Selected model is not available in the local service.")
        selected = matches[0]
        if selected.get("model", self.config.model) != self.config.model:
            raise LocalModelError("Local model inventory does not match the selected model.")
        return selected

    def generate(self, system: str, prompt: str, schema: dict) -> ModelResponse:
        if not isinstance(system, str) or not system.strip():
            raise LocalModelError("A nonempty system instruction is required.")
        if not isinstance(prompt, str) or not prompt.strip():
            raise LocalModelError("A nonempty prompt is required.")
        if not isinstance(schema, dict):
            raise LocalModelError("A JSON schema object is required.")
        payload = self._request("/api/generate", {
            "model": self.config.model,
            "system": system,
            "prompt": prompt,
            "format": schema,
            "stream": False,
            "think": False,
            "options": {
                "num_ctx": self.config.num_ctx,
                "num_predict": self.config.max_output_tokens,
                "temperature": 0,
            },
            "keep_alive": "5m",
        })
        if payload.get("model") != self.config.model:
            raise LocalModelError("Local model response does not match the selected model.")
        if payload.get("done") is not True:
            raise LocalModelError("Local model generation did not finish.")
        if "done_reason" in payload and payload["done_reason"] != "stop":
            raise LocalModelError("Local model generation did not finish naturally.")
        response = payload.get("response")
        if not isinstance(response, str) or not response.strip():
            raise LocalModelError("Local model returned no answer.")
        return ModelResponse(
            response=response,
            model=self.config.model,
            prompt_tokens=_usage_integer(payload, "prompt_eval_count"),
            output_tokens=_usage_integer(payload, "eval_count"),
            total_duration_ns=_usage_integer(payload, "total_duration", optional=True),
        )
