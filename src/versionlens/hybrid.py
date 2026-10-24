"""Fixed reciprocal-rank fusion of version-filtered lexical and vector results.

The fused score is a ranking value, never an answer-confidence estimate. Raw
BM25 and cosine scores are deliberately not combined or rescaled.
"""

from pathlib import Path

from .models import SearchRequest, ValidationError
from .retrieval import SearchHit, search
from .vector_store import corpus_fingerprint, load_chunks, vector_search


CANDIDATE_POOL = 20
RRF_CONSTANT = 60


def hybrid_search(index_path: Path, vector_path: Path, request: SearchRequest,
                  client=None) -> tuple[SearchHit, ...]:
    """Fuse up to twenty candidates per engine, then apply the requested limit.

    Each engine receives the exact requested version. A failed or stale vector
    index remains an error; hybrid retrieval never silently becomes a different
    retrieval mode. Defensive checks also reject version or provenance mistakes
    before any fused result is returned.
    """
    initial_corpus = corpus_fingerprint(load_chunks(index_path))
    pool_request = SearchRequest(request.question, request.version, CANDIDATE_POOL, request.access_profile)
    rankings = (
        search(index_path, pool_request),
        vector_search(index_path, vector_path, pool_request, client=client),
    )
    if corpus_fingerprint(load_chunks(index_path)) != initial_corpus:
        raise ValidationError("Source index changed during hybrid retrieval. Retry after rebuilding the vector index.")
    scores: dict[str, float] = {}
    hits: dict[str, SearchHit] = {}
    for ranking in rankings:
        seen: set[str] = set()
        for rank, hit in enumerate(ranking, 1):
            chunk = hit.chunk
            if chunk.source.version != request.version:
                raise ValidationError("Retriever returned evidence from another version.")
            if not request.allows(chunk.source):
                raise ValidationError("Retriever returned evidence outside the configured access profile.")
            if chunk.chunk_id in seen:
                raise ValidationError("Retriever returned duplicate chunk IDs.")
            seen.add(chunk.chunk_id)
            previous = hits.get(chunk.chunk_id)
            if previous is not None and previous.chunk != chunk:
                raise ValidationError("Retrievers returned inconsistent source provenance.")
            hits[chunk.chunk_id] = hit
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (RRF_CONSTANT + rank)
    ordered = sorted(scores, key=lambda chunk_id: (-scores[chunk_id], chunk_id))
    return tuple(SearchHit(hits[chunk_id].chunk, scores[chunk_id])
                 for chunk_id in ordered[:request.limit])
