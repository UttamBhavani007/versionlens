# Local API and browser workspace

The API/UI run on the existing computer with Python's standard library. There
is no frontend build, CDN, remote font, telemetry, hosted server or account.
This is a loopback workstation demo. It is not an authenticated public service;
do not expose it through a tunnel or reverse proxy. Python's
[HTTP server documentation](https://docs.python.org/3/library/http.server.html)
also distinguishes this server library from a production deployment.

## Start

From the repository root, after ingestion:

```sh
PYTHONPATH=src python3 -m versionlens ingest
PYTHONPATH=src python3 -m versionlens serve
```

Open `http://127.0.0.1:8765`. Use that literal address; `localhost` aliases and
other Host values are intentionally rejected. `serve --port 8766` selects an
unprivileged port when the default is occupied. Stop with Ctrl-C.

Catalog, keyword evidence search, source inspection and no-match abstention
work without a model server. For draft generation, start the separately
configured cloud-disabled runtime as described in [LOCAL_MODELS.md](LOCAL_MODELS.md).
Vector/hybrid requests also require the embedding model and a compatible vector
index built with `embed`. Startup does not download models or rebuild indexes.

## Routes

| Method and path | Behavior |
| --- | --- |
| `GET /` | Browser workspace |
| `GET /style.css`, `GET /app.js` | Bundled assets only |
| `HEAD /`, `HEAD /style.css`, `HEAD /app.js` | Asset headers without a body |
| `GET /api/catalog` | Indexed snapshots, available methods, default keyword method, configured access profile and accessible source/chunk counts |
| `POST /api/search` | Ranked version-scoped evidence; `answer` is null |
| `POST /api/ask` | Cited local draft, explicit abstention or operational error |
| `GET /api/chunks/{chunk_id}?version={version}` | Indexed source text, immutable reference, line span and provenance |

No route accepts a filesystem path or changes corpus/index contents. A chunk
ID is 24 lowercase hexadecimal characters and is resolved inside the selected
snapshot; an ID from another snapshot is not a cross-version lookup. Inaccessible IDs
return the same 404 envelope as absent IDs.

Search and answer requests use `Content-Type: application/json`:

```json
{
  "question": "What is the default timeout in HTTPX?",
  "version": "0.28.1",
  "retriever": "keyword",
  "limit": 5
}
```

`question` and `version` are required. `retriever` defaults to `keyword` and
accepts only `keyword`, `vector` or `hybrid`; `limit` defaults to five and must
be an integer from one to twenty. Booleans are not integers here. Versions
must be explicit supported snapshot strings. Questions are nonempty, valid
Unicode and at most 2000 characters. Pasted LF, CR and tab whitespace is
accepted; other controls and surrogates are rejected. Unexpected fields fail.

Search hits contain `chunk_id`, `version`, `section`, `text`, `source_id`,
`source_sha256`, `source_kind`, `access`, `upstream_commit`, `start_line`, `end_line`, `citation_url` and
`score`. Scores describe ranking, not answer confidence. Source inspection
adds the title, product and upstream path and omits score.

Answer responses preserve the [answer policy](ANSWER_POLICY.md), including
`status`, `reason`, `claims`, `model_called`, `semantic_support_verified: false`
and the draft notice. The browser renders claim text and source quotes as text,
not Markdown/HTML. Citation links are constructed from server-owned metadata
and checked again against the exact GitHub repository, commit, path and lines.
Synthetic sources have a separate validated identity: their legacy
`upstream_commit` field holds the 64-character content revision, labelled
Revision SHA in the UI, and their citation is the protected local chunk route.
Catalog returns `access_profile` and `permission_demo: true`. Profile selection
is trusted server configuration (`serve --demo-profile public|support`); role,
access and profile fields in request JSON are rejected. Source counts and
versions reflect that profile. See [the demo boundary](PERMISSIONS_AND_UPDATES.md).
Experimental vector/hybrid answer modes retain the conservative lexical
prerequisite on accessible documents; a missing keyword match avoids both
embedding and generation. Changed selected evidence or access detected during
inference suppresses the draft with reason `evidence_changed`.

## Errors and transport boundaries

An abstention is a successful HTTP 200 application response, separate from an
operational failure. HTTP errors have a bounded, stable envelope:

```json
{"error":{"code":"invalid_request","message":"Select an exact supported version."}}
```

| HTTP status | Examples |
| --- | --- |
| 400 | Invalid question/version/fields, malformed or duplicate-key JSON, ambiguous request framing |
| 403 | Cross-origin or cross-site browser request |
| 404 | Unknown route or source ID absent from the selected snapshot |
| 405 | Unsupported HTTP method |
| 408 | Timed-out request body |
| 413 | Body over 16 KiB |
| 415 | Body without the accepted JSON content type |
| 500 | Unexpected internal failure; no private exception details returned |
| 503 | Another POST is running, worker capacity reached, local model unavailable, or generation failed operationally |

The listener binds only `127.0.0.1`. Host must match the actual port. An Origin
header, when present, must match this exact origin; cross-site fetch metadata
is rejected. No CORS permission is returned. Non-browser local clients may omit
Origin. This is not authentication against other processes on the computer.

Bodies require one ASCII Content-Length; transfer encoding, duplicate framing
headers, nonfinite JSON and invalid UTF-8 are rejected. Connection reads have a
five-second timeout. At most eight handlers run, with a bounded OS listen queue;
only one POST operation runs at a time, while catalog/source reads remain
available. Disconnecting a browser hides stale output but does not cancel a
model call already executing on the server. Additional POSTs receive busy 503
until it finishes. Models retain their separate bounded timeouts.

Responses disable caching and content sniffing and prevent framing. Content
Security Policy defaults to no sources, explicitly allowing only local scripts,
styles and connections. Request bodies, queries and source text are not logged.

## Browser verification

Python tests cover API and real HTTP boundaries without calling models. The
optional browser checks use free Playwright 1.62.1; Node is needed only for these
checks, not for the application:

```sh
npm install
npx playwright install chromium
npm run check:web
```

Run the local server first. `VERSIONLENS_WEB_URL` can select another literal
loopback port. `VERSIONLENS_BROWSER_EXECUTABLE` selects an already installed
Chromium browser. `VERSIONLENS_BROWSER_REPORT` selects the JSON report path;
the default is ignored `reports/local/day4-browser.json`.
`VERSIONLENS_SCREENSHOT_PREFIX` selects new capture filenames when preserving
earlier observations. Set
`VERSIONLENS_CHECK_GENERATION=1` to include a real local cited-draft check;
this requires the separate local model server. The default checks need no model.

Tests cover real evidence/source/version/abstention interactions and labelled
negative fixtures for stale responses, source markup, unsafe links and server
errors. Captured screenshots use actual API results, with mocked routes removed.
Label, focus and responsive checks are not a complete accessibility audit or
screen-reader certification. Actual generation and retrieval quality require
their separate evaluation.
