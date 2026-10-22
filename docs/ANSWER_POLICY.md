# Local draft answers and their limits

Day 2 adds local generation to the keyword baseline. The model is a small local
Qwen3 model, not a paid API. The service does not yet have a measured answer
quality score or a human-reviewed holdout.

Day 3 adds explicit vector/hybrid retrieval experiments. These modes require a
keyword match in the requested snapshot before they can supply generation
context. If no keyword match exists, the answer abstains with
`no_lexical_support_for_experimental_retrieval` without embedding or generation.
The response exposes `lexical_support_gate_applied` and `retrieval_executed`.
Search-only vector/hybrid commands still return their neighbors for inspection.

This conservative prerequisite was added after the retained day-3 initial smoke
run answered an unrelated missing-token question from dense neighbors. It can
abstain on useful paraphrases with no shared words. A keyword match is only a
necessary condition here, never proof that the passage answers the question;
unsupported questions with shared terms remain an evaluation risk.

## What the pipeline checks

1. Validate an explicit HTTPX version and retrieve only that snapshot.
2. Select at most four excerpts with bounded, labelled quotation menus. Quotes
   are chunk paragraphs or list items, copied verbatim from the source. Visible
   fenced code and oversized prose paragraphs are skipped. The source chunker
   can begin inside an original paragraph or code block; quote selection does
   not restore that surrounding context or prove original paragraph completeness.
   Count the
   question, system instructions and JSON grammar as part of a conservative
   UTF-8 input-byte budget, reserving output and template headroom. This is a
   conservative heuristic, not a tokenizer measurement. Oversized quote menus
   are skipped rather than silently truncated.
3. If no excerpt fits or no match exists, abstain without calling the model.
4. Send a JSON evidence envelope to local Ollama with cloud disabled. Include
   release headings; a snapshot's cumulative changelog contains historical
   statements that may no longer apply to the requested version.
5. Require a bounded JSON response: one decision and at most two short cited
   claims, or an explicit evidence-related abstention with no claims. The model
   selects an `(evidence_id, quote_id)` pair from the supplied menu. It cannot
   supply quote text or URLs; the server resolves the exact original quotation.
   Reject duplicate keys, extra fields, unknown evidence/quote IDs and absent
   citations. Quote IDs are local to each excerpt and cannot cross-reference
   another excerpt's quotation.
   Claim text must be plain text: model-supplied links, citation markers, HTML,
   control characters and invalid Unicode are rejected.
   Square brackets are reserved for server-added citations, so technical
   examples containing square brackets in claim text are also conservatively
   rejected at this stage; source quotations retain their original text.
6. Reconstruct every citation URL, version, commit, checksum and line range
   from the selected server-owned excerpt, never from model-supplied metadata.
7. Return no partial answer on validation failure. Treat runtime errors as
   operational errors separately from genuine missing-evidence abstention.

No model-supplied code or URL is executed or fetched. The prompt explicitly
treats questions and retrieved documents as untrusted data. This prompt is a
mitigation; it is not proof of immunity to prompt injection.

## What these checks do not prove

A real quote can be paired with a wrong paraphrase, and a correctly linked old
release note may not describe current behavior. Mechanical citation checks do
not verify semantic entailment, relevance, completeness, or release applicability.
Every answer therefore exposes `semantic_support_verified: false` and remains
a cited draft. A test deliberately records the opposite-claim-with-real-quote
case to keep this limitation visible.

The later evaluation must assess citation support and unsupported claims
separately from source identity. Do not report passing software tests as answer
accuracy, retrieval recall, or a no-hallucination guarantee. A local smoke run is
development evidence, not a held-out benchmark.

## Result categories

| Result | Meaning |
| --- | --- |
| `answered` | A draft passed structure, citation identity and literal quote checks |
| `abstained / no_matching_evidence` | Retrieval found no matching excerpt; no model call |
| `abstained / no_usable_quote_spans` | Matching excerpts contain no bounded quotation; no model call |
| `abstained / context_budget_exceeded` | Available excerpts did not fit the conservative input budget; no model call |
| `abstained / insufficient_evidence` | Model declined on the supplied excerpts |
| `abstained / conflicting_evidence` | Model identified unresolved conflicting evidence |
| `abstained / unrelated_evidence` | Model judged the retrieved excerpts irrelevant |
| `abstained / invalid_generation` | Model output failed validation; draft suppressed |
| `error / local_model_error` | Local runtime unavailable, malformed, truncated or otherwise unusable |

Record whether a model call occurred, prompt/output token counts when returned
by the runtime, model duration and end-to-end latency. Local API fees are zero;
hardware, energy and development time are not measured by that field.
