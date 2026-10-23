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

## 2026-10-22 — day 3

### Implemented and verified

- Downloaded the free Apache-2.0 `nomic-embed-text:v1.5` model through the
  project-owned, cloud-disabled loopback server. Observed full digest:
  `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`.
- A bounded embedding adapter checks identity before/after calls, applies the
  documented document/query prefixes, rejects invalid or non-finite vectors,
  and normalizes all 768 dimensions. No proxy, redirect or remote provider path.
- Embedded all 644 chunks without input truncation in 41 bounded batches.
  The [actual build metadata](../reports/day3-index-build.json) records 86,877
  prompt tokens and 12,450,323,371 ns summed model-reported duration; this is
  not end-to-end build elapsed time. All local API fees were zero.
- The backend capped embedding context at 2048 despite the configured 8192
  request and upstream setting. All full inputs succeeded; no 8192-token
  capacity is claimed for this runtime/model pair.
- The separate SQLite vector index binds exact text and all source metadata
  to the model digest, dimensions and preprocessing revision. Failed builds
  preserve an existing index. Missing, stale, incomplete or corrupt caches fail.
- Cosine search filters the exact snapshot before scoring. Fixed hybrid RRF
  combines twenty candidates per engine with constant 60, deterministic ties
  and corpus-change detection across engines. No raw-score mixing or fallback.
- CLI adds `embed`, `--vector-index` and explicit retrieval mode selection.
  Keyword remains the default for search and local draft answers.
- **132 automated checks pass**, including model identity, vector/cache
  validation, version isolation, real source-change races, transaction rollback,
  strict development-file validation and the no-match generation guard.
- The foreground model server was stopped after verification. Runtime, weights
  and both indexes remain local ignored artifacts. No cloud environment was
  configured or scheduled by this work; the daily schedule remains local.

### Recorded comparison and decisions

The development file was frozen before the first vector comparison at SHA-256
`91c06eb01d0a29a535e3b43ed0f091f3f65ef2d7c35aed79fb15e79cd3ae41c5`.
It contains sixteen answerable questions and four separate qualitative probes;
seventeen source anchors were checked against actual pinned chunks. These are
AI-authored, nonexhaustive labels, **not human review or a held-out benchmark**.

The [final comparison](../reports/day3-retrieval-comparison.json) records
known-evidence hits at five of 13/16 for keyword, 12/16 for vector and 13/16 for
hybrid; corresponding reciprocal ranks are 0.65625, 0.71875 and 0.653125.
Keyword stays the default: hybrid does not improve coverage and adds latency.
No reranker, tuned threshold or post-comparison parameter search was added.
The first comparison is retained separately; validation of malformed development
files was tightened before the final run, without changing questions or labels.

The [initial answer smoke](../reports/day3-initial-answer-smoke.json) exposed
unrelated drafted answers to the missing-token query under vector/hybrid modes.
The [final smoke](../reports/day3-answer-smoke.json) tests a conservative lexical
match prerequisite for experimental generation. That repeated query now abstains
without embedding or generation. This veto can reject useful paraphrases and
does not make matched passages semantically sufficient. Unsupported questions
with shared terms remain an evaluation risk.

The upgrade probe still produces `invalid_generation` in all three modes.
A separate [diagnostic](../reports/day3-upgrade-diagnostic.json) found a response
that selects `insufficient_evidence` while also supplying a claim; strict
validation suppresses the contradiction. Its claim also names removal in
0.28.1 instead of the supplied 0.28.0 heading. Better retrieval alone does not
repair this small model's output-contract and release-reasoning errors.
The old-version probe produced cited drafts in all modes, still labelled
`semantic_support_verified: false`. No answer-accuracy score is inferred.

### Next milestone

Day 4 on 23 October: local API contracts and validation, web UI, source/version
inspection, integration checks and accessibility. Holdout review, synthetic
permission filtering and final screenshots remain later milestones.


## 2026-10-23–24 — day 4

### Implemented and verified

- Added validated API operations for catalog, exact-version retrieval, existing
  draft generation and source inspection by validated chunk ID. Source metadata
  is resolved from the index, with no client-controlled file paths.
- Added a standard-library loopback HTTP server and `serve` command. Requests
  have strict Host/Origin checks, JSON/framing validation, body/read limits,
  bounded handlers and one active POST operation. Capacity errors return JSON;
  malformed targets are input errors. Only three bundled assets are served.
- Built a responsive browser workspace with exact snapshot selection, ranked
  excerpts, immutable source links, provenance inspection, cited drafts and
  explicit abstention/error states. Input changes invalidate previous output
  and prevent late responses from crossing question/version boundaries.
- Dynamic content remains plain text. Unsafe citation links fail closed. Labels,
  live status, keyboard focus, dialog Escape, mobile overflow and selected text
  contrast were checked; this is not full accessibility certification.
- [176 software tests passed](../reports/day4-software-checks.json), including
  18 API contract and 26 real socket boundary tests. Model calls in this suite
  use deterministic substitutes. SQLite test fixture connections now close
  explicitly; the final run emitted no ResourceWarning.
- [13 browser checks passed](../reports/day4-browser-check.json) using isolated
  headless Chrome 155.0.8059.40 and free Playwright 1.62.1. Real interactions
  cover retrieval, version changes, source inspection, abstention and a local
  draft. Negative markup/link/race/error checks use labelled fixtures. No
  external application requests or browser script errors were observed.
- [Actual screenshots](SCREENSHOTS.md) show real API results at desktop and
  360-pixel widths, including an actual model-generated timeout draft. No
  synthetic UI images or fixture responses were used for screenshots.

### Recorded behavior and limits

The [final HTTP development run](../reports/day4-http-smoke.json) records thirteen
actual requests: both snapshots, source identity, wrong-version 404, invalid
version 400, all three missing-evidence abstentions, two generation probes and
vector/hybrid evidence. The timeout draft completed in 1114.575 ms; the upgrade
probe was withheld with `invalid_generation` in 2298.835 ms. Missing-evidence
probes skipped generation, including the experimental lexical veto. Latencies
are fixed-order, repeated development observations, not performance guarantees.
The [initial HTTP run](../reports/day4-initial-http-smoke.json) is retained from
before final transport hardening. Final reports include implementation hashes.

Mechanical source/quote checks still do not establish semantic entailment;
`semantic_support_verified` remains false. No human-reviewed holdout, answer
accuracy, production authentication, synthetic permission filtering, public
hosted service or cloud execution is claimed. All inference and embeddings use
the cached cloud-disabled local server; model/API fees were zero. The optional
browser test dependency is free and is not an application runtime dependency.

### Actual dates and next milestone

The API contract commit was made on 23 October. Work was interrupted and resumed
on 24 October; server, interface and verification commits use their actual
24 October dates. No backdating or extra milestone was used to recover a daily
quota. Finishing day 4 consumes the 24 October development slot; day 5 was not
started. The original target dates remain visible in the delivery plan.

Next unfinished milestone: incremental snapshots/deletion and prominently
labelled synthetic permission filtering, with a version/permission change demo.
The daily schedule remains local, with the existing 26 October cutoff; later
work is not silently scheduled beyond the approved window.
