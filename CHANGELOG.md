# Changelog

All notable changes to **simplicio-loop** are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); the project uses SemVer.

## [1.2.0] — 2026-06-23

### Changed
- **Rebranded the token monitor from "headroom" to Simplicio.** The localhost dashboard is now
  the **Simplicio Token Monitor** (header + footer brand lockup rendered green + yellow).
  Our hooks/services/files were renamed: `hooks/headroom_dashboard.py` → `hooks/simplicio_dashboard.py`,
  `hooks/headroom_watch.py` → `hooks/simplicio_watch.py`, `scripts/setup_headroom.sh` →
  `scripts/setup_simplicio.sh`; launchd services `ai.simplicio.headroom` → `ai.simplicio.proxy`
  and `ai.simplicio.headroom-dashboard` → `ai.simplicio.token-monitor`; env var
  `HEADROOM_PORT` → `SIMPLICIO_PROXY_PORT` (old name still honored as fallback); proxy log
  targets → `~/.hermes/logs/simplicio-proxy*.log`.
- **Carve-out:** the underlying compression accelerator is the third-party **headroom-ai**
  product, so its real binary/install names are kept functional (`pip install headroom-ai`,
  `headroom proxy`, `headroom memory stats`) and its OSS attribution is preserved — only
  Simplicio-owned naming was changed.

### Added
- **Token Monitor auto-starts on macOS** via the renamed launchd service `ai.simplicio.token-monitor`,
  so the dashboard is live without a manual start.

## [1.1.0] — 2026-06-23

### Changed
- **Token dashboard redesigned to the Simplicio brand.** The localhost monitor
  (`hooks/simplicio_dashboard.py`, `:9090`) now renders the full Simplicio lockup faithfully
  in a neon-framed hero instead of a cropped square, echoes the brand tagline as four pillars
  (smart orchestration · neural cache · compressed context · maximum efficiency), and leads
  with a savings gauge (reduction %) + before→after token flow.
- **Runtime coverage is now a first-class panel** — all ten supported runtimes (Claude, Codex,
  Hermes, OpenClaw, VS Code, Gemini, Cursor, OpenCode, Kiro, Antigravity) each show how the
  skills load and how the loop drive is bound, with a coverage state pill.
- **Front-end construction cleaned up.** The single opaque HTML blob is split into
  `STYLE` / `BADGE_SVG` / `BODY` / `SCRIPT` constants composed via placeholder substitution —
  still single-file (deploy-friendly), no longer one unmaintainable string. The backend
  (`get_status` + handlers) is unchanged.

### Added
- **Repo-local brand asset** `assets/simplicio-loop-logo.png` — the dashboard now serves the
  logo from inside the repo (first logo candidate) instead of depending on a path outside it.
- **Faithful inline badge** (`BADGE_SVG`) — a vector of the hexagon-S mark (extruded S +
  stacked-layers core + circuit traces + speed particles), used as the favicon and the no-PNG
  fallback logo.

### Fixed
- Log viewer `tok_*=` highlight (`.hl`) had no CSS rule and rendered unstyled — now themed green.

## [1.0.5] — 2026-06-23

- Headroom integration: live web dashboard + monitor on `:9090`, context-compression proxy,
  MCP accelerator, setup script and launchd services.
- LMCache inference accelerator, agentsview session-observability source adapter.
- 11 runtime adapters + universal installer; hardened Ralph loop with bound operators
  (`simplicio-mapper` + `simplicio-cli`).
