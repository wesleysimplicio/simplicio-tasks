#!/usr/bin/env bash
# simplicio-capture.sh — wire real token capture across the runtimes Simplicio can intercept.
#
# Token capture works by routing a runtime's LLM HTTP traffic through the local Simplicio
# compression proxy, which logs tokens (before/after) per request. The proxy is powered by
# the headroom-ai engine; its `init` subcommand installs the engine's *blessed, transparent*
# integration per client (provider routing that forwards to each client's REAL provider — it
# does NOT swap the model). Three tiers:
#
#   native   Claude · Codex · VS Code (Copilot) · OpenClaw   → `simplicio capture init <client>`
#   base-url Hermes · Cursor · OpenCode                       → point OPENAI/ANTHROPIC_BASE_URL at the proxy
#   none     Gemini · Kiro · Antigravity                      → proprietary API, not interceptable (yet)
#
# Usage:
#   bash scripts/simplicio-capture.sh status      # show capture status (read-only: `headroom doctor`)
#   bash scripts/simplicio-capture.sh init        # install durable capture for every INSTALLED native client
#   bash scripts/simplicio-capture.sh init claude # install for one client
set -euo pipefail

PORT="${SIMPLICIO_PROXY_PORT:-8788}"

# Resolve the capture engine binary (headroom-ai), wherever it landed.
ENGINE="$(command -v headroom 2>/dev/null || true)"
[ -z "$ENGINE" ] && ENGINE="$(find "$HOME" -path '*/bin/headroom' -type f 2>/dev/null | head -1)"
if [ -z "$ENGINE" ]; then
  echo "❌ capture engine not installed — run: pip install headroom-ai" >&2
  exit 1
fi

# Native clients the engine can integrate durably + transparently.
NATIVE_CLIENTS="claude codex copilot openclaw"

cmd_status() {
  echo "⬡ Simplicio capture status (engine: $ENGINE, proxy port $PORT)"
  echo ""
  # `doctor` reads the port from HEADROOM_PORT (no --port flag).
  HEADROOM_PORT="$PORT" "$ENGINE" doctor 2>&1 || true
}

cmd_init() {
  local only="${1:-}"
  echo "⬡ Wiring durable token capture (transparent provider routing)..."
  for c in $NATIVE_CLIENTS; do
    [ -n "$only" ] && [ "$only" != "$c" ] && continue
    # copilot client binary is `copilot`; others share their name.
    if command -v "$c" >/dev/null 2>&1 || { [ "$c" = "copilot" ] && command -v copilot >/dev/null 2>&1; }; then
      echo "  → $c: installing capture integration"
      "$ENGINE" init "$c" --port "$PORT" 2>&1 | sed 's/^/      /' || echo "      (init $c skipped/failed)"
    else
      echo "  · $c: not installed — skipped"
    fi
  done
  echo ""
  echo "Base-url runtimes (Hermes/Cursor/OpenCode): set their model base_url to"
  echo "  http://127.0.0.1:$PORT   (OpenAI-compatible) or  /v1  as the API root."
  echo ""
  cmd_status
}

case "${1:-status}" in
  status) cmd_status ;;
  init)   cmd_init "${2:-}" ;;
  *) echo "Usage: $0 {status|init [client]}" >&2; exit 1 ;;
esac
