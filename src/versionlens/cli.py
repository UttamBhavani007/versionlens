"""Offline ingestion, index inspection, and version-filtered evidence search."""

import argparse
import json
from pathlib import Path
import sqlite3
import sys

from .ingest import load_corpus
from .models import SearchRequest, SUPPORTED_VERSIONS, ValidationError
from .retrieval import search
from .store import index_stats, replace_corpus


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="VersionLens local HTTPX evidence retrieval")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root containing data/sources.json")
    parser.add_argument("--index", type=Path, default=Path("data/versionlens.sqlite3"))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("ingest", help="Verify all source checksums and replace the local index atomically")
    commands.add_parser("stats", help="Inspect index counts and supported snapshots")
    query = commands.add_parser("search", help="Return ranked evidence; this does not generate an answer")
    query.add_argument("question")
    query.add_argument("--version", choices=SUPPORTED_VERSIONS, required=True)
    query.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    index = args.index if args.index.is_absolute() else root / args.index
    try:
        if args.command == "ingest":
            result = replace_corpus(index, load_corpus(root))
        elif args.command == "stats":
            result = index_stats(index)
        else:
            request = SearchRequest(args.question, args.version, args.limit)
            hits = search(index, request)
            result = {
                "status": "evidence_found" if hits else "no_matching_evidence",
                "mode": "keyword_retrieval_only",
                "version": request.version,
                "question": request.question,
                "answer": None,
                "notice": "Ranked source excerpts, not a generated or verified answer. Scores are not confidence.",
                "hits": [hit.to_dict() for hit in hits],
            }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValidationError, OSError, sqlite3.Error) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
