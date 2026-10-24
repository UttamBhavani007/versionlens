"""Validated application operations for the local HTTP boundary.

Requests select questions, exact versions, and retrieval methods. Filesystem
locations are supplied only by the application at construction time.
"""

from pathlib import Path
import re
import unicodedata

from .answering import answer
from .models import SearchRequest, ValidationError, validate_version, validate_access_profile
from .retrieval import SearchHit
from .search_service import RETRIEVERS, retrieve
from .store import index_stats
from .vector_store import load_chunks


QUERY_FIELDS = frozenset({"question", "version", "retriever", "limit"})
REQUIRED_QUERY_FIELDS = frozenset({"question", "version"})


class ApiNotFound(ValidationError):
    """The requested indexed excerpt is absent from the selected version."""


def _query(payload: dict, access_profile: str = "public") -> tuple[SearchRequest, str]:
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")
    if not REQUIRED_QUERY_FIELDS.issubset(payload) or set(payload) - QUERY_FIELDS:
        raise ValidationError("Provide question and version, with only optional retriever and limit fields.")
    question = payload["question"]
    version = payload["version"]
    method = payload.get("retriever", "keyword")
    limit = payload.get("limit", 5)
    if not isinstance(question, str):
        raise ValidationError("Question must be a string.")
    if any(
        unicodedata.category(character) in {"Cc", "Cs"} and character not in "\n\r\t"
        for character in question
    ):
        raise ValidationError("Question must not contain control characters or invalid Unicode.")
    if not isinstance(version, str):
        raise ValidationError("Version must be an exact supported version string.")
    if not isinstance(method, str) or method not in RETRIEVERS:
        raise ValidationError("Choose keyword, vector, or hybrid retrieval.")
    # SearchRequest rejects booleans, nonintegers, empty questions, unsupported
    # versions, invalid Unicode, and lengths beyond the shared CLI contract.
    return SearchRequest(question, version, limit, access_profile), method


class ApiService:
    def __init__(self, index_path: Path, vector_path: Path, access_profile: str = "public"):
        self.access_profile = validate_access_profile(access_profile)
        self.index_path = Path(index_path)
        self.vector_path = Path(vector_path)

    def catalog(self) -> dict:
        """Describe indexed snapshots and supported operations, without probing models."""
        stats = index_stats(self.index_path, access_profile=self.access_profile)
        return {
            "product": "httpx",
            "versions": stats["versions"],
            "retrievers": list(RETRIEVERS),
            "default_retriever": "keyword",
            "access_profile": self.access_profile, "permission_demo": True,
            "index": stats,
        }

    def search(self, payload: dict) -> dict:
        request, method = _query(payload, self.access_profile)
        hits = retrieve(self.index_path, request, method=method, vector_path=self.vector_path)
        if any(hit.chunk.source.version != request.version for hit in hits):
            raise ValidationError("Retrieval returned evidence from another version.")
        if any(not request.allows(hit.chunk.source) for hit in hits):
            raise ValidationError("Retrieval returned evidence outside the configured access profile.")
        return {
            "access_profile": self.access_profile,
            "status": "evidence_found" if hits else "no_matching_evidence",
            "mode": f"{method}_retrieval_only",
            "retrieval_method": method,
            "version": request.version,
            "question": request.question,
            "answer": None,
            "notice": "Ranked source excerpts, not a generated or verified answer. Scores are not confidence.",
            "hits": [hit.to_dict() for hit in hits],
        }

    def ask(self, payload: dict) -> dict:
        request, method = _query(payload, self.access_profile)
        # Preserve the answering policy's draft notice, mechanical-check flags,
        # abstention reasons, and sanitized runtime-error result unchanged.
        return answer(
            self.index_path, request, retrieval_method=method, vector_path=self.vector_path
        )

    def chunk(self, chunk_id: str, version: str) -> dict:
        if not isinstance(chunk_id, str) or re.fullmatch(r"[0-9a-f]{24}", chunk_id) is None:
            raise ValidationError("Source excerpt ID must be 24 lowercase hexadecimal characters.")
        if not isinstance(version, str):
            raise ValidationError("Version must be an exact supported version string.")
        validate_version(version)
        for chunk in load_chunks(self.index_path):
            if (chunk.chunk_id == chunk_id and chunk.source.version == version
                    and SearchRequest("inspect", version, access_profile=self.access_profile).allows(chunk.source)):
                result = SearchHit(chunk, 0.0).to_dict()
                del result["score"]
                result.update({
                    "product": chunk.source.product,
                    "title": chunk.source.title,
                    "upstream_path": chunk.source.upstream_path,
                })
                return result
        raise ApiNotFound("Source excerpt not found.")
