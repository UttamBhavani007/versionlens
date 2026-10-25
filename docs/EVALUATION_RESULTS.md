# Development evaluation observations — 25 October 2026

**These are provisional development observations, not a human-reviewed held-out benchmark.**

The [raw run](../reports/day6-development-evaluation.json) records 40 questions
in seven topic groups across three methods: 120 trials. All 60 candidate
holdout questions in ten separate groups remain unrun. The shared isolated
corpus contains 38 sources and 650 chunks, including four clearly labelled
fictional conflict documents. The ordinary application/demo indexes are unchanged.

Candidate dataset SHA-256: `09a64d3923d7817228fbf99b568caf944dfcf1ddcfa8991582efc8ee0640fbde`.
Corpus fingerprint: `62d9c3a98fe05e3f805bbd6e286f5358d3305a7977aa6f5563c73cfd4817aac2`.

## Retrieval coverage and operational outcomes

Only 19 draft-answerable positive-anchor cases per method enter hit/MRR
aggregates. Anchors are source-checked, nonexhaustive and not human relevance
judgments. Retrieval-stage errors count as misses in the main aggregate;
successful-call-only coverage and all errors are also recorded separately.
An answer-stage failure does not erase a successful retrieval observation.

| Method | Known-anchor hit at 5 | MRR at 5 | Retrieval median ms, all 40 | Answer-pipeline median ms | Answered / abstained |
| --- | --- | --- | --- | --- | --- |
| keyword | 17/19 | 0.7228 | 0.863 | 2281.863 | 16 / 24 |
| vector | 17/19 | 0.7895 | 489.227 | 3456.695 | 17 / 23 |
| hybrid | 18/19 | 0.7675 | 512.864 | 3566.046 | 18 / 22 |

No runtime errors, wrong-version hits or access-violating hits were observed.
Answer-pipeline latency includes its own retrieval, context selection, local
generation and final source checks; it is not pure inference time. The earlier
retrieval measurement is a separate call. Fixed method order, repeated prompts,
model loading/warming/swapping and this single local run limit comparisons.
No production latency or throughput guarantee is inferred. Token usage and zero
model/API fees are reported separately in JSON; local resource use is not zero.

Hybrid found one extra known anchor in this small draft-labelled development
sample. That does not establish a general winner. Keyword remains the default;
no reranker, prompt change, chunk change or threshold tuning followed the run.

## Mechanical citations and unresolved answer behavior

All 55 returned citations matched canonical source identity, checksum, version,
access and exact quote-menu text: 17 keyword, 19 vector and 19 hybrid. The
independent audit also checks output contracts. It is not a semantic entailment
judge and does not by itself reconstruct every evidence-ID/context mapping.
These counts must not be presented as semantic citation correctness or answer
accuracy. An opposite claim can still carry a mechanically valid quotation;
a regression test preserves that limitation.

Every method retrieved both sources for all five same-version synthetic
conflict questions. Each method nevertheless returned four drafts and withheld
one as invalid generation: 12 of 15 trials answered despite draft abstention
labels. The withheld case does not demonstrate conflict-based abstention.
This indicates a conflict-handling limitation even when retrieval covers both
sources. The full outputs and source context are retained for human inspection.

There were also drafts on some missing-evidence/wrong-version cases. The JSON
lists every case and category. Their draft labels and generated claims require
review; these counts are not a measured unsupported-answer rate.

## Human review remains pending

The owner agreed to review the [100 question candidates](evaluation/review-pack/QUESTIONS.md).
All 100 question review records are still pending. No real lock has been
released and no holdout has run. The [actual gate checks](../reports/day6-review-gates.json)
confirm that pending question reviews block freezing/execution.

The [answer review pack](evaluation/answer-review-pack/ANSWERS.md) contains the
51 answered case/method trials and 55 generated claims, all pending judgment.
Claim support and factual/release correctness are separate booleans. Scoring
requires complete, digest-matching human attestations; pending claims cannot
produce semantic scores. Unsupported-answer rates use answered trials only;
abstentions and operational errors remain separate. Citation-level semantic
support still needs separate citation judgments.

Thus semantic citation correctness and unsupported-answer rate are currently
`null`, not zero or perfect. Development outputs remain development after
review. See [the review protocol](QUESTION_REVIEW_PROTOCOL.md).

## Reproduce locally

Start the existing cloud-disabled local model server, then:

```sh
python3 scripts/evaluate_support.py prepare
python3 scripts/evaluate_support.py run --generate --output reports/local/my-development-run.json
python3 scripts/review_answers.py --report reports/local/my-development-run.json export --output-dir reports/local/my-answer-review
```

Both evaluation SQLite files are separate ignored artifacts. No model or
database service, API key, paid judge, external inference or automatic billing
is used. Existing reports and reviews are preserved through exclusive outputs.
