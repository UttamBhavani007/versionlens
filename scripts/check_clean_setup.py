#!/usr/bin/env python3
"""Verify a fresh source archive in a pip-free interpreter using only loopback.

This checks source deployment, not wheel installation, fresh model provisioning,
public hosting, or answer quality. The working checkout and its ignored runtime,
weights, credentials and indexes are never copied into the scratch checkout.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import socket
import subprocess
import sys
import tarfile
from tempfile import TemporaryDirectory
from time import monotonic, perf_counter, sleep
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
MAX_OUTPUT = 1024 * 1024
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_MEMBER = 8 * 1024 * 1024

# Python children cannot inherit cloud credentials/proxy settings, and their
# socket calls can reach only literal loopback, excluding both model ports.
SOCKET_GUARD = '''import json, os, socket
_original_connect = socket.socket.connect
_original_connect_ex = socket.socket.connect_ex
_original_getaddrinfo = socket.getaddrinfo

def _allowed(address):
    allowed = (isinstance(address, tuple) and len(address) >= 2
               and address[0] in {"127.0.0.1", "::1"}
               and address[1] not in {11434, 11435})
    if not allowed:
        with open(os.environ["VERSIONLENS_CLEAN_NETWORK_LOG"], "a") as output:
            output.write(json.dumps({"rejected_address": str(address)[:200]}) + "\\n")
        raise OSError("Clean setup permits literal loopback only and prohibits model endpoints")

def _getaddrinfo(host, port, *args, **kwargs):
    if host not in {"127.0.0.1", "::1"} or str(port) in {"11434", "11435"}:
        _allowed((host, int(port) if str(port).isdigit() else port))
    return _original_getaddrinfo(host, port, *args, **kwargs)

def _connect(self, address):
    _allowed(address)
    return _original_connect(self, address)

def _connect_ex(self, address):
    _allowed(address)
    return _original_connect_ex(self, address)

socket.socket.connect = _connect
socket.socket.connect_ex = _connect_ex
socket.getaddrinfo = _getaddrinfo
socket._versionlens_clean_guard = True
'''


class CleanSetupError(ValueError):
    pass


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise CleanSetupError("The clean deployment check rejects redirects")


def controlled_environment() -> dict[str, str]:
    allowed = ("PATH", "SYSTEMROOT", "WINDIR", "TMPDIR", "TMP", "TEMP", "LANG", "LC_ALL")
    environment = {name: os.environ[name] for name in allowed if name in os.environ}
    environment.update(PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1",
                       PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1",
                       PIP_CONFIG_FILE=os.devnull, NO_PROXY="127.0.0.1,::1")
    return environment


def capture(command, cwd: Path, environment: dict, log: Path, timeout=60):
    started = perf_counter()
    with log.open("wb") as output:
        try:
            completed = subprocess.run(command, cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=output, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            raise CleanSetupError("A clean setup command exceeded its bounded timeout") from None
    with log.open("rb") as output:
        raw = output.read(MAX_OUTPUT + 1)
    if len(raw) > MAX_OUTPUT:
        raise CleanSetupError("A clean setup command exceeded the diagnostic output limit")
    return completed.returncode, raw.decode("utf-8", errors="replace"), {
        "exit_code": completed.returncode, "latency_ms": round((perf_counter()-started)*1000, 3),
        "output_sha256": sha256(raw).hexdigest(), "output_bytes": len(raw),
    }


def extract_archive(archive_path: Path, target: Path) -> int:
    seen = set()
    total = 0
    with tarfile.open(archive_path, "r:") as archive:
        members = archive.getmembers()
        if not 1 <= len(members) <= 10_000:
            raise CleanSetupError("Unexpected source archive member count")
        for member in members:
            name = member.name.rstrip("/") if member.isdir() else member.name
            path = PurePosixPath(name)
            if (not name or path.is_absolute() or "\\" in name or "\x00" in name
                    or any(part in {"", ".", ".."} for part in name.split("/"))
                    or name in seen or not (member.isfile() or member.isdir())):
                raise CleanSetupError("Source archive contains an unsafe, duplicate or nonregular member")
            seen.add(name)
            destination = target.joinpath(*path.parts)
            if not destination.resolve().is_relative_to(target.resolve()):
                raise CleanSetupError("Source archive escapes its temporary checkout")
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            total += member.size
            if member.size < 0 or member.size > MAX_MEMBER or total > MAX_ARCHIVE:
                raise CleanSetupError("Source archive exceeds its bounded size")
            handle = archive.extractfile(member)
            if handle is None:
                raise CleanSetupError("Source archive member could not be read")
            with handle:
                data = handle.read(MAX_MEMBER + 1)
            if len(data) != member.size:
                raise CleanSetupError("Source archive member size is inconsistent")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as output:
                output.write(data)
            destination.chmod(member.mode & 0o777)
    return len(seen)


def checkout_state(checkout: Path) -> dict[str, str]:
    """Bind both the names and contents of files around readiness-only checks."""
    return {str(path.relative_to(checkout)): sha256(path.read_bytes()).hexdigest()
            for path in checkout.rglob("*") if path.is_file()}


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    if not 1024 <= port <= 65535:
        raise CleanSetupError("Could not select an unprivileged loopback port")
    return port


def verify(reference: str, report: dict):
    environment = controlled_environment()
    with TemporaryDirectory(prefix="versionlens-clean-") as temporary:
        work = Path(temporary)
        checkout = work / "checkout"
        checkout.mkdir()
        foreign = work / "outside-checkout"
        foreign.mkdir()
        archive = work / "source.tar"
        code, revision, metadata = capture(["git", "rev-parse", "--verify", reference+"^{commit}"], ROOT,
                                            environment, work/"revision.log")
        revision = revision.strip()
        if code or re.fullmatch(r"[0-9a-f]{40,64}", revision) is None:
            raise CleanSetupError("The requested local revision is not a commit")
        report["source_commit"] = revision
        with archive.open("wb") as output:
            completed = subprocess.run(["git", "archive", "--format=tar", revision], cwd=ROOT,
                                       env=environment, stdin=subprocess.DEVNULL, stdout=output,
                                       stderr=subprocess.PIPE, timeout=60, check=False)
        if completed.returncode or archive.stat().st_size > MAX_ARCHIVE:
            raise CleanSetupError("Could not produce a bounded local source archive")
        report["archive_sha256"] = sha256(archive.read_bytes()).hexdigest()
        report["archive_members"] = extract_archive(archive, checkout)
        forbidden = (".git", ".tools", ".ollama", "node_modules", ".venv", "error.log", "data/versionlens.sqlite3",
                     "data/versionlens-vectors.sqlite3", "data/versionlens-evaluation.sqlite3",
                     "data/versionlens-evaluation-vectors.sqlite3")
        if any((checkout/name).exists() for name in forbidden):
            raise CleanSetupError("A fresh archive unexpectedly contains ignored local artifacts")
        report["checks"].append({"name": "source_archive_excludes_local_state", "status": "passed"})
        if not (checkout/"scripts/run_local.py").is_file():
            raise CleanSetupError("The selected commit does not contain the local deployment launcher")
        import tomllib
        project = tomllib.loads((checkout/"pyproject.toml").read_text())
        if project["project"].get("dependencies") != []:
            raise CleanSetupError("The standard-library-only runtime contract changed")
        report["project_version"] = project["project"]["version"]
        report["third_party_runtime_dependencies"] = []
        virtual = work / "venv"
        code, output, metadata = capture([sys.executable, "-m", "venv", "--without-pip", str(virtual)],
                                        foreign, environment, work/"venv.log")
        report["checks"].append({"name": "pip_free_virtual_environment", "status": "passed" if code == 0 else "failed", **metadata})
        if code:
            raise CleanSetupError("Could not create the isolated standard-library interpreter")
        interpreter = virtual/("Scripts/python.exe" if os.name == "nt" else "bin/python")
        guard = work / "guard"
        guard.mkdir()
        (guard/"sitecustomize.py").write_text(SOCKET_GUARD)
        network_log = work/"network.jsonl"
        environment.update(PYTHONPATH=os.pathsep.join((str(guard), str(checkout/"src"))),
                           VERSIONLENS_CLEAN_NETWORK_LOG=str(network_log))
        program = ("import importlib.util,json,site,sqlite3,socket,sys; "
                   "assert sys.prefix != sys.base_prefix; assert site.ENABLE_USER_SITE is False; "
                   "assert importlib.util.find_spec('pip') is None; "
                   "assert getattr(socket,'_versionlens_clean_guard',False); "
                   "c=sqlite3.connect(':memory:'); c.execute('CREATE VIRTUAL TABLE f USING fts5(text)'); c.close(); "
                   "print(json.dumps({'python_version':sys.version.split()[0],'isolated_venv':True,"
                   "'user_site_enabled':site.ENABLE_USER_SITE,'sqlite_version':sqlite3.sqlite_version,'fts5':True,"
                   "'python_socket_guard':True,'pip_installed':False}))")
        code, output, metadata = capture([str(interpreter), "-c", program], foreign, environment, work/"environment.log")
        if code:
            raise CleanSetupError("The isolated interpreter, SQLite FTS5 or socket guard is unavailable")
        report["python_environment"] = json.loads(output)
        command = [str(interpreter), "scripts/fetch_sources.py", "--check"]
        code, output, metadata = capture(command, checkout, environment, work/"sources.log")
        report["checks"].append({"name": "offline_source_checksums", "status": "passed" if code == 0 else "failed", **metadata})
        if code or "Verified 32 pinned HTTPX sources" not in output:
            raise CleanSetupError("Fresh source checksums did not verify")
        launcher = str(checkout/"scripts/run_local.py")
        index = checkout/"data/versionlens.sqlite3"
        before = checkout_state(checkout)
        code, output, metadata = capture([str(interpreter), launcher, "--check"], foreign, environment, work/"missing.log")
        if code != 2 or json.loads(output).get("status") != "not_ready" or index.exists():
            raise CleanSetupError("Missing-index readiness check did not fail without creating an index")
        after = checkout_state(checkout)
        if before != after:
            raise CleanSetupError("Read-only missing-index check changed checkout files")
        report["checks"].append({"name": "missing_readiness_is_read_only", "status": "passed", **metadata})
        code, output, metadata = capture([str(interpreter), launcher, "--prepare"], foreign, environment, work/"prepare.log")
        prepared = json.loads(output) if code == 0 else {}
        if code or prepared.get("status") != "ready" or prepared.get("index", {}).get("sources") != 32 or prepared["index"].get("chunks") != 644:
            raise CleanSetupError("Fresh source preparation did not produce 32 sources and 644 chunks")
        report["checks"].append({"name": "fresh_offline_preparation", "status": "passed", "result": prepared, **metadata})
        before = checkout_state(checkout)
        code, output, metadata = capture([str(interpreter), launcher, "--check"], foreign, environment, work/"ready.log")
        if code or json.loads(output).get("status") != "ready" or checkout_state(checkout) != before:
            raise CleanSetupError("Ready-state check changed checkout files or failed")
        report["checks"].append({"name": "prepared_readiness_is_read_only", "status": "passed", **metadata})
        command = [str(interpreter), "-W", "error::ResourceWarning", "-m", "unittest", "discover", "-s", "tests", "-q"]
        code, output, metadata = capture(command, checkout, environment, work/"tests.log")
        count = re.search(r"Ran (\d+) tests in ([0-9.]+)s", output)
        if code or count is None or not re.search(r"\nOK\s*$", output) or "ResourceWarning:" in output:
            report["test_diagnostic_tail"] = output[-4000:]
            raise CleanSetupError("The fresh-source software suite did not pass")
        report["software_tests"] = {"status": "passed", "tests_run": int(count[1]),
                                    "reported_elapsed_seconds": float(count[2]), **metadata}
        _verify_http(checkout, interpreter, launcher, foreign, environment, work, report)
        rejected = [json.loads(line) for line in network_log.read_text().splitlines()] if network_log.exists() else []
        report["rejected_socket_attempts"] = rejected
        if rejected:
            raise CleanSetupError("A Python child attempted a prohibited external or model connection")
        report["checks"].append({"name": "no_external_or_model_socket_attempts", "status": "passed"})


def _verify_http(checkout, interpreter, launcher, foreign, environment, work, report):
    port = free_port()
    origin = f"http://127.0.0.1:{port}"
    opener = build_opener(ProxyHandler({}), NoRedirects())
    server_log = work/"server.log"
    child = None

    def call(name, route, payload=None, expected=200, json_response=True, headers=None):
        started = perf_counter()
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        fields = {"Content-Type": "application/json"} if body is not None else {}
        fields.update(headers or {})
        request = Request(origin+route, data=body, headers=fields)
        try:
            response = opener.open(request, timeout=10)
        except HTTPError as error:
            response = error
        with response:
            raw = response.read(MAX_OUTPUT + 1)
            status = response.status
            fields = {key: response.headers.get(key) for key in ("Content-Type", "Content-Security-Policy", "Cache-Control", "X-Content-Type-Options")}
        if status != expected or len(raw) > MAX_OUTPUT:
            raise CleanSetupError(f"Unexpected HTTP response for {name}")
        if (fields["Cache-Control"] != "no-store" or fields["X-Content-Type-Options"] != "nosniff"
                or not fields["Content-Security-Policy"]):
            raise CleanSetupError(f"Missing local security headers for {name}")
        result = json.loads(raw) if json_response else raw
        row = {"name": name, "status": "passed", "http_status": status,
               "latency_ms": round((perf_counter()-started)*1000, 3), "headers": fields,
               "body_sha256": sha256(raw).hexdigest(), "body_bytes": len(raw)}
        if json_response:
            row["result"] = result
        report["http_checks"].append(row)
        return result

    try:
        with server_log.open("wb") as output:
            child = subprocess.Popen([str(interpreter), launcher, "--port", str(port)], cwd=foreign,
                                     env=environment, stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT)
            deadline = monotonic()+10
            while monotonic() < deadline:
                if child.poll() is not None:
                    raise CleanSetupError("The clean local server exited during startup")
                if f"VersionLens local UI: {origin}" in server_log.read_text(errors="replace"):
                    break
                sleep(.1)
            else:
                raise CleanSetupError("The clean local server did not announce readiness within ten seconds")
            catalog = call("public_catalog", "/api/catalog")
            if catalog.get("access_profile") != "public" or catalog.get("index", {}).get("sources") != 32 or catalog["index"].get("chunks") != 644:
                raise CleanSetupError("The clean server catalog is not the public pinned corpus")
            for route, filename in (("/", "index.html"), ("/style.css", "style.css"), ("/app.js", "app.js")):
                body = call("bundled_"+filename, route, json_response=False)
                if body != (checkout/"src/versionlens/web"/filename).read_bytes():
                    raise CleanSetupError("A served bundled asset differs from its archived source")
            selected = None
            for version in ("0.27.2", "0.28.1"):
                found = call("keyword_"+version, "/api/search", {"question": "default timeout", "version": version})
                if not found.get("hits") or any(hit["version"] != version or hit["access"] != "public" for hit in found["hits"]):
                    raise CleanSetupError("Clean keyword retrieval violated version/access isolation")
                if version == "0.28.1":
                    selected = found["hits"][0]
            inspected = call("source_inspection", f"/api/chunks/{selected['chunk_id']}?version=0.28.1")
            if inspected["text"] != selected["text"] or inspected["source_sha256"] != selected["source_sha256"]:
                raise CleanSetupError("Clean source inspection changed source identity")
            call("wrong_version_source", f"/api/chunks/{selected['chunk_id']}?version=0.27.2", expected=404)
            call("unsupported_version", "/api/search", {"question": "timeout", "version": "latest"}, expected=400)
            call("browser_self_promotion", "/api/search", {"question": "timeout", "version": "0.28.1", "access_profile": "support"}, expected=400)
            call("cross_origin", "/api/search", {"question": "timeout", "version": "0.28.1"}, expected=403,
                 headers={"Origin": "https://example.invalid"})
            for method in ("keyword", "vector", "hybrid"):
                result = call("missing_"+method, "/api/ask", {"question": "quantumgiraffeunsupported", "version": "0.28.1", "retriever": method})
                if result.get("status") != "abstained" or result.get("model_called") is not False or result.get("answer") is not None or result.get("claims") != []:
                    raise CleanSetupError("Missing evidence did not abstain without a model")
            if child.poll() is not None:
                raise CleanSetupError("Owned clean server exited before verification finished")
    finally:
        forced = False
        if child is not None:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    forced = True
                    child.kill()
                    child.wait(timeout=5)
            report["owned_server_shutdown"] = {"stopped": child.poll() is not None,
                                                "exit_code": child.returncode, "forced_kill": forced,
                                                "log_sha256": sha256(server_log.read_bytes()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="HEAD", help="Existing local commit/ref; no fetch is performed")
    parser.add_argument("--output", type=Path, default=ROOT/"reports/local/clean-setup.json")
    args = parser.parse_args()
    if not args.ref or args.ref.startswith("-") or "\x00" in args.ref or len(args.ref) > 200:
        parser.error("Choose an existing local commit/ref")
    if args.output.exists():
        parser.error("Output exists; choose a new path to preserve the earlier result")
    report = {
        "schema_version": 1, "kind": "fresh_source_deployment", "status": "running",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(), "requested_ref": args.ref,
        "host": {"system": platform.system(), "machine": platform.machine(), "python_version": platform.python_version()},
        "isolated_source_checkout": True, "python_package_installation_tested": False,
        "pip_used": False, "local_model_calls": False, "external_network_downloads": False,
        "candidate_holdout_executed": False, "human_review_completed": False,
        "check_script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "checks": [], "http_checks": [],
        "limitations": ["Fresh tracked source and pip-free interpreter, not a wheel/install test.",
                        "Model downloads, real generation, dense positive retrieval and browser rendering are separate prior checks.",
                        "No external service, public hosting, human review or answer-quality result is established.",
                        "Python socket guards are additional controls, not an operating-system sandbox."],
    }
    started = perf_counter()
    try:
        verify(args.ref, report)
        report["status"] = "passed"
    except Exception as error:
        # A failing assertion/response shape must still produce a failed report.
        report["status"] = "failed"
        report["error"] = {"type": type(error).__name__, "message": str(error)[:1000]}
    report["elapsed_seconds"] = round(perf_counter()-started, 3)
    report["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with args.output.open("x", encoding="utf-8") as output:
            json.dump(report, output, indent=2, ensure_ascii=False, allow_nan=False)
            output.write("\n")
    except FileExistsError:
        print("Output appeared during verification; the previous file was preserved", file=sys.stderr)
        return 2
    print(json.dumps({"report": str(args.output), "status": report["status"],
                      "software_tests": report.get("software_tests", {}).get("tests_run"),
                      "http_checks": len(report["http_checks"]), "error": report.get("error")}, indent=2))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
