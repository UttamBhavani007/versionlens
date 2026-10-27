# Reproducible local source deployment

VersionLens runs on the existing computer using Python 3.11 or newer and SQLite
with FTS5. The application has no third-party Python runtime dependencies. This
procedure runs a source checkout; it is not a claim of a tested wheel/pip
installation, public hosting or production authentication.

## Start without models or paid services

From a checkout, run:

```sh
python3 scripts/run_local.py
```

The launcher verifies the checked-in source checksums and prepares a missing
public index, then starts the foreground interface at `http://127.0.0.1:8765`.
It also works by absolute script path from another working directory. Use that
literal loopback address. Stop with Ctrl-C. No account, API key, package install,
model download, cloud fallback or background service is started.

Keyword evidence search, source inspection and missing-evidence abstention work
without a model server. The default corpus is 32 pinned HTTPX sources and 644
chunks. To prepare without serving or check readiness without writing files:

```sh
python3 scripts/run_local.py --prepare
python3 scripts/run_local.py --check
```

`--check` tests Python/FTS5 in memory, verifies sources and compares the existing
index to the selected corpus. It does not create directories/indexes, contact a
model, or establish generation/vector readiness. Missing or mismatched indexes
return JSON `not_ready` and exit code 2. A ready check exits 0. Bytecode cache
writes are disabled. An owner-modified WAL-mode index is rejected before SQLite
opens it, so readiness does not create or modify WAL sidecars; the application
normally creates DELETE-journal indexes.

An existing index is retained when its full source/chunk fingerprint and counts
match. The launcher refuses an implicit corpus replacement. If the existing
index differs, inspect the choice before explicitly rebuilding:

```sh
python3 scripts/run_local.py --prepare --include-synthetic --rebuild
python3 scripts/run_local.py --include-synthetic --demo-profile support --port 8766
```

The opt-in corpus adds two prominently labelled fictional runbooks: 34 sources
and 646 chunks. A public-profile catalog still exposes only accessible 32/644.
The support profile is selected by the trusted local operator; it is a
permission simulation, not a sign-in system. The launcher accepts only
unprivileged ports and the server binds to `127.0.0.1`. It offers no host override.

`--rebuild` explicitly replaces a supported source index; unknown schemas and
corrupt files remain rejected rather than being deleted. Symlinks in fixed deployment paths, including the data directory, index and
vector sidecar, are rejected. Use the lower-level snapshot commands for incremental maintenance.
A changed source/policy can invalidate the separate vector cache, which requires
an explicit `embed` rebuild. The launcher does not refresh vectors automatically.

## Add the free local models explicitly

The pinned model/runtime installer currently supports Apple Silicon macOS. It
requires initial free public downloads; consult [model provenance and setup](LOCAL_MODELS.md)
for reviewed licenses, checksums, platform limits and cloud-off controls.
It uses the project-local port 11435, separate from the web interface.

```sh
python3 scripts/local_runtime.py install
python3 scripts/local_runtime.py serve
```

Keep the foreground model server running. In another terminal:

```sh
python3 scripts/local_runtime.py pull
python3 scripts/local_runtime.py pull --embedding
PYTHONPATH=src python3 -m versionlens embed
python3 scripts/run_local.py
```

Models and SQLite files are ignored local artifacts. Stop each foreground
server with Ctrl-C. After initial setup, inference and retrieval run locally.
Never expose this demo through a public tunnel or treat its profiles as
protection for real private documents.

## Verification and limitations

Run the standard software checks from the checkout:

```sh
PYTHONPATH=src python3 -W error::ResourceWarning -m unittest discover -s tests -v
```

Source-launcher tests cover setup from another working directory, actual corpus
counts, read-only checks, idempotence, explicit replacement, symlink/schema
preservation and absence of model construction. Clean-checkout verification is
recorded separately from existing model/download/browser observations.

From a Git checkout with local history, verify an archived commit in a temporary,
pip-free virtual environment:

```sh
python3 scripts/check_clean_setup.py --output reports/local/my-clean-setup.json
```

The verifier does not fetch sources, install packages, download models, execute
candidate holdout questions or run generation. It starts and stops its own
loopback API, checks both versions and inspects real evidence. Python socket
guards add controls but are not an operating-system sandbox. Source ZIP users
can run the application and software tests; this archive verifier requires Git.

Software setup checks and literal citations do not establish answer correctness.
The [evaluation results](EVALUATION_RESULTS.md) retain conflict-handling and
release-reasoning limitations. Human question/claim reviews and held-out results
remain pending. Existing [screenshots](SCREENSHOTS.md) show actual local runs
with their capture dates; they do not imply a permanently hosted endpoint.
