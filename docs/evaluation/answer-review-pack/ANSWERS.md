# Pending human answer review

**No claim has been approved or judged semantically supported.**

Evaluation report SHA-256: `ff5235665571ef71323df4a6dccf2bd3f9785910925aabcd560133b85b549771`

Check support for each entire claim against its quoted source and surrounding
versioned document. Separately judge factual/release correctness. A real quote
alone does not establish either. Mark unsupported or incorrect claims honestly;
completing a review is not endorsing the generated answer.

The unsupported-answer denominator contains answered case/method trials only.
Abstentions and errors are reported separately, not counted as correct answers.
These outputs are development observations and remain development after review.
Use review-template.json as a copy, preserve digests, and fill completed status,
reviewer_type human, reviewer, timezone-aware timestamp and claim booleans.

## C001 · keyword

HTTPX `0.28.1` · Profile `public`
**Question:** What is the documented default network-inactivity timeout?

### Claim 0

The documented default network-inactivity timeout is 5 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:docs/advanced/timeouts.md` · SHA-256 `48959a587ecc6430f9051ab1b1c76fcebc3f3e95ec01199281aab813a2dcfaa1`
Version `0.28.1` · Timeouts · lines 1–5
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/advanced/timeouts.md?plain=1#L1-L5

> The default behavior is to raise a `TimeoutException` after 5 seconds of
> network inactivity.

## C001 · vector

HTTPX `0.28.1` · Profile `public`
**Question:** What is the documented default network-inactivity timeout?

### Claim 0

The documented default network-inactivity timeout is five seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:docs/advanced/timeouts.md` · SHA-256 `48959a587ecc6430f9051ab1b1c76fcebc3f3e95ec01199281aab813a2dcfaa1`
Version `0.28.1` · Timeouts · lines 1–5
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/advanced/timeouts.md?plain=1#L1-L5

> The default behavior is to raise a `TimeoutException` after 5 seconds of
> network inactivity.

## C001 · hybrid

HTTPX `0.28.1` · Profile `public`
**Question:** What is the documented default network-inactivity timeout?

### Claim 0

The documented default network-inactivity timeout is 5 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:docs/advanced/timeouts.md` · SHA-256 `48959a587ecc6430f9051ab1b1c76fcebc3f3e95ec01199281aab813a2dcfaa1`
Version `0.28.1` · Timeouts · lines 1–5
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/advanced/timeouts.md?plain=1#L1-L5

> The default behavior is to raise a `TimeoutException` after 5 seconds of
> network inactivity.

## C002 · vector

HTTPX `0.27.2` · Profile `public`
**Question:** How long does HTTPX allow network inactivity before its default timeout?

### Claim 0

The default timeout for network inactivity is five seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Version `0.27.2` · QuickStart > Timeouts · lines 448–468
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L448-L468

> The default timeout for network inactivity is five seconds. You can modify the
> value to be more or less strict:

## C003 · hybrid

HTTPX `0.28.1` · Profile `public`
**Question:** Does the five-second default describe network inactivity or the entire download duration?

### Claim 0

The five-second default describes network inactivity.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:docs/advanced/timeouts.md` · SHA-256 `48959a587ecc6430f9051ab1b1c76fcebc3f3e95ec01199281aab813a2dcfaa1`
Version `0.28.1` · Timeouts · lines 1–5
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/advanced/timeouts.md?plain=1#L1-L5

> The default behavior is to raise a `TimeoutException` after 5 seconds of
> network inactivity.

## C004 · vector

HTTPX `0.27.2` · Profile `public`
**Question:** Which default timeout is documented when no timeout option is supplied?

### Claim 0

The default timeout for network inactivity is five seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Version `0.27.2` · QuickStart > Timeouts · lines 448–468
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L448-L468

> The default timeout for network inactivity is five seconds. You can modify the
> value to be more or less strict:

## C004 · hybrid

HTTPX `0.27.2` · Profile `public`
**Question:** Which default timeout is documented when no timeout option is supplied?

### Claim 0

The default timeout is 5 seconds for network inactivity.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Version `0.27.2` · QuickStart > Timeouts · lines 448–468
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/quickstart.md?plain=1#L448-L468

> The default timeout for network inactivity is five seconds. You can modify the
> value to be more or less strict:

## C005 · vector

HTTPX `0.28.1` · Profile `public`
**Question:** What timeout value should I expect from the quickstart defaults?

### Claim 0

HTTPX defaults to including reasonable timeouts for all network operations, meaning that if a connection is not properly established then it should always raise an error rather than hanging indefinitely.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:docs/compatibility.md` · SHA-256 `e30d0a254fc89e5a891739607e289432b48930ac68be285810dd4e540f304776`
Version `0.28.1` · Requests Compatibility Guide > Timeouts · lines 148–157
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/compatibility.md?plain=1#L148-L157

> HTTPX defaults to including reasonable [timeouts](quickstart.md#timeouts) for all network operations, while Requests has no timeouts by default.

### Claim 1

The default timeout for network inactivity is five seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:docs/quickstart.md` · SHA-256 `9f8351551dd18be0ed7e40dea2f1c231523a2e8833a0bb5c471630178ec2aea8`
Version `0.28.1` · QuickStart > Timeouts · lines 448–468
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/quickstart.md?plain=1#L448-L468

> The default timeout for network inactivity is five seconds. You can modify the
> value to be more or less strict:

## C007 · keyword

HTTPX `0.27.2` · Profile `public`
**Question:** What replacement for the deprecated proxies argument is mentioned in the changelog?

### Claim 0

The `proxy` argument is the replacement for the deprecated `proxies` argument.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.26.0 (20th December, 2023) > Added · lines 37–40
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L37-L40

> * The `proxy` argument was added. You should use the `proxy` argument instead of the deprecated `proxies`, or use `mounts=` for more complex configurations. (#2879)

## C007 · vector

HTTPX `0.27.2` · Profile `public`
**Question:** What replacement for the deprecated proxies argument is mentioned in the changelog?

### Claim 0

The `proxy` argument is the replacement for the deprecated `proxies` argument.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.26.0 (20th December, 2023) > Added · lines 37–40
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L37-L40

> * The `proxy` argument was added. You should use the `proxy` argument instead of the deprecated `proxies`, or use `mounts=` for more complex configurations. (#2879)

## C007 · hybrid

HTTPX `0.27.2` · Profile `public`
**Question:** What replacement for the deprecated proxies argument is mentioned in the changelog?

### Claim 0

The `proxy` argument is the replacement for the deprecated `proxies` argument.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.26.0 (20th December, 2023) > Added · lines 37–40
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L37-L40

> * The `proxy` argument was added. You should use the `proxy` argument instead of the deprecated `proxies`, or use `mounts=` for more complex configurations. (#2879)

## C008 · vector

HTTPX `0.27.2` · Profile `public`
**Question:** Was proxies already removed at the time of this selected version?

### Claim 0

Proxies were removed at the time of this selected version.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.26.0 (20th December, 2023) > Deprecated · lines 41–44
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L41-L44

> * The `proxies` argument is now deprecated. It will still continue to work, but it will be removed in the future. (#2879)

## C008 · hybrid

HTTPX `0.27.2` · Profile `public`
**Question:** Was proxies already removed at the time of this selected version?

### Claim 0

Proxies were removed in version 0.27.2.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.7.6 (November 2, 2019) > Removed · lines 952–955
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L952-L955

> - Drop `proxies` parameter from the high-level API. (Pull #485)

## C013 · vector

HTTPX `0.27.2` · Profile `public`
**Question:** Quote the 0.28.0 proxies-removal entry from the selected 0.27.2 snapshot.

### Claim 0

The `proxies` parameter was removed in the high-level API in version 0.27.2.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.7.6 (November 2, 2019) > Removed · lines 952–955
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L952-L955

> - Drop `proxies` parameter from the high-level API. (Pull #485)

## C013 · hybrid

HTTPX `0.27.2` · Profile `public`
**Question:** Quote the 0.28.0 proxies-removal entry from the selected 0.27.2 snapshot.

### Claim 0

The `proxies` parameter was removed from the high-level API in version 0.27.2.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.7.6 (November 2, 2019) > Removed · lines 952–955
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L952-L955

> - Drop `proxies` parameter from the high-level API. (Pull #485)

## C014 · keyword

HTTPX `0.27.2` · Profile `public`
**Question:** What does the selected 0.27.2 documentation say about proxies being removed in the future 0.28.0 release?

### Claim 0

The `proxies` argument is now deprecated and will be removed in the future.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.26.0 (20th December, 2023) > Deprecated · lines 41–44
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L41-L44

> * The `proxies` argument is now deprecated. It will still continue to work, but it will be removed in the future. (#2879)

## C014 · vector

HTTPX `0.27.2` · Profile `public`
**Question:** What does the selected 0.27.2 documentation say about proxies being removed in the future 0.28.0 release?

### Claim 0

The `proxies` argument is now deprecated and will be removed in the future.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.26.0 (20th December, 2023) > Deprecated · lines 41–44
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L41-L44

> * The `proxies` argument is now deprecated. It will still continue to work, but it will be removed in the future. (#2879)

## C014 · hybrid

HTTPX `0.27.2` · Profile `public`
**Question:** What does the selected 0.27.2 documentation say about proxies being removed in the future 0.28.0 release?

### Claim 0

The `proxies` argument is now deprecated and will be removed in the future.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.26.0 (20th December, 2023) > Deprecated · lines 41–44
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L41-L44

> * The `proxies` argument is now deprecated. It will still continue to work, but it will be removed in the future. (#2879)

## C015 · vector

HTTPX `0.27.2` · Profile `public`
**Question:** From this older snapshot, confirm the later removal of proxies in 0.28.0.

### Claim 0

The `proxies` argument is now deprecated and will be removed in the future.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.26.0 (20th December, 2023) > Deprecated · lines 41–44
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L41-L44

> * The `proxies` argument is now deprecated. It will still continue to work, but it will be removed in the future. (#2879)

## C015 · hybrid

HTTPX `0.27.2` · Profile `public`
**Question:** From this older snapshot, confirm the later removal of proxies in 0.28.0.

### Claim 0

The `proxies` parameter was removed in 0.28.0.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.7.6 (November 2, 2019) > Removed · lines 952–955
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L952-L955

> - Drop `proxies` parameter from the high-level API. (Pull #485)

## C016 · keyword

HTTPX `0.27.2` · Profile `support`
**Question:** In the synthetic orchidrelay demo, what is the retry budget?

### Claim 0

In the synthetic orchidrelay demo, the retry budget is 2 attempts.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.27.2:orchidrelay.md` · SHA-256 `ca9dc33427368b866df338f8b74ea39d99446e5795fe99d1ca9f009564e6a41d`
Version `0.27.2` · SYNTHETIC DEMO: Orchidrelay support runbook · lines 1–5
Reference: /api/chunks/7ea92265e087a7f5baf43640?version=0.27.2

> In the synthetic demo for HTTPX 0.27.2, the orchidrelay retry budget is 2 attempts.

## C016 · vector

HTTPX `0.27.2` · Profile `support`
**Question:** In the synthetic orchidrelay demo, what is the retry budget?

### Claim 0

In the synthetic orchidrelay demo, the retry budget is 2 attempts.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.27.2:orchidrelay.md` · SHA-256 `ca9dc33427368b866df338f8b74ea39d99446e5795fe99d1ca9f009564e6a41d`
Version `0.27.2` · SYNTHETIC DEMO: Orchidrelay support runbook · lines 1–5
Reference: /api/chunks/7ea92265e087a7f5baf43640?version=0.27.2

> In the synthetic demo for HTTPX 0.27.2, the orchidrelay retry budget is 2 attempts.

## C016 · hybrid

HTTPX `0.27.2` · Profile `support`
**Question:** In the synthetic orchidrelay demo, what is the retry budget?

### Claim 0

In the synthetic orchidrelay demo, the retry budget is 2 attempts.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.27.2:orchidrelay.md` · SHA-256 `ca9dc33427368b866df338f8b74ea39d99446e5795fe99d1ca9f009564e6a41d`
Version `0.27.2` · SYNTHETIC DEMO: Orchidrelay support runbook · lines 1–5
Reference: /api/chunks/7ea92265e087a7f5baf43640?version=0.27.2

> In the synthetic demo for HTTPX 0.27.2, the orchidrelay retry budget is 2 attempts.

## C017 · keyword

HTTPX `0.28.1` · Profile `support`
**Question:** Which retry budget applies to the newer synthetic orchidrelay scenario?

### Claim 0

The retry budget for the newer synthetic orchidrelay scenario is 3 attempts.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:orchidrelay.md` · SHA-256 `66ff856f5f551fb3c036b167d38058b5d8a7c8af5be166df278e1efbcc2bbe06`
Version `0.28.1` · SYNTHETIC DEMO: Orchidrelay support runbook · lines 1–5
Reference: /api/chunks/c2b628e0c6b549d0bfe325b9?version=0.28.1

> In the synthetic demo for HTTPX 0.28.1, the orchidrelay retry budget is 3 attempts.

## C017 · vector

HTTPX `0.28.1` · Profile `support`
**Question:** Which retry budget applies to the newer synthetic orchidrelay scenario?

### Claim 0

The retry budget for the newer synthetic orchidrelay scenario is 3 attempts.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:orchidrelay.md` · SHA-256 `66ff856f5f551fb3c036b167d38058b5d8a7c8af5be166df278e1efbcc2bbe06`
Version `0.28.1` · SYNTHETIC DEMO: Orchidrelay support runbook · lines 1–5
Reference: /api/chunks/c2b628e0c6b549d0bfe325b9?version=0.28.1

> In the synthetic demo for HTTPX 0.28.1, the orchidrelay retry budget is 3 attempts.

## C017 · hybrid

HTTPX `0.28.1` · Profile `support`
**Question:** Which retry budget applies to the newer synthetic orchidrelay scenario?

### Claim 0

The retry budget for the newer synthetic orchidrelay scenario is 3 attempts.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:orchidrelay.md` · SHA-256 `66ff856f5f551fb3c036b167d38058b5d8a7c8af5be166df278e1efbcc2bbe06`
Version `0.28.1` · SYNTHETIC DEMO: Orchidrelay support runbook · lines 1–5
Reference: /api/chunks/c2b628e0c6b549d0bfe325b9?version=0.28.1

> In the synthetic demo for HTTPX 0.28.1, the orchidrelay retry budget is 3 attempts.

## C022 · keyword

HTTPX `0.27.2` · Profile `public`
**Question:** Explain quantumgiraffeunsupported using the selected documentation.

### Claim 0

Quantumgiraffeunsupported is not supported in version 0.27.2.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.23.0 (23rd May, 2022) > Changed · lines 162–166
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L162-L166

> * Drop support for Python 3.6. (#2097)
> * Use `utf-8` as the default character set, instead of falling back to `charset-normalizer` for auto-detection. To enable automatic character set detection, see [the documentation](https://www.python-httpx.org/advanced/text-encodings/#using-auto-detection). (#2165)

## C025 · keyword

HTTPX `0.28.1` · Profile `public`
**Question:** Can you cite a setup guide for quantumgiraffeunsupported?

### Claim 0

HTTPX aims to be broadly compatible with the `requests` API, although there are a few design differences in places.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:docs/compatibility.md` · SHA-256 `e30d0a254fc89e5a891739607e289432b48930ac68be285810dd4e540f304776`
Version `0.28.1` · Requests Compatibility Guide · lines 1–7
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/compatibility.md?plain=1#L1-L7

> HTTPX aims to be broadly compatible with the `requests` API, although there are a
> few design differences in places.

## C026 · keyword

HTTPX `0.28.1` · Profile `support`
**Question:** What is the quartzbridge lease window in the synthetic evaluation scenario?

### Claim 0

The quartzbridge lease window in the synthetic evaluation scenario is 6 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.

## C026 · vector

HTTPX `0.28.1` · Profile `support`
**Question:** What is the quartzbridge lease window in the synthetic evaluation scenario?

### Claim 0

The quartzbridge lease window in the synthetic evaluation scenario is 6 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.

## C026 · hybrid

HTTPX `0.28.1` · Profile `support`
**Question:** What is the quartzbridge lease window in the synthetic evaluation scenario?

### Claim 0

The quartzbridge lease window in the synthetic evaluation scenario is 6 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.

## C027 · keyword

HTTPX `0.28.1` · Profile `support`
**Question:** Resolve the two equal-authority quartzbridge lease-window policies for this snapshot.

### Claim 0

The quartzbridge lease window is 6 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.

### Claim 1

The cobaltbridge lease window is 12 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:cobaltbridge-a.md` · SHA-256 `d28eba885d0b46f6c972783fbcb0e8cb87572bd7c7d86157142b780e15f76d3f`
Version `0.28.1` · SYNTHETIC DEMO: Cobaltbridge policy A · lines 1–7
Reference: /api/chunks/b324cdd5fd47dfe629cfb315?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 12 seconds.

## C027 · vector

HTTPX `0.28.1` · Profile `support`
**Question:** Resolve the two equal-authority quartzbridge lease-window policies for this snapshot.

### Claim 0

The quartzbridge lease window is 6 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.

### Claim 1

The cobaltbridge lease window is 12 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:cobaltbridge-a.md` · SHA-256 `d28eba885d0b46f6c972783fbcb0e8cb87572bd7c7d86157142b780e15f76d3f`
Version `0.28.1` · SYNTHETIC DEMO: Cobaltbridge policy A · lines 1–7
Reference: /api/chunks/b324cdd5fd47dfe629cfb315?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 12 seconds.

## C027 · hybrid

HTTPX `0.28.1` · Profile `support`
**Question:** Resolve the two equal-authority quartzbridge lease-window policies for this snapshot.

### Claim 0

The quartzbridge lease window is 6 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.

### Claim 1

The cobaltbridge lease window is 12 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:cobaltbridge-a.md` · SHA-256 `d28eba885d0b46f6c972783fbcb0e8cb87572bd7c7d86157142b780e15f76d3f`
Version `0.28.1` · SYNTHETIC DEMO: Cobaltbridge policy A · lines 1–7
Reference: /api/chunks/b324cdd5fd47dfe629cfb315?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 cobaltbridge scenario. The cobaltbridge lease window is 12 seconds.

## C028 · keyword

HTTPX `0.28.1` · Profile `support`
**Question:** Which number should I use for the quartzbridge lease window?

### Claim 0

The quartzbridge lease window is 6 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.

## C028 · vector

HTTPX `0.28.1` · Profile `support`
**Question:** Which number should I use for the quartzbridge lease window?

### Claim 0

The quartzbridge lease window is 9 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-b.md` · SHA-256 `5e4193bfeb4f373dafddc464d912c04f26e95f0be94e76a6537638eb23c8ba71`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy B · lines 1–7
Reference: /api/chunks/a314deff824a14c9b01f7594?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 9 seconds.

## C028 · hybrid

HTTPX `0.28.1` · Profile `support`
**Question:** Which number should I use for the quartzbridge lease window?

### Claim 0

The quartzbridge lease window is 6 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.

## C030 · keyword

HTTPX `0.28.1` · Profile `support`
**Question:** Give a single supported lease-window value for quartzbridge.

### Claim 0

The quartzbridge lease window is 6 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.

## C030 · vector

HTTPX `0.28.1` · Profile `support`
**Question:** Give a single supported lease-window value for quartzbridge.

### Claim 0

The quartzbridge lease window is 6 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.

## C030 · hybrid

HTTPX `0.28.1` · Profile `support`
**Question:** Give a single supported lease-window value for quartzbridge.

### Claim 0

The quartzbridge lease window is 6 seconds.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `synthetic:httpx:0.28.1:quartzbridge-a.md` · SHA-256 `c745ff7a92f7d9873f71634ff32a61bd75a1338678157dca74a3643fc6447b68`
Version `0.28.1` · SYNTHETIC DEMO: Quartzbridge policy A · lines 1–7
Reference: /api/chunks/3d92314800619da3e1271d52?version=0.28.1

> This policy is applicable only to the synthetic HTTPX 0.28.1 quartzbridge scenario. The quartzbridge lease window is 6 seconds.

## C033 · keyword

HTTPX `0.28.1` · Profile `public`
**Question:** Which setting stops HTTPX from using environment variables?

### Claim 0

Setting `trust_env=False` stops HTTPX from using environment variables.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:docs/environment_variables.md` · SHA-256 `d0cdf4d740dc3ed8b21c4ee45735551e05d4e57d0fda05a2f18c4684197a27eb`
Version `0.28.1` · Environment Variables · lines 1–10
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/environment_variables.md?plain=1#L1-L10

> * On the client via `httpx.Client(trust_env=False)`.
> * Using the top-level API, such as `httpx.get("<url>", trust_env=False)`.

## C033 · vector

HTTPX `0.28.1` · Profile `public`
**Question:** Which setting stops HTTPX from using environment variables?

### Claim 0

Setting `trust_env=False` stops HTTPX from using environment variables.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:docs/environment_variables.md` · SHA-256 `d0cdf4d740dc3ed8b21c4ee45735551e05d4e57d0fda05a2f18c4684197a27eb`
Version `0.28.1` · Environment Variables · lines 1–10
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/environment_variables.md?plain=1#L1-L10

> * On the client via `httpx.Client(trust_env=False)`.
> * Using the top-level API, such as `httpx.get("<url>", trust_env=False)`.

## C033 · hybrid

HTTPX `0.28.1` · Profile `public`
**Question:** Which setting stops HTTPX from using environment variables?

### Claim 0

Setting `trust_env` to `False` stops HTTPX from using environment variables.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:docs/environment_variables.md` · SHA-256 `d0cdf4d740dc3ed8b21c4ee45735551e05d4e57d0fda05a2f18c4684197a27eb`
Version `0.28.1` · Environment Variables · lines 1–10
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/environment_variables.md?plain=1#L1-L10

> The HTTPX library can be configured via environment variables.
> Environment variables are used by default. To ignore environment variables, `trust_env` has to be set `False`. There are two ways to set `trust_env` to disable environment variables:

## C034 · keyword

HTTPX `0.28.1` · Profile `public`
**Question:** Which HTTP protocol versions does the overview say HTTPX supports?

### Claim 0

HTTPX supports HTTP protocol versions including HTTP/1.1 and HTTP/2.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:docs/advanced/proxies.md` · SHA-256 `38f3be3b3babe015f9b9878c8ed207144e860a572b5c1dbf8eb7924d4a738960`
Version `0.28.1` · SOCKS · lines 68–83
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/docs/advanced/proxies.md?plain=1#L68-L83

> In addition to HTTP proxies, `httpcore` also supports proxies using the SOCKS protocol.
> This is an optional feature that requires an additional third-party library be installed before use.

## C034 · hybrid

HTTPX `0.28.1` · Profile `public`
**Question:** Which HTTP protocol versions does the overview say HTTPX supports?

### Claim 0

HTTPX supports HTTP/1.1 and HTTP/2.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:README.md` · SHA-256 `0025293013043e0c49d494dbbde876a6ac558fa70a74f93a86ed10e7ecba0ea3`
Version `0.28.1` · HTTPX overview · lines 1–58
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/README.md?plain=1#L1-L58

> HTTPX is a fully featured HTTP client library for Python 3. It includes **an integrated command line client**, has support for both **HTTP/1.1 and HTTP/2**, and provides both **sync and async APIs**.

## C035 · keyword

HTTPX `0.27.2` · Profile `public`
**Question:** Has the response body necessarily been read when a response event hook runs?

### Claim 0

Response event hooks are called before determining if the response body should be read or not.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:docs/advanced/event-hooks.md` · SHA-256 `96d292f95b3412c54f7f862fd38a569b0efb2bd51a6cacdd5b391072262b9558`
Version `0.27.2` · Event Hooks · lines 1–48
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/advanced/event-hooks.md?plain=1#L1-L48

> !!! note
>     Response event hooks are called before determining if the response body
>     should be read or not.

## C035 · hybrid

HTTPX `0.27.2` · Profile `public`
**Question:** Has the response body necessarily been read when a response event hook runs?

### Claim 0

Response event hooks are called before determining if the response body should be read or not.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:docs/advanced/event-hooks.md` · SHA-256 `96d292f95b3412c54f7f862fd38a569b0efb2bd51a6cacdd5b391072262b9558`
Version `0.27.2` · Event Hooks · lines 1–48
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/docs/advanced/event-hooks.md?plain=1#L1-L48

> !!! note
>     Response event hooks are called before determining if the response body
>     should be read or not.

## C036 · vector

HTTPX `0.28.1` · Profile `public`
**Question:** Which client-certificate SSL case is fixed by the 0.28.1 entry?

### Claim 0

The 0.28.1 entry fixes the SSL case where `verify=False` together with client side certificates.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:CHANGELOG.md` · SHA-256 `2cd04b965b20eff7a4d3b30cc020c63b125da9f731874513bad2e59ca9743258`
Version `0.28.1` · Changelog > 0.28.1 (6th December, 2024) · lines 7–10
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/CHANGELOG.md?plain=1#L7-L10

> ## 0.28.1 (6th December, 2024)

## C036 · hybrid

HTTPX `0.28.1` · Profile `public`
**Question:** Which client-certificate SSL case is fixed by the 0.28.1 entry?

### Claim 0

The 0.28.1 entry fixes the SSL case where `verify=False` together with client side certificates.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:CHANGELOG.md` · SHA-256 `2cd04b965b20eff7a4d3b30cc020c63b125da9f731874513bad2e59ca9743258`
Version `0.28.1` · Changelog > 0.28.1 (6th December, 2024) · lines 7–10
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/CHANGELOG.md?plain=1#L7-L10

> ## 0.28.1 (6th December, 2024)

## C037 · keyword

HTTPX `0.28.1` · Profile `public`
**Question:** What happened to the deprecated app shortcut in the 0.28.0 release?

### Claim 0

The `app=...` shortcut was deprecated in the 0.28.0 release and replaced with explicit transport configurations.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.28.1:CHANGELOG.md` · SHA-256 `2cd04b965b20eff7a4d3b30cc020c63b125da9f731874513bad2e59ca9743258`
Version `0.28.1` · Changelog > 0.27.0 (21st February, 2024) > Deprecated · lines 56–59
Reference: https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/CHANGELOG.md?plain=1#L56-L59

> ### Deprecated

## C040 · keyword

HTTPX `0.27.2` · Profile `public`
**Question:** What changed specifically in the unreleased-for-this-snapshot 0.28.1 verify=False client-certificate fix?

### Claim 0

Support for custom `cert` parameters even if `verify=False` was added in the unreleased-for-this-snapshot 0.28.1 client-certificate fix.

Supported by the supplied evidence: pending. Factual/release correctness: pending.

Source `httpx:0.27.2:CHANGELOG.md` · SHA-256 `f0fddf6cb8e545c6f4864d16c9f2575d8a347d9803c5b870260edc4ce019b545`
Version `0.27.2` · Changelog > 0.12.0 (March 9th, 2020) > Fixed · lines 766–776
Reference: https://github.com/encode/httpx/blob/609df7ecc0f7cb10a1c998aa9c269bba77337c5f/CHANGELOG.md?plain=1#L766-L776

> * Support basic auth credentials in proxy URLs. (Pull #780)
> * Fix `httpx.Proxy(url, mode="FORWARD_ONLY")` configuration. (Pull #788)
> * Fallback to setting headers as UTF-8 if no encoding is specified. (Pull #820)
> * Close proxy dispatches classes on client close. (Pull #826)
> * Support custom `cert` parameters even if `verify=False`. (Pull #796)
> * Don't support invalid dict-of-dicts form data in `data=...`. (Pull #811)
