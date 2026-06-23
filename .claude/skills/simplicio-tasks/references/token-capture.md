# Token capture — how Simplicio really intercepts tokens

The **Simplicio Token Monitor** (`hooks/simplicio_dashboard.py`, `:9090`) only *displays* numbers.
The actual capture is done by the **Simplicio capture proxy** — a local HTTP server (powered by the
open-source `headroom-ai` engine) that sits between a runtime and its LLM provider. Every request
that flows through it is logged with `tok_before` / `tok_after` / `tok_saved` and written to
`proxy_savings.json` (lifetime totals + per-request `history`). No proxy in the path → no capture.

## The one rule

> A runtime's tokens are captured **only when its LLM HTTP traffic flows through the proxy.**

So "make capture work for runtime X" always means one of: route X's API base URL through the proxy,
or install the engine's durable integration for X. Some runtimes can do neither.

## Interceptability matrix (honest)

| Tier | Runtimes | How capture is wired | Notes |
|---|---|---|---|
| **native** | Claude · Codex · VS Code (Copilot) · OpenClaw | `simplicio capture init <client>` (engine's durable hooks + **transparent** provider routing) | Forwards to the client's REAL provider — does not change the model. |
| **base-url** | Hermes · Cursor · OpenCode | point the client's model `base_url` at `http://127.0.0.1:<port>` (OpenAI/Anthropic-compatible) | Hermes is wired this way today (→ DeepSeek). |
| **none** | Gemini · Kiro · Antigravity | — | Proprietary Google/AWS APIs the proxy can't speak; not interceptable yet. |

**7 of 10 runtimes are interceptable; 3 are not.** The dashboard shows this live with per-runtime
logos and tier badges, and dims the non-interceptable ones.

## Critical caveat — proxy backend

A single proxy forwards to **one upstream**. The proxy installed by `setup_simplicio.sh` targets
DeepSeek (for Hermes). If you route a *different* client (e.g. Codex) through that same proxy, its
requests also go to DeepSeek — that's a **model swap, not transparent capture**.

For real multi-runtime capture you want the engine's **transparent provider routing** (each client
forwarded to its own real provider). That is exactly what `simplicio capture init <client>` sets up.
Wire each client through `init`; don't hand-point everything at the DeepSeek proxy.

## Commands

```bash
bash scripts/simplicio-capture.sh status        # read-only: proxy + per-client routing + lifetime savings
bash scripts/simplicio-capture.sh init           # durable capture for every INSTALLED native client
bash scripts/simplicio-capture.sh init claude    # one client
```

`status` runs the engine's `doctor`: proxy reachability/version, per-client routing, and lifetime
tokens/$ saved. `init` installs the transparent integration for each installed native client.

## Always-on (so it "just works")

`setup_simplicio.sh` registers two launchd services that auto-start and self-restart (KeepAlive):

- `ai.simplicio.proxy` — the capture proxy (data source).
- `ai.simplicio.token-monitor` — the dashboard on `:9090`.

After install, capture is active for any client wired via `init`/base-url, the proxy survives
reboots, and the monitor is always live. Verify any time with `scripts/simplicio-capture.sh status`.
