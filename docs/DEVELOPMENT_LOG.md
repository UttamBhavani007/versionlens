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
