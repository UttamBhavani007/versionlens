#!/usr/bin/env python3
"""Verify or re-download the pinned public HTTPX corpus using only the stdlib.

The checked-in manifest is the trust anchor. This tool never discovers new
sources, updates checksums, follows redirects, or accepts arbitrary destinations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "data/sources.json"
MAX_BYTES = 512 * 1024
COMMITS = {
    "0.27.2": "609df7ecc0f7cb10a1c998aa9c269bba77337c5f",
    "0.28.1": "26d48e0634e6ee9cdc0533996db289ce4b430177",
}
FIELDS = {
    "source_id", "product", "version", "path", "upstream_path", "commit",
    "sha256", "url", "title",
}


class SourceError(ValueError):
    """A manifest, path, or downloaded source did not meet the contract."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SourceError("Source redirects are not allowed")


def relative_path(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise SourceError("Source paths must be nonempty POSIX relative paths")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise SourceError("Absolute paths and traversal are not allowed")
    if path.suffix != ".md" or re.fullmatch(r"[A-Za-z0-9_./-]+", value) is None:
        raise SourceError("Only plain Markdown source paths are allowed")
    return path


def checked_destination(relative: str, root: Path = ROOT) -> Path:
    """Reject traversal and symlinks, including existing parent components."""
    path = relative_path(relative)
    current = root
    if current.is_symlink():
        raise SourceError("Repository root must not be a symlink")
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise SourceError(f"Symlink is not allowed: {relative}")
    if current.exists() and not current.is_file():
        raise SourceError(f"Destination is not a regular file: {relative}")
    return current


def load_manifest(root: Path = ROOT) -> list[dict[str, str]]:
    manifest_path = root / MANIFEST
    for path in (root / "data", manifest_path):
        if path.is_symlink():
            raise SourceError("Manifest and its directory must not be symlinks")
    if manifest_path.stat().st_size > MAX_BYTES:
        raise SourceError("Manifest exceeds size limit")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "sources"}:
        raise SourceError("Manifest must contain exactly schema_version and sources")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise SourceError("Unsupported manifest schema")
    sources = manifest["sources"]
    if not isinstance(sources, list) or not sources or len(sources) > 64:
        raise SourceError("Manifest must list between 1 and 64 sources")
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for source in sources:
        if not isinstance(source, dict) or set(source) != FIELDS:
            raise SourceError("Unexpected source fields")
        if any(not isinstance(value, str) for value in source.values()):
            raise SourceError("Source fields must be strings")
        version = source["version"]
        if source["product"] != "httpx" or version not in COMMITS:
            raise SourceError("Only the approved HTTPX snapshots are allowed")
        commit = COMMITS[version]
        upstream = str(relative_path(source["upstream_path"]))
        expected_path = f"data/corpus/httpx/{version}/{upstream}"
        expected_id = f"httpx:{version}:{upstream}"
        expected_url = f"https://github.com/encode/httpx/blob/{commit}/{upstream}"
        if (source["commit"], source["path"], source["source_id"], source["url"]) != (
            commit, expected_path, expected_id, expected_url,
        ):
            raise SourceError("Source identity, path, or immutable URL is invalid")
        if re.fullmatch(r"[0-9a-f]{64}", source["sha256"]) is None:
            raise SourceError("Source checksum must be a lowercase SHA-256 digest")
        if not source["title"].strip() or len(source["title"]) > 200:
            raise SourceError("Source title must contain 1 to 200 characters")
        if expected_id in seen_ids or expected_path in seen_paths:
            raise SourceError("Duplicate source ID or path")
        seen_ids.add(expected_id)
        seen_paths.add(expected_path)
        checked_destination(expected_path, root)
    return sources


def download(commit: str, upstream_path: str) -> bytes:
    """Fetch an allowlisted raw GitHub URL with TLS verification and a size cap."""
    if commit not in COMMITS.values():
        raise SourceError("Unapproved upstream commit")
    upstream = str(relative_path(upstream_path))
    url = f"https://raw.githubusercontent.com/encode/httpx/{commit}/{upstream}"
    opener = urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(url, headers={"User-Agent": "VersionLens-source-fetcher/1"})
    with opener.open(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != url:
            raise SourceError("Unexpected source response")
        content_length = response.headers.get("Content-Length")
        if content_length is not None and int(content_length) > MAX_BYTES:
            raise SourceError("Source exceeds size limit")
        content = response.read(MAX_BYTES + 1)
    if not content or len(content) > MAX_BYTES:
        raise SourceError("Source is empty or exceeds size limit")
    content.decode("utf-8")
    return content


def verify_local(sources: list[dict[str, str]], root: Path = ROOT) -> None:
    for source in sources:
        path = checked_destination(source["path"], root)
        if not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise SourceError(f"Missing or oversized source: {source['path']}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise SourceError(f"Checksum mismatch: {source['path']}")


def refresh(sources: list[dict[str, str]], root: Path = ROOT) -> None:
    # Stage and verify EVERY download before changing any corpus file. A failure
    # in networking or integrity verification leaves the existing corpus intact.
    with tempfile.TemporaryDirectory(prefix="versionlens-sources-", dir=root) as staging:
        pending: list[tuple[Path, str]] = []
        for index, source in enumerate(sources):
            content = download(source["commit"], source["upstream_path"])
            if hashlib.sha256(content).hexdigest() != source["sha256"]:
                raise SourceError(f"Upstream checksum mismatch: {source['source_id']}")
            staged = Path(staging) / f"{index}.md"
            with staged.open("xb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            pending.append((staged, source["path"]))
        # Each replacement is atomic on the same filesystem. This is not a
        # multi-file transaction if the process or filesystem fails mid-publish.
        for staged, relative in pending:
            destination = checked_destination(relative, root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination = checked_destination(relative, root)
            os.replace(staged, destination)
    verify_local(sources, root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify local files without network access")
    args = parser.parse_args()
    try:
        sources = load_manifest()
        if args.check:
            verify_local(sources)
        else:
            refresh(sources)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"Source verification failed: {exc}", file=sys.stderr)
        return 1
    print(f"Verified {len(sources)} pinned HTTPX sources across {len(COMMITS)} versions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
