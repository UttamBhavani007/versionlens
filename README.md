# VersionLens

A local, version-aware technical support service for **HTTPX**. The goal is to
answer upgrade and troubleshooting questions from the documentation that matches
the requested version, with inspectable evidence and explicit abstention.

**Status: day 3 complete, local retrieval comparison.** Pinned ingestion,
version-filtered keyword/vector/hybrid retrieval, cloud-disabled local models,
cited draft answers and abstention are implemented. Keyword retrieval remains
the default after the first development comparison. The API, UI, held-out
evaluation and screenshots remain future milestones.
See [the delivery plan](docs/DELIVERY_PLAN.md).

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
`search` is retrieval-only. Missing keyword matches return `no_matching_evidence`.
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

## Local vector and hybrid retrieval

With the same foreground server running, pull the free Apache-2.0 embedding
model and build its separate SQLite vector index:

```sh
python3 scripts/local_runtime.py pull --embedding
PYTHONPATH=src python3 -m versionlens embed
PYTHONPATH=src python3 -m versionlens search 'Why did the proxies argument stop working after upgrading HTTPX?' --version 0.28.1 --retriever vector
PYTHONPATH=src python3 -m versionlens search 'Why did the proxies argument stop working after upgrading HTTPX?' --version 0.28.1 --retriever hybrid
python3 scripts/compare_retrieval.py
python3 scripts/smoke_retrievers.py
```

Nomic `nomic-embed-text:v1.5` downloads approximately 274 MB and produces
768-dimensional embeddings locally. Full inputs are retained, with document/query
prefixes and no silent truncation. Exact cosine search filters the requested
version before scoring; hybrid uses fixed reciprocal-rank fusion over twenty
candidates per engine. There is no reranker or similarity confidence threshold.

The vector cache binds every chunk and its provenance to the model digest,
dimensions and preprocessing revision. Missing, changed or incomplete caches
fail explicitly; rerun `embed` when those inputs change. Failed builds preserve
the previous index. Both SQLite indexes and all model weights remain ignored.

The [development comparison](reports/day3-retrieval-comparison.json) uses sixteen
answerable questions and four separate qualitative probes. Labels are
AI-authored, source-checked and **not human-reviewed or held out**.

| Retrieval | Known-evidence hit at 5 | Known-evidence MRR at 5 |
| --- | --- | --- |
| Keyword | 13/16 | 0.65625 |
| Vector | 12/16 | 0.71875 |
| Hybrid | 13/16 | 0.653125 |

These scores describe nonexhaustive source anchors, not answer accuracy or
complete relevance judgments. Hybrid did not improve coverage over the simpler
keyword baseline, so keyword stays the default. No reranker was added.
See [methodology, latency and limitations](docs/RETRIEVAL_EVALUATION.md).

`ask --retriever vector` and `ask --retriever hybrid` are explicit experimental
options. Dense search returns neighbors even for unsupported questions. An
[initial smoke run](reports/day3-initial-answer-smoke.json) showed unrelated
answers for the missing-token probe. Generation now requires at least one
keyword match before using either experimental mode; otherwise it abstains
without embedding or generation. This conservative check can reject useful
paraphrases and does **not** prove semantic support when a term matches.
The [final smoke run](reports/day3-answer-smoke.json) retains the remaining
upgrade-generation failure. All answers remain unverified drafts.

**Verified on 22 October:** 132 automated checks pass. Model/API fees were zero;
local memory, disk, electricity and elapsed time are still resources consumed.

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
