# Question review and held-out release

Question candidates are AI-authored drafts until a person checks them against
the versioned sources. A source substring match proves existence, not relevance,
answer completeness or correctness. The review records are human attestations;
this local workflow does not authenticate a reviewer or certify judgment quality.

## Drafts and contamination

Each candidate binds the question, exact snapshot, demo access profile, category,
draft decision, reference/rubric, source-ID/checksum anchors, topic group and
prior development overlap. Paraphrases and version pairs in a topic group stay
in the same split. Known prior probes belong in development. Group assignment
and undeclared semantic overlap also require human review; software can reject
declared overlap and duplicate wording, but cannot prove conceptual novelty.

The current pack contains 100 candidates in 17 topic groups: 40 development
questions in seven groups and 60 candidate-holdout questions in ten groups.
They cover answerable, missing-evidence, wrong-version, permission-denied and
same-version conflicting evidence. Conflicts use separate, prominently labelled
fictional fixtures. Candidate holdout has not been run against retrieval or
answer generation. The corpus is shared; evaluating RAG does not require hiding
its source documents from the retrieval system.

## Human workflow

Read [the questions, draft labels and source excerpts](evaluation/review-pack/QUESTIONS.md).
Check each selected snapshot and source context, access constraints, answerability,
reference answer and abstention/conflict rubric. Reject or request edits when
uncertain. All records in [the template](evaluation/review-pack/review-template.json)
start pending, with reviewer fields blank. Agreeing to review does not approve
any case. Make a separate review copy and preserve its case digests.

Approved or rejected records need a human reviewer name, reviewer_type `human`,
a timezone-aware ISO reviewed_at timestamp, and notes. All 60 candidate-holdout
questions need approval before release; development records may remain pending.
A label, question, split, policy or corpus change invalidates earlier approvals
and requires review of the new exact version. Never fill human approvals through
an automated label generator. Unit-test approvals are fictional temporary data.

## Export, freeze and run

```sh
python3 scripts/review_questions.py export --output-dir reports/local/my-review
python3 scripts/review_questions.py freeze --reviews path/to/completed-review.json --output data/evaluation/holdout.lock.json
python3 scripts/evaluate_support.py run --split holdout --reviews path/to/completed-review.json --lock data/evaluation/holdout.lock.json --generate --output reports/local/reviewed-holdout.json
```

Freezing creates a new lock exclusively; previous releases are preserved. The
lock binds exact raw dataset/review digests, the full corpus fingerprint, case
membership and each complete case digest. Execution revalidates these inputs
before contacting a model and after the run. Pending, rejected, stale, duplicate
or missing records cannot release a holdout. The current repository contains
no real completed reviews and no released holdout lock.

Generated claims require a separate human answer review. Mechanical citation
identity/quotation validity is not semantic entailment, release applicability
or answer correctness. Unsupported-answer and semantic correctness rates stay
unavailable until the corresponding judgments are completed.
