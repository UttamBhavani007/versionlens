# Interview walkthrough

This is a local prototype demonstration. Run source-checkout setup first as
shown in [LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md). Initial model downloads
are outside the walkthrough; the suggested sequence assumes weights are cached.
No hosted endpoint or production authentication is claimed.

## 1. Inspect versioned evidence

Start the public workspace with `python3 scripts/run_local.py` and open the
literal address shown at startup. This assumes the default public corpus. If a
previous run prepared the synthetic corpus, keep `--include-synthetic`, or
explicitly restore the public corpus with `--prepare --rebuild` first.
Search for the default timeout, switch
between HTTPX 0.27.2 and 0.28.1, and inspect a source. Show the exact snapshot,
immutable upstream commit, source SHA-256 and original line range. Explain that
ranking scores are not confidence and snapshot identity alone is not relevance.

## 2. Show a cited local draft and abstention

Start the separately configured cloud-disabled model server using
`python3 scripts/local_runtime.py serve`. Ask the default-timeout question and
inspect its literal quotation. A real quotation does not verify a claim's
meaning. Ask `quantumgiraffeunsupported`: the service abstains without a model
call. Try the upgrade example and show the retained invalid-generation behavior
when it occurs; [recorded runs](EVALUATION_RESULTS.md) preserve the limitation.
Do not promise the small model will produce an identical draft on every run.

## 3. Show simulated access and version changes

Stop the UI, explicitly prepare the fictional demonstration corpus, then start
two foreground interfaces in separate terminals:

```sh
python3 scripts/run_local.py --prepare --include-synthetic --rebuild
python3 scripts/run_local.py --include-synthetic
```

```sh
python3 scripts/run_local.py --include-synthetic --demo-profile support --port 8766
```

Search `orchidrelay` on both. Public access has no matching evidence; support
access shows a clearly labelled fictional runbook. Switch the support version:
the synthetic budget is two attempts in 0.27.2 and three in 0.28.1. Inspect the
content revision, which is a SHA-256 rather than an upstream Git commit.
Profiles are chosen by the local server operator; requests cannot grant roles.
These are public fictional fixtures, not real confidential company documents.

For a reproducible content-update/grant/revocation/deletion sequence, run:

```sh
python3 scripts/demo_changes.py --generate --vectors
```

This uses a separate scratch index and leaves checked-in source documents
unchanged. It demonstrates a newer synthetic revision of four attempts,
obsolete source-ID denial, stale-vector rejection, access grant/revocation and
isolated snapshot deletion. [The actual earlier run](../reports/day5-change-demo.json)
retains every observed output. It is a development demonstration, not a benchmark.

## 4. Explain the evaluation honestly

Show [development results](EVALUATION_RESULTS.md): 40 questions in seven topic
groups across three methods. Known-anchor hits were 17/19, 17/19 and 18/19.
All 55 returned citations passed source/quote checks, yet 12/15 synthetic
conflict trials returned drafts despite draft abstention labels. Retrieval
coverage did not resolve the model's conflict-handling weakness.

Show [the question review protocol](QUESTION_REVIEW_PROTOCOL.md). The proposed
60-question holdout has not run; question labels and claim judgments are still
pending human review. Semantic correctness and unsupported-answer rates are
unavailable. Explain why passing software tests, correct source IDs, abstention
status counts and human answer judgments are different evidence.

Stop both UI terminals and the model terminal with Ctrl-C after the demo.
