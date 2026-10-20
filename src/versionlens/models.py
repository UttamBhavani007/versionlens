"""Validated provenance and version contracts, independent of retrieval engines."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import PurePosixPath
import re


SUPPORTED_VERSIONS = ("0.27.2", "0.28.1")
UPSTREAM_COMMITS = {
    "0.27.2": "609df7ecc0f7cb10a1c998aa9c269bba77337c5f",
    "0.28.1": "26d48e0634e6ee9cdc0533996db289ce4b430177",
}


class ValidationError(ValueError):
    """The request or source metadata violates the supported contract."""


def validate_version(value: str) -> str:
    if value not in SUPPORTED_VERSIONS:
        raise ValidationError(
            f"Select an exact supported version: {', '.join(SUPPORTED_VERSIONS)}."
        )
    return value


def validate_relative_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValidationError("Source paths must be relative POSIX paths.")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValidationError("Source paths cannot be absolute or contain traversal.")
    return value


@dataclass(frozen=True)
class Source:
    source_id: str
    product: str
    version: str
    path: str
    upstream_path: str
    commit: str
    sha256: str
    url: str
    title: str

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value for value in vars(self).values()):
            raise ValidationError("All source fields must be nonempty strings.")
        validate_version(self.version)
        validate_relative_path(self.path)
        validate_relative_path(self.upstream_path)
        if self.product != "httpx" or self.commit != UPSTREAM_COMMITS[self.version]:
            raise ValidationError("Source must match its approved HTTPX snapshot commit.")
        if not re.fullmatch(r"[0-9a-f]{64}", self.sha256):
            raise ValidationError("Source checksum must be a SHA-256 hex digest.")
        if self.source_id != f"httpx:{self.version}:{self.upstream_path}":
            raise ValidationError("Source ID does not match its version and upstream path.")
        if self.path != f"data/corpus/httpx/{self.version}/{self.upstream_path}":
            raise ValidationError("Source path is outside the expected snapshot directory.")
        expected_url = f"https://github.com/encode/httpx/blob/{self.commit}/{self.upstream_path}"
        if self.url != expected_url:
            raise ValidationError("Source URL must point to its immutable upstream commit.")


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source: Source
    section: str
    start_line: int
    end_line: int
    text: str

    @property
    def citation_url(self) -> str:
        return f"{self.source.url}#L{self.start_line}-L{self.end_line}"

    @classmethod
    def create(cls, source: Source, section: str, start: int, end: int, text: str) -> "Chunk":
        if not (1 <= start <= end) or not text.strip():
            raise ValidationError("A chunk needs a valid line range and nonempty text.")
        identity = f"{source.source_id}:{source.sha256}:{start}:{end}"
        return cls(sha256(identity.encode()).hexdigest()[:24], source, section, start, end, text)


@dataclass(frozen=True)
class SearchRequest:
    question: str
    version: str
    limit: int = 5

    def __post_init__(self) -> None:
        validate_version(self.version)
        if not isinstance(self.question, str) or not self.question.strip():
            raise ValidationError("Question must not be empty.")
        if len(self.question) > 2000:
            raise ValidationError("Question is limited to 2000 characters.")
        if type(self.limit) is not int or not 1 <= self.limit <= 20:
            raise ValidationError("Result limit must be between 1 and 20.")
