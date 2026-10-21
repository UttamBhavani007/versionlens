# Development log

## 2026-10-20 — day 1

The owner requested a version-aware support RAG project delivered in meaningful
stages over seven days, with zero paid services. Development is AI-assisted
through Codex; maintainers must understand and verify the submitted work.

- Scope: HTTPX documentation at fixed snapshots 0.27.2 and 0.28.1.
- Starting environment: Python 3.13.7, Apple Silicon, 16 GiB system RAM.
- Ollama, Docker, and GitHub CLI are not installed at project start.
- GitHub is connected as UttamBhavani007. Public publication was explicitly
  approved by the owner after reviewing the repository setup.
- Commit authorship uses the name and email from the authenticated GitHub
  profile, configured only for this repository.

### Implemented and verified

- Strict exact-version requests and immutable source metadata.
- 32 unmodified upstream files, 270,391 bytes; both BSD licenses preserved.
- Markdown chunking with heading hierarchy and exact line references. GitHub
  Markdown links explicitly use `?plain=1` so line anchors work.
- Transactional SQLite/FTS5 index: 644 chunks across the two snapshots.
- BM25 keyword baseline and JSON CLI: ingest, stats, and search.
- 26 automated tests pass on Python 3.13.7. The full checked-in corpus passes
  checksum verification; all chunk text matches its original source lines.
- Live CLI smoke checks return only the requested snapshot for both versions,
  and an absent token returns no matches. No model or network is used by the
  running ingestion/retrieval commands.

### Observed limitation

For the development probe `proxies argument removed`, the 0.28.1 keyword search
returns the 0.26.0 deprecation entry above the 0.28.0 removal entry. This is a
real baseline weakness: snapshot isolation alone is not release-applicability
reasoning. It must be measured in later development evaluation; no answer
correctness or retrieval-quality score is inferred from software tests.

### Next milestone

Day 2: install/configure the free local model runtime inside the project where
practical, disable cloud features, implement a loopback-only model adapter,
add cited generation and abstention, then record an actual local smoke run.
No model weights are downloaded or generation performance claimed on day 1.

No generation, vector retrieval, hosted deployment, or evaluation scores are
claimed at this stage.

## 2026-10-21 — day 2

### Implemented and verified

- Pinned free Ollama v0.40.7 installed as a regular project-local executable,
  with exact release-asset SHA-256 and per-file integrity checks. It does not
  install a desktop app or login service. Ollama created its normal local
  identity files under the user's home directory; no sign-in was performed.
- Project server ran at `127.0.0.1:11435`. Startup explicitly reported
  `Ollama cloud disabled: true`; child environment excludes provider tokens,
  inherited proxies and remote Ollama overrides.
- Approved `qwen3:1.7b` downloaded locally. The exact observed model digest is
  `8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7`.
  Model tag names are mutable; evaluation must record the digest.
- Bounded local adapter rejects remote endpoints, redirects, environment
  proxies, wrong models, malformed/oversized responses and truncated output.
- Local draft answer pipeline validates decision, claims and scoped evidence/
  quotation IDs, resolving quotes and source metadata server-side. Empty
  retrieval avoids model execution. Runtime errors are distinct from evidence
  abstention. Answers do not claim semantic support is verified.
- CLI now supports `doctor` and `ask`; existing retrieval commands remain
  offline. `scripts/smoke_local.py` records actual local development probes.
- Final automated suite: **74 tests pass**, including loopback HTTP failure
  cases, input/output bounds, Unicode/markup rejection, source integrity,
  policy enforcement and CLI integration. No paid API was used.
- The project-owned foreground server was stopped after verification; the
  project port no longer has a listener. Runtime and weights remain cached.
  Start `python3 scripts/local_runtime.py serve` before the next generation run.

### Actual live runs and the change they motivated

The first [four-case development run](../reports/day2-initial-smoke.json)
suppressed all three generated drafts as `invalid_generation`. The absent-token
query correctly made no model call. A diagnostic found contradictory
`status`/`reason` fields and inaccurate copying of some source quotes.

The internal output contract was then simplified to one decision and at most
two claims. The model selects known `(evidence_id, quote_id)` pairs instead of
rewriting quote text. The server returns exact source spans. This reduces the
copying burden without accepting fabricated quotations or claiming semantic
verification. Quote menus omit visible fenced code and oversized prose;
original chunk boundaries may still omit surrounding source context.

The [final run](../reports/day2-local-smoke.json), using `quote_menu_v2`, recorded:

| Development probe | Actual result | End-to-end latency |
| --- | --- | --- |
| HTTPX 0.28.1 default timeout | Cited draft: five seconds of network inactivity | 1755.093 ms |
| HTTPX 0.28.1 proxies upgrade | Invalid generation suppressed; no answer shown | 1315.057 ms |
| HTTPX 0.27.2 proxies deprecation | Cited draft: argument is deprecated | 1088.853 ms |
| Missing token | Abstained, no model call | 0.597 ms |

All generated-result outputs still set `semantic_support_verified: false`.
Both reports set `human_reviewed: false` and are explicitly not held-out
benchmarks. Development changes, model warming and repeated prompts prevent
interpreting these timings or outcomes as a controlled quality improvement.
The upgrade-case failure remains visible rather than being replaced by a
handwritten success. No API/UI, semantic retrieval, public hosted endpoint or
manually reviewed benchmark is claimed.

### Next milestone

Day 3: add local embeddings and vector/hybrid retrieval, compare them against
the keyword baseline on development questions, and investigate the remaining
upgrade failure. Keep these probes out of the later frozen holdout. Do not
adopt reranking without measured benefit.
