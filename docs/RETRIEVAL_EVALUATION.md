# Development retrieval comparison

The checked-in [development questions](../data/evaluation/development-retrieval.json)
compare retrieval engines on the same pinned corpus and unchanged chunking. They
are **not a held-out benchmark**, are not independently human-reviewed, and do
not establish answer accuracy or generalization to real support requests.

## Fixed setup before the first vector comparison

- Twenty questions: sixteen answerable evidence probes, two missing-evidence
  probes, and two wrong-version traps.
- Questions and anchors were AI-authored by inspecting the shipped corpus.
  Every expected anchor was automatically verified to occur in a single chunk
  of the requested snapshot before comparing engines. This verifies existence,
  not human relevance judgments or semantic completeness.
- Some questions revisit earlier development probes. Their IDs are recorded in
  `prior_development_overlap`; all development questions must stay out of the
  later frozen holdout.
- Each request names exactly `0.27.2` or `0.28.1`. BM25 and vector retrieval
  constrain candidates to that snapshot before their final ranking and limit.
- Compare top five results. Hybrid retrieval uses twenty candidates from each
  engine and fixed reciprocal-rank fusion: each occurrence contributes
  `1 / (60 + rank)`, with ranks starting at one. Sum contributions by chunk ID
  and break equal fused scores by chunk ID. Raw BM25 and cosine values are not
  rescaled or mixed; fused scores are not probabilities or answer confidence.
- No reranker, tuned similarity cutoff, learned weighting, or query rewriting
  is introduced for this comparison. These settings are fixed rather than
  chosen after inspecting which configuration wins on these questions.

The JSON records this initial setup with `frozen_before_first_vector_comparison`.
If labels or protocol need a repair, preserve the earlier dataset and report,
explain the correction, and distinguish later runs. A development freeze does
not turn development data into an untouched holdout.

## What the automatic metrics mean

An expected entry specifies an upstream source path, a section-heading substring,
and an exact evidence-text substring. A returned hit matches only when all three
conditions hold in the same chunk of the requested snapshot. Multiple expected
entries are alternative acceptable anchors, not a requirement to retrieve all.

For the sixteen answerable cases, report:

| Measurement | Definition |
| --- | --- |
| Known-evidence hit at five | Fraction with at least one matching anchor in the first five results |
| Known-evidence reciprocal rank at five | Mean of `1 / first_matching_rank`; zero when no anchor appears in the first five results |
| End-to-end retrieval latency | Measured time for the engine call, including a query embedding when required |
| Version violations | Count of returned hits whose source snapshot differs from the request; any violation is a defect |

Anchors are deliberately inspectable but nonexhaustive. Relevant material outside
an anchor can count as an automatic miss; a matching text fragment need not be a
complete answer. Do not rename these metrics precision, recall, semantic answer
correctness, citation support, or a human-reviewed relevance score. Retain
per-question ranks and source links so misses and narrow labels can be inspected.

Latency is a local observation. Record model identity/digest, corpus fingerprint,
configuration, request order and warming conditions where available. Do not infer
deployment throughput or claim a controlled performance improvement from a
single ordered run.

## Qualitative probes stay separate

Missing-evidence and wrong-version cases have empty expected-anchor lists and are
excluded from the answerable aggregate. Dense retrieval normally returns nearest
neighbors even when no document answers a question; nonempty results are not a
failure of an uncalibrated abstention threshold. Record their returned evidence,
version violations and the interpretation boundary separately.

The wrong-version probes ask about releases newer than the selected snapshot.
Returning only older-version candidates verifies isolation; it does not prove
that an answering model will recognize unavailable future evidence. The separate
answering evaluation must measure unsupported claims, release applicability,
abstention and citation entailment. Software tests and retrieval anchors cannot
substitute for those judgments.

## Decisions after the run

Publish the actual result for every engine, including failures and regressions.
Prefer the simpler keyword baseline unless a measured change justifies a different
default for the intended use. An apparent improvement on this small source-derived
development set needs later independent evaluation. Add a free local reranker only
when its measured value justifies its extra latency and complexity; a reranker is
not required to declare this milestone complete.

## Recorded on 22 October 2026

The [final comparison](../reports/day3-retrieval-comparison.json) contains all
sixty engine/question results, source links, model and corpus fingerprints,
implementation checksums and the unchanged development-set checksum.

| Engine | Known-evidence hit at 5 | Known-evidence MRR at 5 |
| --- | --- | --- |
| Keyword | 13/16 (0.8125) | 0.65625 |
| Vector | 12/16 (0.7500) | 0.71875 |
| Hybrid | 13/16 (0.8125) | 0.653125 |

Median end-to-end retrieval latency on the sixteen answerable cases was
0.643 ms for keyword, 183.476 ms for vector and 199.805 ms for hybrid.
Nearest-rank p95 was 0.962, 739.922 and 219.197 ms respectively. The run executes
keyword, vector, then hybrid for each question; model warming and reuse affect
timing. This is not a controlled throughput test or production latency promise.
The API fee was zero for every mode; resource use is not zero.

Keyword remains the default. Vector places some known anchors earlier, but
misses more of them within five results. Hybrid does not improve anchor coverage
over keyword and has slightly lower reciprocal rank. No reranker or post-result
parameter tuning was introduced. These observations do not establish a general
ranking winner from sixteen source-derived, unreviewed questions.

The upgrade development question D01 finds the 0.28.0 removal anchor at rank one
with keyword, while vector and hybrid miss it within five. D02 finds the older
deprecation anchor at rank one in all modes. Wording differs between D01 and
the earlier answer smoke probe; query variation can alter rankings. Neither
case establishes that the answer generator interprets release history correctly.

The [initial retrieval run](../reports/day3-initial-retrieval-comparison.json)
is retained. A later review tightened malformed-development-file validation
(boolean versions, floating protocol values and non-string categories); the
questions, anchors, retrieval methods and parameters were unchanged. The final
run records the repaired implementation hashes rather than rewriting the
earlier timings or results.

The separate [initial answer smoke](../reports/day3-initial-answer-smoke.json)
showed that an unrelated missing-token query could produce cited drafts from
dense neighbors. The [final answer smoke](../reports/day3-answer-smoke.json)
tests a conservative lexical prerequisite for experimental vector/hybrid answer
modes. That prerequisite is not part of this retrieval comparison and is not
a calibrated semantic relevance or abstention classifier. The original failure
is preserved, and the repeated probe is no longer an independent test case.
