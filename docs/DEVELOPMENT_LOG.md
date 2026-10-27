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


## 2026-10-24 — day 5, explicitly resumed by the owner

The owner requested today's originally planned work after the overnight day-4
completion. This new instruction resumed day 5 on 24 October; it supersedes the
earlier instruction to defer that milestone. All three milestone commits use
the actual date. No future evaluation or final-delivery milestone was started.
An approval-review usage limit interrupted final verification; work resumed
when review became available. Earlier saved observations were preserved.

### Implemented and verified

- Added schema-2 access/provenance metadata and transactional explicit migration
  from schema 1 during ingestion. Unknown schemas are rejected and preserved.
- Added validated per-snapshot synchronization: add/change/remove desired
  sources, retain unchanged rows, preserve other versions and roll back SQL/FTS
  failures. Whole-snapshot deletion is explicit and supports the final snapshot.
- Added two opt-in MIT-licensed synthetic runbooks with prominent fictional
  labels, independent checksums and protected local source citations. Original
  pinned HTTPX files remain unchanged. Opt-in totals: 34 sources/646 chunks;
  the public profile sees only its accessible 32 sources/644 chunks.
- Added trusted `public`/`support` demo profiles to CLI/server configuration.
  Browser JSON cannot grant roles or override source ACLs. Keyword, vector,
  hybrid pools, source inspection, catalog and model context enforce the same
  profile. Selected evidence changed during inference suppresses the draft.
- Updated the UI with visible demo-only profile/provenance labels and strict
  synthetic revision/link validation. This is not production authentication.
- [227 software tests passed](../reports/day5-software-checks.json), including
  28 permission, 15 snapshot update and eight synthetic-ingestion/CLI tests.
  Tests cover restricted top candidates before LIMIT, unknown policies, source
  ID probing, metadata-only policy changes, actual schema-1 migration, SQL/FTS
  rollback, stale vectors and content/access deletion during generation.
- [Eight real access browser checks](../reports/day5-access-browser.json),
  [23 explicitly mocked UI fixture checks](../reports/day5-permission-fixtures.json),
  [13 browser regression checks](../reports/day5-browser-regression.json) and
  [13 public API probes](../reports/day5-http-smoke.json) passed. Actual screenshots
  include source inspection, public abstention, a synthetic draft and mobile UI.
  No external application requests or browser script errors were observed.

### Observed changes and limitations

The [29-step isolated change run](../reports/day5-change-demo.json) used real
local embeddings and generation. Support drafts cited the fictional budget of
2 attempts for 0.27.2 and 3 for 0.28.1, then 4 after revising the newer document.
Granting public access produced another cited draft of 4. Revoking access
restored abstention without generation and denied a previously known source ID.
The changed document's obsolete source ID was absent; its vector cache was
rejected as stale. Deleting only the newer snapshot preserved the older one.
The demonstration changed scratch copies, not checked-in source documents.

These are repeated synthetic development observations, not human review or a
held-out answer-quality benchmark. `semantic_support_verified` remains false.
The real HTTPX upgrade probe still abstains with `invalid_generation`; the
remaining release-reasoning limitation is not considered solved. Keyword
remains default and no reranker was added. No new model, paid service or cloud
execution was used; local model/API fees were zero. Both local interfaces and
the foreground model server were stopped after verification; weights and
indexes remain local ignored artifacts.

Raw source SHA verification belongs to the manifest loader; normalized chunks
cannot reconstruct original raw newline bytes. Permission revocation does not
erase previously viewed content or cancel an authorized in-flight model call.
FTS5 ranking statistics are collection-wide; no score/timing isolation or
production multi-user security is claimed. Vector rebuilds still embed the full
corpus and are explicit after content or ACL changes.

### Next milestone

Day 6 on 25 October: draft evaluation candidates and review workflow, evaluation
runner and citation audit. Candidate labels remain drafts until human review;
a frozen holdout must remain separate from tuning. Day 7 and the approved local
schedule still end on 26 October. No further day-5 work is needed after delivery.


## 2026-10-25 — day 6 engineering; human review pending

### Implemented and verified

- Added 100 AI-authored draft cases in 17 topic groups: 40 development questions
  in seven groups and 60 candidate holdout questions in ten. Categories total
  59 answerable, 13 wrong-version, eight permission-denied, ten missing-evidence
  and ten conflicting-evidence questions. These are not 100 independent topics.
- Source-checked 79 exact identity/checksum/version/section/text anchors without
  running any candidate-holdout question. Known prior intents remain in
  development. Four prominently labelled same-version conflict documents are
  isolated in the evaluation manifest; normal application/demo files are unchanged.
  Evaluation corpus: 38 sources, 650 chunks.
- Added strict draft validation, pending human review exports and digest-bound
  holdout release/execution checks. Question, label, group, access, corpus, review
  or lock changes invalidate the binding. The tool validates attestations, not
  a reviewer's identity or semantic judgment quality.
- Added an evaluation runner with explicit profiles, per-method/case error rows,
  positive-anchor denominators, status counts, retrieval and answer-pipeline
  timing, tokens, local zero API fees and unchanged default keyword retrieval.
- Added independent mechanical citation checks and a separate human claim-review
  workflow. Claim support and factual/release correctness are independent;
  unsupported-answer scoring requires complete human judgments.
- [282 software tests passed](../reports/day6-software-checks.json), including
  18 question-review, 20 evaluator/audit and 17 answer-review tests. Human
  approvals in tests are explicitly fictional temporary fixtures. No genuine
  approval or holdout lock was generated by tests or exports.
- [Actual gate checks](../reports/day6-review-gates.json) rejected freezing with
  pending question reviews, holdout execution without reviews/lock, and semantic
  scoring with pending claim judgments. No prohibited outputs were created.

### Actual observations, not reviewed benchmark results

The [raw run](../reports/day6-development-evaluation.json) records 120 trials on
40 development questions. No candidate-holdout question was executed. Dataset
SHA-256 is `09a64d3923d7817228fbf99b568caf944dfcf1ddcfa8991582efc8ee0640fbde`;
corpus fingerprint is `62d9c3a98fe05e3f805bbd6e286f5358d3305a7977aa6f5563c73cfd4817aac2`.
The [results document](EVALUATION_RESULTS.md) describes all denominators and limits.

Known-anchor hit at five was 17/19 keyword, 17/19 vector and 18/19 hybrid;
corresponding MRR was 0.7228, 0.7895 and 0.7675. There were no retrieval/version/
access or runtime violations. The extra hybrid hit is insufficient evidence for
changing the default from this small, provisional, grouped development sample.

All 55 returned citations passed canonical source and exact quotation checks.
This does not establish semantic correctness. Each method returned drafts for
four of five synthetic conflict questions even though both sources were found;
12/15 conflict trials answered despite draft abstention labels. The remaining
case was withheld for invalid generation, not demonstrated conflict resolution.
Some missing-evidence/wrong-version cases also produced drafts; their outputs
are retained. No prompt, threshold, reranker or chunk tuning followed the run.

Keyword returned 16 drafts/24 abstentions, vector 17/23 and hybrid 18/22.
There were 117 real local generation calls. The 51 answered trials and 55 claims
have a separate pending review pack. Semantic citation correctness and
unsupported-answer rate remain `null`; they are not inferred from literal
quotes or provisional question labels. Latencies are fixed-order local
observations, not controlled performance or availability guarantees. All model/
API fees were zero; cached local models and separate ignored SQLite files were
used. The foreground model server was stopped after the run.

### Required human work and next independent milestone

The owner replied “I’ll review the questions.” This is agreement to review,
not evidence that any labels were approved. All 100 question records and all
51 answer-trial records are still pending. No real holdout lock, reviewed
holdout run, semantic score or human-review completion is claimed. Freezing
and reviewed results remain unfinished until actual review records arrive.

Day 7 on 26 October may proceed with independent reproducible local deployment,
clean setup checks and final release documentation while clearly preserving
this open evaluation requirement. The approved schedule still ends on
26 October; no extension or work beyond that cutoff is assumed.


## 2026-10-27 — final source deployment and prototype release

### Schedule and scope

The original local schedule ended on 26 October before final verification was
finished. No day-7 commit was backdated. The owner explicitly replied “Allow
completion past midnight” and later requested continuation. This final work
uses its actual 27 October date. The expired recurring automation was removed
and not recreated; the extension authorizes completion rather than a new schedule.

### Implemented and verified

- Added `scripts/run_local.py`: Python/FTS5 prerequisites, checksum-verified
  default preparation, explicit synthetic selection/rebuild, foreground
  loopback serving and JSON readiness. Matching indexes remain byte-identical;
  differing/unknown/corrupt indexes are preserved unless a supported explicit
  rebuild is requested. Fixed-path symlinks are rejected. Readiness disables
  bytecode writes and rejects WAL-mode indexes before SQLite opens them.
- Added 17 meaningful launcher checks, bringing the full suite to **299 passing
  tests** with ResourceWarning treated as an error. Tests include fresh copied
  source execution from another working directory and no-write/WAL preservation.
- Added a safe temporary Git-archive verifier, a pip-free virtual environment,
  offline source verification and actual HTTP deployment probes. It excludes
  ignored runtime state, credentials, weights and databases. Allowlisted
  environments and Python socket guards are additional controls, not an
  operating-system sandbox.
- The [fresh-source report](../reports/day7-clean-setup.json) records archived
  commit `94b796b1af9ecdcdfd7020118540fda050569ae4`, Python 3.13.7, SQLite
  3.50.4/FTS5, pip absent, **299 passing tests and 14 passing real HTTP probes**.
  A missing-index check changed no files; preparation produced 32 sources/644
  chunks; ready-state checking changed no files. Both versions, source identity,
  invalid requests, browser-origin/role rejection and three model-free
  missing-evidence paths were exercised. No prohibited socket attempts were
  observed, no downloads/model calls occurred, and the owned server was stopped.
- The [release browser check](../reports/day7-browser-check.json) passed **12
  checks**, with no external application requests or script errors. Four
  negative/race cases use labelled fixtures. Three [real screenshots](SCREENSHOTS.md)
  show desktop evidence, source inspection and a 360-pixel mobile view. Generation
  was not repeated; earlier cited-draft screenshots retain their actual dates.
  The release-capture interface was also stopped after verification.
- Added source-checkout deployment instructions, a reproducible interview
  walkthrough, final README, license clarification and prototype release notes.
  Source deployment includes `data/corpus/` and manifests; a self-contained
  wheel/pip installation is not claimed. Runtime/model downloads remain explicit
  optional steps and the pinned native installer supports Apple Silicon macOS.

### Release boundary and remaining human work

Commits 23–25 complete independent packaging and verification. The final commit
adds documentation and reports without changing the application/test source
verified at commit 24. Publication is a **0.1.0 local prototype prerelease**.
There is no public hosted endpoint, production authentication or paid service.
All model weights and SQLite builds remain ignored local artifacts; the
untracked pre-existing `error.log` is preserved and excluded from publication.

All 100 question-label records and all 51 generated-answer trial reviews remain
pending. The 60 candidate holdout questions remain unexecuted, and no real
holdout lock or semantic score exists. The 12/15 synthetic-conflict drafts and
prior `invalid_generation` upgrade failures are retained limitations. Mechanical
quote validity is not semantic correctness. No evaluation tuning, reranker or
new generation run was added during packaging. Human review and the reviewed
holdout remain unfinished external requirements, not completed release criteria.

Development used AI coding assistance with automated verification and retained
raw observations. AI-authored evaluation labels remain explicitly marked drafts.
