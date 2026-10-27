#!/usr/bin/env python3
"""Prepare and run the local source deployment without installing dependencies."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys

# Readiness must not create bytecode caches in a fresh source checkout.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def prerequisites() -> dict:
    """Probe only the interpreter and an in-memory SQLite database."""
    if sys.version_info < (3, 11):
        raise RuntimeError("Python 3.11 or newer is required for this source deployment.")
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE VIRTUAL TABLE deployment_probe USING fts5(text)")
    except sqlite3.Error as error:
        raise RuntimeError("This Python SQLite build needs FTS5 support.") from error
    finally:
        connection.close()
    return {"python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version, "fts5": True}


def prepare_index(root: Path, *, include_synthetic: bool = False, rebuild: bool = False,
                  read_only: bool = False) -> dict:
    """Compare all desired chunks/provenance before retaining or changing an index."""
    from versionlens.ingest import load_corpus, load_demo_corpus
    from versionlens.models import ValidationError
    from versionlens.store import index_stats, replace_corpus
    from versionlens.vector_store import corpus_fingerprint, load_chunks

    root = Path(root).resolve()
    for relative in ("data/versionlens.sqlite3", "data/versionlens-vectors.sqlite3"):
        cursor = root
        for component in Path(relative).parts:
            cursor = cursor / component
            if cursor.is_symlink():
                raise ValidationError("Fixed deployment paths must not contain symlinks.")
    corpus = load_demo_corpus(root) if include_synthetic else load_corpus(root)
    index = root / "data/versionlens.sqlite3"
    desired = corpus_fingerprint(corpus.chunks)
    report = {"corpus": "upstream_and_synthetic" if include_synthetic else "upstream",
              "corpus_fingerprint": desired, "model_server_checked": False, "local_only": True}
    if index.is_symlink():
        raise ValidationError("The deployment index must not be a symlink.")
    if index.exists() and not index.is_file():
        raise ValidationError("The deployment index path is not a regular file.")
    if not index.exists():
        if read_only:
            return {**report, "status": "not_ready", "reason": "index_missing", "operation": "checked", "index": None}
        stats = replace_corpus(index, corpus)
        operation = "created"
    else:
        if read_only:
            # mode=ro alone can create/manage WAL sidecars. Inspect bytes before
            # letting SQLite open an owner-modified WAL-mode deployment index.
            with index.open("rb") as stream:
                header = stream.read(20)
            if len(header) == 20 and (header[18] == 2 or header[19] == 2):
                raise ValidationError("Readiness checks reject WAL-mode indexes before SQLite opens them. Use the project-default DELETE journal mode after separately inspecting the index.")
        try:
            existing = load_chunks(index)
            stats = index_stats(index)
            matches = (corpus_fingerprint(existing) == desired
                       and stats["sources"] == len(corpus.sources)
                       and stats["chunks"] == len(corpus.chunks)
                       and stats["versions"] == sorted({source.version for source in corpus.sources}))
        except (ValidationError, sqlite3.Error):
            # A rebuild is explicitly requested and the store still rejects
            # unknown schemas/corrupt files without deleting them.
            if read_only or not rebuild:
                raise ValidationError("The existing index is invalid or incompatible. Inspect it; an explicit --rebuild is required for supported repair.") from None
            matches = False
        if not matches and not rebuild:
            if read_only:
                return {**report, "status": "not_ready", "reason": "index_mismatch", "operation": "checked", "index": stats}
            raise ValidationError("The existing index differs from the selected source corpus. Use --include-synthetic for that corpus or explicitly --rebuild to replace it.")
        if rebuild and not read_only:
            stats = replace_corpus(index, corpus)
            operation = "rebuilt"
        else:
            operation = "checked" if read_only else "unchanged"
    return {**report, "status": "ready", "operation": operation, "index": stats}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prepare", action="store_true", help="Verify source checksums and prepare the index, then exit")
    mode.add_argument("--check", action="store_true", help="Report readiness without writing files or checking models")
    parser.add_argument("--include-synthetic", action="store_true", help="Explicitly include the two labelled fictional access-demo documents")
    parser.add_argument("--rebuild", action="store_true", help="Explicitly replace an existing supported source index")
    parser.add_argument("--demo-profile", choices=("public", "support"), default="public")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    if not 1024 <= args.port <= 65535:
        parser.error("Choose an unprivileged local port from 1024 to 65535.")
    if args.check and args.rebuild:
        parser.error("--check cannot be combined with --rebuild.")
    try:
        runtime = prerequisites()
        result = prepare_index(ROOT, include_synthetic=args.include_synthetic,
                               rebuild=args.rebuild, read_only=args.check)
        result["prerequisites"] = runtime
        result["access_profile"] = args.demo_profile
        if args.check or args.prepare:
            print(json.dumps(result, indent=2))
            return 0 if result["status"] == "ready" else 2
        from versionlens.server import serve
        return serve(ROOT / "data/versionlens.sqlite3", ROOT / "data/versionlens-vectors.sqlite3",
                     args.port, args.demo_profile)
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as error:
        result = {"status": "not_ready" if args.check else "error", "error": str(error),
                  "model_server_checked": False, "local_only": True}
        print(json.dumps(result), file=sys.stdout if args.check else sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
