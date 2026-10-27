# VersionLens 0.1.0 — local prototype

This prerelease provides a reproducible local HTTPX support workspace, a Python
API/CLI, a browser UI and inspectable evaluation tooling. Deploy from a source
checkout or GitHub source archive, including `data/corpus/` and manifests. A
self-contained wheel, hosted endpoint and production authentication are not
part of this release.

## Included behavior

- Two pinned historical HTTPX snapshots, 32 upstream sources and 644 chunks,
  with checksum-verified ingestion and immutable line-level provenance.
- Exact-version keyword, local vector and fixed hybrid retrieval; keyword stays
  the default. Local generation returns mechanically validated cited drafts or
  abstention, with no remote model fallback.
- A loopback-only bounded API and responsive source-inspection interface.
- Transactional snapshot updates/deletion and opt-in fictional permission
  demonstrations. Access is selected by the local operator, not by requests.
- A dependency-free Python source launcher, read-only readiness checks and an
  isolated source-deployment verifier. Model provisioning is a separate,
  explicit optional operation; the pinned installer supports Apple Silicon macOS.

## Release verification: 27 October 2026

- [Fresh source-deployment report](../reports/day7-clean-setup.json): **299
  software tests and 14 real HTTP checks passed**, from archive commit
  `94b796b1af9ecdcdfd7020118540fda050569ae4`. The isolated Python 3.13.7
  environment had no pip or third-party runtime packages. All 32 source
  checksums verified and preparation produced 644 chunks.
- [Browser report](../reports/day7-browser-check.json): **12 checks passed**,
  including real evidence, source inspection, version changes, missing-evidence
  abstention and mobile layout. Four negative/race checks use labelled fixtures.
  Three fresh screenshots show actual local responses.
- No external/model socket attempts were observed by the clean verifier's
  Python guard. Model provisioning, positive dense retrieval and generation
  were not repeated during release verification; earlier measured runs remain
  available with their dates. No candidate holdout was executed.
- Owned verification servers were stopped. The final documentation/report commit
  does not change the verified application or test code.

## Evaluation status

The 25 October development run contains 120 trials on 40 AI-authored development
questions across three methods. Known-anchor hits at five were 17/19 keyword,
17/19 vector and 18/19 hybrid. All 55 returned citations passed mechanical
source/quote checks. These figures do not establish answer correctness.

**Known failure:** 12/15 synthetic-conflict trials returned drafts despite draft
abstention labels, even when both conflicting sources were retrieved. Some real
HTTPX upgrade probes remain withheld as `invalid_generation`. The experimental
keyword gate before vector/hybrid generation does not establish entailment.
No reranker or post-run prompt/threshold tuning was added.

All 100 question-label reviews and all 51 answer-trial reviews remain pending.
The 60 candidate holdout questions have not been executed; no actual holdout lock
or reviewed benchmark exists. Semantic citation correctness and unsupported-answer
rate remain unavailable pending genuine human judgments. See
[EVALUATION_RESULTS.md](EVALUATION_RESULTS.md) and the two pending review packs.

## Operational boundaries

All services run locally on existing hardware with no paid APIs, cloud model
fallback, hosted database, subscription, trial or automatic billing. No model
weights, credentials or local database builds are included in Git. Permission
fixtures are public fictional examples, not confidential documents. Do not use
this prototype as production multi-user authentication or public hosting.

Software/setup checks, actual browser captures and earlier local model runs
are distinct evidence; none substitutes for human semantic evaluation.
The [deployment guide](LOCAL_DEPLOYMENT.md), [actual screenshots](SCREENSHOTS.md)
and [interview walkthrough](INTERVIEW_DEMO.md) describe reproduction and limits.

## Delivery dates

The first 22 commits were made on their actual development dates, 20–25 October
2026. Final packaging and verification continued on **27 October 2026**, after
the owner explicitly allowed completion past the original 26 October cutoff.
Final commits use their actual dates. The recurring schedule was removed; this
extension does not establish a new recurring automation.
