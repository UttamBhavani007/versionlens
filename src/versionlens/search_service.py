"""Explicit retrieval selection; keyword remains the default baseline."""

from pathlib import Path

from .models import SearchRequest, ValidationError
from .retrieval import SearchHit, search


RETRIEVERS = ("keyword", "vector", "hybrid")


def retrieve(index_path: Path, request: SearchRequest, *, method: str = "keyword",
             vector_path: Path | None = None, client=None) -> tuple[SearchHit, ...]:
    if method not in RETRIEVERS:
        raise ValidationError("Choose keyword, vector, or hybrid retrieval.")
    if method == "keyword":
        return search(index_path, request)
    if vector_path is None:
        raise ValidationError("Vector and hybrid retrieval require a vector index path.")
    if method == "vector":
        from .vector_store import vector_search
        return vector_search(index_path, vector_path, request, client)
    from .hybrid import hybrid_search
    return hybrid_search(index_path, vector_path, request, client)
