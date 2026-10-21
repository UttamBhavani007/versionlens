"""Bounded configuration for the project's free local generation service."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class LocalModelConfig:
    """Only literal loopback endpoints and the reviewed local model are allowed."""

    base_url: str = "http://127.0.0.1:11435"
    model: str = "qwen3:1.7b"
    timeout_seconds: float = 120.0
    num_ctx: int = 8192
    max_output_tokens: int = 600

    def __post_init__(self) -> None:
        # Exact canonical strings avoid DNS resolution, URL parser normalization,
        # userinfo ambiguity, encoded hosts, and accidental remote endpoints.
        if not isinstance(self.base_url, str) or self.base_url not in {
            "http://127.0.0.1:11435", "http://[::1]:11435",
        }:
            raise ValueError("Local model endpoint must be HTTP literal loopback on port 11435")
        if self.model != "qwen3:1.7b":
            raise ValueError("Only the approved local model qwen3:1.7b is allowed")
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not 0 < self.timeout_seconds <= 300
            or not math.isfinite(self.timeout_seconds)
        ):
            raise ValueError("Local model timeout must be finite and in (0, 300] seconds")
        if type(self.num_ctx) is not int or not 512 <= self.num_ctx <= 8192:
            raise ValueError("Local model context must be an integer from 512 to 8192")
        if type(self.max_output_tokens) is not int or not 1 <= self.max_output_tokens <= 600:
            raise ValueError("Local model output limit must be an integer from 1 to 600")
