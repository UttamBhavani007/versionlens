# Local support workspace

The browser UI uses local HTML, CSS and JavaScript with system fonts. It loads
no external assets, analytics, libraries or service credentials. It relies on
the same-origin API and leaves model execution to the local service.

## Interaction

- The exact snapshot selector is populated from the server catalog. The visible
  initial selection is the historical `0.28.1` snapshot when available; it is
  not labelled as the latest release. Keyword retrieval is the default.
- Find evidence returns ranked source excerpts. Generate draft is a separate
  action with explicit draft/abstention/error states. Model answer Markdown is
  never rendered; displayed claims and quotations are plain text.
- Changing a question, version or retrieval method clears the previous results,
  aborts the browser request, and increments a request generation counter. A late
  response must still match that counter and all three current input values.
  Browser cancellation does not promise cancellation of backend model work.
- Source inspection fetches only the selected chunk ID and exact version from
  `/api/chunks/<id>?version=<version>`. The native dialog closes when inputs
  change, and stale inspector responses cannot reopen it.
- A local-service error keeps the user's question and selection. Empty questions
  and server validation errors are associated with the labelled question field.

## Evidence and safety

Dynamic content uses `textContent`, `createElement` and DOM node composition.
Source HTML, Markdown and model-generated markup remain literal text. Citation
links must match the approved HTTPS GitHub repository, full immutable commit,
source path and `?plain=1#Lx-Ly` line range. The displayed metadata must agree
with that link and the selected version. External source tabs use `noopener
noreferrer`.

An answered result is labelled: **Draft answer; check the cited sources.**
Citation identity and quotations are distinct from semantic correctness. A
withheld draft does not become a partial answer in the interface. Search
scores are never displayed as confidence or accuracy.

## Accessibility and layout checks

The implementation includes visible labels, focus outlines, a skip link,
`aria-live` status, associated input errors, disabled action buttons while a
request is pending, a native keyboard-accessible source dialog and reduced
motion styles. Layout breakpoints support a single-column workspace on small
screens and separate composer/evidence panels on desktop.

Before claiming visual verification, inspect the running application at desktop
and 360-pixel widths. Check keyboard-only submission and dialog dismissal,
input changes during a pending request, invalid source links, literal HTML in
evidence, empty results, API errors and withheld drafts. Screenshots must show
the actual running application; these implementation notes are not evidence
that browser checks have already passed.

Small muted text and placeholder foregrounds use `#677262`. A limited computed
contrast check against their solid backgrounds exceeds 4.5:1; this does not
constitute a complete WCAG or assistive-technology audit.


## Synthetic provenance and permission demo

The catalog provides a server-selected `public` or `support` demo profile. A
visible notice names the profile and explains that this demonstrates access
rules without signing in real users. There is no browser role selector or
role field in query payloads; the local operator selects the server profile.

Every hit must declare a known source kind and access level. The UI rejects
support-only evidence under a public catalog, unknown access levels, and
unknown provenance kinds. Official HTTPX sources retain strict immutable
GitHub link validation. Synthetic documents use a separate source-ID prefix,
SHA-256 revision and an exact same-origin protected chunk route. No synthetic
document is given an HTTPX Git commit or upstream source link.

Synthetic evidence has a prominent `SYNTHETIC DEMO` notice on cards and in the
source inspector, identifies its access level, and says it is not official
HTTPX guidance. Synthetic citation links also name the demo origin. The
inspector verifies source kind, access and source identity against the displayed
result before showing the fetched excerpt. Dynamic labels remain plain text.
These browser checks are an additional consistency guard; backend filtering
and source-route access checks are authoritative. Previously viewed material
cannot be erased from a user's memory by changing a demo profile.
