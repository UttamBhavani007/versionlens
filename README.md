# VersionLens

A local, version-aware technical support service for **HTTPX**. The goal is to
answer upgrade and troubleshooting questions from the documentation that matches
the requested version, with inspectable evidence and explicit abstention.

**Status: day 2 complete, local cited drafts.** Pinned ingestion, version-filtered keyword
retrieval, a cloud-disabled local model, cited draft answers and abstention are
implemented. Semantic retrieval, the API, UI, held-out evaluation and screenshots
remain future milestones. See [the delivery plan](docs/DELIVERY_PLAN.md).

## Zero paid services

- No OpenAI API, paid inference, hosted vector database, cloud account, or trial.
- Python and SQLite run on your existing computer.
- Inference uses a downloaded open model through local Ollama with cloud
  features disabled. No account or API key is required for local inference.
- Source code and documentation are intended for a public GitHub Free repository.
  Local checks remain the default. Any optional CI must refuse private repositories
  and use only standard free public runners, with no artifact or cache storage.
- No remote inference fallback, automatic billing, or paid deployment is allowed.

See [the cost policy](docs/COST_POLICY.md). Internet is needed to download public
documentation and, later, model weights. After setup, retrieval works offline.

## Why HTTPX?

The initial corpus contains the historical **0.27.2** and **0.28.1** snapshots;
these are demonstration versions, not a claim about the latest release. HTTPX
0.28.0 removed deprecated `proxies` and `app` arguments, giving the project real
version-specific support cases. Each source will carry an immutable upstream
commit, checksum, and line reference. See [source provenance](docs/SOURCES.md).

## Development

Requires Python 3.11 or newer with SQLite FTS5. The day-1 runtime and tests have
no third-party dependencies. From this repository:

```sh
python3 scripts/fetch_sources.py --check
PYTHONPATH=src python3 -m versionlens ingest
PYTHONPATH=src python3 -m versionlens search 'proxies argument removed' --version 0.27.2 --limit 3
PYTHONPATH=src python3 -m versionlens search 'proxies argument removed' --version 0.28.1 --limit 3
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The checked-in corpus works offline: 32 source files, 16 per snapshot, indexed
into 644 line-preserving chunks with the default settings. The index is a local,
ignored build artifact; rebuild it from the manifest after cloning. An editable
installation is optional; running with `PYTHONPATH=src` avoids installing build
tools. No service account is required.

`search` returns JSON with ranked excerpts, exact version, immutable source
links, line ranges, and SHA-256 provenance. It sets `answer` to `null` because
`search` is retrieval-only. Missing matches return `no_matching_evidence`.
Unsupported versions and malformed requests fail explicitly.

**Known baseline limitation:** BM25 can rank an old release-history entry above
a more recent applicable change, even within the correct snapshot. Selecting
the correct snapshot is necessary but does not prove the retrieved passage
answers the question. Release headings are preserved for the later answering
and evaluation layers. Ranking scores are not confidence probabilities.

Automated checks cover source integrity and line references, transactional
ingestion, wrong-version isolation, local endpoint/model restrictions, proxy
and redirect rejection, malformed or truncated model responses, citation
validation, conservative abstention and CLI behavior. These are software
checks, not a held-out answer-quality benchmark.

## Free local draft answers

The native runtime installer currently supports **Apple Silicon macOS**.
Generation uses `qwen3:1.7b` locally on a separate loopback port, with cloud
features disabled. See [runtime/model provenance and setup](docs/LOCAL_MODELS.md).
The application and tests still use Python's standard library only.

In one terminal, install the pinned runtime and start its foreground server:

```sh
python3 scripts/local_runtime.py install
python3 scripts/local_runtime.py serve
```

Leave that terminal running. In a second terminal:

```sh
python3 scripts/local_runtime.py pull
PYTHONPATH=src python3 -m versionlens doctor
PYTHONPATH=src python3 -m versionlens ask 'What is the default timeout in HTTPX?' --version 0.28.1
PYTHONPATH=src python3 -m versionlens ask 'Why did the proxies argument stop working after upgrading?' --version 0.28.1
PYTHONPATH=src python3 -m versionlens ask 'quantumgiraffeunsupported' --version 0.28.1
python3 scripts/smoke_local.py
```

The first model pull downloads approximately 1.4 GB of free model weights;
weights and runtime artifacts are ignored by Git. Stop the server with Ctrl-C.
No desktop app, sign-in, key, system background service or paid API is required.

`ask` emits structured JSON and a cited draft. The model selects source and
quotation IDs; the server resolves the exact original text and constructs
source links from trusted metadata.
Empty retrieval does not call the model. Invalid drafts are suppressed; runtime
failure is an operational error, separately from evidence abstention.

**A real quote does not prove that a paraphrase is correct.** Answers expose
`semantic_support_verified: false`; citation relevance, entailment and release
applicability still need evaluation. See [the answer policy](docs/ANSWER_POLICY.md).

**Verified on 21 October:** 74 automated checks pass. The actual four-case
[local development run](reports/day2-local-smoke.json) produced two cited drafts,
suppressed one invalid generation on the upgrade question, and skipped the model
for one missing-evidence query. The
[initial failed run](reports/day2-initial-smoke.json) is retained. These prompts
were used during development and are not held-out evaluation questions; the
recorded roughly 1.1–1.8 second end-to-end latencies for model-calling probes are warmed, small-sample
observations, not a deployment speed guarantee or controlled comparison.

## Evaluation commitments

The planned 80–120-question dataset needs human review. Development questions
and a frozen holdout must be separate. We will report retrieval, citation
correctness, unsupported answers, abstention, latency, and usage independently.
No scores, human-review claims, screenshots, or deployment claims will be
published before they are supported by an actual run or review.

## License and attribution

Project code: [MIT](LICENSE). Vendored HTTPX documentation remains under its
upstream license and attribution, documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
AI assistance and limitations will be recorded in [the development log](docs/DEVELOPMENT_LOG.md).
