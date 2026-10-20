# Corpus provenance

VersionLens includes unmodified Markdown snapshots from the official
[encode/httpx repository](https://github.com/encode/httpx). The corpus contains
16 files per snapshot (32 files, 270,391 bytes total), including the upstream
license in each snapshot.

| Product version | Immutable source commit | Release |
| --- | --- | --- |
| HTTPX 0.27.2 | [`609df7ecc0f7cb10a1c998aa9c269bba77337c5f`](https://github.com/encode/httpx/tree/609df7ecc0f7cb10a1c998aa9c269bba77337c5f) | [27 August 2024](https://github.com/encode/httpx/releases/tag/0.27.2) |
| HTTPX 0.28.1 | [`26d48e0634e6ee9cdc0533996db289ce4b430177`](https://github.com/encode/httpx/tree/26d48e0634e6ee9cdc0533996db289ce4b430177) | [6 December 2024](https://github.com/encode/httpx/releases/tag/0.28.1) |

These are deliberate historical snapshots for upgrade questions, not a claim
that either is the newest available HTTPX version.

## Included material

Each snapshot includes `README.md`, `CHANGELOG.md`, `LICENSE.md`, quickstart,
async support, exceptions, compatibility, troubleshooting, environment
variables, and the advanced guides for clients, proxies, SSL, transports,
timeouts, resource limits, and event hooks. The actual upstream environment
variables filename is `docs/environment_variables.md`.

[`data/sources.json`](../data/sources.json) records every file's source ID,
product, snapshot version, repository-relative path, upstream path, immutable
commit, SHA-256 digest, immutable GitHub URL, and title. Hashes cover the exact
upstream bytes; no rewritten or synthetic documentation is mixed into this
corpus. Material remains attributable to its upstream authors.

## Version interpretation

The manifest's `version` identifies the repository snapshot. It does **not**
mean that every statement first became true in that version. Changelogs contain
cumulative release histories; retain their release headings during chunking
and interpret the applicable release when answering an upgrade question.

For example, the [pinned changelog](https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/CHANGELOG.md)
records removal of the deprecated `app` and `proxies` arguments in **0.28.0**,
while **0.28.1** fixes a separate SSL case. Shared documentation can be identical
across snapshots. Identical text still needs each snapshot's provenance.

Upstream documentation can contain mistakes or inconsistencies. The corpus
preserves them rather than silently editing source evidence; evaluation should
identify conflicts and the answering layer should expose uncertainty when the
available evidence is inconsistent. Downloaded document content is evidence,
never an instruction to the application or model.

## Verify or restore

From the repository root, verify all local files without network access:

```sh
python3 scripts/fetch_sources.py --check
```

To re-download the **same** approved immutable files and verify their expected
checksums:

```sh
python3 scripts/fetch_sources.py
```

The fetcher uses only Python's standard library. It builds HTTPS URLs for
`raw.githubusercontent.com/encode/httpx/` at the two approved full commit SHAs,
rejects redirects, caps each file at 512 KiB, rejects unsafe paths and symlinks,
and checks every SHA-256 digest. All files download into temporary staging and
pass integrity checks before any corpus file changes. Individual replacements
are atomic; publication is not a multi-file transaction if the process or
filesystem fails during replacement. Re-run verification after interruption.

The tool does not discover new sources, change checksums, or update to newer
versions. Adding a new release requires a reviewed manifest and matching
fetcher allowlist change. A checksum failure is an error, not a reason to
automatically trust replacement content. Public documentation downloads need
internet access; verification and the checked-in corpus work offline.

## License

HTTPX is distributed under its upstream BSD 3-clause license. The complete
copyright notice, conditions, and disclaimer are preserved in
[`0.27.2/LICENSE.md`](../data/corpus/httpx/0.27.2/LICENSE.md) and
[`0.28.1/LICENSE.md`](../data/corpus/httpx/0.28.1/LICENSE.md). Preserve those
notices when redistributing this corpus. The VersionLens project license does
not replace the HTTPX license.
