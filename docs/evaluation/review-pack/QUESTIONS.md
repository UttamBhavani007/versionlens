# Draft question review pack

**All labels are AI-authored drafts. No question is approved or human-reviewed.**

Dataset SHA-256: `09a64d3923d7817228fbf99b568caf944dfcf1ddcfa8991582efc8ee0640fbde`
Corpus fingerprint: `62d9c3a98fe05e3f805bbd6e286f5358d3305a7977aa6f5563c73cfd4817aac2`

Development and candidate holdout are split by topic group. Previously used
intents remain in development. Reading source anchors is not a retrieval or
generation trial. Candidate-holdout questions must remain unrun until review.

For every question, check version, profile, answerability, exact source context,
reference answer and the abstention/conflict rubric. Approve only after checking
the original source. Reject or request changes when uncertain. Source excerpts
below are nonexhaustive anchors, not complete relevance judgments.

Copy `review-template.json` to your own review file. Fill status, reviewer_type
(human), reviewer, timezone-aware reviewed_at and notes. Preserve case digests.
All 60 candidate-holdout records need approval before a lock can be released.
The tool checks attestations and content digests; it cannot verify identity.
Claim entailment/unsupported answers need a separate later review of outputs.

Upstream excerpts retain the HTTPX BSD attribution in THIRD_PARTY_NOTICES.md;
synthetic material is fictional MIT-licensed project data.

## C001 — development

Group: `seen-timeout-default` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What is the documented default network-inactivity timeout?

**Draft reference/rubric:** Five seconds of network inactivity; do not reinterpret this as a guaranteed whole-request duration.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D04, D09, D10

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Timeouts · lines 448–468
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L448-L468
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Timeouts
>
> HTTPX defaults to including reasonable timeouts for all network operations,
> meaning that if a connection is not properly established then it should always
> raise an error rather than hanging indefinitely.
>
> The default timeout for network inactivity is five seconds. You can modify the
> value to be more or less strict:
>
> ```pycon
> >>> httpx.get('https://github.com/', timeout=0.001)
> ```
>
> You can also disable the timeout behavior completely...
>
> ```pycon
> >>> httpx.get('https://github.com/', timeout=None)
> ```
>
> For advanced timeout management, see [Timeout fine-tuning](advanced/timeouts.md#fine-tuning-the-configuration).

## C002 — development

Group: `seen-timeout-default` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How long does HTTPX allow network inactivity before its default timeout?

**Draft reference/rubric:** Five seconds of network inactivity; do not reinterpret this as a guaranteed whole-request duration.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D04, D09, D10

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Timeouts · lines 448–468
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L448-L468
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Timeouts
>
> HTTPX defaults to including reasonable timeouts for all network operations,
> meaning that if a connection is not properly established then it should always
> raise an error rather than hanging indefinitely.
>
> The default timeout for network inactivity is five seconds. You can modify the
> value to be more or less strict:
>
> ```pycon
> >>> httpx.get('https://github.com/', timeout=0.001)
> ```
>
> You can also disable the timeout behavior completely...
>
> ```pycon
> >>> httpx.get('https://github.com/', timeout=None)
> ```
>
> For advanced timeout management, see [Timeout fine-tuning](advanced/timeouts.md#fine-tuning-the-configuration).

## C003 — development

Group: `seen-timeout-default` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Does the five-second default describe network inactivity or the entire download duration?

**Draft reference/rubric:** Five seconds of network inactivity; do not reinterpret this as a guaranteed whole-request duration.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D04, D09, D10

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Timeouts · lines 448–468
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L448-L468
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Timeouts
>
> HTTPX defaults to including reasonable timeouts for all network operations,
> meaning that if a connection is not properly established then it should always
> raise an error rather than hanging indefinitely.
>
> The default timeout for network inactivity is five seconds. You can modify the
> value to be more or less strict:
>
> ```pycon
> >>> httpx.get('https://github.com/', timeout=0.001)
> ```
>
> You can also disable the timeout behavior completely...
>
> ```pycon
> >>> httpx.get('https://github.com/', timeout=None)
> ```
>
> For advanced timeout management, see [Timeout fine-tuning](advanced/timeouts.md#fine-tuning-the-configuration).

## C004 — development

Group: `seen-timeout-default` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which default timeout is documented when no timeout option is supplied?

**Draft reference/rubric:** Five seconds of network inactivity; do not reinterpret this as a guaranteed whole-request duration.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D04, D09, D10

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Timeouts · lines 448–468
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L448-L468
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Timeouts
>
> HTTPX defaults to including reasonable timeouts for all network operations,
> meaning that if a connection is not properly established then it should always
> raise an error rather than hanging indefinitely.
>
> The default timeout for network inactivity is five seconds. You can modify the
> value to be more or less strict:
>
> ```pycon
> >>> httpx.get('https://github.com/', timeout=0.001)
> ```
>
> You can also disable the timeout behavior completely...
>
> ```pycon
> >>> httpx.get('https://github.com/', timeout=None)
> ```
>
> For advanced timeout management, see [Timeout fine-tuning](advanced/timeouts.md#fine-tuning-the-configuration).

## C005 — development

Group: `seen-timeout-default` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What timeout value should I expect from the quickstart defaults?

**Draft reference/rubric:** Five seconds of network inactivity; do not reinterpret this as a guaranteed whole-request duration.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D04, D09, D10

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Timeouts · lines 448–468
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L448-L468
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Timeouts
>
> HTTPX defaults to including reasonable timeouts for all network operations,
> meaning that if a connection is not properly established then it should always
> raise an error rather than hanging indefinitely.
>
> The default timeout for network inactivity is five seconds. You can modify the
> value to be more or less strict:
>
> ```pycon
> >>> httpx.get('https://github.com/', timeout=0.001)
> ```
>
> You can also disable the timeout behavior completely...
>
> ```pycon
> >>> httpx.get('https://github.com/', timeout=None)
> ```
>
> For advanced timeout management, see [Timeout fine-tuning](advanced/timeouts.md#fine-tuning-the-configuration).

## C006 — development

Group: `seen-proxy-migration` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Is proxies deprecated in this snapshot, and does it still work?

**Draft reference/rubric:** The proxies argument is deprecated but remains usable in this snapshot; the later removal must not be imported.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D01, D02

**Source:** `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Section: Changelog > 0.26.0 (20th December, 2023) > Deprecated · lines 41–44
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L41-L44
Local source file: [data/corpus/httpx/0.27.2/CHANGELOG.md](../../../data/corpus/httpx/0.27.2/CHANGELOG.md)

> ### Deprecated
>
> * The `proxies` argument is now deprecated. It will still continue to work, but it will be removed in the future. (#2879)

## C007 — development

Group: `seen-proxy-migration` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What replacement for the deprecated proxies argument is mentioned in the changelog?

**Draft reference/rubric:** Use proxy for the simple case or mounts for more complex configurations, as described by the pinned changelog.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D01, D02

**Source:** `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Section: Changelog > 0.26.0 (20th December, 2023) > Added · lines 37–40
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L37-L40
Local source file: [data/corpus/httpx/0.27.2/CHANGELOG.md](../../../data/corpus/httpx/0.27.2/CHANGELOG.md)

> ### Added
>
> * The `proxy` argument was added. You should use the `proxy` argument instead of the deprecated `proxies`, or use `mounts=` for more complex configurations. (#2879)

## C008 — development

Group: `seen-proxy-migration` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Was proxies already removed at the time of this selected version?

**Draft reference/rubric:** No removal is established by this snapshot; its changelog describes deprecation and continued operation.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D01, D02

**Source:** `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Section: Changelog > 0.26.0 (20th December, 2023) > Deprecated · lines 41–44
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L41-L44
Local source file: [data/corpus/httpx/0.27.2/CHANGELOG.md](../../../data/corpus/httpx/0.27.2/CHANGELOG.md)

> ### Deprecated
>
> * The `proxies` argument is now deprecated. It will still continue to work, but it will be removed in the future. (#2879)

## C009 — development

Group: `seen-proxy-migration` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which release entry documents removal of the deprecated proxies argument?

**Draft reference/rubric:** The 0.28.0 entry records removal; 0.28.1 is the selected snapshot, not the removal release.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D01, D02

**Source:** `httpx:0.28.1:CHANGELOG.md` · SHA-256 `2cd04b965b20eff7a4d3b30cc020c63b125da9f731874513bad2e59ca9743258`
Section: Changelog > 0.28.0 (28th November, 2024) · lines 11–36
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/CHANGELOG.md?plain=1#L11-L36
Local source file: [data/corpus/httpx/0.28.1/CHANGELOG.md](../../../data/corpus/httpx/0.28.1/CHANGELOG.md)

> ## 0.28.0 (28th November, 2024)
>
> The 0.28 release includes a limited set of deprecations.
>
> **Deprecations**:
>
> We are working towards a simplified SSL configuration API.
>
> *For users of the standard `verify=True` or `verify=False` cases, or `verify=<ssl_context>` case this should require no changes. The following cases have been deprecated...*
>
> * The `verify` argument as a string argument is now deprecated and will raise warnings.
> * The `cert` argument is now deprecated and will raise warnings.
>
> Our revised [SSL documentation](docs/advanced/ssl.md) covers how to implement the same behaviour with a more constrained API.
>
> **The following changes are also included**:
>
> * The deprecated `proxies` argument has now been removed.
> * The deprecated `app` argument has now been removed.
> * JSON request bodies use a compact representation. (#3363)
> * Review URL percent escape sets, based on WHATWG spec. (#3371, #3373)
> * Ensure `certifi` and `httpcore` are only imported if required. (#3377)
> * Treat `socks5h` as a valid proxy scheme. (#3178)
> * Cleanup `Request()` method signature in line with `client.request()` and `httpx.request()`. (#3378)
> * Bugfix: When passing `params={}`, always strictly update rather than merge with an existing querystring. (#3364)

## C010 — development

Group: `seen-proxy-migration` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Why does an old proxies keyword no longer match the newer HTTPX API?

**Draft reference/rubric:** The deprecated proxies argument was removed in 0.28.0; cite that applicable release entry.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D01, D02

**Source:** `httpx:0.28.1:CHANGELOG.md` · SHA-256 `2cd04b965b20eff7a4d3b30cc020c63b125da9f731874513bad2e59ca9743258`
Section: Changelog > 0.28.0 (28th November, 2024) · lines 11–36
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/CHANGELOG.md?plain=1#L11-L36
Local source file: [data/corpus/httpx/0.28.1/CHANGELOG.md](../../../data/corpus/httpx/0.28.1/CHANGELOG.md)

> ## 0.28.0 (28th November, 2024)
>
> The 0.28 release includes a limited set of deprecations.
>
> **Deprecations**:
>
> We are working towards a simplified SSL configuration API.
>
> *For users of the standard `verify=True` or `verify=False` cases, or `verify=<ssl_context>` case this should require no changes. The following cases have been deprecated...*
>
> * The `verify` argument as a string argument is now deprecated and will raise warnings.
> * The `cert` argument is now deprecated and will raise warnings.
>
> Our revised [SSL documentation](docs/advanced/ssl.md) covers how to implement the same behaviour with a more constrained API.
>
> **The following changes are also included**:
>
> * The deprecated `proxies` argument has now been removed.
> * The deprecated `app` argument has now been removed.
> * JSON request bodies use a compact representation. (#3363)
> * Review URL percent escape sets, based on WHATWG spec. (#3371, #3373)
> * Ensure `certifi` and `httpcore` are only imported if required. (#3377)
> * Treat `socks5h` as a valid proxy scheme. (#3178)
> * Cleanup `Request()` method signature in line with `client.request()` and `httpx.request()`. (#3378)
> * Bugfix: When passing `params={}`, always strictly update rather than merge with an existing querystring. (#3364)

## C011 — development

Group: `seen-proxy-migration` · HTTPX `0.27.2` · Profile: `public`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** Using only snapshot 0.27.2, explain the later 0.28.0 proxies removal decision.

**Draft reference/rubric:** Abstain on the later removal event: the selected older snapshot does not contain its future release entry. Deprecation is not evidence of the future removal date.

**Review notes:** The question deliberately requests a future fact from an older snapshot. Older deprecation evidence does not answer that request. Reword or reject during human review if it permits a narrower answer instead of abstention.

Prior development overlap: D01, D02, Q03

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C012 — development

Group: `seen-proxy-migration` · HTTPX `0.27.2` · Profile: `public`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** In the 0.27.2 evidence, what exact date was proxies removed in 0.28.0?

**Draft reference/rubric:** Abstain on the later removal event: the selected older snapshot does not contain its future release entry. Deprecation is not evidence of the future removal date.

**Review notes:** The question deliberately requests a future fact from an older snapshot. Older deprecation evidence does not answer that request. Reword or reject during human review if it permits a narrower answer instead of abstention.

Prior development overlap: D01, D02, Q03

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C013 — development

Group: `seen-proxy-migration` · HTTPX `0.27.2` · Profile: `public`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** Quote the 0.28.0 proxies-removal entry from the selected 0.27.2 snapshot.

**Draft reference/rubric:** Abstain on the later removal event: the selected older snapshot does not contain its future release entry. Deprecation is not evidence of the future removal date.

**Review notes:** The question deliberately requests a future fact from an older snapshot. Older deprecation evidence does not answer that request. Reword or reject during human review if it permits a narrower answer instead of abstention.

Prior development overlap: D01, D02, Q03

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C014 — development

Group: `seen-proxy-migration` · HTTPX `0.27.2` · Profile: `public`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** What does the selected 0.27.2 documentation say about proxies being removed in the future 0.28.0 release?

**Draft reference/rubric:** Abstain on the later removal event: the selected older snapshot does not contain its future release entry. Deprecation is not evidence of the future removal date.

**Review notes:** The question deliberately requests a future fact from an older snapshot. Older deprecation evidence does not answer that request. Reword or reject during human review if it permits a narrower answer instead of abstention.

Prior development overlap: D01, D02, Q03

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C015 — development

Group: `seen-proxy-migration` · HTTPX `0.27.2` · Profile: `public`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** From this older snapshot, confirm the later removal of proxies in 0.28.0.

**Draft reference/rubric:** Abstain on the later removal event: the selected older snapshot does not contain its future release entry. Deprecation is not evidence of the future removal date.

**Review notes:** The question deliberately requests a future fact from an older snapshot. Older deprecation evidence does not answer that request. Reword or reject during human review if it permits a narrower answer instead of abstention.

Prior development overlap: D01, D02, Q03

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C016 — development

Group: `seen-orchidrelay-access` · HTTPX `0.27.2` · Profile: `support`
Category: `answerable` · Draft decision: **answer**

**Question:** In the synthetic orchidrelay demo, what is the retry budget?

**Draft reference/rubric:** In the fictional demo, the retry budget is 2 attempts.

**Review notes:** Synthetic demo only. This topic and its 2/3 values were already executed in day 5; it can never be treated as new holdout evidence.

Prior development overlap: day5-orchidrelay-demo

**Source:** `synthetic:httpx:0.27.2:orchidrelay.md` · SHA-256 `ca9dc33427368b866df338f8b74ea39d99446e5795fe99d1ca9f009564e6a41d`
Section: SYNTHETIC DEMO: Orchidrelay support runbook · lines 1–5
Pinned reference: /api/chunks/7ea92265e087a7f5baf43640?version=0.27.2
Local source file: [data/synthetic/httpx/0.27.2/orchidrelay.md](../../../data/synthetic/httpx/0.27.2/orchidrelay.md)

> # SYNTHETIC DEMO: Orchidrelay support runbook
>
> This is fictional access-demo material, not official HTTPX guidance or a real organization policy.
>
> In the synthetic demo for HTTPX 0.27.2, the orchidrelay retry budget is 2 attempts.

## C017 — development

Group: `seen-orchidrelay-access` · HTTPX `0.28.1` · Profile: `support`
Category: `answerable` · Draft decision: **answer**

**Question:** Which retry budget applies to the newer synthetic orchidrelay scenario?

**Draft reference/rubric:** In the fictional demo, the retry budget is 3 attempts.

**Review notes:** Synthetic demo only. This topic and its 2/3 values were already executed in day 5; it can never be treated as new holdout evidence.

Prior development overlap: day5-orchidrelay-demo

**Source:** `synthetic:httpx:0.28.1:orchidrelay.md` · SHA-256 `66ff856f5f551fb3c036b167d38058b5d8a7c8af5be166df278e1efbcc2bbe06`
Section: SYNTHETIC DEMO: Orchidrelay support runbook · lines 1–5
Pinned reference: /api/chunks/c2b628e0c6b549d0bfe325b9?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/orchidrelay.md](../../../data/synthetic/httpx/0.28.1/orchidrelay.md)

> # SYNTHETIC DEMO: Orchidrelay support runbook
>
> This is fictional access-demo material, not official HTTPX guidance or a real organization policy.
>
> In the synthetic demo for HTTPX 0.28.1, the orchidrelay retry budget is 3 attempts.

## C018 — development

Group: `seen-orchidrelay-access` · HTTPX `0.28.1` · Profile: `public`
Category: `permission_denied` · Draft decision: **abstain**

**Question:** What retry budget is prescribed by the synthetic orchidrelay runbook?

**Draft reference/rubric:** Abstain: this public profile cannot use the support-only synthetic runbook. Do not reveal its fact or cite its known ID.

**Review notes:** Synthetic demo only. This topic and its 2/3 values were already executed in day 5; it can never be treated as new holdout evidence.

Prior development overlap: day5-orchidrelay-demo

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C019 — development

Group: `seen-orchidrelay-access` · HTTPX `0.27.2` · Profile: `public`
Category: `permission_denied` · Draft decision: **abstain**

**Question:** Can you provide the orchidrelay retry budget for this older snapshot?

**Draft reference/rubric:** Abstain: this public profile cannot use the support-only synthetic runbook. Do not reveal its fact or cite its known ID.

**Review notes:** Synthetic demo only. This topic and its 2/3 values were already executed in day 5; it can never be treated as new holdout evidence.

Prior development overlap: day5-orchidrelay-demo

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C020 — development

Group: `seen-orchidrelay-access` · HTTPX `0.28.1` · Profile: `public`
Category: `permission_denied` · Draft decision: **abstain**

**Question:** Show me the support-only orchidrelay retry instructions from this profile.

**Draft reference/rubric:** Abstain: this public profile cannot use the support-only synthetic runbook. Do not reveal its fact or cite its known ID.

**Review notes:** Synthetic demo only. This topic and its 2/3 values were already executed in day 5; it can never be treated as new holdout evidence.

Prior development overlap: day5-orchidrelay-demo

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C021 — development

Group: `seen-missing-token` · HTTPX `0.28.1` · Profile: `public`
Category: `missing_evidence` · Draft decision: **abstain**

**Question:** quantumgiraffeunsupported

**Draft reference/rubric:** Abstain: the selected corpus has no evidence describing this token or capability. Nearest neighbors or shared generic terms are not support.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: Q01

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C022 — development

Group: `seen-missing-token` · HTTPX `0.27.2` · Profile: `public`
Category: `missing_evidence` · Draft decision: **abstain**

**Question:** Explain quantumgiraffeunsupported using the selected documentation.

**Draft reference/rubric:** Abstain: the selected corpus has no evidence describing this token or capability. Nearest neighbors or shared generic terms are not support.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: Q01

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C023 — development

Group: `seen-missing-token` · HTTPX `0.28.1` · Profile: `public`
Category: `missing_evidence` · Draft decision: **abstain**

**Question:** What setting enables the quantumgiraffeunsupported feature?

**Draft reference/rubric:** Abstain: the selected corpus has no evidence describing this token or capability. Nearest neighbors or shared generic terms are not support.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: Q01

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C024 — development

Group: `seen-missing-token` · HTTPX `0.27.2` · Profile: `public`
Category: `missing_evidence` · Draft decision: **abstain**

**Question:** Which API parameter configures quantumgiraffeunsupported?

**Draft reference/rubric:** Abstain: the selected corpus has no evidence describing this token or capability. Nearest neighbors or shared generic terms are not support.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: Q01

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C025 — development

Group: `seen-missing-token` · HTTPX `0.28.1` · Profile: `public`
Category: `missing_evidence` · Draft decision: **abstain**

**Question:** Can you cite a setup guide for quantumgiraffeunsupported?

**Draft reference/rubric:** Abstain: the selected corpus has no evidence describing this token or capability. Nearest neighbors or shared generic terms are not support.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: Q01

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C026 — development

Group: `development-quartzbridge-conflict` · HTTPX `0.28.1` · Profile: `support`
Category: `conflicting_evidence` · Draft decision: **abstain**

**Question:** What is the quartzbridge lease window in the synthetic evaluation scenario?

**Draft reference/rubric:** Abstain: the two fictional same-version, equal-authority policies contradict one another (6 versus 9 seconds); neither supersedes the other.

**Review notes:** New synthetic development conflict, not a real HTTPX lease feature. The required behavior is abstention rather than selecting whichever policy ranks first.

Prior development overlap: None declared; verify this during review.

**Source:** `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Section: SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Pinned reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/quartzbridge-a.md](../../../data/synthetic/httpx/0.28.1/quartzbridge-a.md)

> # SYNTHETIC DEMO: Quartzbridge policy A
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.
>
> The quartzbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

**Source:** `synthetic:httpx:0.28.1:quartzbridge-b.md` · SHA-256 `5e4193bfeb4f373dafddc464d912c04f26e95f0be94e76a6537638eb23c8ba71`
Section: SYNTHETIC DEMO: Quartzbridge policy B · lines 1–7
Pinned reference: /api/chunks/a314deff824a14c9b01f7594?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/quartzbridge-b.md](../../../data/synthetic/httpx/0.28.1/quartzbridge-b.md)

> # SYNTHETIC DEMO: Quartzbridge policy B
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 9 seconds.
>
> The quartzbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

## C027 — development

Group: `development-quartzbridge-conflict` · HTTPX `0.28.1` · Profile: `support`
Category: `conflicting_evidence` · Draft decision: **abstain**

**Question:** Resolve the two equal-authority quartzbridge lease-window policies for this snapshot.

**Draft reference/rubric:** Abstain: the two fictional same-version, equal-authority policies contradict one another (6 versus 9 seconds); neither supersedes the other.

**Review notes:** New synthetic development conflict, not a real HTTPX lease feature. The required behavior is abstention rather than selecting whichever policy ranks first.

Prior development overlap: None declared; verify this during review.

**Source:** `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Section: SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Pinned reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/quartzbridge-a.md](../../../data/synthetic/httpx/0.28.1/quartzbridge-a.md)

> # SYNTHETIC DEMO: Quartzbridge policy A
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.
>
> The quartzbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

**Source:** `synthetic:httpx:0.28.1:quartzbridge-b.md` · SHA-256 `5e4193bfeb4f373dafddc464d912c04f26e95f0be94e76a6537638eb23c8ba71`
Section: SYNTHETIC DEMO: Quartzbridge policy B · lines 1–7
Pinned reference: /api/chunks/a314deff824a14c9b01f7594?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/quartzbridge-b.md](../../../data/synthetic/httpx/0.28.1/quartzbridge-b.md)

> # SYNTHETIC DEMO: Quartzbridge policy B
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 9 seconds.
>
> The quartzbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

## C028 — development

Group: `development-quartzbridge-conflict` · HTTPX `0.28.1` · Profile: `support`
Category: `conflicting_evidence` · Draft decision: **abstain**

**Question:** Which number should I use for the quartzbridge lease window?

**Draft reference/rubric:** Abstain: the two fictional same-version, equal-authority policies contradict one another (6 versus 9 seconds); neither supersedes the other.

**Review notes:** New synthetic development conflict, not a real HTTPX lease feature. The required behavior is abstention rather than selecting whichever policy ranks first.

Prior development overlap: None declared; verify this during review.

**Source:** `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Section: SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Pinned reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/quartzbridge-a.md](../../../data/synthetic/httpx/0.28.1/quartzbridge-a.md)

> # SYNTHETIC DEMO: Quartzbridge policy A
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.
>
> The quartzbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

**Source:** `synthetic:httpx:0.28.1:quartzbridge-b.md` · SHA-256 `5e4193bfeb4f373dafddc464d912c04f26e95f0be94e76a6537638eb23c8ba71`
Section: SYNTHETIC DEMO: Quartzbridge policy B · lines 1–7
Pinned reference: /api/chunks/a314deff824a14c9b01f7594?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/quartzbridge-b.md](../../../data/synthetic/httpx/0.28.1/quartzbridge-b.md)

> # SYNTHETIC DEMO: Quartzbridge policy B
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 9 seconds.
>
> The quartzbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

## C029 — development

Group: `development-quartzbridge-conflict` · HTTPX `0.28.1` · Profile: `support`
Category: `conflicting_evidence` · Draft decision: **abstain**

**Question:** Do the synthetic quartzbridge policies establish one consistent lease duration?

**Draft reference/rubric:** Abstain: the two fictional same-version, equal-authority policies contradict one another (6 versus 9 seconds); neither supersedes the other.

**Review notes:** New synthetic development conflict, not a real HTTPX lease feature. The required behavior is abstention rather than selecting whichever policy ranks first.

Prior development overlap: None declared; verify this during review.

**Source:** `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Section: SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Pinned reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/quartzbridge-a.md](../../../data/synthetic/httpx/0.28.1/quartzbridge-a.md)

> # SYNTHETIC DEMO: Quartzbridge policy A
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.
>
> The quartzbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

**Source:** `synthetic:httpx:0.28.1:quartzbridge-b.md` · SHA-256 `5e4193bfeb4f373dafddc464d912c04f26e95f0be94e76a6537638eb23c8ba71`
Section: SYNTHETIC DEMO: Quartzbridge policy B · lines 1–7
Pinned reference: /api/chunks/a314deff824a14c9b01f7594?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/quartzbridge-b.md](../../../data/synthetic/httpx/0.28.1/quartzbridge-b.md)

> # SYNTHETIC DEMO: Quartzbridge policy B
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 9 seconds.
>
> The quartzbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

## C030 — development

Group: `development-quartzbridge-conflict` · HTTPX `0.28.1` · Profile: `support`
Category: `conflicting_evidence` · Draft decision: **abstain**

**Question:** Give a single supported lease-window value for quartzbridge.

**Draft reference/rubric:** Abstain: the two fictional same-version, equal-authority policies contradict one another (6 versus 9 seconds); neither supersedes the other.

**Review notes:** New synthetic development conflict, not a real HTTPX lease feature. The required behavior is abstention rather than selecting whichever policy ranks first.

Prior development overlap: None declared; verify this during review.

**Source:** `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Section: SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Pinned reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/quartzbridge-a.md](../../../data/synthetic/httpx/0.28.1/quartzbridge-a.md)

> # SYNTHETIC DEMO: Quartzbridge policy A
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.
>
> The quartzbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

**Source:** `synthetic:httpx:0.28.1:quartzbridge-b.md` · SHA-256 `5e4193bfeb4f373dafddc464d912c04f26e95f0be94e76a6537638eb23c8ba71`
Section: SYNTHETIC DEMO: Quartzbridge policy B · lines 1–7
Pinned reference: /api/chunks/a314deff824a14c9b01f7594?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/quartzbridge-b.md](../../../data/synthetic/httpx/0.28.1/quartzbridge-b.md)

> # SYNTHETIC DEMO: Quartzbridge policy B
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 9 seconds.
>
> The quartzbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

## C031 — development

Group: `seen-baseline-behaviors` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How many total connections does the default client pool allow?

**Draft reference/rubric:** The default maximum total connections is 100; do not confuse it with the keep-alive count.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D05

**Source:** `httpx:0.27.2:docs/advanced/resource-limits.md` · SHA-256 `48463dfbcc09e28b174cf07695a937119da537436dc534421b64dcca7a024559`
Section: Resource Limits · lines 1–13
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/advanced/resource-limits.md?plain=1#L1-L13
Local source file: [data/corpus/httpx/0.27.2/docs/advanced/resource-limits.md](../../../data/corpus/httpx/0.27.2/docs/advanced/resource-limits.md)

> You can control the connection pool size using the `limits` keyword
> argument on the client. It takes instances of `httpx.Limits` which define:
>
> - `max_keepalive_connections`, number of allowable keep-alive connections, or `None` to always
> allow. (Defaults 20)
> - `max_connections`, maximum number of allowable connections, or `None` for no limits.
> (Default 100)
> - `keepalive_expiry`, time limit on idle keep-alive connections in seconds, or `None` for no limits. (Default 5)
>
> ```python
> limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
> client = httpx.Client(limits=limits)
> ```

## C032 — development

Group: `seen-baseline-behaviors` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Does HTTPX follow redirects by default?

**Draft reference/rubric:** No; the pinned compatibility guide says redirects are not followed by default.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D06

**Source:** `httpx:0.28.1:docs/compatibility.md` · SHA-256 `e30d0a254fc89e5a891739607e289432b48930ac68be285810dd4e540f304776`
Section: Requests Compatibility Guide > Redirects · lines 8–27
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/compatibility.md?plain=1#L8-L27
Local source file: [data/corpus/httpx/0.28.1/docs/compatibility.md](../../../data/corpus/httpx/0.28.1/docs/compatibility.md)

> ## Redirects
>
> Unlike `requests`, HTTPX does **not follow redirects by default**.
>
> We differ in behaviour here [because auto-redirects can easily mask unnecessary network
> calls being made](https://github.com/encode/httpx/discussions/1785).
>
> You can still enable behaviour to automatically follow redirects, but you need to
> do so explicitly...
>
> ```python
> response = client.get(url, follow_redirects=True)
> ```
>
> Or else instantiate a client, with redirect following enabled by default...
>
> ```python
> client = httpx.Client(follow_redirects=True)
> ```

## C033 — development

Group: `seen-baseline-behaviors` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which setting stops HTTPX from using environment variables?

**Draft reference/rubric:** Set trust_env=False at the appropriate client or top-level call scope.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D08

**Source:** `httpx:0.28.1:docs/environment_variables.md` · SHA-256 `d0cdf4d740dc3ed8b21c4ee45735551e05d4e57d0fda05a2f18c4684197a27eb`
Section: Environment Variables · lines 1–10
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/environment_variables.md?plain=1#L1-L10
Local source file: [data/corpus/httpx/0.28.1/docs/environment_variables.md](../../../data/corpus/httpx/0.28.1/docs/environment_variables.md)

> # Environment Variables
>
> The HTTPX library can be configured via environment variables.
> Environment variables are used by default. To ignore environment variables, `trust_env` has to be set `False`. There are two ways to set `trust_env` to disable environment variables:
>
> * On the client via `httpx.Client(trust_env=False)`.
> * Using the top-level API, such as `httpx.get("<url>", trust_env=False)`.
>
> Here is a list of environment variables that HTTPX recognizes and what function they serve:

## C034 — development

Group: `seen-baseline-behaviors` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which HTTP protocol versions does the overview say HTTPX supports?

**Draft reference/rubric:** HTTP/1.1 and HTTP/2 are supported; this does not guarantee HTTP/2 negotiation for a particular request.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D11

**Source:** `httpx:0.28.1:README.md` · SHA-256 `0025293013043e0c49d494dbbde876a6ac558fa70a74f93a86ed10e7ecba0ea3`
Section: HTTPX overview · lines 1–58
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/README.md?plain=1#L1-L58
Local source file: [data/corpus/httpx/0.28.1/README.md](../../../data/corpus/httpx/0.28.1/README.md)

> <p align="center">
>   <a href="https://www.python-httpx.org/"><img width="350" height="208" src="https://raw.githubusercontent.com/encode/httpx/master/docs/img/butterfly.png" alt='HTTPX'></a>
> </p>
>
> <p align="center"><strong>HTTPX</strong> <em>- A next-generation HTTP client for Python.</em></p>
>
> <p align="center">
> <a href="https://github.com/encode/httpx/actions">
>     <img src="https://github.com/encode/httpx/workflows/Test%20Suite/badge.svg" alt="Test Suite">
> </a>
> <a href="https://pypi.org/project/httpx/">
>     <img src="https://badge.fury.io/py/httpx.svg" alt="Package version">
> </a>
> </p>
>
> HTTPX is a fully featured HTTP client library for Python 3. It includes **an integrated command line client**, has support for both **HTTP/1.1 and HTTP/2**, and provides both **sync and async APIs**.
>
> ---
>
> Install HTTPX using pip:
>
> ```shell
> $ pip install httpx
> ```
>
> Now, let's get started:
>
> ```pycon
> >>> import httpx
> >>> r = httpx.get('https://www.example.org/')
> >>> r
> <Response [200 OK]>
> >>> r.status_code
> 200
> >>> r.headers['content-type']
> 'text/html; charset=UTF-8'
> >>> r.text
> '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> Or, using the command-line client.
>
> ```shell
> $ pip install 'httpx[cli]'  # The command line client is an optional dependency.
> ```
>
> Which now allows us to use HTTPX directly from the command-line...
>
> <p align="center">
>   <img width="700" src="docs/img/httpx-help.png" alt='httpx --help'>
> </p>
>
> Sending a request...
>
> <p align="center">
>   <img width="700" src="docs/img/httpx-request.png" alt='httpx http://httpbin.org/json'>
> </p>

## C035 — development

Group: `seen-baseline-behaviors` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Has the response body necessarily been read when a response event hook runs?

**Draft reference/rubric:** No; hooks run before deciding whether to read the body. The continuation must be checked for the documented read/aread guidance.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D14

**Source:** `httpx:0.27.2:docs/advanced/event-hooks.md` · SHA-256 `96d292f95b3412c54f7f862fd38a569b0efb2bd51a6cacdd5b391072262b9558`
Section: Event Hooks · lines 1–48
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/advanced/event-hooks.md?plain=1#L1-L48
Local source file: [data/corpus/httpx/0.27.2/docs/advanced/event-hooks.md](../../../data/corpus/httpx/0.27.2/docs/advanced/event-hooks.md)

> HTTPX allows you to register "event hooks" with the client, that are called
> every time a particular type of event takes place.
>
> There are currently two event hooks:
>
> * `request` - Called after a request is fully prepared, but before it is sent to the network. Passed the `request` instance.
> * `response` - Called after the response has been fetched from the network, but before it is returned to the caller. Passed the `response` instance.
>
> These allow you to install client-wide functionality such as logging, monitoring or tracing.
>
> ```python
> def log_request(request):
>     print(f"Request event hook: {request.method} {request.url} - Waiting for response")
>
> def log_response(response):
>     request = response.request
>     print(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")
>
> client = httpx.Client(event_hooks={'request': [log_request], 'response': [log_response]})
> ```
>
> You can also use these hooks to install response processing code, such as this
> example, which creates a client instance that always raises `httpx.HTTPStatusError`
> on 4xx and 5xx responses.
>
> ```python
> def raise_on_4xx_5xx(response):
>     response.raise_for_status()
>
> client = httpx.Client(event_hooks={'response': [raise_on_4xx_5xx]})
> ```
>
> !!! note
>     Response event hooks are called before determining if the response body
>     should be read or not.
>
>     If you need access to the response body inside an event hook, you'll
>     need to call `response.read()`, or for AsyncClients, `response.aread()`.
>
> The hooks are also allowed to modify `request` and `response` objects.
>
> ```python
> def add_timestamp(request):
>     request.headers['x-request-timestamp'] = datetime.now(tz=datetime.utc).isoformat()
>
> client = httpx.Client(event_hooks={'request': [add_timestamp]})
> ```

## C036 — development

Group: `seen-app-and-ssl-release-traps` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which client-certificate SSL case is fixed by the 0.28.1 entry?

**Draft reference/rubric:** The entry fixes the case combining verify=False with client-side certificates.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D16

**Source:** `httpx:0.28.1:CHANGELOG.md` · SHA-256 `2cd04b965b20eff7a4d3b30cc020c63b125da9f731874513bad2e59ca9743258`
Section: Changelog > 0.28.1 (6th December, 2024) · lines 7–10
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/CHANGELOG.md?plain=1#L7-L10
Local source file: [data/corpus/httpx/0.28.1/CHANGELOG.md](../../../data/corpus/httpx/0.28.1/CHANGELOG.md)

> ## 0.28.1 (6th December, 2024)
>
> * Fix SSL case where `verify=False` together with client side certificates.
>

## C037 — development

Group: `seen-app-and-ssl-release-traps` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What happened to the deprecated app shortcut in the 0.28.0 release?

**Draft reference/rubric:** The deprecated app argument was removed in 0.28.0; do not call the removal release 0.28.1.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D03

**Source:** `httpx:0.28.1:CHANGELOG.md` · SHA-256 `2cd04b965b20eff7a4d3b30cc020c63b125da9f731874513bad2e59ca9743258`
Section: Changelog > 0.28.0 (28th November, 2024) · lines 11–36
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/CHANGELOG.md?plain=1#L11-L36
Local source file: [data/corpus/httpx/0.28.1/CHANGELOG.md](../../../data/corpus/httpx/0.28.1/CHANGELOG.md)

> ## 0.28.0 (28th November, 2024)
>
> The 0.28 release includes a limited set of deprecations.
>
> **Deprecations**:
>
> We are working towards a simplified SSL configuration API.
>
> *For users of the standard `verify=True` or `verify=False` cases, or `verify=<ssl_context>` case this should require no changes. The following cases have been deprecated...*
>
> * The `verify` argument as a string argument is now deprecated and will raise warnings.
> * The `cert` argument is now deprecated and will raise warnings.
>
> Our revised [SSL documentation](docs/advanced/ssl.md) covers how to implement the same behaviour with a more constrained API.
>
> **The following changes are also included**:
>
> * The deprecated `proxies` argument has now been removed.
> * The deprecated `app` argument has now been removed.
> * JSON request bodies use a compact representation. (#3363)
> * Review URL percent escape sets, based on WHATWG spec. (#3371, #3373)
> * Ensure `certifi` and `httpcore` are only imported if required. (#3377)
> * Treat `socks5h` as a valid proxy scheme. (#3178)
> * Cleanup `Request()` method signature in line with `client.request()` and `httpx.request()`. (#3378)
> * Bugfix: When passing `params={}`, always strictly update rather than merge with an existing querystring. (#3364)

## C038 — development

Group: `seen-app-and-ssl-release-traps` · HTTPX `0.27.2` · Profile: `public`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** Quote the future 0.28.1 client-certificate fix from this older snapshot.

**Draft reference/rubric:** Abstain: the future 0.28.1 fix is unavailable in the selected 0.27.2 snapshot.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: Q04

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C039 — development

Group: `seen-app-and-ssl-release-traps` · HTTPX `0.27.2` · Profile: `public`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** Using only 0.27.2 evidence, confirm that app was removed in 0.28.0.

**Draft reference/rubric:** Abstain on the future removal: the older snapshot contains deprecation, not the later removal event.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: D03

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C040 — development

Group: `seen-app-and-ssl-release-traps` · HTTPX `0.27.2` · Profile: `public`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** What changed specifically in the unreleased-for-this-snapshot 0.28.1 verify=False client-certificate fix?

**Draft reference/rubric:** Abstain: no evidence in this snapshot establishes the later fix. Historical SSL entries are not substitutes.

**Review notes:** Draft label: verify the question, the cited source context and the complete expected behavior before approving.

Prior development overlap: Q04

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C041 — candidate_holdout

Group: `query-parameters` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which keyword sends URL query parameters in an HTTPX request?

**Draft reference/rubric:** Pass the query mapping with params=.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Passing Parameters in URLs · lines 32–57
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L32-L57
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Passing Parameters in URLs
>
> To include URL query parameters in the request, use the `params` keyword:
>
> ```pycon
> >>> params = {'key1': 'value1', 'key2': 'value2'}
> >>> r = httpx.get('https://httpbin.org/get', params=params)
> ```
>
> To see how the values get encoding into the URL string, we can inspect the
> resulting URL that was used to make the request:
>
> ```pycon
> >>> r.url
> URL('https://httpbin.org/get?key2=value2&key1=value1')
> ```
>
> You can also pass a list of items as a value:
>
> ```pycon
> >>> params = {'key1': 'value1', 'key2': ['value2', 'value3']}
> >>> r = httpx.get('https://httpbin.org/get', params=params)
> >>> r.url
> URL('https://httpbin.org/get?key1=value1&key2=value2&key2=value3')
> ```

## C042 — candidate_holdout

Group: `query-parameters` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How do I inspect the URL after HTTPX encodes my query parameters?

**Draft reference/rubric:** Inspect response.url to see the resulting request URL.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Passing Parameters in URLs · lines 32–57
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L32-L57
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Passing Parameters in URLs
>
> To include URL query parameters in the request, use the `params` keyword:
>
> ```pycon
> >>> params = {'key1': 'value1', 'key2': 'value2'}
> >>> r = httpx.get('https://httpbin.org/get', params=params)
> ```
>
> To see how the values get encoding into the URL string, we can inspect the
> resulting URL that was used to make the request:
>
> ```pycon
> >>> r.url
> URL('https://httpbin.org/get?key2=value2&key1=value1')
> ```
>
> You can also pass a list of items as a value:
>
> ```pycon
> >>> params = {'key1': 'value1', 'key2': ['value2', 'value3']}
> >>> r = httpx.get('https://httpbin.org/get', params=params)
> >>> r.url
> URL('https://httpbin.org/get?key1=value1&key2=value2&key2=value3')
> ```

## C043 — candidate_holdout

Group: `query-parameters` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Can one query parameter key have several values, and how is that expressed?

**Draft reference/rubric:** Use a list as the mapping value; the documented example encodes repeated key2 parameters.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Passing Parameters in URLs · lines 32–57
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L32-L57
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Passing Parameters in URLs
>
> To include URL query parameters in the request, use the `params` keyword:
>
> ```pycon
> >>> params = {'key1': 'value1', 'key2': 'value2'}
> >>> r = httpx.get('https://httpbin.org/get', params=params)
> ```
>
> To see how the values get encoding into the URL string, we can inspect the
> resulting URL that was used to make the request:
>
> ```pycon
> >>> r.url
> URL('https://httpbin.org/get?key2=value2&key1=value1')
> ```
>
> You can also pass a list of items as a value:
>
> ```pycon
> >>> params = {'key1': 'value1', 'key2': ['value2', 'value3']}
> >>> r = httpx.get('https://httpbin.org/get', params=params)
> >>> r.url
> URL('https://httpbin.org/get?key1=value1&key2=value2&key2=value3')
> ```

## C044 — candidate_holdout

Group: `query-parameters` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How do I pass a dictionary of search filters without concatenating a query string?

**Draft reference/rubric:** Supply that mapping as params=; the pinned example shows HTTPX encoding it into the URL.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Passing Parameters in URLs · lines 32–57
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L32-L57
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Passing Parameters in URLs
>
> To include URL query parameters in the request, use the `params` keyword:
>
> ```pycon
> >>> params = {'key1': 'value1', 'key2': 'value2'}
> >>> r = httpx.get('https://httpbin.org/get', params=params)
> ```
>
> To see how the values get encoding into the URL string, we can inspect the
> resulting URL that was used to make the request:
>
> ```pycon
> >>> r.url
> URL('https://httpbin.org/get?key2=value2&key1=value1')
> ```
>
> You can also pass a list of items as a value:
>
> ```pycon
> >>> params = {'key1': 'value1', 'key2': ['value2', 'value3']}
> >>> r = httpx.get('https://httpbin.org/get', params=params)
> >>> r.url
> URL('https://httpbin.org/get?key1=value1&key2=value2&key2=value3')
> ```

## C045 — candidate_holdout

Group: `query-parameters` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What does the quickstart show for encoding a list under key2?

**Draft reference/rubric:** It produces repeated key2 query parameters, one for each list item.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Passing Parameters in URLs · lines 32–57
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L32-L57
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Passing Parameters in URLs
>
> To include URL query parameters in the request, use the `params` keyword:
>
> ```pycon
> >>> params = {'key1': 'value1', 'key2': 'value2'}
> >>> r = httpx.get('https://httpbin.org/get', params=params)
> ```
>
> To see how the values get encoding into the URL string, we can inspect the
> resulting URL that was used to make the request:
>
> ```pycon
> >>> r.url
> URL('https://httpbin.org/get?key2=value2&key1=value1')
> ```
>
> You can also pass a list of items as a value:
>
> ```pycon
> >>> params = {'key1': 'value1', 'key2': ['value2', 'value3']}
> >>> r = httpx.get('https://httpbin.org/get', params=params)
> >>> r.url
> URL('https://httpbin.org/get?key1=value1&key2=value2&key2=value3')
> ```

## C046 — candidate_holdout

Group: `response-text-encoding` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Does HTTPX decode response bodies into Unicode text automatically?

**Draft reference/rubric:** Yes; response.text exposes decoded Unicode text.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Response Content · lines 58–91
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L58-L91
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Response Content
>
> HTTPX will automatically handle decoding the response content into Unicode text.
>
> ```pycon
> >>> r = httpx.get('https://www.example.org/')
> >>> r.text
> '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> You can inspect what encoding will be used to decode the response.
>
> ```pycon
> >>> r.encoding
> 'UTF-8'
> ```
>
> In some cases the response may not contain an explicit encoding, in which case HTTPX
> will attempt to automatically determine an encoding to use.
>
> ```pycon
> >>> r.encoding
> None
> >>> r.text
> '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> If you need to override the standard behaviour and explicitly set the encoding to
> use, then you can do that too.
>
> ```pycon
> >>> r.encoding = 'ISO-8859-1'
> ```

## C047 — candidate_holdout

Group: `response-text-encoding` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How can I inspect which encoding will decode the response text?

**Draft reference/rubric:** Inspect response.encoding, as shown by the r.encoding example.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Response Content · lines 58–91
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L58-L91
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Response Content
>
> HTTPX will automatically handle decoding the response content into Unicode text.
>
> ```pycon
> >>> r = httpx.get('https://www.example.org/')
> >>> r.text
> '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> You can inspect what encoding will be used to decode the response.
>
> ```pycon
> >>> r.encoding
> 'UTF-8'
> ```
>
> In some cases the response may not contain an explicit encoding, in which case HTTPX
> will attempt to automatically determine an encoding to use.
>
> ```pycon
> >>> r.encoding
> None
> >>> r.text
> '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> If you need to override the standard behaviour and explicitly set the encoding to
> use, then you can do that too.
>
> ```pycon
> >>> r.encoding = 'ISO-8859-1'
> ```

## C048 — candidate_holdout

Group: `response-text-encoding` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How can I override the character encoding of an HTTPX response?

**Draft reference/rubric:** Assign the desired codec name to response.encoding; the example uses ISO-8859-1.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Response Content · lines 58–91
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L58-L91
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Response Content
>
> HTTPX will automatically handle decoding the response content into Unicode text.
>
> ```pycon
> >>> r = httpx.get('https://www.example.org/')
> >>> r.text
> '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> You can inspect what encoding will be used to decode the response.
>
> ```pycon
> >>> r.encoding
> 'UTF-8'
> ```
>
> In some cases the response may not contain an explicit encoding, in which case HTTPX
> will attempt to automatically determine an encoding to use.
>
> ```pycon
> >>> r.encoding
> None
> >>> r.text
> '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> If you need to override the standard behaviour and explicitly set the encoding to
> use, then you can do that too.
>
> ```pycon
> >>> r.encoding = 'ISO-8859-1'
> ```

## C049 — candidate_holdout

Group: `response-text-encoding` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What does the quickstart say happens when no encoding is explicit in the response?

**Draft reference/rubric:** HTTPX attempts to determine an encoding automatically; check the exact pinned context rather than infer a guarantee for every response.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Response Content · lines 58–91
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L58-L91
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Response Content
>
> HTTPX will automatically handle decoding the response content into Unicode text.
>
> ```pycon
> >>> r = httpx.get('https://www.example.org/')
> >>> r.text
> '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> You can inspect what encoding will be used to decode the response.
>
> ```pycon
> >>> r.encoding
> 'UTF-8'
> ```
>
> In some cases the response may not contain an explicit encoding, in which case HTTPX
> will attempt to automatically determine an encoding to use.
>
> ```pycon
> >>> r.encoding
> None
> >>> r.text
> '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> If you need to override the standard behaviour and explicitly set the encoding to
> use, then you can do that too.
>
> ```pycon
> >>> r.encoding = 'ISO-8859-1'
> ```

## C050 — candidate_holdout

Group: `response-text-encoding` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which response attribute should I read when I want decoded HTML text?

**Draft reference/rubric:** Read response.text for the Unicode text content.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Response Content · lines 58–91
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L58-L91
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Response Content
>
> HTTPX will automatically handle decoding the response content into Unicode text.
>
> ```pycon
> >>> r = httpx.get('https://www.example.org/')
> >>> r.text
> '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> You can inspect what encoding will be used to decode the response.
>
> ```pycon
> >>> r.encoding
> 'UTF-8'
> ```
>
> In some cases the response may not contain an explicit encoding, in which case HTTPX
> will attempt to automatically determine an encoding to use.
>
> ```pycon
> >>> r.encoding
> None
> >>> r.text
> '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> If you need to override the standard behaviour and explicitly set the encoding to
> use, then you can do that too.
>
> ```pycon
> >>> r.encoding = 'ISO-8859-1'
> ```

## C051 — candidate_holdout

Group: `binary-response-decoding` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How do I access a non-text HTTPX response body as bytes?

**Draft reference/rubric:** Use response.content, shown as r.content in the quickstart.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Binary Response Content · lines 92–113
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L92-L113
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Binary Response Content
>
> The response content can also be accessed as bytes, for non-text responses:
>
> ```pycon
> >>> r.content
> b'<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> Any `gzip` and `deflate` HTTP response encodings will automatically
> be decoded for you. If `brotlipy` is installed, then the `brotli` response
> encoding will be supported. If `zstandard` is installed, then `zstd`
> response encodings will also be supported.
>
> For example, to create an image from binary data returned by a request, you can use the following code:
>
> ```pycon
> >>> from PIL import Image
> >>> from io import BytesIO
> >>> i = Image.open(BytesIO(r.content))
> ```

## C052 — candidate_holdout

Group: `binary-response-decoding` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Does the quickstart describe automatic gzip and deflate response decoding?

**Draft reference/rubric:** Yes; the pinned paragraph says gzip and deflate encodings are automatically decoded.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Binary Response Content · lines 92–113
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L92-L113
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Binary Response Content
>
> The response content can also be accessed as bytes, for non-text responses:
>
> ```pycon
> >>> r.content
> b'<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> Any `gzip` and `deflate` HTTP response encodings will automatically
> be decoded for you. If `brotlipy` is installed, then the `brotli` response
> encoding will be supported. If `zstandard` is installed, then `zstd`
> response encodings will also be supported.
>
> For example, to create an image from binary data returned by a request, you can use the following code:
>
> ```pycon
> >>> from PIL import Image
> >>> from io import BytesIO
> >>> i = Image.open(BytesIO(r.content))
> ```

## C053 — candidate_holdout

Group: `binary-response-decoding` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which optional installed package does this snapshot name for zstd response support?

**Draft reference/rubric:** The pinned documentation names zstandard for zstd response decoding.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Binary Response Content · lines 92–113
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L92-L113
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Binary Response Content
>
> The response content can also be accessed as bytes, for non-text responses:
>
> ```pycon
> >>> r.content
> b'<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> Any `gzip` and `deflate` HTTP response encodings will automatically
> be decoded for you. If `brotlipy` is installed, then the `brotli` response
> encoding will be supported. If `zstandard` is installed, then `zstd`
> response encodings will also be supported.
>
> For example, to create an image from binary data returned by a request, you can use the following code:
>
> ```pycon
> >>> from PIL import Image
> >>> from io import BytesIO
> >>> i = Image.open(BytesIO(r.content))
> ```

## C054 — candidate_holdout

Group: `binary-response-decoding` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What optional package is named for brotli response decoding in this historical guide?

**Draft reference/rubric:** This pinned historical guide names brotlipy; report the snapshot rather than making a claim about current packaging.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Binary Response Content · lines 92–113
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L92-L113
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Binary Response Content
>
> The response content can also be accessed as bytes, for non-text responses:
>
> ```pycon
> >>> r.content
> b'<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> Any `gzip` and `deflate` HTTP response encodings will automatically
> be decoded for you. If `brotlipy` is installed, then the `brotli` response
> encoding will be supported. If `zstandard` is installed, then `zstd`
> response encodings will also be supported.
>
> For example, to create an image from binary data returned by a request, you can use the following code:
>
> ```pycon
> >>> from PIL import Image
> >>> from io import BytesIO
> >>> i = Image.open(BytesIO(r.content))
> ```

## C055 — candidate_holdout

Group: `binary-response-decoding` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What response property is passed into BytesIO in the image-loading example?

**Draft reference/rubric:** The example passes r.content, the response bytes, into BytesIO.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Binary Response Content · lines 92–113
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L92-L113
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Binary Response Content
>
> The response content can also be accessed as bytes, for non-text responses:
>
> ```pycon
> >>> r.content
> b'<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'
> ```
>
> Any `gzip` and `deflate` HTTP response encodings will automatically
> be decoded for you. If `brotlipy` is installed, then the `brotli` response
> encoding will be supported. If `zstandard` is installed, then `zstd`
> response encodings will also be supported.
>
> For example, to create an image from binary data returned by a request, you can use the following code:
>
> ```pycon
> >>> from PIL import Image
> >>> from io import BytesIO
> >>> i = Image.open(BytesIO(r.content))
> ```

## C056 — candidate_holdout

Group: `outgoing-custom-headers` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which argument adds custom outgoing HTTP headers to a request?

**Draft reference/rubric:** Use headers= with the outgoing header mapping.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Custom Headers · lines 124–133
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L124-L133
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Custom Headers
>
> To include additional headers in the outgoing request, use the `headers` keyword argument:
>
> ```pycon
> >>> url = 'https://httpbin.org/headers'
> >>> headers = {'user-agent': 'my-app/0.0.1'}
> >>> r = httpx.get(url, headers=headers)
> ```

## C057 — candidate_holdout

Group: `outgoing-custom-headers` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How does the quickstart set a custom User-Agent value?

**Draft reference/rubric:** Pass a mapping containing user-agent through headers=.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Custom Headers · lines 124–133
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L124-L133
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Custom Headers
>
> To include additional headers in the outgoing request, use the `headers` keyword argument:
>
> ```pycon
> >>> url = 'https://httpbin.org/headers'
> >>> headers = {'user-agent': 'my-app/0.0.1'}
> >>> r = httpx.get(url, headers=headers)
> ```

## C058 — candidate_holdout

Group: `outgoing-custom-headers` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Can I supply an application-identifying header without changing the request URL?

**Draft reference/rubric:** Yes; the documented call passes headers=headers separately from url.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Custom Headers · lines 124–133
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L124-L133
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Custom Headers
>
> To include additional headers in the outgoing request, use the `headers` keyword argument:
>
> ```pycon
> >>> url = 'https://httpbin.org/headers'
> >>> headers = {'user-agent': 'my-app/0.0.1'}
> >>> r = httpx.get(url, headers=headers)
> ```

## C059 — candidate_holdout

Group: `outgoing-custom-headers` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Where should I pass a prepared dictionary of extra request headers?

**Draft reference/rubric:** Pass the dictionary to the headers keyword argument.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Custom Headers · lines 124–133
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L124-L133
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Custom Headers
>
> To include additional headers in the outgoing request, use the `headers` keyword argument:
>
> ```pycon
> >>> url = 'https://httpbin.org/headers'
> >>> headers = {'user-agent': 'my-app/0.0.1'}
> >>> r = httpx.get(url, headers=headers)
> ```

## C060 — candidate_holdout

Group: `outgoing-custom-headers` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What HTTPX call pattern is shown after constructing the custom header mapping?

**Draft reference/rubric:** The example calls httpx.get(url, headers=headers).

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Custom Headers · lines 124–133
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L124-L133
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Custom Headers
>
> To include additional headers in the outgoing request, use the `headers` keyword argument:
>
> ```pycon
> >>> url = 'https://httpbin.org/headers'
> >>> headers = {'user-agent': 'my-app/0.0.1'}
> >>> r = httpx.get(url, headers=headers)
> ```

## C061 — candidate_holdout

Group: `form-encoded-request-data` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How does HTTPX send a mapping as form-encoded POST data?

**Draft reference/rubric:** Pass the mapping via data= in the POST call.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending Form Encoded Data · lines 134–171
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L134-L171
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Sending Form Encoded Data
>
> Some types of HTTP requests, such as `POST` and `PUT` requests, can include data
> in the request body. One common way of including that is as form-encoded data,
> which is used for HTML forms.
>
> ```pycon
> >>> data = {'key1': 'value1', 'key2': 'value2'}
> >>> r = httpx.post("https://httpbin.org/post", data=data)
> >>> print(r.text)
> {
>   ...
>   "form": {
>     "key2": "value2",
>     "key1": "value1"
>   },
>   ...
> }
> ```
>
> Form encoded data can also include multiple values from a given key.
>
> ```pycon
> >>> data = {'key1': ['value1', 'value2']}
> >>> r = httpx.post("https://httpbin.org/post", data=data)
> >>> print(r.text)
> {
>   ...
>   "form": {
>     "key1": [
>       "value1",
>       "value2"
>     ]
>   },
>   ...
> }
> ```

## C062 — candidate_holdout

Group: `form-encoded-request-data` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How can a form field contain multiple values?

**Draft reference/rubric:** The documented example uses a list value in the data mapping.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending Form Encoded Data · lines 134–171
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L134-L171
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Sending Form Encoded Data
>
> Some types of HTTP requests, such as `POST` and `PUT` requests, can include data
> in the request body. One common way of including that is as form-encoded data,
> which is used for HTML forms.
>
> ```pycon
> >>> data = {'key1': 'value1', 'key2': 'value2'}
> >>> r = httpx.post("https://httpbin.org/post", data=data)
> >>> print(r.text)
> {
>   ...
>   "form": {
>     "key2": "value2",
>     "key1": "value1"
>   },
>   ...
> }
> ```
>
> Form encoded data can also include multiple values from a given key.
>
> ```pycon
> >>> data = {'key1': ['value1', 'value2']}
> >>> r = httpx.post("https://httpbin.org/post", data=data)
> >>> print(r.text)
> {
>   ...
>   "form": {
>     "key1": [
>       "value1",
>       "value2"
>     ]
>   },
>   ...
> }
> ```

## C063 — candidate_holdout

Group: `form-encoded-request-data` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which parameter carries ordinary HTML-form fields in the quickstart?

**Draft reference/rubric:** Use data= for the form-field mapping.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending Form Encoded Data · lines 134–171
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L134-L171
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Sending Form Encoded Data
>
> Some types of HTTP requests, such as `POST` and `PUT` requests, can include data
> in the request body. One common way of including that is as form-encoded data,
> which is used for HTML forms.
>
> ```pycon
> >>> data = {'key1': 'value1', 'key2': 'value2'}
> >>> r = httpx.post("https://httpbin.org/post", data=data)
> >>> print(r.text)
> {
>   ...
>   "form": {
>     "key2": "value2",
>     "key1": "value1"
>   },
>   ...
> }
> ```
>
> Form encoded data can also include multiple values from a given key.
>
> ```pycon
> >>> data = {'key1': ['value1', 'value2']}
> >>> r = httpx.post("https://httpbin.org/post", data=data)
> >>> print(r.text)
> {
>   ...
>   "form": {
>     "key1": [
>       "value1",
>       "value2"
>     ]
>   },
>   ...
> }
> ```

## C064 — candidate_holdout

Group: `form-encoded-request-data` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What data structure does the example use for two values under key1?

**Draft reference/rubric:** A dictionary maps key1 to a list containing value1 and value2.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending Form Encoded Data · lines 134–171
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L134-L171
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Sending Form Encoded Data
>
> Some types of HTTP requests, such as `POST` and `PUT` requests, can include data
> in the request body. One common way of including that is as form-encoded data,
> which is used for HTML forms.
>
> ```pycon
> >>> data = {'key1': 'value1', 'key2': 'value2'}
> >>> r = httpx.post("https://httpbin.org/post", data=data)
> >>> print(r.text)
> {
>   ...
>   "form": {
>     "key2": "value2",
>     "key1": "value1"
>   },
>   ...
> }
> ```
>
> Form encoded data can also include multiple values from a given key.
>
> ```pycon
> >>> data = {'key1': ['value1', 'value2']}
> >>> r = httpx.post("https://httpbin.org/post", data=data)
> >>> print(r.text)
> {
>   ...
>   "form": {
>     "key1": [
>       "value1",
>       "value2"
>     ]
>   },
>   ...
> }
> ```

## C065 — candidate_holdout

Group: `form-encoded-request-data` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Does the form example use the json parameter or the data parameter?

**Draft reference/rubric:** It uses data= for form-encoded data; do not substitute the separate JSON request example.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending Form Encoded Data · lines 134–171
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L134-L171
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Sending Form Encoded Data
>
> Some types of HTTP requests, such as `POST` and `PUT` requests, can include data
> in the request body. One common way of including that is as form-encoded data,
> which is used for HTML forms.
>
> ```pycon
> >>> data = {'key1': 'value1', 'key2': 'value2'}
> >>> r = httpx.post("https://httpbin.org/post", data=data)
> >>> print(r.text)
> {
>   ...
>   "form": {
>     "key2": "value2",
>     "key1": "value1"
>   },
>   ...
> }
> ```
>
> Form encoded data can also include multiple values from a given key.
>
> ```pycon
> >>> data = {'key1': ['value1', 'value2']}
> >>> r = httpx.post("https://httpbin.org/post", data=data)
> >>> print(r.text)
> {
>   ...
>   "form": {
>     "key1": [
>       "value1",
>       "value2"
>     ]
>   },
>   ...
> }
> ```

## C066 — candidate_holdout

Group: `multipart-file-uploads` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which HTTPX parameter sends files using multipart encoding?

**Draft reference/rubric:** Use files= with the file mapping.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending Multipart File Uploads · lines 172–223
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L172-L223
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Sending Multipart File Uploads
>
> You can also upload files, using HTTP multipart encoding:
>
> ```pycon
> >>> files = {'upload-file': open('report.xls', 'rb')}
> >>> r = httpx.post("https://httpbin.org/post", files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "upload-file": "<... binary content ...>"
>   },
>   ...
> }
> ```
>
> You can also explicitly set the filename and content type, by using a tuple
> of items for the file value:
>
> ```pycon
> >>> files = {'upload-file': ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel')}
> >>> r = httpx.post("https://httpbin.org/post", files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "upload-file": "<... binary content ...>"
>   },
>   ...
> }
> ```
>
> If you need to include non-file data fields in the multipart form, use the `data=...` parameter:
>
> ```pycon
> >>> data = {'message': 'Hello, world!'}
> >>> files = {'file': open('report.xls', 'rb')}
> >>> r = httpx.post("https://httpbin.org/post", data=data, files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "file": "<... binary content ...>"
>   },
>   "form": {
>     "message": "Hello, world!",
>   },
>   ...
> }
> ```

## C067 — candidate_holdout

Group: `multipart-file-uploads` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How can I specify both a filename and content type for an uploaded file?

**Draft reference/rubric:** Use a tuple for the file mapping value; inspect the adjacent example for filename, binary file object and media type.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending Multipart File Uploads · lines 172–223
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L172-L223
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Sending Multipart File Uploads
>
> You can also upload files, using HTTP multipart encoding:
>
> ```pycon
> >>> files = {'upload-file': open('report.xls', 'rb')}
> >>> r = httpx.post("https://httpbin.org/post", files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "upload-file": "<... binary content ...>"
>   },
>   ...
> }
> ```
>
> You can also explicitly set the filename and content type, by using a tuple
> of items for the file value:
>
> ```pycon
> >>> files = {'upload-file': ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel')}
> >>> r = httpx.post("https://httpbin.org/post", files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "upload-file": "<... binary content ...>"
>   },
>   ...
> }
> ```
>
> If you need to include non-file data fields in the multipart form, use the `data=...` parameter:
>
> ```pycon
> >>> data = {'message': 'Hello, world!'}
> >>> files = {'file': open('report.xls', 'rb')}
> >>> r = httpx.post("https://httpbin.org/post", data=data, files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "file": "<... binary content ...>"
>   },
>   "form": {
>     "message": "Hello, world!",
>   },
>   ...
> }
> ```

## C068 — candidate_holdout

Group: `multipart-file-uploads` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How do I include ordinary fields alongside an uploaded file?

**Draft reference/rubric:** Pass non-file fields through data= alongside files=.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending Multipart File Uploads · lines 172–223
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L172-L223
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Sending Multipart File Uploads
>
> You can also upload files, using HTTP multipart encoding:
>
> ```pycon
> >>> files = {'upload-file': open('report.xls', 'rb')}
> >>> r = httpx.post("https://httpbin.org/post", files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "upload-file": "<... binary content ...>"
>   },
>   ...
> }
> ```
>
> You can also explicitly set the filename and content type, by using a tuple
> of items for the file value:
>
> ```pycon
> >>> files = {'upload-file': ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel')}
> >>> r = httpx.post("https://httpbin.org/post", files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "upload-file": "<... binary content ...>"
>   },
>   ...
> }
> ```
>
> If you need to include non-file data fields in the multipart form, use the `data=...` parameter:
>
> ```pycon
> >>> data = {'message': 'Hello, world!'}
> >>> files = {'file': open('report.xls', 'rb')}
> >>> r = httpx.post("https://httpbin.org/post", data=data, files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "file": "<... binary content ...>"
>   },
>   "form": {
>     "message": "Hello, world!",
>   },
>   ...
> }
> ```

## C069 — candidate_holdout

Group: `multipart-file-uploads` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** In what mode does the multipart example open report.xls?

**Draft reference/rubric:** The example opens the file in binary read mode, rb.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending Multipart File Uploads · lines 172–223
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L172-L223
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Sending Multipart File Uploads
>
> You can also upload files, using HTTP multipart encoding:
>
> ```pycon
> >>> files = {'upload-file': open('report.xls', 'rb')}
> >>> r = httpx.post("https://httpbin.org/post", files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "upload-file": "<... binary content ...>"
>   },
>   ...
> }
> ```
>
> You can also explicitly set the filename and content type, by using a tuple
> of items for the file value:
>
> ```pycon
> >>> files = {'upload-file': ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel')}
> >>> r = httpx.post("https://httpbin.org/post", files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "upload-file": "<... binary content ...>"
>   },
>   ...
> }
> ```
>
> If you need to include non-file data fields in the multipart form, use the `data=...` parameter:
>
> ```pycon
> >>> data = {'message': 'Hello, world!'}
> >>> files = {'file': open('report.xls', 'rb')}
> >>> r = httpx.post("https://httpbin.org/post", data=data, files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "file": "<... binary content ...>"
>   },
>   "form": {
>     "message": "Hello, world!",
>   },
>   ...
> }
> ```

## C070 — candidate_holdout

Group: `multipart-file-uploads` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Can one POST call contain both a file mapping and a text-field mapping?

**Draft reference/rubric:** Yes; the documented multipart example supplies data=data and files=files together.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending Multipart File Uploads · lines 172–223
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L172-L223
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Sending Multipart File Uploads
>
> You can also upload files, using HTTP multipart encoding:
>
> ```pycon
> >>> files = {'upload-file': open('report.xls', 'rb')}
> >>> r = httpx.post("https://httpbin.org/post", files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "upload-file": "<... binary content ...>"
>   },
>   ...
> }
> ```
>
> You can also explicitly set the filename and content type, by using a tuple
> of items for the file value:
>
> ```pycon
> >>> files = {'upload-file': ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel')}
> >>> r = httpx.post("https://httpbin.org/post", files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "upload-file": "<... binary content ...>"
>   },
>   ...
> }
> ```
>
> If you need to include non-file data fields in the multipart form, use the `data=...` parameter:
>
> ```pycon
> >>> data = {'message': 'Hello, world!'}
> >>> files = {'file': open('report.xls', 'rb')}
> >>> r = httpx.post("https://httpbin.org/post", data=data, files=files)
> >>> print(r.text)
> {
>   ...
>   "files": {
>     "file": "<... binary content ...>"
>   },
>   "form": {
>     "message": "Hello, world!",
>   },
>   ...
> }
> ```

## C071 — candidate_holdout

Group: `json-request-bodies` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How does the quickstart send a nested data structure as a JSON request body?

**Draft reference/rubric:** Pass the data structure through json=.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending JSON Encoded Data · lines 224–247
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L224-L247
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Sending JSON Encoded Data
>
> Form encoded data is okay if all you need is a simple key-value data structure.
> For more complicated data structures you'll often want to use JSON encoding instead.
>
> ```pycon
> >>> data = {'integer': 123, 'boolean': True, 'list': ['a', 'b', 'c']}
> >>> r = httpx.post("https://httpbin.org/post", json=data)
> >>> print(r.text)
> {
>   ...
>   "json": {
>     "boolean": true,
>     "integer": 123,
>     "list": [
>       "a",
>       "b",
>       "c"
>     ]
>   },
>   ...
> }
> ```

## C072 — candidate_holdout

Group: `json-request-bodies` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which keyword serializes the shown integer, boolean and list mapping as JSON?

**Draft reference/rubric:** Use json=data, as shown in the JSON request example.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending JSON Encoded Data · lines 224–247
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L224-L247
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Sending JSON Encoded Data
>
> Form encoded data is okay if all you need is a simple key-value data structure.
> For more complicated data structures you'll often want to use JSON encoding instead.
>
> ```pycon
> >>> data = {'integer': 123, 'boolean': True, 'list': ['a', 'b', 'c']}
> >>> r = httpx.post("https://httpbin.org/post", json=data)
> >>> print(r.text)
> {
>   ...
>   "json": {
>     "boolean": true,
>     "integer": 123,
>     "list": [
>       "a",
>       "b",
>       "c"
>     ]
>   },
>   ...
> }
> ```

## C073 — candidate_holdout

Group: `json-request-bodies` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Why does the guide suggest JSON instead of form encoding for more complicated data?

**Draft reference/rubric:** The guide recommends considering JSON for more complicated structures; do not invent unsupported serialization guarantees.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending JSON Encoded Data · lines 224–247
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L224-L247
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Sending JSON Encoded Data
>
> Form encoded data is okay if all you need is a simple key-value data structure.
> For more complicated data structures you'll often want to use JSON encoding instead.
>
> ```pycon
> >>> data = {'integer': 123, 'boolean': True, 'list': ['a', 'b', 'c']}
> >>> r = httpx.post("https://httpbin.org/post", json=data)
> >>> print(r.text)
> {
>   ...
>   "json": {
>     "boolean": true,
>     "integer": 123,
>     "list": [
>       "a",
>       "b",
>       "c"
>     ]
>   },
>   ...
> }
> ```

## C074 — candidate_holdout

Group: `json-request-bodies` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What request-body option is used for the example containing a list of a, b and c?

**Draft reference/rubric:** The example passes the mapping as json=data.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending JSON Encoded Data · lines 224–247
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L224-L247
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Sending JSON Encoded Data
>
> Form encoded data is okay if all you need is a simple key-value data structure.
> For more complicated data structures you'll often want to use JSON encoding instead.
>
> ```pycon
> >>> data = {'integer': 123, 'boolean': True, 'list': ['a', 'b', 'c']}
> >>> r = httpx.post("https://httpbin.org/post", json=data)
> >>> print(r.text)
> {
>   ...
>   "json": {
>     "boolean": true,
>     "integer": 123,
>     "list": [
>       "a",
>       "b",
>       "c"
>     ]
>   },
>   ...
> }
> ```

## C075 — candidate_holdout

Group: `json-request-bodies` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Should the complex JSON example be sent with data=data or json=data?

**Draft reference/rubric:** Use json=data for this example; data=data is used separately for form encoding.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Sending JSON Encoded Data · lines 224–247
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L224-L247
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Sending JSON Encoded Data
>
> Form encoded data is okay if all you need is a simple key-value data structure.
> For more complicated data structures you'll often want to use JSON encoding instead.
>
> ```pycon
> >>> data = {'integer': 123, 'boolean': True, 'list': ['a', 'b', 'c']}
> >>> r = httpx.post("https://httpbin.org/post", json=data)
> >>> print(r.text)
> {
>   ...
>   "json": {
>     "boolean": true,
>     "integer": 123,
>     "list": [
>       "a",
>       "b",
>       "c"
>     ]
>   },
>   ...
> }
> ```

## C076 — candidate_holdout

Group: `cookie-access-and-scope` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How can I inspect a cookie set on an HTTPX response?

**Draft reference/rubric:** Read the response.cookies mapping, as shown by r.cookies["chocolate"].

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Cookies · lines 384–414
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L384-L414
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Cookies
>
> Any cookies that are set on the response can be easily accessed:
>
> ```pycon
> >>> r = httpx.get('https://httpbin.org/cookies/set?chocolate=chip')
> >>> r.cookies['chocolate']
> 'chip'
> ```
>
> To include cookies in an outgoing request, use the `cookies` parameter:
>
> ```pycon
> >>> cookies = {"peanut": "butter"}
> >>> r = httpx.get('https://httpbin.org/cookies', cookies=cookies)
> >>> r.json()
> {'cookies': {'peanut': 'butter'}}
> ```
>
> Cookies are returned in a `Cookies` instance, which is a dict-like data structure
> with additional API for accessing cookies by their domain or path.
>
> ```pycon
> >>> cookies = httpx.Cookies()
> >>> cookies.set('cookie_on_domain', 'hello, there!', domain='httpbin.org')
> >>> cookies.set('cookie_off_domain', 'nope.', domain='example.org')
> >>> r = httpx.get('http://httpbin.org/cookies', cookies=cookies)
> >>> r.json()
> {'cookies': {'cookie_on_domain': 'hello, there!'}}
> ```

## C077 — candidate_holdout

Group: `cookie-access-and-scope` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Which request parameter includes a supplied cookie mapping?

**Draft reference/rubric:** Pass the mapping through cookies=.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Cookies · lines 384–414
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L384-L414
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Cookies
>
> Any cookies that are set on the response can be easily accessed:
>
> ```pycon
> >>> r = httpx.get('https://httpbin.org/cookies/set?chocolate=chip')
> >>> r.cookies['chocolate']
> 'chip'
> ```
>
> To include cookies in an outgoing request, use the `cookies` parameter:
>
> ```pycon
> >>> cookies = {"peanut": "butter"}
> >>> r = httpx.get('https://httpbin.org/cookies', cookies=cookies)
> >>> r.json()
> {'cookies': {'peanut': 'butter'}}
> ```
>
> Cookies are returned in a `Cookies` instance, which is a dict-like data structure
> with additional API for accessing cookies by their domain or path.
>
> ```pycon
> >>> cookies = httpx.Cookies()
> >>> cookies.set('cookie_on_domain', 'hello, there!', domain='httpbin.org')
> >>> cookies.set('cookie_off_domain', 'nope.', domain='example.org')
> >>> r = httpx.get('http://httpbin.org/cookies', cookies=cookies)
> >>> r.json()
> {'cookies': {'cookie_on_domain': 'hello, there!'}}
> ```

## C078 — candidate_holdout

Group: `cookie-access-and-scope` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** What object provides the cookie API for domain or path access?

**Draft reference/rubric:** Use the Cookies object, whose documented API includes domain/path access.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Cookies · lines 384–414
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L384-L414
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Cookies
>
> Any cookies that are set on the response can be easily accessed:
>
> ```pycon
> >>> r = httpx.get('https://httpbin.org/cookies/set?chocolate=chip')
> >>> r.cookies['chocolate']
> 'chip'
> ```
>
> To include cookies in an outgoing request, use the `cookies` parameter:
>
> ```pycon
> >>> cookies = {"peanut": "butter"}
> >>> r = httpx.get('https://httpbin.org/cookies', cookies=cookies)
> >>> r.json()
> {'cookies': {'peanut': 'butter'}}
> ```
>
> Cookies are returned in a `Cookies` instance, which is a dict-like data structure
> with additional API for accessing cookies by their domain or path.
>
> ```pycon
> >>> cookies = httpx.Cookies()
> >>> cookies.set('cookie_on_domain', 'hello, there!', domain='httpbin.org')
> >>> cookies.set('cookie_off_domain', 'nope.', domain='example.org')
> >>> r = httpx.get('http://httpbin.org/cookies', cookies=cookies)
> >>> r.json()
> {'cookies': {'cookie_on_domain': 'hello, there!'}}
> ```

## C079 — candidate_holdout

Group: `cookie-access-and-scope` · HTTPX `0.27.2` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** How does the example scope a cookie to httpbin.org?

**Draft reference/rubric:** Use Cookies.set with domain="httpbin.org", as shown in the example.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Cookies · lines 384–414
Pinned reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L384-L414
Local source file: [data/corpus/httpx/0.27.2/docs/quickstart.md](../../../data/corpus/httpx/0.27.2/docs/quickstart.md)

> ## Cookies
>
> Any cookies that are set on the response can be easily accessed:
>
> ```pycon
> >>> r = httpx.get('https://httpbin.org/cookies/set?chocolate=chip')
> >>> r.cookies['chocolate']
> 'chip'
> ```
>
> To include cookies in an outgoing request, use the `cookies` parameter:
>
> ```pycon
> >>> cookies = {"peanut": "butter"}
> >>> r = httpx.get('https://httpbin.org/cookies', cookies=cookies)
> >>> r.json()
> {'cookies': {'peanut': 'butter'}}
> ```
>
> Cookies are returned in a `Cookies` instance, which is a dict-like data structure
> with additional API for accessing cookies by their domain or path.
>
> ```pycon
> >>> cookies = httpx.Cookies()
> >>> cookies.set('cookie_on_domain', 'hello, there!', domain='httpbin.org')
> >>> cookies.set('cookie_off_domain', 'nope.', domain='example.org')
> >>> r = httpx.get('http://httpbin.org/cookies', cookies=cookies)
> >>> r.json()
> {'cookies': {'cookie_on_domain': 'hello, there!'}}
> ```

## C080 — candidate_holdout

Group: `cookie-access-and-scope` · HTTPX `0.28.1` · Profile: `public`
Category: `answerable` · Draft decision: **answer**

**Question:** Does the domain-scoping example send the example.org cookie to httpbin.org?

**Draft reference/rubric:** The shown response contains cookie_on_domain only; the example.org cookie is not included in that request.

**Review notes:** Candidate holdout, not executed. Confirm this intent is distinct from prior development prompts, inspect adjacent source context, and reject or revise ambiguous labels before approving.

Prior development overlap: None declared; verify this during review.

**Source:** `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Section: QuickStart > Cookies · lines 384–414
Pinned reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L384-L414
Local source file: [data/corpus/httpx/0.28.1/docs/quickstart.md](../../../data/corpus/httpx/0.28.1/docs/quickstart.md)

> ## Cookies
>
> Any cookies that are set on the response can be easily accessed:
>
> ```pycon
> >>> r = httpx.get('https://httpbin.org/cookies/set?chocolate=chip')
> >>> r.cookies['chocolate']
> 'chip'
> ```
>
> To include cookies in an outgoing request, use the `cookies` parameter:
>
> ```pycon
> >>> cookies = {"peanut": "butter"}
> >>> r = httpx.get('https://httpbin.org/cookies', cookies=cookies)
> >>> r.json()
> {'cookies': {'peanut': 'butter'}}
> ```
>
> Cookies are returned in a `Cookies` instance, which is a dict-like data structure
> with additional API for accessing cookies by their domain or path.
>
> ```pycon
> >>> cookies = httpx.Cookies()
> >>> cookies.set('cookie_on_domain', 'hello, there!', domain='httpbin.org')
> >>> cookies.set('cookie_off_domain', 'nope.', domain='example.org')
> >>> r = httpx.get('http://httpbin.org/cookies', cookies=cookies)
> >>> r.json()
> {'cookies': {'cookie_on_domain': 'hello, there!'}}
> ```

## C081 — candidate_holdout

Group: `unrecorded-adoption-statistics` · HTTPX `0.28.1` · Profile: `public`
Category: `missing_evidence` · Draft decision: **abstain**

**Question:** How many PyPI downloads did HTTPX 0.28.1 receive on 24 October 2026?

**Draft reference/rubric:** Abstain: the pinned corpus contains no measurement establishing this exact dated adoption statistic. Do not infer a count from defaults, badge links or general product descriptions.

**Review notes:** Candidate holdout, not executed. This asks for an exact external adoption measurement, a distinct intent from prior unsupported-feature probes. Source pages may contain links or badges, but those do not establish the requested dated count. Confirm bounded-corpus absence during human review.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C082 — candidate_holdout

Group: `unrecorded-adoption-statistics` · HTTPX `0.27.2` · Profile: `public`
Category: `missing_evidence` · Draft decision: **abstain**

**Question:** How many active production users ran HTTPX 0.27.2 during September 2026?

**Draft reference/rubric:** Abstain: the pinned corpus contains no measurement establishing this exact dated adoption statistic. Do not infer a count from defaults, badge links or general product descriptions.

**Review notes:** Candidate holdout, not executed. This asks for an exact external adoption measurement, a distinct intent from prior unsupported-feature probes. Source pages may contain links or badges, but those do not establish the requested dated count. Confirm bounded-corpus absence during human review.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C083 — candidate_holdout

Group: `unrecorded-adoption-statistics` · HTTPX `0.28.1` · Profile: `public`
Category: `missing_evidence` · Draft decision: **abstain**

**Question:** What exact GitHub stargazer count did HTTPX have at 12:00 UTC on 24 October 2026?

**Draft reference/rubric:** Abstain: the pinned corpus contains no measurement establishing this exact dated adoption statistic. Do not infer a count from defaults, badge links or general product descriptions.

**Review notes:** Candidate holdout, not executed. This asks for an exact external adoption measurement, a distinct intent from prior unsupported-feature probes. Source pages may contain links or badges, but those do not establish the requested dated count. Confirm bounded-corpus absence during human review.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C084 — candidate_holdout

Group: `unrecorded-adoption-statistics` · HTTPX `0.27.2` · Profile: `public`
Category: `missing_evidence` · Draft decision: **abstain**

**Question:** How many HTTP requests were made worldwide with HTTPX 0.27.2 on 23 October 2026?

**Draft reference/rubric:** Abstain: the pinned corpus contains no measurement establishing this exact dated adoption statistic. Do not infer a count from defaults, badge links or general product descriptions.

**Review notes:** Candidate holdout, not executed. This asks for an exact external adoption measurement, a distinct intent from prior unsupported-feature probes. Source pages may contain links or badges, but those do not establish the requested dated count. Confirm bounded-corpus absence during human review.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C085 — candidate_holdout

Group: `unrecorded-adoption-statistics` · HTTPX `0.28.1` · Profile: `public`
Category: `missing_evidence` · Draft decision: **abstain**

**Question:** What was the exact number of distinct organizations using HTTPX 0.28.1 in production during September 2026?

**Draft reference/rubric:** Abstain: the pinned corpus contains no measurement establishing this exact dated adoption statistic. Do not infer a count from defaults, badge links or general product descriptions.

**Review notes:** Candidate holdout, not executed. This asks for an exact external adoption measurement, a distinct intent from prior unsupported-feature probes. Source pages may contain links or badges, but those do not establish the requested dated count. Confirm bounded-corpus absence during human review.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C086 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.28.1` · Profile: `support`
Category: `conflicting_evidence` · Draft decision: **abstain**

**Question:** What is the cobaltbridge lease window in the synthetic evaluation scenario?

**Draft reference/rubric:** Abstain: the two same-version fictional policies have equal authority but contradict one another (12 versus 18 seconds). Neither source supplies a precedence rule.

**Review notes:** Candidate holdout, not executed. This is fictional support-only evidence. A single ranked policy is not sufficient to resolve the contradictory record.

Prior development overlap: None declared; verify this during review.

**Source:** `synthetic:httpx:0.28.1:cobaltbridge-a.md` · SHA-256 `d28eba885d0b46f6c972783fbcb0e8cb87572bd7c7d86157142b780e15f76d3f`
Section: SYNTHETIC DEMO: Cobaltbridge policy A · lines 1–7
Pinned reference: /api/chunks/b324cdd5fd47dfe629cfb315?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/cobaltbridge-a.md](../../../data/synthetic/httpx/0.28.1/cobaltbridge-a.md)

> # SYNTHETIC DEMO: Cobaltbridge policy A
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 12 seconds.
>
> The cobaltbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

**Source:** `synthetic:httpx:0.28.1:cobaltbridge-b.md` · SHA-256 `fecae22a61800939804c86a76719a02eb969f63ac52c6e8cd8f926dce3729945`
Section: SYNTHETIC DEMO: Cobaltbridge policy B · lines 1–7
Pinned reference: /api/chunks/9f1f9a411ed1d93fa54663c8?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/cobaltbridge-b.md](../../../data/synthetic/httpx/0.28.1/cobaltbridge-b.md)

> # SYNTHETIC DEMO: Cobaltbridge policy B
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 18 seconds.
>
> The cobaltbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

## C087 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.28.1` · Profile: `support`
Category: `conflicting_evidence` · Draft decision: **abstain**

**Question:** Which lease duration applies to the fictional cobaltbridge policy?

**Draft reference/rubric:** Abstain: the two same-version fictional policies have equal authority but contradict one another (12 versus 18 seconds). Neither source supplies a precedence rule.

**Review notes:** Candidate holdout, not executed. This is fictional support-only evidence. A single ranked policy is not sufficient to resolve the contradictory record.

Prior development overlap: None declared; verify this during review.

**Source:** `synthetic:httpx:0.28.1:cobaltbridge-a.md` · SHA-256 `d28eba885d0b46f6c972783fbcb0e8cb87572bd7c7d86157142b780e15f76d3f`
Section: SYNTHETIC DEMO: Cobaltbridge policy A · lines 1–7
Pinned reference: /api/chunks/b324cdd5fd47dfe629cfb315?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/cobaltbridge-a.md](../../../data/synthetic/httpx/0.28.1/cobaltbridge-a.md)

> # SYNTHETIC DEMO: Cobaltbridge policy A
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 12 seconds.
>
> The cobaltbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

**Source:** `synthetic:httpx:0.28.1:cobaltbridge-b.md` · SHA-256 `fecae22a61800939804c86a76719a02eb969f63ac52c6e8cd8f926dce3729945`
Section: SYNTHETIC DEMO: Cobaltbridge policy B · lines 1–7
Pinned reference: /api/chunks/9f1f9a411ed1d93fa54663c8?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/cobaltbridge-b.md](../../../data/synthetic/httpx/0.28.1/cobaltbridge-b.md)

> # SYNTHETIC DEMO: Cobaltbridge policy B
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 18 seconds.
>
> The cobaltbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

## C088 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.28.1` · Profile: `support`
Category: `conflicting_evidence` · Draft decision: **abstain**

**Question:** Can you give one supported lease-window value for cobaltbridge?

**Draft reference/rubric:** Abstain: the two same-version fictional policies have equal authority but contradict one another (12 versus 18 seconds). Neither source supplies a precedence rule.

**Review notes:** Candidate holdout, not executed. This is fictional support-only evidence. A single ranked policy is not sufficient to resolve the contradictory record.

Prior development overlap: None declared; verify this during review.

**Source:** `synthetic:httpx:0.28.1:cobaltbridge-a.md` · SHA-256 `d28eba885d0b46f6c972783fbcb0e8cb87572bd7c7d86157142b780e15f76d3f`
Section: SYNTHETIC DEMO: Cobaltbridge policy A · lines 1–7
Pinned reference: /api/chunks/b324cdd5fd47dfe629cfb315?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/cobaltbridge-a.md](../../../data/synthetic/httpx/0.28.1/cobaltbridge-a.md)

> # SYNTHETIC DEMO: Cobaltbridge policy A
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 12 seconds.
>
> The cobaltbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

**Source:** `synthetic:httpx:0.28.1:cobaltbridge-b.md` · SHA-256 `fecae22a61800939804c86a76719a02eb969f63ac52c6e8cd8f926dce3729945`
Section: SYNTHETIC DEMO: Cobaltbridge policy B · lines 1–7
Pinned reference: /api/chunks/9f1f9a411ed1d93fa54663c8?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/cobaltbridge-b.md](../../../data/synthetic/httpx/0.28.1/cobaltbridge-b.md)

> # SYNTHETIC DEMO: Cobaltbridge policy B
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 18 seconds.
>
> The cobaltbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

## C089 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.28.1` · Profile: `support`
Category: `conflicting_evidence` · Draft decision: **abstain**

**Question:** What single lease-window duration should the synthetic cobaltbridge client use?

**Draft reference/rubric:** Abstain: the two same-version fictional policies have equal authority but contradict one another (12 versus 18 seconds). Neither source supplies a precedence rule.

**Review notes:** Candidate holdout, not executed. This is fictional support-only evidence. A single ranked policy is not sufficient to resolve the contradictory record.

Prior development overlap: None declared; verify this during review.

**Source:** `synthetic:httpx:0.28.1:cobaltbridge-a.md` · SHA-256 `d28eba885d0b46f6c972783fbcb0e8cb87572bd7c7d86157142b780e15f76d3f`
Section: SYNTHETIC DEMO: Cobaltbridge policy A · lines 1–7
Pinned reference: /api/chunks/b324cdd5fd47dfe629cfb315?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/cobaltbridge-a.md](../../../data/synthetic/httpx/0.28.1/cobaltbridge-a.md)

> # SYNTHETIC DEMO: Cobaltbridge policy A
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 12 seconds.
>
> The cobaltbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

**Source:** `synthetic:httpx:0.28.1:cobaltbridge-b.md` · SHA-256 `fecae22a61800939804c86a76719a02eb969f63ac52c6e8cd8f926dce3729945`
Section: SYNTHETIC DEMO: Cobaltbridge policy B · lines 1–7
Pinned reference: /api/chunks/9f1f9a411ed1d93fa54663c8?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/cobaltbridge-b.md](../../../data/synthetic/httpx/0.28.1/cobaltbridge-b.md)

> # SYNTHETIC DEMO: Cobaltbridge policy B
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 18 seconds.
>
> The cobaltbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

## C090 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.28.1` · Profile: `support`
Category: `conflicting_evidence` · Draft decision: **abstain**

**Question:** State the lease window required by the cobaltbridge evaluation policy.

**Draft reference/rubric:** Abstain: the two same-version fictional policies have equal authority but contradict one another (12 versus 18 seconds). Neither source supplies a precedence rule.

**Review notes:** Candidate holdout, not executed. This is fictional support-only evidence. A single ranked policy is not sufficient to resolve the contradictory record.

Prior development overlap: None declared; verify this during review.

**Source:** `synthetic:httpx:0.28.1:cobaltbridge-a.md` · SHA-256 `d28eba885d0b46f6c972783fbcb0e8cb87572bd7c7d86157142b780e15f76d3f`
Section: SYNTHETIC DEMO: Cobaltbridge policy A · lines 1–7
Pinned reference: /api/chunks/b324cdd5fd47dfe629cfb315?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/cobaltbridge-a.md](../../../data/synthetic/httpx/0.28.1/cobaltbridge-a.md)

> # SYNTHETIC DEMO: Cobaltbridge policy A
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 12 seconds.
>
> The cobaltbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

**Source:** `synthetic:httpx:0.28.1:cobaltbridge-b.md` · SHA-256 `fecae22a61800939804c86a76719a02eb969f63ac52c6e8cd8f926dce3729945`
Section: SYNTHETIC DEMO: Cobaltbridge policy B · lines 1–7
Pinned reference: /api/chunks/9f1f9a411ed1d93fa54663c8?version=0.28.1
Local source file: [data/synthetic/httpx/0.28.1/cobaltbridge-b.md](../../../data/synthetic/httpx/0.28.1/cobaltbridge-b.md)

> # SYNTHETIC DEMO: Cobaltbridge policy B
>
> This is fictional evaluation material, not official HTTPX guidance or a real organization policy.
>
> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 18 seconds.
>
> The cobaltbridge A and B evaluation policies have equal authority and the same applicability. Neither record supersedes the other.

## C091 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.27.2` · Profile: `support`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** Using only snapshot 0.27.2, give the cobaltbridge lease window from its later 0.28.1 policy.

**Draft reference/rubric:** Abstain: cobaltbridge fixtures exist only for 0.28.1; no selected 0.27.2 evidence can supply their later facts.

**Review notes:** Candidate holdout, not executed. The future document is synthetic rather than a claim about actual HTTPX release capabilities. Keep its version variants and permission variants in this same group.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C092 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.27.2` · Profile: `support`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** From the older 0.27.2 evidence, quote the synthetic cobaltbridge policy introduced only in the 0.28.1 fixtures.

**Draft reference/rubric:** Abstain: cobaltbridge fixtures exist only for 0.28.1; no selected 0.27.2 evidence can supply their later facts.

**Review notes:** Candidate holdout, not executed. The future document is synthetic rather than a claim about actual HTTPX release capabilities. Keep its version variants and permission variants in this same group.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C093 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.27.2` · Profile: `support`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** What cobaltbridge lease window does the future 0.28.1 fixture prescribe, using only selected snapshot 0.27.2?

**Draft reference/rubric:** Abstain: cobaltbridge fixtures exist only for 0.28.1; no selected 0.27.2 evidence can supply their later facts.

**Review notes:** Candidate holdout, not executed. The future document is synthetic rather than a claim about actual HTTPX release capabilities. Keep its version variants and permission variants in this same group.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C094 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.27.2` · Profile: `support`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** Can the selected 0.27.2 documents establish a lease duration for the later synthetic cobaltbridge scenario?

**Draft reference/rubric:** Abstain: cobaltbridge fixtures exist only for 0.28.1; no selected 0.27.2 evidence can supply their later facts.

**Review notes:** Candidate holdout, not executed. The future document is synthetic rather than a claim about actual HTTPX release capabilities. Keep its version variants and permission variants in this same group.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C095 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.27.2` · Profile: `support`
Category: `wrong_version_trap` · Draft decision: **abstain**

**Question:** Verify the newer 0.28.1 cobaltbridge lease policy from the currently selected older snapshot.

**Draft reference/rubric:** Abstain: cobaltbridge fixtures exist only for 0.28.1; no selected 0.27.2 evidence can supply their later facts.

**Review notes:** Candidate holdout, not executed. The future document is synthetic rather than a claim about actual HTTPX release capabilities. Keep its version variants and permission variants in this same group.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C096 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.28.1` · Profile: `public`
Category: `permission_denied` · Draft decision: **abstain**

**Question:** What is the cobaltbridge lease window in the synthetic evaluation scenario?

**Draft reference/rubric:** Abstain: this public profile cannot access either support-only cobaltbridge fixture. Do not expose their facts, text or known source IDs.

**Review notes:** Candidate holdout, not executed. Matching support-profile questions intentionally repeat across profiles to test access; both belong to the same holdout group. Protected fixtures: synthetic:httpx:0.28.1:cobaltbridge-a.md and cobaltbridge-b.md.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C097 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.28.1` · Profile: `public`
Category: `permission_denied` · Draft decision: **abstain**

**Question:** Which lease duration applies to the fictional cobaltbridge policy?

**Draft reference/rubric:** Abstain: this public profile cannot access either support-only cobaltbridge fixture. Do not expose their facts, text or known source IDs.

**Review notes:** Candidate holdout, not executed. Matching support-profile questions intentionally repeat across profiles to test access; both belong to the same holdout group. Protected fixtures: synthetic:httpx:0.28.1:cobaltbridge-a.md and cobaltbridge-b.md.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C098 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.28.1` · Profile: `public`
Category: `permission_denied` · Draft decision: **abstain**

**Question:** Can you give one supported lease-window value for cobaltbridge?

**Draft reference/rubric:** Abstain: this public profile cannot access either support-only cobaltbridge fixture. Do not expose their facts, text or known source IDs.

**Review notes:** Candidate holdout, not executed. Matching support-profile questions intentionally repeat across profiles to test access; both belong to the same holdout group. Protected fixtures: synthetic:httpx:0.28.1:cobaltbridge-a.md and cobaltbridge-b.md.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C099 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.28.1` · Profile: `public`
Category: `permission_denied` · Draft decision: **abstain**

**Question:** What single lease-window duration should the synthetic cobaltbridge client use?

**Draft reference/rubric:** Abstain: this public profile cannot access either support-only cobaltbridge fixture. Do not expose their facts, text or known source IDs.

**Review notes:** Candidate holdout, not executed. Matching support-profile questions intentionally repeat across profiles to test access; both belong to the same holdout group. Protected fixtures: synthetic:httpx:0.28.1:cobaltbridge-a.md and cobaltbridge-b.md.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.

## C100 — candidate_holdout

Group: `candidate-cobaltbridge-policy` · HTTPX `0.28.1` · Profile: `public`
Category: `permission_denied` · Draft decision: **abstain**

**Question:** State the lease window required by the cobaltbridge evaluation policy.

**Draft reference/rubric:** Abstain: this public profile cannot access either support-only cobaltbridge fixture. Do not expose their facts, text or known source IDs.

**Review notes:** Candidate holdout, not executed. Matching support-profile questions intentionally repeat across profiles to test access; both belong to the same holdout group. Protected fixtures: synthetic:httpx:0.28.1:cobaltbridge-a.md and cobaltbridge-b.md.

Prior development overlap: None declared; verify this during review.

No positive answer anchor is supplied. Check the stated absence,
snapshot or permission boundary; nearest neighbors are not proof of support.
