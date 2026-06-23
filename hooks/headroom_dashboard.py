#!/usr/bin/env python3
"""headroom-dashboard — web dashboard + monitor for headroom token savings.

Usage:
    python3 hooks/headroom_dashboard.py              # start web server on :9090
    python3 hooks/headroom_dashboard.py --port 9091
"""
import http.server
import json
import os
import subprocess
import time
from pathlib import Path

HOME = os.path.expanduser("~")
LOG = Path(HOME) / ".headroom" / "logs" / "proxy.log"
PID_FILE = Path("/tmp") / "headroom-dashboard.pid"

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Headroom Monitor · simplicio-loop</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'SF Mono', 'Fira Code', monospace;
    background: #080808;
    color: #c8c8c8;
    padding: 24px;
    min-height: 100vh;
  }
  .wrap { max-width: 1100px; margin: 0 auto; }

  /* Header */
  header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 24px; padding-bottom: 16px;
    border-bottom: 1px solid #1a1a1a;
  }
  header h1 {
    font-size: 1.1em; font-weight: 600; color: #d4a574;
    letter-spacing: -0.3px;
  }
  header h1 span { color: #555; font-weight: 400; }
  header .badge {
    background: #141414; border: 1px solid #222; border-radius: 100px;
    padding: 4px 14px; font-size: 0.7em; color: #888;
  }
  header .badge .dot {
    display: inline-block; width: 6px; height: 6px; border-radius: 50%;
    margin-right: 6px; vertical-align: middle;
  }
  header .badge .dot.green { background: #4ade80; box-shadow: 0 0 6px #4ade8040; }
  header .badge .dot.red { background: #f87171; box-shadow: 0 0 6px #f8717140; }

  /* Stats grid */
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
    margin-bottom: 24px;
  }
  .card {
    background: #0e0e0e;
    border: 1px solid #1c1c1c;
    border-radius: 10px;
    padding: 14px 16px;
    transition: border 0.2s, background 0.2s;
    position: relative;
    overflow: hidden;
  }
  .card:hover { border-color: #2a2a2a; background: #111; }
  .card .label {
    font-size: 0.6em;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #555;
    margin-bottom: 6px;
  }
  .card .value {
    font-size: 1.5em;
    font-weight: 700;
    color: #e0e0e0;
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
  }
  .card .sub {
    font-size: 0.65em;
    color: #555;
    margin-top: 4px;
  }
  .card .value.gold { color: #d4a574; }
  .card .value.green { color: #4ade80; }
  .card .value.amber { color: #fbbf24; }
  .card .value.red { color: #f87171; }
  .card .value.blue { color: #60a5fa; }
  .card .value.purple { color: #a78bfa; }
  .card .bar {
    height: 2px;
    border-radius: 1px;
    margin-top: 8px;
    background: #1a1a1a;
    overflow: hidden;
  }
  .card .bar .fill {
    height: 100%;
    border-radius: 1px;
    transition: width 0.5s ease;
  }
  .card .bar .fill.gold { background: #d4a574; }
  .card .bar .fill.green { background: #4ade80; }

  /* Sections */
  .section-title {
    font-size: 0.7em;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #444;
    margin-bottom: 10px;
  }

  /* Log viewer */
  .log-wrap {
    background: #0a0a0a;
    border: 1px solid #161616;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 24px;
  }
  .log-wrap .log {
    font-size: 0.62em;
    line-height: 1.6;
    max-height: 280px;
    overflow-y: auto;
    color: #555;
  }
  .log-wrap .log::-webkit-scrollbar { width: 4px; }
  .log-wrap .log::-webkit-scrollbar-track { background: transparent; }
  .log-wrap .log::-webkit-scrollbar-thumb { background: #222; border-radius: 2px; }
  .log-line {
    display: flex;
    gap: 8px;
    padding: 1px 4px;
    border-radius: 2px;
  }
  .log-line:hover { background: #111; }
  .log-line .ts { color: #333; white-space: nowrap; }
  .log-line .level {
    font-weight: 600;
    min-width: 50px;
  }
  .log-line .level.INFO { color: #60a5fa; }
  .log-line .level.WARNING { color: #fbbf24; }
  .log-line .level.ERROR { color: #f87171; }
  .log-line .msg { color: #555; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .log-line .msg .hl { color: #888; }
  .log-line .msg .num { color: #d4a574; }

  /* Timestamp */
  .footer {
    text-align: center;
    color: #333;
    font-size: 0.65em;
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid #141414;
  }

  /* Responsive */
  @media (max-width: 600px) {
    body { padding: 12px; }
    .grid { grid-template-columns: repeat(2, 1fr); gap: 8px; }
    .card .value { font-size: 1.2em; }
    header { flex-direction: column; align-items: flex-start; gap: 8px; }
  }

  /* Pulse animation for live indicator */
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
  .live-dot { animation: pulse 1.5s ease-in-out infinite; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>⬡ headroom <span>· token monitor</span></h1>
    <div class="badge"><span class="dot" id="statusDot"></span><span id="statusLabel">checking...</span> · <span id="uptimeLabel">—</span></div>
  </header>

  <div class="grid" id="stats"></div>

  <div class="section-title">proxy log · last 30 lines</div>
  <div class="log-wrap">
    <div class="log" id="log"></div>
  </div>

  <div class="footer">simplicio-loop · headroom v0.27.0 · <span id="ts">—</span></div>
</div>

<script>
const COLORS = { gold:'gold', green:'green', amber:'amber', red:'red', blue:'blue', purple:'purple' };

function val(v, color='gold', sub='') {
  return `<div class="value ${color}">${v}</div>${sub ? `<div class="sub">${sub}</div>` : ''}`;
}
function card(label, value, color='gold', sub='', bar=0, barColor='gold') {
  return `<div class="card"><div class="label">${label}</div>${val(value,color,sub)}${bar ? `<div class="bar"><div class="fill ${barColor}" style="width:${Math.min(bar,100)}%"></div></div>` : ''}</div>`;
}

async function refresh() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();

    // Status header
    const dot = document.getElementById('statusDot');
    const label = document.getElementById('statusLabel');
    const uptime = document.getElementById('uptimeLabel');
    if (d.proxy_running) {
      dot.className = 'dot green live-dot';
      label.textContent = 'proxy live';
    } else {
      dot.className = 'dot red';
      label.textContent = 'stopped';
    }
    uptime.textContent = d.uptime;

    // Stats cards
    const svgPct = d.tokens_saved > 0 ? Math.round((d.tokens_saved / Math.max(d.tokens_before,1)) * 100) : 0;
    const memPct = d.memories > 0 ? Math.min(100, Math.round((d.memories / 100) * 100)) : 0;
    document.getElementById('stats').innerHTML = `
      ${card('proxy status', d.proxy_running ? 'running' : 'stopped', d.proxy_running ? 'green' : 'red', '', 0)}
      ${card('port', d.port, 'gold', '')}
      ${card('uptime', d.uptime, 'blue', '')}
      ${card('requests', d.requests.toString(), 'purple', '', 0)}
      ${card('tokens before', d.tokens_before.toLocaleString(), 'amber', '', d.tokens_before > 0 ? Math.min(100, Math.round((d.tokens_before / 50000) * 100)) : 0, 'amber')}
      ${card('tokens after', d.tokens_after.toLocaleString(), 'blue', '', d.tokens_after > 0 ? Math.min(100, Math.round((d.tokens_after / 50000) * 100)) : 0, 'blue')}
      ${card('tokens saved', d.tokens_saved.toLocaleString(), d.tokens_saved > 0 ? 'green' : 'gold', `~${d.savings_pct}% reduction`, svgPct, 'green')}
      ${card('cache hit', d.cache_hit_pct + '%', d.cache_hit_pct > 50 ? 'green' : 'amber', '', d.cache_hit_pct, 'green')}
      ${card('memories', d.memories.toString(), 'purple', '', memPct, 'purple')}
      ${card('ledger events', d.ledger_events.toString(), 'amber', '', 0)}
    `;

    // Log lines
    const logEl = document.getElementById('log');
    logEl.innerHTML = d.log_lines.map(l => {
      let level = 'INFO', msg = l;
      if (l.includes('WARNING')) level = 'WARNING';
      if (l.includes('UPSTREAM_ERROR') || l.includes('Error:')) level = 'ERROR';
      const ts = l.match(/^[\\d-]+ [\\d:,]+/)?.[0] || '';
      msg = l.replace(ts, '').trim();
      // Highlight numbers
      msg = msg.replace(/tok_\\w+=(\\d+)/g, '<span class="hl">$1</span>');
      msg = msg.replace(/(\\d+)/g, '<span class="num">$1</span>');
      msg = msg.replace(/tok_\\w+=/g, '');
      return `<div class="log-line"><span class="ts">${ts}</span><span class="level ${level}">${level}</span><span class="msg">${msg}</span></div>`;
    }).join('');
    logEl.scrollTop = logEl.scrollHeight;

    document.getElementById('ts').textContent = d.timestamp;
  } catch(e) {
    document.getElementById('stats').innerHTML = card('error', e.message, 'red');
  }
}
setInterval(refresh, 3000);
refresh();
</script>
</body>
</html>"""


def get_status():
    proxy_running = False
    port = "8788"
    uptime = "—"
    requests = 0
    tok_before = 0
    tok_after = 0
    tok_saved = 0
    cache_hit = 0.0
    log_lines = []
    cache_count = 0

    r = subprocess.run(["lsof", "-i", f":{port}"], capture_output=True, text=True, timeout=3)
    proxy_running = "LISTEN" in r.stdout

    if proxy_running:
        if LOG.exists():
            text = LOG.read_text(errors="replace")
            lines = text.strip().split("\n")
            log_lines = lines[-30:]
            for line in lines:
                if "PERF" in line:
                    requests += 1
                    for part in line.split():
                        if part.startswith("tok_before="):
                            tok_before += int(part.split("=")[1])
                        elif part.startswith("tok_after="):
                            tok_after += int(part.split("=")[1])
                        elif part.startswith("cache_hit_pct="):
                            try:
                                v = float(part.split("=")[1])
                                cache_hit += v
                                cache_count += 1
                            except:
                                pass
            tok_saved = tok_before - tok_after
            cache_hit = round(cache_hit / max(cache_count, 1), 1)

        r2 = subprocess.run(
            ["ps", "-o", "etime=", "-p", "48563"],
            capture_output=True, text=True, timeout=2
        )
        if r2.stdout.strip():
            uptime = r2.stdout.strip()
        else:
            r3 = subprocess.run(
                ["pgrep", "-f", "headroom proxy"],
                capture_output=True, text=True, timeout=2
            )
            pids = r3.stdout.strip().split("\n")
            if pids and pids[0]:
                r4 = subprocess.run(
                    ["ps", "-o", "etime=", "-p", pids[0]],
                    capture_output=True, text=True, timeout=2
                )
                uptime = r4.stdout.strip() or "running"

    mr = subprocess.run(["headroom", "memory", "stats"],
                        capture_output=True, text=True, timeout=5)
    mem = 0
    for hl in mr.stdout.split("\n"):
        if "Total Memories" in hl:
            try:
                mem = int(hl.split(":")[1].strip())
            except:
                pass

    ledger = Path(HOME) / "projetos" / "ai" / "simplicio-loop" / \
             ".simplicio" / "ledger" / "savings-events.jsonl"
    lc = sum(1 for _ in open(ledger)) if ledger.exists() else 0

    savings_pct = round((tok_saved / max(tok_before, 1)) * 100, 1)

    return {
        "proxy_running": proxy_running,
        "port": port,
        "uptime": uptime,
        "requests": requests,
        "tokens_before": tok_before,
        "tokens_after": tok_after,
        "tokens_saved": tok_saved,
        "savings_pct": savings_pct,
        "cache_hit_pct": cache_hit,
        "memories": mem,
        "ledger_events": lc,
        "log_lines": log_lines,
        "timestamp": time.strftime("%H:%M:%S"),
    }


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(json.dumps(get_status()).encode())
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(HTML.encode())

    def log_message(self, format, *args):
        pass


def main():
    port = int(os.environ.get("PORT", "9090"))
    srv = http.server.HTTPServer(("127.0.0.1", port), Handler)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    print(f"⬡ headroom monitor · http://127.0.0.1:{port}")
    print(f"   api: /api/status · refresh: 3s")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.server_close()
        if PID_FILE.exists():
            PID_FILE.unlink()


if __name__ == "__main__":
    main()
