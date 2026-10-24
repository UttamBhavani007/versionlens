# Snapshot updates and synthetic permission demonstration

This local demonstration uses two fictional runbooks alongside the unchanged
32 pinned HTTPX sources. All fictional documents are prominently labelled
**SYNTHETIC DEMO**, are MIT-licensed project material and contain no real users
or secrets. They are public files in this repository. The two startup profiles
simulate access rules; they do not authenticate people or isolate local users.

## Start the demonstration

From the repository root, with the separately configured free local model
server running for generated drafts:

```sh
PYTHONPATH=src python3 -m versionlens ingest --include-synthetic
PYTHONPATH=src python3 -m versionlens embed
PYTHONPATH=src python3 -m versionlens serve --demo-profile public
```

In a second terminal:

```sh
PYTHONPATH=src python3 -m versionlens serve --port 8766 --demo-profile support
```

Open the literal loopback addresses on ports 8765 and 8766. Search or ask for
`orchidrelay`. Public access cannot retrieve the fictional runbook and abstains
without generation. Support access can inspect it and request a cited draft.
The interface labels the configured demo profile, synthetic provenance and
unverified semantic support. Stop both foreground servers with Ctrl-C.

Default `ingest` includes only public upstream HTTPX sources. Explicit opt-in
adds two synthetic sources: 34 sources and 646 chunks in total; the public
catalog continues to show only its accessible 32 sources and 644 chunks.
Raw source checksums and visible synthetic headings are checked before indexing.
Synthetic citations resolve through the access-checked local source route;
their revision is a content SHA-256, never a forged upstream Git commit.

## Filtering and boundaries

The trusted CLI/server operator selects `public` or `support`; browser request
bodies cannot set a role, ACL or profile. Unknown profiles and access policies
fail validation. Permissions come from validated source metadata, never from
document instructions, question text or model output.

Keyword candidates are constrained before LIMIT; vector candidates before
cosine scoring; both hybrid pools receive the same profile. Model context has
an independent access check. Source inspection returns the same 404 for an
inaccessible or absent ID. Catalog counts and versions are also filtered.
Selected evidence is rechecked before generation and after model return;
changed content/access suppresses the result as `evidence_changed`.

This does not erase previously viewed text or cancel an authorized model call
already in flight. The local server has no production authentication. SQLite
and model files are local trusted assets. FTS5 uses collection-wide ranking
statistics, so this is not a claim of timing or score side-channel isolation.

## Maintain one complete snapshot

`sync` accepts the desired complete state of one selected version. Added or
changed sources are written transactionally, omitted sources are deleted,
unchanged source/chunk rows are retained, and the other version is preserved:

```sh
PYTHONPATH=src python3 -m versionlens sync --version 0.28.1 --include-synthetic
PYTHONPATH=src python3 -m versionlens delete-snapshot --version 0.28.1
```

The deletion command explicitly removes the selected local snapshot. Restore
from the validated manifest with `sync` or rebuild all snapshots with `ingest`.
A sync without `--include-synthetic` removes synthetic sources in that selected
version. Empty accidental input is rejected; whole-snapshot removal is explicit.
Update counters and resulting statistics are recorded in the same transaction.

The original source-byte SHA check belongs to the manifest loader; normalized
`Corpus` chunks cannot reconstruct original newline bytes. Update validation
also checks source/chunk membership, identities, ranges and stored policy
consistency. Schema-1 indexes migrate transactionally during explicit `ingest`;
unknown schemas are preserved and rejected. Sync requires schema 2.

Content, provenance or policy changes invalidate the vector fingerprint. Rebuild
with `embed`; there is no stale-cache use, silent retrieval-mode fallback or
remote inference fallback. Embedding rebuilds currently process the full corpus.

## Reproduce actual changes without modifying checked-in documents

```sh
python3 scripts/demo_changes.py --generate --vectors
```

The script copies the checksummed source fixtures into a temporary workspace,
builds an isolated index, observes both profiles and retrieval methods, then:

1. Shows the fictional budget of 2 attempts for 0.27.2 and 3 for 0.28.1.
2. Revises the newer document to 4 attempts while preserving the older version.
3. Rejects its obsolete source ID and the now-stale vector cache.
4. Grants public access, then revokes it and verifies abstention and source denial.
5. Deletes only the newer snapshot and checks the older one remains available.

The [actual 29-step run](../reports/day5-change-demo.json) retained four cited
local drafts with the observed 2/3/4/4 values. This is a repeated synthetic
development demonstration, not a held-out benchmark or human review. All outputs
keep `semantic_support_verified: false`. Model/API fees were zero.

## Browser checks

With the two local servers running, optional free Playwright checks are:

```sh
node scripts/check_access_web.cjs
node scripts/check_permission_fixtures.cjs
```

`VERSIONLENS_BROWSER_EXECUTABLE` can select an installed Chromium browser.
`VERSIONLENS_ACCESS_REPORT` and `VERSIONLENS_FIXTURE_REPORT` select report paths;
defaults are ignored under `reports/local/`. The access script records real
HTTP responses and screenshots; its [eight checks](../reports/day5-access-browser.json)
include rejected browser self-promotion and protected source lookup. The
[23 separate fixture checks](../reports/day5-permission-fixtures.json) exercise
client-side metadata/link/markup guards and are explicitly mocked observations.
The [13 existing browser checks](../reports/day5-browser-regression.json) and
[13 public API probes](../reports/day5-http-smoke.json) passed again. The upgrade
probe still abstains with `invalid_generation`. None measures answer accuracy.
