#!/usr/bin/env python3
"""Record actual local API responses; no held-out quality claims or cloud calls."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import perf_counter
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from versionlens.local_model import LocalModelClient


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/local/day4-http-smoke.json")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535 or args.output.exists():
        parser.error("Choose an unprivileged port and a new output filename.")
    opener = build_opener(ProxyHandler({}), NoRedirects())
    results = []

    def call(case_id, route, payload=None, expected=200):
        started = perf_counter()
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(f"http://127.0.0.1:{args.port}" + route, data=body,
                          headers={"Content-Type": "application/json"} if body else {})
        try:
            response = opener.open(request, timeout=150)
        except HTTPError as error:
            response = error
        with response:
            raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise ValueError("Unexpectedly large API response")
            data = json.loads(raw)
            status = response.status
            headers = {name: response.headers.get(name) for name in
                       ("Content-Security-Policy", "X-Content-Type-Options", "Cache-Control")}
        if status != expected:
            raise ValueError(f"Unexpected HTTP status for {case_id}: {status}")
        result = {"case_id": case_id, "route": route, "request": payload,
                  "http_status": status, "latency_ms": round((perf_counter()-started)*1000,3),
                  "security_headers": headers, "result": data}
        results.append(result)
        print(json.dumps({"case_id": case_id, "http_status": status,
                          "status": data.get("status"), "reason": data.get("reason")}), flush=True)
        return data

    try:
        inventory = LocalModelClient().health()
        catalog = call("catalog", "/api/catalog")
        if catalog["index"]["chunks"] != 644:
            raise ValueError("Unexpected pinned corpus size")
        hits = {}
        for version in ("0.27.2", "0.28.1"):
            data = call("keyword_" + version, "/api/search",
                        {"question": "default timeout", "version": version})
            if not data["hits"] or any(hit["version"] != version for hit in data["hits"]):
                raise ValueError("Version-isolation smoke failed")
            hits[version] = data["hits"][0]
        selected = hits["0.28.1"]
        inspected = call("source_inspection", f"/api/chunks/{selected['chunk_id']}?version=0.28.1")
        if inspected["text"] != selected["text"] or inspected["source_sha256"] != selected["source_sha256"]:
            raise ValueError("Source inspection changed provenance")
        call("source_wrong_version", f"/api/chunks/{selected['chunk_id']}?version=0.27.2", expected=404)
        call("unsupported_version", "/api/search", {"question": "timeout", "version": "latest"}, expected=400)
        for method in ("keyword", "vector", "hybrid"):
            result = call("missing_" + method, "/api/ask",
                          {"question": "quantumgiraffeunsupported", "version": "0.28.1", "retriever": method})
            if result["status"] != "abstained" or result["model_called"]:
                raise ValueError("Missing-evidence smoke unexpectedly called generation")
        call("timeout_draft", "/api/ask", {"question": "What is the default timeout in HTTPX?", "version": "0.28.1"})
        call("upgrade_draft", "/api/ask", {"question": "Why did the proxies argument stop working after upgrading?", "version": "0.28.1"})
        for method in ("vector", "hybrid"):
            result = call(method + "_evidence", "/api/search",
                          {"question": "default timeout", "version": "0.28.1", "retriever": method})
            if any(hit["version"] != "0.28.1" for hit in result["hits"]):
                raise ValueError("Experimental retrieval returned the wrong version")
        if LocalModelClient().health().get("digest") != inventory.get("digest"):
            raise ValueError("Generation model changed during the API smoke")
        report = {"schema_version": 1, "kind": "local_http_development_smoke",
                  "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                  "not_a_held_out_benchmark": True, "human_reviewed": False,
                  "semantic_support_verified": False, "api_fee_usd": 0,
                  "generation_model_inventory": inventory,
                  "limitations": ["Repeated development probes; no answer-accuracy or citation-entailment score.",
                                  "End-to-end latencies include model loading/swapping in a fixed order.",
                                  "This verifies a local API, not public hosting or production readiness."],
                  "implementation_sha256": {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
                                            for path in sorted((ROOT / "src/versionlens").glob("*.py"))},
                  "results": results}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as output:
            json.dump(report, output, indent=2, ensure_ascii=False, allow_nan=False)
            output.write("\n")
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Local HTTP smoke failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
