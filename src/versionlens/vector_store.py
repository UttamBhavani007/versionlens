"""A complete, version-filtered cosine index in a separate SQLite sidecar.

The small corpus is scanned directly: there is no approximate index, implicit
refresh, or score threshold presented as confidence. Cache identity binds every
source field and exact chunk text to the model digest and preprocessing revision.
"""

from contextlib import contextmanager
from dataclasses import asdict
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import sqlite3

from .embeddings import LocalEmbeddingClient, LocalEmbeddingConfig, PREPROCESSING_REVISION
from .models import Chunk, SearchRequest, Source, ValidationError
from .retrieval import SearchHit
from .store import _check_schema, connect


VECTOR_SCHEMA_VERSION = "1"
BATCH_SIZE = 16
UNIT_NORM_TOLERANCE = 1e-5


class VectorIndexError(ValidationError):
    """The vector sidecar is missing, stale, incomplete, or invalid."""


def _canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _chunks_from_connection(connection) -> tuple[Chunk, ...]:
    _check_schema(connection)
    rows = connection.execute(
        "SELECT c.*, s.metadata_json FROM chunks c "
        "LEFT JOIN sources s ON s.source_id=c.source_id ORDER BY c.chunk_id"
    ).fetchall()
    if not rows:
        raise VectorIndexError("Cannot use an empty source index.")
    chunks = []
    try:
        for row in rows:
            source = Source(**json.loads(row["metadata_json"]))
            if row["source_id"] != source.source_id or row["version"] != source.version:
                raise VectorIndexError("Source index contains inconsistent version metadata.")
            if (
                type(row["start_line"]) is not int or type(row["end_line"]) is not int
                or not isinstance(row["section"], str) or not row["section"].strip()
                or not isinstance(row["text"], str)
            ):
                raise VectorIndexError("Source index contains invalid chunk metadata.")
            chunk = Chunk.create(
                source, row["section"], row["start_line"], row["end_line"], row["text"]
            )
            if chunk.chunk_id != row["chunk_id"]:
                raise VectorIndexError("Source index contains an invalid chunk identity.")
            chunks.append(chunk)
    except (TypeError, KeyError, ValueError, UnicodeError) as exc:
        if isinstance(exc, VectorIndexError):
            raise
        raise VectorIndexError("Source index contains invalid provenance or chunks.") from None
    return tuple(chunks)


@contextmanager
def _source_snapshot(index_path: Path):
    with connect(index_path, readonly=True) as connection:
        connection.execute("BEGIN")
        try:
            yield _chunks_from_connection(connection)
        except sqlite3.Error:
            raise VectorIndexError("Source index could not be read. Rebuild the source index.") from None
        finally:
            connection.rollback()


def load_chunks(index_path: Path) -> tuple[Chunk, ...]:
    """Read validated chunks in stable chunk-ID order from one SQLite snapshot."""
    with _source_snapshot(index_path) as chunks:
        return chunks


def corpus_fingerprint(chunks: tuple[Chunk, ...]) -> str:
    """Hash exact text, spans, version, and all provenance in stable ID order."""
    payload = [asdict(chunk) for chunk in sorted(chunks, key=lambda chunk: chunk.chunk_id)]
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _validate_identity(identity):
    approved = LocalEmbeddingConfig()
    if (
        getattr(identity, "model", None) != approved.model
        or type(getattr(identity, "dimensions", None)) is not int
        or identity.dimensions != approved.dimensions
        or not isinstance(getattr(identity, "digest", None), str)
        or re.fullmatch(r"[0-9a-f]{64}", identity.digest) is None
    ):
        raise VectorIndexError("Embedding model identity or dimensions are invalid.")
    return identity


def _validate_vector(vector, dimensions: int) -> tuple[float, ...]:
    if not isinstance(vector, (tuple, list)) or len(vector) != dimensions:
        raise VectorIndexError("Embedding vector dimensions do not match the index.")
    if any(type(value) not in (int, float) for value in vector):
        raise VectorIndexError("Embedding vectors must contain only finite numbers.")
    try:
        normalized = tuple(float(value) for value in vector)
    except (ValueError, OverflowError):
        raise VectorIndexError("Embedding vectors must contain only finite numbers.") from None
    if any(not math.isfinite(value) for value in normalized):
        raise VectorIndexError("Embedding vectors must contain only finite numbers.")
    try:
        norm = math.sqrt(math.fsum(value * value for value in normalized))
    except (ValueError, OverflowError):
        raise VectorIndexError("Embedding vectors must have unit length.") from None
    if not math.isfinite(norm) or abs(norm - 1.0) > UNIT_NORM_TOLERANCE:
        raise VectorIndexError("Embedding vectors must have unit length.")
    return normalized


def _validated_batch(batch, identity, count: int):
    if getattr(batch, "identity", None) != identity:
        raise VectorIndexError("Embedding model changed while processing the index.")
    vectors = getattr(batch, "vectors", None)
    if not isinstance(vectors, (tuple, list)) or len(vectors) != count:
        raise VectorIndexError("Embedding service returned an incomplete batch.")
    for field in ("prompt_tokens", "total_duration_ns"):
        if type(getattr(batch, field, None)) is not int or getattr(batch, field) < 0:
            raise VectorIndexError("Embedding service returned invalid usage metadata.")
    return tuple(_validate_vector(vector, identity.dimensions) for vector in vectors)


def _metadata(chunks, identity) -> dict[str, str]:
    corpus = corpus_fingerprint(chunks)
    configuration = {
        "corpus_fingerprint": corpus, "model": identity.model, "model_digest": identity.digest,
        "dimensions": identity.dimensions, "preprocessing_revision": PREPROCESSING_REVISION,
    }
    return {
        "schema_version": VECTOR_SCHEMA_VERSION,
        "corpus_fingerprint": corpus,
        "index_fingerprint": sha256(_canonical_json(configuration).encode("utf-8")).hexdigest(),
        "model": identity.model,
        "model_digest": identity.digest,
        "dimensions": str(identity.dimensions),
        "preprocessing_revision": PREPROCESSING_REVISION,
        "chunks": str(len(chunks)),
    }


def _separate_paths(index_path, vector_path):
    if Path(index_path).resolve() == Path(vector_path).resolve():
        raise VectorIndexError("The vector sidecar must be separate from the source index.")


def _prepare_schema(connection):
    tables = {row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )}
    if not tables:
        connection.execute("CREATE TABLE vector_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        connection.execute(
            "CREATE TABLE vectors (chunk_id TEXT PRIMARY KEY, version TEXT NOT NULL, vector_json TEXT NOT NULL)"
        )
        connection.execute("CREATE INDEX vectors_version ON vectors(version)")
    elif "vector_metadata" not in tables or "vectors" not in tables:
        raise VectorIndexError("Unknown vector sidecar schema; use a separate empty sidecar.")
    else:
        schema = connection.execute(
            "SELECT value FROM vector_metadata WHERE key='schema_version'"
        ).fetchone()
        if schema is None or schema[0] != VECTOR_SCHEMA_VERSION:
            raise VectorIndexError("Unsupported vector sidecar schema.")


def build_vector_index(index_path: Path, vector_path: Path, client=None) -> dict:
    """Embed a full snapshot, then atomically replace a validated sidecar.

    No sidecar rows change until every embedding has passed validation. A final
    source read transaction prevents ingestion from committing between the
    fingerprint recheck and publication. Failure preserves any prior cache.
    """
    _separate_paths(index_path, vector_path)
    chunks = load_chunks(index_path)
    client = client if client is not None else LocalEmbeddingClient()
    identity = _validate_identity(client.identity())
    expected_metadata = _metadata(chunks, identity)
    vectors = []
    prompt_tokens = total_duration_ns = batches = 0
    for offset in range(0, len(chunks), BATCH_SIZE):
        selected = chunks[offset:offset + BATCH_SIZE]
        batch = client.embed_documents([chunk.text for chunk in selected])
        vectors.extend(_validated_batch(batch, identity, len(selected)))
        prompt_tokens += batch.prompt_tokens
        total_duration_ns += batch.total_duration_ns
        batches += 1
    if _validate_identity(client.identity()) != identity:
        raise VectorIndexError("Embedding model changed before vector publication.")
    with _source_snapshot(index_path) as current_chunks:
        if corpus_fingerprint(current_chunks) != expected_metadata["corpus_fingerprint"]:
            raise VectorIndexError("Source index changed during embedding. Build the vector index again.")
        try:
            with connect(vector_path) as connection:
                connection.isolation_level = None
                connection.execute("BEGIN IMMEDIATE")
                try:
                    _prepare_schema(connection)
                    connection.execute("DELETE FROM vectors")
                    connection.execute("DELETE FROM vector_metadata")
                    connection.executemany(
                        "INSERT INTO vector_metadata(key,value) VALUES (?,?)", sorted(expected_metadata.items())
                    )
                    connection.executemany(
                        "INSERT INTO vectors(chunk_id,version,vector_json) VALUES (?,?,?)",
                        [(chunk.chunk_id, chunk.source.version, _canonical_json(vector))
                         for chunk, vector in zip(chunks, vectors)],
                    )
                    connection.execute("COMMIT")
                except BaseException:
                    connection.execute("ROLLBACK")
                    raise
        except sqlite3.Error:
            raise VectorIndexError("Vector publication failed; any previous index was preserved.") from None
    return {
        **expected_metadata, "chunks": len(chunks), "dimensions": identity.dimensions,
        "versions": sorted({chunk.source.version for chunk in chunks}), "batches": batches,
        "prompt_tokens": prompt_tokens, "total_duration_ns": total_duration_ns,
    }


def _read_vectors(vector_path, chunks, identity):
    if not vector_path.is_file():
        raise VectorIndexError("Vector index not found. Run the embed command first.")
    try:
        with connect(vector_path, readonly=True) as connection:
            connection.execute("BEGIN")
            metadata = dict(connection.execute("SELECT key,value FROM vector_metadata"))
            rows = connection.execute("SELECT chunk_id,version,vector_json FROM vectors").fetchall()
    except sqlite3.Error:
        raise VectorIndexError("Vector sidecar could not be read. Rebuild the vector index.") from None
    if metadata != _metadata(chunks, identity):
        raise VectorIndexError("Vector index is stale or incompatible. Run the embed command again.")
    expected = {chunk.chunk_id: chunk.source.version for chunk in chunks}
    if len(rows) != len(expected) or {row["chunk_id"] for row in rows} != set(expected):
        raise VectorIndexError("Vector index is incomplete. Run the embed command again.")
    vectors = {}
    for row in rows:
        if row["version"] != expected[row["chunk_id"]]:
            raise VectorIndexError("Vector index contains inconsistent version metadata.")
        try:
            vector = json.loads(row["vector_json"])
        except (TypeError, ValueError, RecursionError):
            raise VectorIndexError("Vector index contains invalid vector data.") from None
        vectors[row["chunk_id"]] = _validate_vector(vector, identity.dimensions)
    return vectors


def vector_search(index_path: Path, vector_path: Path, request: SearchRequest, client=None) -> tuple[SearchHit, ...]:
    """Score only the requested exact version after validating the full cache."""
    _separate_paths(index_path, vector_path)
    chunks = load_chunks(index_path)
    client = client if client is not None else LocalEmbeddingClient()
    identity = _validate_identity(client.identity())
    vectors = _read_vectors(vector_path, chunks, identity)
    batch = client.embed_query(request.question)
    query_vector = _validated_batch(batch, identity, 1)[0]
    if _validate_identity(client.identity()) != identity:
        raise VectorIndexError("Embedding model changed while searching the vector index.")
    with _source_snapshot(index_path) as current_chunks:
        if corpus_fingerprint(current_chunks) != corpus_fingerprint(chunks):
            raise VectorIndexError("Source index changed during retrieval. Rebuild the vector index.")
        candidates = (chunk for chunk in chunks if chunk.source.version == request.version)
        hits = [
            SearchHit(chunk, max(-1.0, min(1.0, math.fsum(
                left * right for left, right in zip(query_vector, vectors[chunk.chunk_id])
            ))))
            for chunk in candidates
        ]
    return tuple(sorted(hits, key=lambda hit: (-hit.score, hit.chunk.chunk_id))[:request.limit])
