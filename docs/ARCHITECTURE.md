# Architecture and boundaries

## Implemented through day 6 engineering

```mermaid
flowchart LR
    A[HTTPX Git commit snapshots] --> B[Checksum and schema validation]
    B --> C[Markdown chunks with line references]
    C --> D[Local SQLite index]
    L[Local browser or CLI] --> E[Question and exact version]
    E --> P[Exact version and trusted demo access profile]
    P --> F[Keyword, cosine or RRF hybrid]
    D --> F
    D --> H[Local Nomic embeddings]
    H --> I[Digest-bound SQLite vector sidecar]
    I --> F
    F --> G[Ranked evidence with source links]
    G --> J[Bounded quote menus and local draft generation]
    J --> K[Validated citation identity and quotes, or abstention]
    G --> M[Version-scoped source inspector]
    K --> N[Plain-text draft with unverified-support warning]
```

The application uses Python's standard library, SQLite and project-local Ollama.
A loopback-only API and bundled browser workspace expose the same validated
application operations. Transactional per-snapshot updates and clearly labelled
synthetic access-demo documents are implemented. Reranking is deferred because
the first development comparison does
not justify additional complexity.

The vector sidecar records the complete corpus fingerprint, embedding model
digest, dimensions and preprocessing revision. Publication occurs only after
every full-input embedding validates; a final source snapshot check rejects
concurrent changes. Queries reject missing/stale/corrupt/incomplete caches and
score only the requested snapshot. Cosine search scans this small corpus
directly; no approximate index or hosted vector database is needed.

Hybrid uses fixed RRF with constant 60 and twenty candidates per engine. It
checks source consistency across both retrieval calls and uses chunk IDs to
break ties. A broken vector index is an error, never an implicit keyword fallback.
Raw BM25 and cosine scores are not combined as if they shared a scale.

Keyword retrieval remains the default. Experimental vector/hybrid answer modes
require a keyword match before retrieval/generation, because dense neighbors
alone do not establish answerability. This conservative veto can miss relevant
semantic paraphrases and does not validate entailment. Search-only comparisons
do not apply this generation gate.

## Local API and browser boundary

The standard-library HTTP server binds only to literal `127.0.0.1`. An explicit
asset allowlist, exact Host/Origin checks, strict bounded JSON, eight handler
slots, read timeouts and a single POST operation limit protect this workstation
demo. It is not an authenticated public server. See [the API contract](API.md).

Source inspection resolves a validated chunk ID within the selected snapshot;
clients cannot supply filesystem paths. The browser builds nodes with plain
text, validates immutable citation URLs and invalidates results when inputs
change. Aborted or late responses cannot replace evidence for a newer question
or version. Browser cancellation does not stop backend model work.

The interface calls only its local same-origin API. No external fonts, libraries,
analytics or cloud model calls are loaded. Opening a source link is an explicit
user navigation to the pinned upstream GitHub document.

## Version policy

- A request selects an explicit supported snapshot: `0.27.2` or `0.28.1`.
- Missing, ambiguous, and unsupported versions are errors; never silently use
  the newest version.
- All candidates are filtered to the requested version before ranking.
- A changelog is a historical document available in a given snapshot; a release
  mentioned inside it is not the same thing as the snapshot version. Preserve
  the section heading so that generation can distinguish the two.
- Cross-version comparisons will be explicit requests with separate retrieval
  for each version, not an unfiltered search.
- Updates replace a complete snapshot transactionally; incomplete downloads do
  not partially overwrite an existing index.

## Evidence and access

Each chunk carries source identity, snapshot version, checksum, line span and
provenance kind. Upstream sources retain immutable HTTPX Git references.
Synthetic sources use distinct IDs and digest revisions with access-checked
local citations; they cannot impersonate upstream GitHub documentation.

Validated policy is stored consistently in source metadata and SQL columns.
A trusted startup profile constrains keyword candidates before LIMIT, cosine
candidates before scoring, both hybrid pools, catalog counts and source lookup.
Model context independently rejects inaccessible evidence. Selected evidence is
rechecked before and after generation; a concurrent change suppresses output.
This is a synthetic local permission simulation, not production authentication.

`sync` reconciles one nonempty complete desired snapshot and retains unchanged
rows. Explicit deletion can remove a whole snapshot. Both preserve other
versions and roll back failed writes, including FTS changes. Schema-1 migration
occurs only during explicit full ingestion. All source/policy changes invalidate
the vector sidecar; incremental embedding reuse is not implemented.
See [update and access contracts](PERMISSIONS_AND_UPDATES.md).

## Evaluation boundaries

Retrieval relevance is separate from answer faithfulness and citation support.
A valid source ID or quoted span alone does not establish that every generated
claim is supported. Do not label automatic checks as human review. Holdout
questions must not be used to tune chunk size, thresholds, or prompts.


## Evaluation release boundary

A separate ignored evaluation index combines the normal corpus with labelled
conflict fixtures. Draft question anchors bind exact source identity/checksum
and topic groups separate development from candidate holdout. A real release
lock must match complete human question-review attestations and exact dataset,
corpus and case digests before holdout execution; pending reviews are rejected.

Development observations keep retrieval errors, answer decisions, literal
citation checks, latency and local usage separate. Mechanical checks do not
establish semantic correctness. Human claim review is a later digest-bound
step with separate support/correctness judgments. All genuine reviews and
held-out results currently remain pending; see [the evaluation observations](EVALUATION_RESULTS.md).
