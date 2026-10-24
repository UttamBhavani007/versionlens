"""Explicit, transactional updates of one complete validated snapshot.

The byte-checksum gate remains ingest.load_corpus: Corpus contains normalized
chunks rather than the original source bytes. This module independently checks
metadata, membership, ranges and deterministic chunk identities before writing.
"""

from dataclasses import asdict
import json
from pathlib import Path

from .ingest import Corpus
from .models import Chunk, Source, ValidationError, validate_version
from .store import SCHEMA_VERSION, _check_schema, _chunk_values, _source_values, connect


_SOURCE_COLUMNS = "source_id,version,metadata_json,access,source_kind"
_CHUNK_COLUMNS = "chunk_id,source_id,version,section,start_line,end_line,text"


def _validate_snapshot(corpus: Corpus, version: str) -> Corpus:
    if type(version) is not str:
        raise ValidationError("Select an exact supported snapshot version.")
    validate_version(version)
    if (not isinstance(corpus, Corpus) or type(corpus.sources) is not tuple
            or type(corpus.chunks) is not tuple or not corpus.sources or not corpus.chunks):
        raise ValidationError("Sync requires one complete nonempty snapshot. Use delete-snapshot to remove it.")
    sources = {}
    paths = set()
    for source in corpus.sources:
        if type(source) is not Source:
            raise ValidationError("Snapshot sources must be validated Source records.")
        try:
            checked = Source(**asdict(source))
            for value in vars(checked).values():
                value.encode("utf-8", errors="strict")
        except (TypeError, ValueError, AttributeError, UnicodeError, RecursionError):
            raise ValidationError("Snapshot source metadata is invalid.") from None
        if checked.version != version:
            raise ValidationError("Every sync source must belong to the selected snapshot.")
        if checked.source_id in sources or checked.path in paths:
            raise ValidationError("Snapshot contains duplicate source IDs or paths.")
        sources[checked.source_id] = checked
        paths.add(checked.path)
    ids = set()
    source_chunks = {source_id: [] for source_id in sources}
    for chunk in corpus.chunks:
        if type(chunk) is not Chunk or type(chunk.source) is not Source:
            raise ValidationError("Snapshot chunks must be validated Chunk records.")
        expected = sources.get(chunk.source.source_id)
        if expected is None or chunk.source != expected:
            raise ValidationError("Chunk source metadata does not match this snapshot.")
        if (type(chunk.start_line) is not int or type(chunk.end_line) is not int
                or not isinstance(chunk.section, str) or not chunk.section.strip()
                or not isinstance(chunk.text, str)):
            raise ValidationError("Chunk text, section or line metadata is invalid.")
        try:
            chunk.section.encode("utf-8", errors="strict")
            chunk.text.encode("utf-8", errors="strict")
            checked = Chunk.create(expected, chunk.section, chunk.start_line, chunk.end_line, chunk.text)
        except (TypeError, ValueError, UnicodeError):
            raise ValidationError("Chunk text, section or line metadata is invalid.") from None
        if len(chunk.text.split("\n")) != chunk.end_line - chunk.start_line + 1:
            raise ValidationError("Chunk line range does not match its normalized text.")
        if type(chunk.chunk_id) is not str or checked.chunk_id != chunk.chunk_id:
            raise ValidationError("Chunk identity does not match its source and line range.")
        if chunk.chunk_id in ids:
            raise ValidationError("Snapshot contains duplicate chunk IDs.")
        ids.add(chunk.chunk_id)
        source_chunks[expected.source_id].append(checked)
    for chunks in source_chunks.values():
        if not chunks:
            raise ValidationError("Every snapshot source must have at least one chunk.")
        previous_end = 0
        for chunk in sorted(chunks, key=lambda item: item.start_line):
            if chunk.start_line <= previous_end:
                raise ValidationError("Snapshot chunks have overlapping line ranges.")
            previous_end = chunk.end_line
    return Corpus(tuple(sources.values()), tuple(corpus.chunks))


def _existing_snapshot(connection, version: str) -> Corpus | None:
    rows = connection.execute(
        f"SELECT {_SOURCE_COLUMNS} FROM sources WHERE version=? ORDER BY source_id", (version,)
    ).fetchall()
    sources = {}
    try:
        for row in rows:
            source = Source(**json.loads(row["metadata_json"]))
            if (row["source_id"] != source.source_id or row["version"] != source.version
                    or row["access"] != source.access or row["source_kind"] != source.source_kind):
                raise ValidationError("Indexed source columns and metadata disagree.")
            sources[source.source_id] = source
        chunks = []
        for row in connection.execute(
            f"SELECT {_CHUNK_COLUMNS} FROM chunks WHERE version=? OR source_id IN "
            "(SELECT source_id FROM sources WHERE version=?) ORDER BY chunk_id", (version, version)
        ):
            source = sources.get(row["source_id"])
            if source is None or row["version"] != source.version:
                raise ValidationError("Indexed chunk source/version metadata is inconsistent.")
            chunks.append(Chunk(row["chunk_id"], source, row["section"], row["start_line"], row["end_line"], row["text"]))
        if not sources and not chunks:
            return None
        return _validate_snapshot(Corpus(tuple(sources.values()), tuple(chunks)), version)
    except (TypeError, KeyError, ValueError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, ValidationError):
            raise
        raise ValidationError("Indexed snapshot metadata is invalid; rebuild the index.") from None


def _stats(connection) -> dict:
    # Read inside the write transaction so counters and index stats describe the
    # same committed snapshot, even if another updater runs immediately after.
    return {
        "schema_version": SCHEMA_VERSION,
        "sources": connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
        "chunks": connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0],
        "versions": [row[0] for row in connection.execute("SELECT DISTINCT version FROM sources ORDER BY version")],
    }


def _group(corpus: Corpus | None):
    if corpus is None:
        return {}, {}
    sources = {source.source_id: source for source in corpus.sources}
    chunks = {source_id: [] for source_id in sources}
    for chunk in corpus.chunks:
        chunks[chunk.source.source_id].append(_chunk_values(chunk))
    return sources, {key: tuple(sorted(values)) for key, values in chunks.items()}


def _require_existing(path: Path) -> None:
    if not Path(path).is_file():
        raise ValidationError("Index not found. Run the ingest command before updating snapshots.")


def sync_snapshot(path: Path, corpus: Corpus, version: str) -> dict:
    """Replace the desired state of exactly one snapshot, retaining unchanged rows.

    Omitted source IDs are deleted only within this selected version. Empty
    desired input is rejected so an accidental empty manifest cannot delete it.
    Invalid inputs are rejected before opening the database for writing.
    """
    desired = _validate_snapshot(corpus, version)
    _require_existing(path)
    new_sources, new_chunks = _group(desired)
    with connect(path) as connection:
        connection.isolation_level = None
        connection.execute("BEGIN IMMEDIATE")
        try:
            _check_schema(connection)
            previous = _existing_snapshot(connection, version)
            old_sources, old_chunks = _group(previous)
            added = new_sources.keys() - old_sources.keys()
            deleted = old_sources.keys() - new_sources.keys()
            shared = new_sources.keys() & old_sources.keys()
            unchanged = {key for key in shared if old_sources[key] == new_sources[key] and old_chunks[key] == new_chunks[key]}
            updated = shared - unchanged
            for source_id in sorted(deleted | updated):
                connection.execute("DELETE FROM chunks WHERE source_id=?", (source_id,))
                connection.execute("DELETE FROM sources WHERE source_id=?", (source_id,))
            for source_id in sorted(added | updated):
                connection.execute(
                    f"INSERT INTO sources({_SOURCE_COLUMNS}) VALUES(?,?,?,?,?)", _source_values(new_sources[source_id])
                )
                connection.executemany(
                    f"INSERT INTO chunks({_CHUNK_COLUMNS}) VALUES(?,?,?,?,?,?,?)", new_chunks[source_id]
                )
            result = {"operation": "sync_snapshot", "version": version, "added": len(added),
                      "updated": len(updated), "deleted": len(deleted), "unchanged": len(unchanged),
                      "index": _stats(connection)}
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise
    return result


def delete_snapshot(path: Path, version: str) -> dict:
    """Explicitly remove an entire exact snapshot, preserving all other versions."""
    if type(version) is not str:
        raise ValidationError("Select an exact supported snapshot version.")
    validate_version(version)
    _require_existing(path)
    with connect(path) as connection:
        connection.isolation_level = None
        connection.execute("BEGIN IMMEDIATE")
        try:
            _check_schema(connection)
            previous = _existing_snapshot(connection, version)
            deleted = len(previous.sources) if previous else 0
            connection.execute("DELETE FROM chunks WHERE version=?", (version,))
            connection.execute("DELETE FROM sources WHERE version=?", (version,))
            result = {"operation": "delete_snapshot", "version": version, "added": 0,
                      "updated": 0, "deleted": deleted, "unchanged": 0, "index": _stats(connection)}
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise
    return result
