# VersionLens

A local, version-aware technical support service for **HTTPX**. The goal is to
answer upgrade and troubleshooting questions from the documentation that matches
the requested version, with inspectable evidence and explicit abstention.

**Status: day 1 complete, retrieval foundation.** Generated answers, semantic retrieval,
the API, UI, evaluation report, and screenshots are future milestones. This is
not yet a finished RAG application. See [the delivery plan](docs/DELIVERY_PLAN.md).

## Zero paid services

- No OpenAI API, paid inference, hosted vector database, cloud account, or trial.
- Python and SQLite run on your existing computer.
- Later inference uses a downloaded open model through local Ollama with cloud
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
generation is not implemented. Missing matches return `no_matching_evidence`.
Unsupported versions and malformed requests fail explicitly.

**Known baseline limitation:** BM25 can rank an old release-history entry above
a more recent applicable change, even within the correct snapshot. Selecting
the correct snapshot is necessary but does not prove the retrieved passage
answers the question. Release headings are preserved for the later answering
and evaluation layers. Ranking scores are not confidence probabilities.

The 26 automated checks cover checksum tampering, unsafe paths and symlinks,
exact source line references, failed-update rollback, repeat ingestion,
wrong-version isolation, query punctuation, and CLI behavior. These are software
checks, not a held-out answer-quality benchmark.

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
