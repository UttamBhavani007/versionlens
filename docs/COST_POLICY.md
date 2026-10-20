# Zero-service-cost policy

This requirement comes from the project owner: **everything built throughout
the project must be free; no paid services under any circumstances.**

## Allowed

| Component | Choice | Boundary |
| --- | --- | --- |
| Runtime | Python on existing hardware | No rented compute |
| Database | Local SQLite with FTS5 | No hosted database |
| Retrieval | Local keyword and later local embeddings | No remote embedding API |
| Generation | Local Ollama and a permissively licensed open model | Cloud disabled, loopback only |
| Repository | Public GitHub Free repository | No Codespaces, LFS, paid add-ons, or paid runners |
| Demo | Local application and checked-in screenshots | No paid hosting; no uptime promise |

No account with a credit card, free trial with an upgrade path, cloud-only model,
metered inference provider, hosted telemetry, domain purchase, or auto recharge
is required or permitted. If a feature cannot meet this constraint, keep it local
or leave it unimplemented and explain the limitation.

Existing hardware, electricity, and Internet are prerequisites rather than
services purchased by this project. No claim is made that running a computer
consumes no resources.

## Enforcement to implement before generation

- Use an explicit local model allowlist, rejecting cloud tags and remote hosts.
- Start the project-managed Ollama server with `OLLAMA_NO_CLOUD=1`.
- Disable proxy inheritance for model calls and reject HTTP redirects.
- Do not add any cloud inference credentials or cloud fallback path.
- Track request and token counts as usage; local API fees are zero. Do not
  invent dollar equivalents or confuse zero API fees with zero resource use.
- CI is optional. If added, it must be guarded for public repositories only,
  use a standard Ubuntu runner, and not upload artifacts or create caches.

## Verified reference points (2026-10-20)

- [Ollama local API](https://docs.ollama.com/api/introduction): local requests
  do not require an API key.
- [Disable Ollama cloud](https://docs.ollama.com/faq#how-do-i-disable-ollamas-cloud-features):
  `OLLAMA_NO_CLOUD=1` disables cloud features.
- [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions):
  standard public-repository runners are free, but larger runners and excess
  storage can incur charges. Local checks avoid that dependency entirely.

Recheck upstream terms before introducing any external service.
