#!/usr/bin/env bash
# update.sh — pull the latest simplicio-loop, reinstall skills/hooks/operators, restart the
# always-on services so they run the new code. Idempotent + safe (won't clobber local changes).
#
# Usage: bash scripts/update.sh [<runtime>]      # runtime defaults to claude
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"
RUNTIME="${1:-claude}"
_ver() { grep -m1 'version = ' pyproject.toml | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "?"; }

echo "⬡ Simplicio update  (current v$(_ver))"

# 1. Pull latest — never clobber local edits. Stash if dirty, restore after.
STASHED=0
if [ -n "$(git status --porcelain 2>/dev/null | grep -v '^?? ' || true)" ]; then
  git stash push -u -m "simplicio-update-autostash" >/dev/null 2>&1 && STASHED=1 && echo "  · stashed local changes"
fi
git fetch origin 2>&1 | tail -1 || true
if git pull --ff-only origin main 2>&1 | tail -2; then
  echo "  → updated to v$(_ver)"
else
  echo "  ! main isn't a fast-forward (diverged/local commits) — pull/merge manually, then re-run"
fi
[ "$STASHED" = "1" ] && { git stash pop >/dev/null 2>&1 && echo "  · restored local changes" || echo "  ! stash pop conflicted — see 'git stash list'"; }

# 2. Reinstall skills + hooks + operators from the freshly-pulled source (global).
echo "⬡ Reinstalling skills/hooks/operators..."
bash "$DIR/scripts/install.sh" "$RUNTIME" --global 2>&1 \
  | grep -E "operators (installed|verified)|skills ->|hooks ->|hooks wired|done" | sed 's/^/  /' || true

# 3. Restart the always-on services so they run the new code.
echo "⬡ Restarting services..."
if command -v launchctl >/dev/null 2>&1; then            # macOS
  UID_="$(id -u)"
  for svc in ai.simplicio.proxy ai.simplicio.token-monitor ai.simplicio.tray; do
    launchctl kickstart -k "gui/$UID_/$svc" 2>/dev/null && echo "  → restarted $svc" || echo "  · $svc not registered (run setup_simplicio.sh)"
  done
elif command -v systemctl >/dev/null 2>&1; then          # Linux
  for svc in simplicio-proxy simplicio-token-monitor simplicio-tray; do
    systemctl --user restart "$svc" 2>/dev/null && echo "  → restarted $svc" || true
  done
else
  echo "  · restart your Simplicio services manually for this OS"
fi
sleep 2

# 4. Report the live stack.
echo ""
bash "$DIR/scripts/simplicio-economy.sh" status 2>/dev/null | grep -E "capture proxy|token monitor|auto-capture|savings" | sed 's/^/  /' || true
echo "⬡ Update complete — now on v$(_ver)."
