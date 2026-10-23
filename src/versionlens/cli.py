"""Offline ingestion, index inspection, and version-filtered evidence search."""

import argparse
import json
from pathlib import Path
import sqlite3
import sys

from .ingest import load_corpus
from .local_model import LocalModelError
from .models import SearchRequest, SUPPORTED_VERSIONS, ValidationError
from .search_service import RETRIEVERS, retrieve
from .store import index_stats, replace_corpus


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="VersionLens local HTTPX evidence retrieval")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root containing data/sources.json")
    parser.add_argument("--index", type=Path, default=Path("data/versionlens.sqlite3"))
    parser.add_argument("--vector-index", type=Path, default=Path("data/versionlens-vectors.sqlite3"))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("ingest", help="Verify all source checksums and replace the local index atomically")
    commands.add_parser("stats", help="Inspect index counts and supported snapshots")
    commands.add_parser("doctor", help="Check the approved local model; never contact cloud inference")
    commands.add_parser("embed", help="Build a local vector index for the current corpus and model digest")
    web = commands.add_parser("serve", help="Start the local API and browser UI on 127.0.0.1")
    web.add_argument("--port", type=int, default=8765)
    query = commands.add_parser("search", help="Return ranked evidence; this does not generate an answer")
    query.add_argument("question")
    query.add_argument("--version", choices=SUPPORTED_VERSIONS, required=True)
    query.add_argument("--limit", type=int, default=5)
    query.add_argument("--retriever", choices=RETRIEVERS, default="keyword")
    ask = commands.add_parser("ask", help="Generate a cited local draft; abstain on unusable evidence")
    ask.add_argument("question")
    ask.add_argument("--version", choices=SUPPORTED_VERSIONS, required=True)
    ask.add_argument("--limit", type=int, default=5)
    ask.add_argument("--retriever", choices=RETRIEVERS, default="keyword")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    index = args.index if args.index.is_absolute() else root / args.index
    vectors = args.vector_index if args.vector_index.is_absolute() else root / args.vector_index
    try:
        if args.command == "serve":
            from .server import serve
            return serve(index, vectors, args.port)
        elif args.command == "ingest":
            result = replace_corpus(index, load_corpus(root))
        elif args.command == "stats":
            result = index_stats(index)
        elif args.command == "embed":
            from .vector_store import build_vector_index
            result = build_vector_index(index, vectors)
        elif args.command == "doctor":
            from .config import LocalModelConfig
            from .local_model import LocalModelClient
            config = LocalModelConfig()
            result = {"status": "ready", "mode": "local_only", "base_url": config.base_url,
                      "model": LocalModelClient(config).health()}
        elif args.command == "ask":
            from .answering import answer
            result = answer(index, SearchRequest(args.question, args.version, args.limit),
                            retrieval_method=args.retriever, vector_path=vectors)
        else:
            request = SearchRequest(args.question, args.version, args.limit)
            hits = retrieve(index, request, method=args.retriever, vector_path=vectors)
            result = {
                "status": "evidence_found" if hits else "no_matching_evidence",
                "mode": f"{args.retriever}_retrieval_only",
                "retrieval_method": args.retriever,
                "version": request.version,
                "question": request.question,
                "answer": None,
                "notice": "Ranked source excerpts, not a generated or verified answer. Scores are not confidence.",
                "hits": [hit.to_dict() for hit in hits],
            }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get("status") == "error" else 0
    except (ValidationError, OSError, sqlite3.Error, LocalModelError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
