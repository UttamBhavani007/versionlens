# Free local generation

VersionLens uses a project-managed Ollama CLI and **only `qwen3:1.7b`** for
generation. No account, payment card, hosted inference, or API key is needed.
The application has no paid-provider fallback. After initial downloads, local
inference needs no network service. Existing electricity and internet costs
still apply.

## Reviewed runtime and model

The installer targets Apple Silicon macOS. On **21 October 2026**, the official
[latest stable Ollama release](https://github.com/ollama/ollama/releases/tag/v0.40.7)
was **v0.40.7**, confirmed using the
[official GitHub release API](https://api.github.com/repos/ollama/ollama/releases/latest).
The project pins that release rather than silently updating.

The smaller CLI/runtime bundle is
[`ollama-darwin.tgz`](https://github.com/ollama/ollama/releases/download/v0.40.7/ollama-darwin.tgz),
not the desktop application ZIP. Its reviewed release metadata is:

```text
size:   174723727 bytes
sha256: 6c8b378e423a4c959b586c0bb62865d20ae057e817f1a8ee10abcc44bde6abab
```

The installer verifies size and SHA-256 before extraction, including when a
download is cached. HTTPS redirects are limited to GitHub's release hosts.
Archive paths must remain inside the extraction directory. Internal file links
are resolved against archive members and materialized as regular files;
external links and special files are rejected. Installation preserves the
bundle's license and notice files and records a per-file integrity inventory.
Each launcher command verifies that inventory before executing the binary.
The checksum authenticates consistency with the reviewed GitHub release asset;
it is not a separate independent signature verification.

[Ollama's runtime license](https://github.com/ollama/ollama/blob/v0.40.7/LICENSE)
is MIT. The [Qwen publisher model card](https://huggingface.co/Qwen/Qwen3-1.7B)
identifies Qwen3-1.7B as Apache 2.0. The approved
[Ollama library model](https://ollama.com/library/qwen3:1.7b) is a roughly 1.4 GB
quantized download. Actual memory use includes runtime and context caches and
must be measured; download size is not a RAM requirement or speed guarantee.
Model tags can change upstream, so record the local model digest alongside
evaluation results. Do not describe this tag alone as immutable weights.

## Project-local setup

From the repository root:

```sh
python3 scripts/local_runtime.py install
python3 scripts/local_runtime.py serve
```

Keep that foreground server running. In a second terminal:

```sh
python3 scripts/local_runtime.py pull
python3 scripts/local_runtime.py status
```

`pull` downloads only the approved public `qwen3:1.7b` weights. It needs an active
project server; it does not start the desktop app. `status` lists downloaded
models on the project server. Stop the foreground server with **Ctrl-C**.
The launcher does not install login items or alter a system service.

This no-desktop-launch behavior depends on the pinned macOS CLI: its
[`startApp` implementation](https://github.com/ollama/ollama/blob/v0.40.7/cmd/start_darwin.go)
requires the executable to be a symlink into an `Ollama.app` bundle. Our installer
materializes a regular CLI file and runtime verification rejects symlinks,
including a symlinked executable. If the project server is absent, commands
therefore fail instead of starting the desktop application. Recheck this
upstream behavior before changing the pinned runtime release.

Local artifacts are ignored by Git:

| Artifact | Location |
| --- | --- |
| Verified CLI and runtime libraries | `.tools/ollama/` |
| Cached reviewed runtime archive | `.tools/ollama-v0.40.7-darwin.tgz` |
| Downloaded model weights and manifests | `.ollama/models/` |

Ollama may also read or create its ordinary user-level settings or identity files. The
launcher does not sign in, change those settings, override the user's home
directory, or send provider credentials to its child process. It forces cloud
features off regardless of inherited Ollama environment variables. Prompt-body
recording is disabled; ordinary startup and HTTP access logs still appear.

## Local-only controls

Every `serve`, `pull`, and `status` subprocess receives a controlled environment:

```text
OLLAMA_HOST=http://127.0.0.1:11435
OLLAMA_NO_CLOUD=1
OLLAMA_MODELS=<repository>/.ollama/models
OLLAMA_CONTEXT_LENGTH=8192
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_MAX_QUEUE=4
OLLAMA_NOHISTORY=1
OLLAMA_DEBUG_LOG_REQUESTS=0
```

Inherited provider tokens, proxy settings, and Ollama overrides are excluded.
Only essential platform environment settings are retained, with loopback
excluded from proxying. The private loopback port avoids reusing a normal
Ollama desktop instance on port 11434.

The official [Ollama FAQ](https://docs.ollama.com/faq#how-do-i-disable-ollamas-cloud-features)
documents that `OLLAMA_NO_CLOUD=1` disables cloud models and web search. The
[pinned runtime configuration source](https://github.com/ollama/ollama/blob/v0.40.7/envconfig/config.go)
shows that a true environment setting takes precedence over user settings.
Confirm the server startup log reports cloud disabled before a live demo.
These are application/runtime controls, not an operating-system network sandbox.
Downloading public model weights still uses external network connections.

`LocalModelConfig` rejects remote URLs, hostname-based loopback, alternate
ports, credentials, paths, queries, fragments, unapproved model names, and
unbounded generation parameters. It accepts only `http://127.0.0.1:11435` or
`http://[::1]:11435`, `qwen3:1.7b`, a finite timeout in `(0, 300]` seconds,
an integer context of 512–8192 tokens, and output of 1–600 tokens. The default
timeout is 120 seconds. The launcher binds IPv4; IPv6 is available to callers
only when a separately controlled loopback server is deliberately configured.

For the available 16 GiB Mac, the default **8192-token context**, **600-token
output cap**, and **one request at a time** are a conservative starting
configuration, not a performance claim. Budget the full prompt, source chunks,
question, schema, template allowance, and output together. Abstain before model
execution when useful complete evidence cannot fit. Disable model thinking in
the generation adapter when supported so the output budget serves the answer.

## Verification status

Endpoint/model/budget validation is covered by focused offline unit tests.
Runtime installation and live generation are separate checks: a passing config
test does not prove that a model has been downloaded, that Metal is available,
or that generated answers are grounded. Record actual runtime version, model
digest, cloud-off startup evidence, latency, and observed failures in local
smoke reports; do not substitute assumed benchmark results.
