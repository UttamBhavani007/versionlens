# Seven-day delivery plan: 25 meaningful commits

Start: 2026-10-20. Each commit records completed work on its actual date. This
plan is a target, not evidence that future work has already happened. Do not
backdate commits, split empty changes to meet a quota, or publish results before
verification. If a milestone needs longer, record that honestly and continue.

| Day | Target date | Commits | Scope and acceptance evidence |
| --- | --- | --- | --- |
| 1 | 2026-10-20 | 1–4 | Scope and zero-cost policy; metadata and strict version contracts; pinned ingestion and SQLite storage; keyword retrieval and CLI, with isolation tests |
| 2 | 2026-10-21 | 5–8 | Free local runtime configuration; loopback-only model adapter; grounded answer pipeline and evidence abstention; local generation smoke run and failure tests |
| 3 | 2026-10-22 | 9–12 | Local embeddings; vector retrieval; hybrid ranking; development-set retrieval comparison, with reranking adopted only if evidence supports it |
| 4 | 2026-10-23 | 13–16 | API contracts and validation; web UI; source/version inspection; API/UI integration and accessibility checks |
| 5 | 2026-10-24 | 17–19 | Incremental snapshot updates and deletion; labelled synthetic documents and permission filtering; version/permission change demonstration and security tests |
| 6 | 2026-10-25 | 20–22 | Candidate 80–120-question evaluation set and review protocol; evaluation runner and citation audit; freeze reviewed holdout and publish actual results with limitations |
| 7 | 2026-10-26 | 23–25 | Reproducible local deployment and smoke checks; actual screenshots and interview demo; final README, release notes, clean setup verification and GitHub release |

## Actual progress

Day 4 started on 23 October and finished on 24 October after an interruption.
The remaining commits use their actual 24 October dates. Day 5 was not started
on that date; the table above retains the original targets. The authorized
schedule still ends on 26 October, with no unapproved deadline extension.

## Human input and external requirements

- GitHub publication needs an authenticated GitHub connection. Do not invent
  a repository URL, username, or upload status.
- Commit authorship should use the owner's actual Git identity, never a guessed
  noreply address. Verify attribution after publication.
- Human review of the evaluation set requires the owner or another reviewer;
  generated labels are drafts until a person checks them.
- Local model downloads are free but need disk space and network access. Model
  size should fit available RAM; quality and latency need actual measurement.
- Screenshots must show the running application, never a fabricated UI.
- An always-on public LLM endpoint is not promised. Local deployment meets the
  zero-paid-services constraint; a static public walkthrough may complement it.

## Working rhythm

Finish the work and verification for one milestone, make its focused commit,
then proceed. Do not generate 25 commits today and trickle-push them as if the
work occurred on different days. A daily continuation may work through the next
day's unfinished milestones; never advance a date or mark a test passed just
to hit the planned count.
