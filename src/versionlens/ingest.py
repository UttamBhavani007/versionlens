"""Checksum-verified local Markdown ingestion. No network requests are made here."""

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re

from .models import Chunk, Source, ValidationError


MAX_SOURCE_BYTES = 2_000_000
MAX_MANIFEST_BYTES = 1_000_000


@dataclass(frozen=True)
class Corpus:
    sources: tuple[Source, ...]
    chunks: tuple[Chunk, ...]


def _safe_read(root: Path, relative: str, limit: int) -> bytes:
    """Refuse paths outside the repo and symlinks at any path component."""
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValidationError(f"Source path escapes repository: {relative}")
    cursor = root
    for part in Path(relative).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValidationError(f"Source symlinks are not allowed: {relative}")
    if not path.is_file():
        raise ValidationError(f"Source file does not exist: {relative}")
    with path.open("rb") as handle:
        data = handle.read(limit + 1)
    if len(data) > limit:
        raise ValidationError(f"Source exceeds size limit: {relative}")
    return data


def chunk_markdown(source: Source, content: str, max_chars: int = 1800) -> tuple[Chunk, ...]:
    """Split at headings and size bounds, preserving exact original line spans.

    The hard bound applies at a line boundary; a single long source line is kept
    intact so citations still map exactly to upstream text. Headings in fenced
    code blocks do not start a new section. No overlapping text is fabricated.
    """
    if max_chars < 200:
        raise ValidationError("Chunk size must be at least 200 characters.")
    lines = content.splitlines()
    chunks: list[Chunk] = []
    headings: list[tuple[int, str]] = []
    section = source.title
    start = 0
    char_count = 0
    fence_char = ""
    fence_length = 0

    def emit(end: int) -> None:
        if end > start:
            text = "\n".join(lines[start:end])
            if text.strip():
                chunks.append(Chunk.create(source, section, start + 1, end, text))

    for index, line in enumerate(lines):
        heading = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line) if not fence_char else None
        if heading:
            emit(index)
            start = index
            char_count = 0
            level = len(heading[1])
            while headings and headings[-1][0] >= level:
                headings.pop()
            headings.append((level, heading[2]))
            section = " > ".join(title for _, title in headings)
        elif char_count + len(line) + 1 > max_chars and index > start:
            emit(index)
            start = index
            char_count = 0
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            marker, rest = fence.groups()
            if not fence_char:
                fence_char, fence_length = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_length and not rest.strip():
                fence_char, fence_length = "", 0
        char_count += len(line) + 1
    emit(len(lines))
    return tuple(chunks)


def load_corpus(root: Path, manifest_path: str = "data/sources.json", *, allow_synthetic: bool = False) -> Corpus:
    """Validate the complete batch before returning any indexable documents."""
    from .models import validate_relative_path

    validate_relative_path(manifest_path)
    try:
        manifest = json.loads(_safe_read(root, manifest_path, MAX_MANIFEST_BYTES))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValidationError("Source manifest is not valid UTF-8 JSON.") from exc
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "sources"}:
        raise ValidationError("Manifest must contain schema_version and sources only.")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise ValidationError("Unsupported manifest schema version.")
    entries = manifest["sources"]
    if not isinstance(entries, list) or not entries or len(entries) > 1000:
        raise ValidationError("Manifest must contain between 1 and 1000 sources.")
    sources: list[Source] = []
    chunks: list[Chunk] = []
    seen: set[str] = set()
    for entry in entries:
        try:
            source = Source(**entry)
        except (TypeError, AttributeError) as exc:
            raise ValidationError("Source entry does not match the metadata schema.") from exc
        if (source.source_kind == "synthetic") != allow_synthetic:
            raise ValidationError("Synthetic documents require their separate, explicit demo manifest.")
        if source.source_id in seen:
            raise ValidationError(f"Duplicate source ID: {source.source_id}")
        seen.add(source.source_id)
        raw = _safe_read(root, source.path, MAX_SOURCE_BYTES)
        if sha256(raw).hexdigest() != source.sha256:
            raise ValidationError(f"Checksum mismatch: {source.path}")
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(f"Source is not UTF-8: {source.path}") from exc
        if source.source_kind == "synthetic" and content.splitlines()[:1] != ["# " + source.title]:
            raise ValidationError("Synthetic content must start with its prominent SYNTHETIC DEMO title.")
        source_chunks = chunk_markdown(source, content)
        if not source_chunks:
            raise ValidationError(f"Source is empty: {source.path}")
        sources.append(source)
        chunks.extend(source_chunks)
    return Corpus(tuple(sources), tuple(chunks))


def load_demo_corpus(root: Path) -> Corpus:
    """Opt-in fictional material; public upstream sources stay unmodified."""
    public = load_corpus(root)
    synthetic = load_corpus(root, "data/synthetic/sources.json", allow_synthetic=True)
    return Corpus(public.sources + synthetic.sources, public.chunks + synthetic.chunks)
