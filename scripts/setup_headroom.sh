#!/usr/bin/env bash
# setup_headroom.sh — install and configure headroom for simplicio-loop
# Usage: bash scripts/setup_headroom.sh [--port 8788] [--dashboard-port 9090]
set -euo pipefail

PORT="${2:-8788}"
DASH_PORT="${4:-9090}"
HERMES_CONFIG="$HOME/.hermes/config.yaml"
LAUNCHD="$HOME/Library/LaunchAgents"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "⬡ headroom setup — simplicio-loop"
echo ""

# 1. Install
echo "📦 Installing headroom-ai..."
pip install headroom-ai httpx[http2] 2>&1 | tail -2

# 2. Verify headroom binary
HEADROOM=$(which headroom 2>/dev/null || echo "")
if [ -z "$HEADROOM" ]; then
  HEADROOM=$(find ~/ -path "*/bin/headroom" -type f 2>/dev/null | head -1)
fi
if [ -z "$HEADROOM" ]; then
  echo "❌ headroom binary not found after install"
  exit 1
fi
echo "✅ headroom: $HEADROOM"

# 3. Create launchd plist for proxy
echo "📋 Creating launchd plist for proxy..."
mkdir -p "$LAUNCHD"
cat > "$LAUNCHD/ai.simplicio.headroom.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.simplicio.headroom</string>
    <key>ProgramArguments</key>
    <array>
        <string>$HEADROOM</string>
        <string>proxy</string>
        <string>--port</string>
        <string>$PORT</string>
        <string>--openai-api-url</string>
        <string>https://api.deepseek.com/v1</string>
        <string>--host</string>
        <string>127.0.0.1</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.hermes/logs/headroom.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.hermes/logs/headroom.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$HOME/Library/Python/3.9/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF
echo "✅ $LAUNCHD/ai.simplicio.headroom.plist"

# 4. Create launchd plist for dashboard
echo "📋 Creating launchd plist for dashboard..."
cat > "$LAUNCHD/ai.simplicio.headroom-dashboard.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.simplicio.headroom-dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$SCRIPT_DIR/hooks/headroom_dashboard.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.hermes/logs/headroom-dashboard.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.hermes/logs/headroom-dashboard.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PORT</key>
        <string>$DASH_PORT</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF
echo "✅ $LAUNCHD/ai.simplicio.headroom-dashboard.plist"

# 5. Add env vars to .zshrc (idempotent)
echo "🔧 Configuring shell environment..."
for VAR in 'export ANTHROPIC_BASE_URL=http://127.0.0.1:'"$PORT" 'export OPENAI_BASE_URL=https://api.deepseek.com/v1'; do
  KEY=$(echo "$VAR" | cut -d= -f1 | cut -d' ' -f2)
  if grep -q "$KEY" ~/.zshrc 2>/dev/null; then
    echo "  $KEY already in .zshrc"
  else
    echo "$VAR" >> ~/.zshrc
    echo "  ✅ $KEY added to .zshrc"
  fi
  eval "$VAR"
done

# 6. Configure Hermes base_url
echo "🔧 Configuring Hermes base_url..."
if command -v hermes &>/dev/null; then
  CURRENT=$(grep "base_url:" "$HERMES_CONFIG" 2>/dev/null | head -1 | tr -d ' ')
  if [ "$CURRENT" != "base_url:http://127.0.0.1:$PORT/v1" ]; then
    hermes config set model.base_url "http://127.0.0.1:$PORT/v1" 2>&1
    echo "  ✅ model.base_url = http://127.0.0.1:$PORT/v1"
  else
    echo "  model.base_url already set"
  fi
fi

# 7. Load services
echo "🚀 Starting services..."
launchctl bootout gui/$(id -u)/ai.simplicio.headroom 2>/dev/null || true
launchctl bootstrap gui/$(id -u) "$LAUNCHD/ai.simplicio.headroom.plist" 2>&1
launchctl bootout gui/$(id -u)/ai.simplicio.headroom-dashboard 2>/dev/null || true
launchctl bootstrap gui/$(id -u) "$LAUNCHD/ai.simplicio.headroom-dashboard.plist" 2>&1

sleep 3
echo ""
echo "═══════════════════════════════════════"
echo "  ✅ headroom setup complete"
echo "═══════════════════════════════════════"
echo "  Proxy:  http://127.0.0.1:$PORT"
echo "  Dashboard: http://127.0.0.1:$DASH_PORT"
echo "  Hermes: → proxy → DeepSeek"
echo "═══════════════════════════════════════"
echo ""
