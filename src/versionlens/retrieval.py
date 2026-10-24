"""A transparent lexical baseline. Scores indicate ranking, never confidence."""

from dataclasses import dataclass
import json
from pathlib import Path
import re

from .models import Chunk, SearchRequest, Source, ValidationError
from .store import _check_schema, connect


# Small, fixed lexical preprocessing, not tuned against evaluation questions.
STOPWORDS = frozenset(
    "a an and are as at be been by can could did do does for from had has have "
    "how i if in into is it its me my of on or should so than that the their "
    "them there these they this to use using was we were what when where which "
    "why will with would you your".split()
)


@dataclass(frozen=True)
class SearchHit:
    chunk: Chunk
    score: float

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk.chunk_id,
            "version": self.chunk.source.version,
            "section": self.chunk.section,
            "text": self.chunk.text,
            "source_id": self.chunk.source.source_id,
            "source_sha256": self.chunk.source.sha256,
            "source_kind": self.chunk.source.source_kind,
            "access": self.chunk.source.access,
            "upstream_commit": self.chunk.source.commit,
            "start_line": self.chunk.start_line,
            "end_line": self.chunk.end_line,
            "citation_url": self.chunk.citation_url,
            "score": self.score,
        }


def query_terms(question: str) -> tuple[str, ...]:
    # Extract words rather than passing user input as FTS syntax. This also
    # makes literal error messages, punctuation, and adversarial FTS input safe.
    terms = re.findall(r"[^\W_]+", question.casefold(), flags=re.UNICODE)
    return tuple(dict.fromkeys(term for term in terms if term not in STOPWORDS))[:40]


def search(index_path: Path, request: SearchRequest) -> tuple[SearchHit, ...]:
    terms = query_terms(request.question)
    if not terms:
        return ()
    expression = " OR ".join('"' + term + '"' for term in terms)
    with connect(index_path, readonly=True) as connection:
        _check_schema(connection)
        rows = connection.execute(
            "SELECT c.*, s.metadata_json, s.access AS source_access, s.source_kind AS stored_source_kind, bm25(chunk_fts, 2.0, 1.0) AS rank "
            "FROM chunk_fts JOIN chunks c ON c.rowid=chunk_fts.rowid "
            "JOIN sources s ON s.source_id=c.source_id "
            "WHERE chunk_fts MATCH ? AND c.version=? AND (?='support' OR s.access='public') "
            "ORDER BY rank, c.chunk_id LIMIT ?",
            (expression, request.version, request.access_profile, request.limit),
        ).fetchall()
    hits = []
    for row in rows:
        source = Source(**json.loads(row["metadata_json"]))
        if (source.source_id != row["source_id"] or source.version != row["version"]
                or source.access != row["source_access"] or source.source_kind != row["stored_source_kind"]
                or not request.allows(source)):
            raise ValidationError("Source index contains inconsistent access or version metadata.")
        chunk = Chunk.create(source, row["section"], row["start_line"], row["end_line"], row["text"])
        if chunk.chunk_id != row["chunk_id"]:
            raise ValidationError("Source index contains an invalid chunk identity.")
        hits.append(SearchHit(chunk, -row["rank"]))
    return tuple(hits)
