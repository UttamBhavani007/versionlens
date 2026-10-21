#!/usr/bin/env python3
"""Install a pinned free macOS runtime, serve locally, or pull the approved model.

No system installation, account, cloud inference, or background service is used.
The foreground server stops with Ctrl-C. Downloading binaries/model weights needs
internet access; generation runs locally once the model has been downloaded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import posixpath
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from versionlens.config import LocalModelConfig  # noqa: E402

RELEASE = "v0.40.7"
ARCHIVE_URL = f"https://github.com/ollama/ollama/releases/download/{RELEASE}/ollama-darwin.tgz"
ARCHIVE_SHA256 = "6c8b378e423a4c959b586c0bb62865d20ae057e817f1a8ee10abcc44bde6abab"
ARCHIVE_SIZE = 174723727
RUNTIME = ROOT / ".tools" / "ollama"
ARCHIVE = ROOT / ".tools" / f"ollama-{RELEASE}-darwin.tgz"
MODELS = ROOT / ".ollama" / "models"
ALLOWED_DOWNLOAD_HOSTS = {"github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"}


class RuntimeSetupError(ValueError):
    """Runtime setup is unsafe, incomplete, or unsupported."""


class ReleaseRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urlsplit(newurl)
        if (
            target.scheme != "https" or target.hostname not in ALLOWED_DOWNLOAD_HOSTS
            or target.username is not None or target.password is not None
            or target.port not in (None, 443)
        ):
            raise RuntimeSetupError("Release redirected outside the approved HTTPS hosts")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def safe_project_path(path: Path) -> Path:
    relative = path.relative_to(ROOT)
    current = ROOT
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise RuntimeSetupError("Project runtime paths must not contain symlinks")
    return path


def verify_archive(archive: Path) -> None:
    """Always validate the exact approved bytes before any extraction."""
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_size != ARCHIVE_SIZE:
        raise RuntimeSetupError("Runtime archive failed its exact size verification")
    digest = hashlib.sha256()
    with archive.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    if digest.hexdigest() != ARCHIVE_SHA256:
        raise RuntimeSetupError("Runtime archive failed SHA-256 verification")


def install() -> None:
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise RuntimeSetupError("This pinned runtime installer supports Apple Silicon macOS only")
    safe_project_path(RUNTIME)
    if RUNTIME.exists():
        require_runtime()
        print(f"Verified installed Ollama {RELEASE} at {RUNTIME}")
        return
    safe_project_path(ROOT / ".tools").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ollama-install-", dir=ROOT / ".tools") as temporary:
        stage = Path(temporary)
        archive = safe_project_path(ARCHIVE)
        if not archive.exists():
            pending_archive = stage / "ollama-darwin.tgz"
            opener = urllib.request.build_opener(ReleaseRedirect())
            request = urllib.request.Request(ARCHIVE_URL, headers={"User-Agent": "VersionLens-local-runtime/1"})
            digest = hashlib.sha256()
            size = 0
            with opener.open(request, timeout=60) as response, pending_archive.open("xb") as output:
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > ARCHIVE_SIZE:
                        raise RuntimeSetupError("Runtime download exceeds the reviewed size")
                    digest.update(chunk)
                    output.write(chunk)
            if size != ARCHIVE_SIZE or digest.hexdigest() != ARCHIVE_SHA256:
                raise RuntimeSetupError("Runtime archive failed size or SHA-256 verification")
            verify_archive(pending_archive)
            os.replace(pending_archive, archive)
        # Unconditional for both newly downloaded and cached archives. No archive
        # is opened by tarfile until the pinned size AND SHA-256 pass here.
        verify_archive(archive)
        unpacked = stage / "runtime"
        unpacked.mkdir()
        files = {}
        with tarfile.open(archive, "r:gz") as bundle:
            members = bundle.getmembers()
            if len(members) > 1024 or sum(member.size for member in members) > 1024**3:
                raise RuntimeSetupError("Runtime archive exceeds extraction limits")
            member_lookup = {str(PurePosixPath(member.name)): member for member in members}
            if len(member_lookup) != len(members):
                raise RuntimeSetupError("Runtime archive contains duplicate paths")
            for member in members:
                relative = PurePosixPath(member.name)
                if (
                    relative.is_absolute() or ".." in relative.parts or "\\" in member.name
                    or not (member.isfile() or member.isdir() or member.issym() or member.islnk())
                ):
                    raise RuntimeSetupError("Runtime archive contains an unsafe path or link")
                target = unpacked.joinpath(*relative.parts)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                # Official Darwin libraries include links. Resolve only archive
                # members inside this bundle, then materialize regular files so
                # runtime installation never creates filesystem symlinks.
                resolved = member
                seen = set()
                while resolved.issym() or resolved.islnk():
                    key = str(PurePosixPath(resolved.name))
                    if key in seen or len(seen) > 16 or "\\" in resolved.linkname:
                        raise RuntimeSetupError("Runtime archive contains invalid linked files")
                    seen.add(key)
                    linked = posixpath.normpath(posixpath.join(
                        str(PurePosixPath(resolved.name).parent) if resolved.issym() else "",
                        resolved.linkname,
                    ))
                    if PurePosixPath(linked).is_absolute() or ".." in PurePosixPath(linked).parts:
                        raise RuntimeSetupError("Runtime archive link escapes the bundle")
                    resolved = member_lookup.get(linked)
                    if resolved is None:
                        raise RuntimeSetupError("Runtime archive link target is missing")
                if not resolved.isfile():
                    raise RuntimeSetupError("Runtime archive link target is not a regular file")
                target.parent.mkdir(parents=True, exist_ok=True)
                content = bundle.extractfile(resolved)
                if content is None:
                    raise RuntimeSetupError("Runtime archive contains an unreadable file")
                with content, target.open("xb") as output:
                    shutil.copyfileobj(content, output)
                target.chmod(0o755 if resolved.mode & 0o111 else 0o644)
                files[str(relative)] = hashlib.sha256(target.read_bytes()).hexdigest()
        if not (unpacked / "ollama").is_file():
            raise RuntimeSetupError("Official runtime archive did not contain the CLI")
        (unpacked / ".release.json").write_text(json.dumps({
            "release": RELEASE, "archive_url": ARCHIVE_URL,
            "archive_sha256": ARCHIVE_SHA256, "files": files,
        }, indent=2) + "\n", encoding="utf-8")
        safe_project_path(RUNTIME)
        if RUNTIME.exists():
            raise RuntimeSetupError("Runtime appeared during installation; refusing overwrite")
        os.replace(unpacked, RUNTIME)
    require_runtime()
    print(f"Installed verified Ollama {RELEASE} at {RUNTIME}")


def require_runtime() -> Path:
    safe_project_path(RUNTIME)
    stamp = safe_project_path(RUNTIME / ".release.json")
    if not stamp.is_file():
        raise RuntimeSetupError("Project runtime is missing; run the install command first")
    metadata = json.loads(stamp.read_text(encoding="utf-8"))
    if metadata.get("release") != RELEASE or metadata.get("archive_sha256") != ARCHIVE_SHA256:
        raise RuntimeSetupError("Project runtime does not match the reviewed release")
    files = metadata.get("files")
    if not isinstance(files, dict) or "ollama" not in files:
        raise RuntimeSetupError("Project runtime integrity inventory is invalid")
    for relative, expected_hash in files.items():
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts or "\\" in relative:
            raise RuntimeSetupError("Project runtime inventory contains an unsafe path")
        installed = safe_project_path(RUNTIME.joinpath(*path.parts))
        if not installed.is_file() or hashlib.sha256(installed.read_bytes()).hexdigest() != expected_hash:
            raise RuntimeSetupError("Installed runtime integrity verification failed")
    executable = safe_project_path(RUNTIME / "ollama")
    if not os.access(executable, os.X_OK):
        raise RuntimeSetupError("Project runtime CLI is not executable")
    return executable


def runtime_environment() -> dict[str, str]:
    """Inherit essential platform settings, never provider tokens or OLLAMA overrides."""
    allowed = {"PATH", "HOME", "USER", "LOGNAME", "TMPDIR", "LANG", "LC_ALL", "TERM"}
    environment = {key: value for key, value in os.environ.items() if key in allowed}
    config = LocalModelConfig()
    environment.update({
        "OLLAMA_HOST": config.base_url,
        "OLLAMA_MODELS": str(safe_project_path(MODELS)),
        "OLLAMA_NO_CLOUD": "1",
        "OLLAMA_CONTEXT_LENGTH": str(config.num_ctx),
        "OLLAMA_NUM_PARALLEL": "1",
        "OLLAMA_MAX_LOADED_MODELS": "1",
        "OLLAMA_MAX_QUEUE": "4",
        "OLLAMA_NOHISTORY": "1",
        "OLLAMA_DEBUG_LOG_REQUESTS": "0",
        "NO_PROXY": "127.0.0.1,::1,localhost",
        "no_proxy": "127.0.0.1,::1,localhost",
    })
    return environment


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install", "serve", "pull", "status"))
    args = parser.parse_args()
    try:
        if args.command == "install":
            install()
            return 0
        executable = require_runtime()
        environment = runtime_environment()
        safe_project_path(MODELS).mkdir(parents=True, exist_ok=True)
        config = LocalModelConfig()
        command = {
            "serve": [str(executable), "serve"],
            "pull": [str(executable), "pull", config.model],
            "status": [str(executable), "list"],
        }[args.command]
        print(f"Local-only runtime: {config.base_url}; cloud disabled; model {config.model}", flush=True)
        return subprocess.run(command, env=environment, cwd=ROOT, check=False).returncode
    except KeyboardInterrupt:
        return 130
    except (OSError, ValueError, tarfile.TarError) as exc:
        print(f"Local runtime unavailable: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
