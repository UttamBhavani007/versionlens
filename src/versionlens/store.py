"""Transactional SQLite storage. Future retrieval engines share this provenance."""

from contextlib import contextmanager
from dataclasses import asdict
import json
from pathlib import Path
import sqlite3

from .ingest import Corpus
from .models import ValidationError


SCHEMA_VERSION = "1"
SCHEMA = """
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE sources (
    source_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE TABLE chunks (
    rowid INTEGER PRIMARY KEY,
    chunk_id TEXT NOT NULL UNIQUE,
    source_id TEXT NOT NULL REFERENCES sources(source_id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    section TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    text TEXT NOT NULL
);
CREATE INDEX chunks_version ON chunks(version);
CREATE VIRTUAL TABLE chunk_fts USING fts5(
    section, text, content='chunks', content_rowid='rowid',
    tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER chunks_ai AFTER INSERT ON chunks BEGIN
  INSERT INTO chunk_fts(rowid, section, text) VALUES(new.rowid, new.section, new.text);
END;
CREATE TRIGGER chunks_ad AFTER DELETE ON chunks BEGIN
  INSERT INTO chunk_fts(chunk_fts, rowid, section, text)
    VALUES('delete', old.rowid, old.section, old.text);
END;
"""


@contextmanager
def connect(path: Path, *, readonly: bool = False):
    if readonly:
        if not path.is_file():
            raise ValidationError("Index not found. Run the ingest command first.")
        connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        yield connection
    finally:
        connection.close()


def _check_schema(connection: sqlite3.Connection) -> None:
    row = connection.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
    if row is None or row[0] != SCHEMA_VERSION:
        raise ValidationError("Unsupported index schema. Rebuild the local index.")


def replace_corpus(path: Path, corpus: Corpus) -> dict:
    """Replace a completely validated corpus in one transaction.

    Explicit transaction control also makes initial DDL creation atomic. Index
    schema mismatches fail without deleting or upgrading unknown user data.
    """
    if not corpus.sources or not corpus.chunks:
        raise ValidationError("Refusing to replace the index with an empty corpus.")
    with connect(path) as connection:
        connection.isolation_level = None
        connection.execute("BEGIN IMMEDIATE")
        try:
            has_schema = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='metadata'"
            ).fetchone()
            if has_schema:
                _check_schema(connection)
            else:
                # executescript commits implicitly; execute complete statements
                # individually so DDL stays inside this transaction.
                statement = ""
                for line in SCHEMA.splitlines(keepends=True):
                    statement += line
                    if sqlite3.complete_statement(statement):
                        connection.execute(statement)
                        statement = ""
                connection.execute("INSERT INTO metadata VALUES ('schema_version', ?)", (SCHEMA_VERSION,))
            connection.execute("DELETE FROM chunks")
            connection.execute("DELETE FROM sources")
            connection.executemany(
                "INSERT INTO sources VALUES (?, ?, ?)",
                [(source.source_id, source.version, json.dumps(asdict(source), sort_keys=True))
                 for source in corpus.sources],
            )
            connection.executemany(
                "INSERT INTO chunks(chunk_id,source_id,version,section,start_line,end_line,text) "
                "VALUES(?,?,?,?,?,?,?)",
                [(chunk.chunk_id, chunk.source.source_id, chunk.source.version, chunk.section,
                  chunk.start_line, chunk.end_line, chunk.text) for chunk in corpus.chunks],
            )
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise
    return index_stats(path)


def index_stats(path: Path) -> dict:
    with connect(path, readonly=True) as connection:
        _check_schema(connection)
        return {
            "schema_version": SCHEMA_VERSION,
            "sources": connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
            "chunks": connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0],
            "versions": [row[0] for row in connection.execute("SELECT DISTINCT version FROM sources ORDER BY version")],
        }
