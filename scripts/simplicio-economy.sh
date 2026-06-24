#!/usr/bin/env bash
# simplicio-economy.sh — the Simplicio token-economy module.
#
# One entrypoint that brings up and reports the whole always-on savings stack so that,
# AFTER `simplicio-economy up`, token capture + savings work WITHOUT ever invoking
# simplicio-loop. The pieces:
#   1. capture proxy        — intercepts LLM HTTP calls, compresses, logs tokens saved
#   2. token monitor (:9090)— the Simplicio Token Monitor web dashboard
#   3. menu-bar tray        — live tokens saved in the macOS menu bar
#   4. deterministic operator (simplicio-dev-cli) — zero-token edits, always available
#   5. transparent capture  — opt-in proxy that forwards each client to its REAL provider
#                             (proven: captures real OpenAI/Anthropic calls, no model swap)
#
# Usage:
#   simplicio-economy status                 # full-stack health + savings + operator
#   simplicio-economy up                     # ensure proxy + monitor + tray are running
#   simplicio-economy capture openai [port]  # start a TRANSPARENT proxy → api.openai.com
#   simplicio-economy capture anthropic [port]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROXY_PORT="${SIMPLICIO_PROXY_PORT:-8788}"
MONITOR_PORT="${SIMPLICIO_MONITOR_PORT:-9090}"
UID_="$(id -u)"
ENGINE="$SCRIPT_DIR/simplicio-engine"

_up() { python3 -c "import socket,sys; socket.create_connection(('127.0.0.1',int(sys.argv[1])),0.5)" "$1" 2>/dev/null; }

_savings() {
  python3 - "$@" <<'PY' 2>/dev/null || true
import json, os, sys
for p in (os.path.expanduser("~/.simplicio/proxy_savings.json"),
          os.path.expanduser("~/.headroom/proxy_savings.json")):
    if os.path.exists(p):
        try:
            d = json.load(open(p)); life = d.get("lifetime", {})
            saved = int(life.get("tokens_saved", 0) or 0)
            after = int(life.get("total_input_tokens", 0) or 0); before = after + saved
            pct = round(saved / before * 100, 1) if before else 0.0
            print(f"{saved:,} tokens · ${float(life.get('compression_savings_usd',0) or 0):.3f} · "
                  f"{pct}% · {int(life.get('requests',0) or 0)} requests")
            break
        except Exception:
            pass
else:
    print("no savings data yet")
PY
}

cmd_status() {
  echo "⬡ Simplicio token-economy module"
  echo "─────────────────────────────────────────────"
  _up "$PROXY_PORT"   && echo "  ● capture proxy      :$PROXY_PORT  live"   || echo "  ○ capture proxy      :$PROXY_PORT  OFFLINE (run: simplicio-economy up)"
  _up "$MONITOR_PORT" && echo "  ● token monitor      :$MONITOR_PORT  http://127.0.0.1:$MONITOR_PORT" || echo "  ○ token monitor      :$MONITOR_PORT  OFFLINE"
  pgrep -f simplicio_tray.py >/dev/null 2>&1 && echo "  ● menu-bar tray      running" || echo "  ○ menu-bar tray      OFFLINE"
  if command -v simplicio-dev-cli >/dev/null 2>&1; then echo "  ● deterministic op   simplicio-dev-cli ready"; else echo "  ○ deterministic op   simplicio-dev-cli MISSING (pip install simplicio-cli)"; fi
  echo "─────────────────────────────────────────────"
  echo "  savings: $(_savings)"
}

cmd_up() {
  echo "⬡ Bringing up the token-economy stack..."
  for svc in ai.simplicio.proxy ai.simplicio.token-monitor ai.simplicio.tray; do
    if launchctl print "gui/$UID_/$svc" >/dev/null 2>&1; then
      launchctl kickstart "gui/$UID_/$svc" 2>/dev/null && echo "  → $svc kickstarted" || true
    else
      echo "  · $svc not registered — run scripts/setup_simplicio.sh first"
    fi
  done
  sleep 2
  echo ""
  cmd_status
}

cmd_capture() {
  local provider="${1:-}" port="${2:-8790}"
  case "$provider" in
    openai)    url="https://api.openai.com/v1" ;;
    anthropic) url="https://api.anthropic.com/v1" ;;
    *) echo "usage: simplicio-economy capture <openai|anthropic> [port]" >&2; exit 1 ;;
  esac
  echo "⬡ Starting TRANSPARENT capture proxy for $provider on :$port → $url"
  echo "  (forwards each call to the REAL provider — captures tokens, does NOT swap the model)"
  HEADROOM_PORT="$port" nohup "$ENGINE" proxy --port "$port" --openai-api-url "$url" --host 127.0.0.1 \
    > "$HOME/.hermes/logs/simplicio-transparent-$provider.log" 2>&1 &
  sleep 4
  if _up "$port"; then
    echo "  ● transparent proxy live on :$port"
    echo "  Wire a client by pointing its API base_url at  http://127.0.0.1:$port"
  else
    echo "  ○ failed to start — see ~/.hermes/logs/simplicio-transparent-$provider.log" >&2
  fi
}

case "${1:-status}" in
  status)  cmd_status ;;
  up)      cmd_up ;;
  capture) shift; cmd_capture "$@" ;;
  *) echo "Usage: $0 {status|up|capture <openai|anthropic> [port]}" >&2; exit 1 ;;
esac
