# VersionLens

A local, version-aware technical support service for **HTTPX**. The goal is to
answer upgrade and troubleshooting questions from the documentation that matches
the requested version, with inspectable evidence and explicit abstention.

**Status: day 1, retrieval foundation.** Generated answers, semantic retrieval,
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
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Repository setup and commands are extended with each implemented milestone.
An editable installation is optional; running with `PYTHONPATH=src` avoids
installing build tools. No service account is required.

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
