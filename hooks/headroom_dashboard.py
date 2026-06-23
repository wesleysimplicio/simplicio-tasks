#!/usr/bin/env python3
"""headroom-dashboard — web dashboard + monitor for headroom token savings.

Usage:
    python3 hooks/headroom_dashboard.py              # start web server on :9090
    python3 hooks/headroom_dashboard.py --port 9091

Front-end is split into STYLE / BADGE_SVG / BODY / SCRIPT constants and composed
into HTML via placeholder substitution — single-file (deploy-friendly) but no
longer one opaque blob. The backend (get_status + handlers) is unchanged.
"""
import http.server
import json
import os
import subprocess
import time
from pathlib import Path

HOME = os.path.expanduser("~")
REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_CANDIDATES = [
    Path(HOME) / ".headroom" / "logs" / "proxy.log",
    Path(HOME) / ".hermes" / "logs" / "headroom.log",
    Path(HOME) / ".hermes" / "logs" / "headroom.error.log",
]
LOGO_CANDIDATES = [
    REPO_ROOT / "assets" / "simplicio-loop-logo.png",
    Path(HOME) / "Projetos" / "ai" / "simplicio-runtime" / "site" / "assets" / "img" / "simplicio-logo.png",
]
PID_FILE = Path("/tmp") / "headroom-dashboard.pid"
HEADROOM_PORT = os.environ.get("HEADROOM_PORT", "8788")

# Each runtime: how the 6 skills LOAD, how the loop DRIVE is bound, and coverage STATE.
RUNTIMES = [
    {"name": "Claude", "load": ".claude/skills", "loop": "Stop hook", "state": "full"},
    {"name": "Codex", "load": "AGENTS.md", "loop": "self-paced", "state": "partial"},
    {"name": "Hermes", "load": "native recall", "loop": "native loop", "state": "native"},
    {"name": "OpenClaw", "load": "plugin SDK", "loop": "native loop", "state": "native"},
    {"name": "VS Code", "load": "copilot instructions", "loop": "tasks", "state": "partial"},
    {"name": "Gemini", "load": "GEMINI.md", "loop": "self-paced", "state": "partial"},
    {"name": "Cursor", "load": ".cursor-plugin", "loop": "Stop hook", "state": "full"},
    {"name": "OpenCode", "load": "AGENTS.md", "loop": "self-paced", "state": "partial"},
    {"name": "Kiro", "load": ".kiro/steering", "loop": "spec tick", "state": "partial"},
    {"name": "Antigravity", "load": "rules", "loop": "self-paced", "state": "partial"},
]

# ── Brand badge: faithful inline vector of the Simplicio hexagon-S mark ───────
# Hexagon shell + extruded "S" + stacked-layers core + circuit traces (right) +
# speed particles (left). Used as the favicon and the no-PNG fallback logo.
BADGE_SVG = """<svg viewBox="0 0 240 224" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Simplicio">
  <defs>
    <linearGradient id="sFace" x1="0" y1="0" x2="0.2" y2="1">
      <stop offset="0" stop-color="#e4ff5a"/><stop offset="0.55" stop-color="#9cf614"/><stop offset="1" stop-color="#6fd000"/>
    </linearGradient>
    <linearGradient id="sSide" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#3c8a10"/><stop offset="1" stop-color="#1f5a06"/>
    </linearGradient>
    <linearGradient id="layerTop" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#caff3a"/><stop offset="1" stop-color="#7fe000"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <!-- circuit traces (right) -->
  <g stroke="#8cff00" stroke-width="3.4" fill="none" opacity="0.92" stroke-linecap="round">
    <path d="M168 86 H214"/><path d="M168 112 H206"/><path d="M168 138 H214"/>
  </g>
  <g fill="#03060a" stroke="#8cff00" stroke-width="3.4">
    <circle cx="222" cy="86" r="6"/><circle cx="214" cy="112" r="6"/>
    <rect x="216" y="131.5" width="13" height="13" rx="2"/>
  </g>
  <!-- speed particles (left) -->
  <g fill="#caff26">
    <rect x="44" y="98" width="18" height="5" rx="2"/><rect x="22" y="98" width="11" height="5" rx="2"/>
    <rect x="50" y="112" width="12" height="5" rx="2" opacity="0.85"/><rect x="30" y="112" width="7" height="5" rx="2" opacity="0.7"/>
    <rect x="40" y="126" width="15" height="5" rx="2" opacity="0.8"/><rect x="18" y="126" width="9" height="5" rx="2" opacity="0.6"/>
  </g>
  <!-- hexagon shell -->
  <path d="M120 20 192 62 V150 L120 192 48 150 V62 Z" fill="none" stroke="#8cff00"
        stroke-width="7" stroke-linejoin="round" filter="url(#glow)"/>
  <!-- extruded side face of the S (depth) -->
  <path d="M150 66 H96 a22 22 0 0 0 -22 22 v6 a22 22 0 0 0 22 22 h30 a9 9 0 0 1 0 18 H72 v22 h60
           a22 22 0 0 0 22 -22 v-6 a22 22 0 0 0 -22 -22 H100 a9 9 0 0 1 0 -18 h56 Z"
        fill="url(#sSide)" transform="translate(6,7)"/>
  <!-- top face of the S -->
  <path d="M150 66 H96 a22 22 0 0 0 -22 22 v6 a22 22 0 0 0 22 22 h30 a9 9 0 0 1 0 18 H72 v22 h60
           a22 22 0 0 0 22 -22 v-6 a22 22 0 0 0 -22 -22 H100 a9 9 0 0 1 0 -18 h56 Z"
        fill="url(#sFace)"/>
  <!-- stacked-layers core -->
  <g transform="translate(120,108)">
    <path d="M-26 6 0 -7 26 6 0 19 Z" fill="url(#layerTop)" stroke="#04060a" stroke-width="2"/>
    <path d="M-26 -4 0 -17 26 -4 0 9 Z" fill="#a6ff1f" stroke="#04060a" stroke-width="2"/>
    <path d="M-26 -14 0 -27 26 -14 0 -1 Z" fill="#c9ff45" stroke="#04060a" stroke-width="2"/>
  </g>
</svg>"""

STYLE = """<style>
  :root {
    --bg: #03060a; --bg-2: #05090d;
    --panel: #070f0b; --panel-2: #0a1510; --panel-3: #0d1b14;
    --line: #14352a; --line-soft: #0f2419;
    --text: #eafff0; --muted: #86a89a; --faint: #3a5547;
    --green: #9dff1a; --lime: #caff26; --cyan: #36d7ff;
    --amber: #ffc857; --red: #ff5e6c; --violet: #b88cff;
    --glow: 0 0 26px rgba(157,255,26,0.22);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scrollbar-color: var(--line) transparent; }
  body {
    font-family: "Chakra Petch", "IBM Plex Mono", ui-monospace, "SF Mono", monospace;
    background:
      radial-gradient(900px 520px at 50% -8%, rgba(157,255,26,0.08), transparent 70%),
      linear-gradient(rgba(157,255,26,0.028) 1px, transparent 1px),
      linear-gradient(90deg, rgba(157,255,26,0.02) 1px, transparent 1px),
      var(--bg);
    background-size: auto, 36px 36px, 36px 36px;
    color: var(--text);
    padding: 24px 22px 40px;
    min-height: 100vh;
  }
  body::before {
    content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background: repeating-linear-gradient(180deg, rgba(0,0,0,0) 0 2px, rgba(0,0,0,0.12) 2px 3px);
    opacity: 0.5; mix-blend-mode: overlay;
  }
  .wrap { max-width: 1320px; margin: 0 auto; position: relative; z-index: 1; }

  /* ── hero ──────────────────────────────────────────────────── */
  .hero {
    display: grid; grid-template-columns: minmax(0,1fr) 296px; gap: 16px; align-items: stretch;
  }
  .brand {
    position: relative; display: flex; align-items: center; justify-content: center;
    padding: 26px 20px; border: 1px solid var(--line); border-radius: 14px; overflow: hidden;
    background:
      radial-gradient(620px 320px at 50% 50%, rgba(157,255,26,0.10), transparent 72%),
      linear-gradient(160deg, #04080c, #010204 70%);
    box-shadow: var(--glow), inset 0 0 0 1px rgba(157,255,26,0.05);
  }
  .brand::before, .brand::after {
    content: ""; position: absolute; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--green), var(--cyan), transparent);
    opacity: 0.7;
  }
  .brand::before { top: 0; } .brand::after { bottom: 0; }
  .brand .corner { position: absolute; width: 16px; height: 16px; border: 2px solid rgba(157,255,26,0.55); }
  .brand .corner.tl { top: 10px; left: 10px; border-right: 0; border-bottom: 0; }
  .brand .corner.tr { top: 10px; right: 10px; border-left: 0; border-bottom: 0; }
  .brand .corner.bl { bottom: 10px; left: 10px; border-right: 0; border-top: 0; }
  .brand .corner.br { bottom: 10px; right: 10px; border-left: 0; border-top: 0; }
  .logo { max-width: 100%; max-height: 188px; width: auto; height: auto; object-fit: contain;
          filter: drop-shadow(0 0 22px rgba(157,255,26,0.30)); }

  .status {
    display: flex; flex-direction: column; gap: 9px; padding: 16px 16px 14px;
    border: 1px solid var(--line); border-radius: 14px; background: linear-gradient(180deg, var(--panel-2), var(--panel));
  }
  .status .head {
    font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--faint);
    padding-bottom: 8px; margin-bottom: 2px; border-bottom: 1px dashed var(--line-soft);
  }
  .status-row { display: flex; justify-content: space-between; align-items: center; gap: 12px;
                color: var(--muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; }
  .status-row strong { color: var(--text); font-variant-numeric: tabular-nums; letter-spacing: 0.02em; }
  .badge { display: inline-flex; align-items: center; gap: 8px; color: var(--text);
           border: 1px solid var(--line); border-radius: 999px; padding: 5px 11px; background: rgba(0,0,0,0.34);
           font-size: 0.7rem; white-space: nowrap; }
  .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--red); box-shadow: 0 0 10px rgba(255,94,108,0.7); }
  .dot.green { background: var(--green); box-shadow: 0 0 12px rgba(157,255,26,0.9); }

  /* ── pillars (tagline echo) ───────────────────────────────── */
  .pillars { display: flex; align-items: center; justify-content: center; gap: 14px;
             margin: 16px 0 18px; color: var(--green); font-size: 0.66rem; letter-spacing: 0.16em;
             text-transform: uppercase; text-shadow: 0 0 12px rgba(157,255,26,0.4); }
  .pillars .rail { flex: 1; height: 1px; max-width: 120px;
                   background: linear-gradient(90deg, transparent, var(--green)); }
  .pillars .rail.r { background: linear-gradient(90deg, var(--green), transparent); }
  .pillars .items { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
  .pillars .items span::after { content: "•"; margin-left: 8px; color: var(--faint); }
  .pillars .items span:last-child::after { content: ""; }

  /* ── savings hero metric ──────────────────────────────────── */
  .savings {
    display: grid; grid-template-columns: 168px minmax(0,1fr); gap: 22px; align-items: center;
    padding: 18px 22px; margin-bottom: 14px; border: 1px solid var(--line); border-radius: 14px;
    background:
      radial-gradient(420px 220px at 14% 50%, rgba(157,255,26,0.08), transparent 70%),
      linear-gradient(135deg, var(--panel-2), var(--panel));
  }
  .gauge { position: relative; width: 156px; height: 156px; }
  .gauge svg { transform: rotate(-90deg); }
  .gauge .pct { position: absolute; inset: 0; display: flex; flex-direction: column;
                align-items: center; justify-content: center; }
  .gauge .pct b { font-size: 2.1rem; color: var(--green); line-height: 1;
                  text-shadow: 0 0 16px rgba(157,255,26,0.5); font-variant-numeric: tabular-nums; }
  .gauge .pct small { font-size: 0.56rem; letter-spacing: 0.18em; color: var(--muted); text-transform: uppercase; margin-top: 4px; }
  .savings-body { min-width: 0; }
  .savings-body .lead { font-size: 0.66rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); }
  .savings-body .big { font-size: clamp(2rem, 5vw, 3.4rem); font-weight: 700; color: var(--text);
                       line-height: 1; margin: 6px 0 4px; font-variant-numeric: tabular-nums;
                       text-shadow: 0 0 18px rgba(157,255,26,0.28); overflow-wrap: anywhere; }
  .savings-body .big em { color: var(--green); font-style: normal; }
  .flow { display: grid; grid-template-columns: 1fr auto 1fr; gap: 12px; align-items: center; margin-top: 14px; }
  .flow .node { padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px; background: rgba(0,0,0,0.28); min-width: 0; }
  .flow .node span { display: block; color: var(--muted); text-transform: uppercase; font-size: 0.58rem; letter-spacing: 0.1em; margin-bottom: 5px; }
  .flow .node strong { color: var(--text); font-size: clamp(1.1rem, 2.4vw, 1.7rem); font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }
  .flow .node.after strong { color: var(--cyan); }
  .flow .arrow { color: var(--green); font-size: 1.3rem; text-shadow: 0 0 12px rgba(157,255,26,0.7); }

  /* ── kpi grid ─────────────────────────────────────────────── */
  .kpi-grid { display: grid; grid-template-columns: repeat(7, minmax(0,1fr)); gap: 10px; margin-bottom: 14px; }
  .card { position: relative; overflow: hidden; padding: 13px 14px 15px; min-height: 108px;
          border: 1px solid var(--line); border-radius: 12px; background: linear-gradient(180deg, var(--panel-2), var(--panel)); transition: border-color .2s, box-shadow .2s, transform .2s; }
  .card:hover { border-color: rgba(157,255,26,0.6); box-shadow: 0 0 22px rgba(157,255,26,0.12); transform: translateY(-1px); }
  .card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: var(--accent, var(--green)); opacity: 0.85; }
  .card .label { font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); margin-bottom: 10px; }
  .card .value { font-size: clamp(1.2rem, 1.7vw, 1.7rem); font-weight: 700; color: var(--text);
                 font-variant-numeric: tabular-nums; line-height: 1.04; overflow-wrap: anywhere; }
  .card .sub { font-size: 0.62rem; color: var(--faint); margin-top: 7px; letter-spacing: 0.03em; }
  .card .value.green { color: var(--green); text-shadow: 0 0 12px rgba(157,255,26,0.32); }
  .card .value.amber { color: var(--amber); } .card .value.red { color: var(--red); }
  .card .value.blue { color: var(--cyan); } .card .value.purple { color: var(--violet); }
  .card .bar { height: 4px; border-radius: 4px; margin-top: 12px; background: rgba(255,255,255,0.07); overflow: hidden; }
  .card .bar .fill { height: 100%; border-radius: 4px; transition: width .5s ease; }
  .card .bar .fill.green { background: var(--green); box-shadow: 0 0 14px rgba(157,255,26,0.7); }
  .card .bar .fill.amber { background: var(--amber); } .card .bar .fill.blue { background: var(--cyan); }
  .card .bar .fill.purple { background: var(--violet); }

  /* ── two columns: log + runtimes ──────────────────────────── */
  .cols { display: grid; grid-template-columns: minmax(0,1.45fr) minmax(340px,0.85fr); gap: 14px; }
  .panel { border: 1px solid var(--line); border-radius: 14px; overflow: hidden;
           background: linear-gradient(180deg, var(--panel-2), var(--panel)); }
  .panel-head { display: flex; justify-content: space-between; align-items: center; gap: 12px;
                padding: 13px 15px; border-bottom: 1px solid var(--line-soft); }
  .panel-head .title { font-size: 0.68rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--text); }
  .panel-head .meta { font-size: 0.62rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--faint); }
  .panel-body { padding: 14px 15px; }

  .runtime-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 9px; }
  .runtime { position: relative; min-width: 0; padding: 11px 11px 10px; border: 1px solid var(--line-soft);
             border-radius: 10px; background: rgba(0,0,0,0.3); transition: border-color .2s; }
  .runtime:hover { border-color: rgba(157,255,26,0.45); }
  .runtime-top { display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 8px; }
  .runtime-name { color: var(--text); font-weight: 700; font-size: 0.82rem; letter-spacing: 0.02em; overflow-wrap: anywhere; }
  .pill { border: 1px solid currentColor; border-radius: 999px; padding: 2px 8px; font-size: 0.54rem;
          letter-spacing: 0.08em; text-transform: uppercase; white-space: nowrap; }
  .pill.full, .pill.native { color: var(--green); }
  .pill.partial { color: var(--amber); }
  .runtime-meta { color: var(--muted); font-size: 0.62rem; line-height: 1.55; }
  .runtime-meta .k { color: var(--faint); }

  .log { font-size: 0.66rem; line-height: 1.7; max-height: 360px; overflow-y: auto;
         color: var(--muted); font-variant-numeric: tabular-nums; }
  .log::-webkit-scrollbar { width: 7px; } .log::-webkit-scrollbar-track { background: transparent; }
  .log::-webkit-scrollbar-thumb { background: var(--line); border-radius: 7px; }
  .log-line { display: grid; grid-template-columns: minmax(110px,auto) 64px minmax(0,1fr); gap: 9px;
              padding: 2px 5px; border-radius: 6px; }
  .log-line:hover { background: rgba(157,255,26,0.06); }
  .log-line .ts { color: #355346; white-space: nowrap; }
  .log-line .level { font-weight: 700; }
  .log-line .level.INFO { color: var(--cyan); } .log-line .level.WARNING { color: var(--amber); } .log-line .level.ERROR { color: var(--red); }
  .log-line .msg { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .log-line .msg .num, .log-line .msg .hl { color: var(--green); }
  .log-empty { color: var(--faint); padding: 8px 4px; }

  .footer { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap;
            color: #355346; font-size: 0.64rem; letter-spacing: 0.05em; margin-top: 16px; }

  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }
  .live-dot { animation: pulse 1.5s ease-in-out infinite; }

  @media (max-width: 1080px) {
    .hero { grid-template-columns: 1fr; } .status { flex-direction: row; flex-wrap: wrap; align-items: center; }
    .status .head { width: 100%; }
    .kpi-grid { grid-template-columns: repeat(4, minmax(0,1fr)); }
    .cols { grid-template-columns: 1fr; }
  }
  @media (max-width: 720px) {
    body { padding: 14px 12px 28px; }
    .savings { grid-template-columns: 1fr; justify-items: center; text-align: center; }
    .savings-body { text-align: center; } .flow { width: 100%; }
    .kpi-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }
    .runtime-grid { grid-template-columns: 1fr; }
    .pillars .rail { display: none; }
    .log-line { grid-template-columns: 1fr; gap: 1px; }
  }
</style>"""

BODY = """<div class="wrap">
  <header class="hero">
    <div class="brand">
      <span class="corner tl"></span><span class="corner tr"></span>
      <span class="corner bl"></span><span class="corner br"></span>
      <img class="logo" src="/assets/simplicio-logo.png" alt="Simplicio Loop">
    </div>
    <aside class="status">
      <div class="head">runtime status</div>
      <div class="status-row"><span>proxy</span><span class="badge"><span class="dot" id="statusDot"></span><span id="statusLabel">checking</span></span></div>
      <div class="status-row"><span>port</span><strong id="portLabel">--</strong></div>
      <div class="status-row"><span>uptime</span><strong id="uptimeLabel">--</strong></div>
      <div class="status-row"><span>refresh</span><strong>3s</strong></div>
      <div class="status-row"><span>last sample</span><strong id="ts">--</strong></div>
    </aside>
  </header>

  <div class="pillars">
    <span class="rail"></span>
    <div class="items"><span>smart orchestration</span><span>neural cache</span><span>compressed context</span><span>maximum efficiency</span></div>
    <span class="rail r"></span>
  </div>

  <section class="savings">
    <div class="gauge">
      <svg width="156" height="156" viewBox="0 0 156 156">
        <circle cx="78" cy="78" r="64" fill="none" stroke="#14352a" stroke-width="11"/>
        <circle id="gaugeArc" cx="78" cy="78" r="64" fill="none" stroke="#9dff1a" stroke-width="11"
                stroke-linecap="round" stroke-dasharray="402" stroke-dashoffset="402"
                style="filter: drop-shadow(0 0 8px rgba(157,255,26,0.6)); transition: stroke-dashoffset .6s ease;"/>
      </svg>
      <div class="pct"><b id="savingsPct">0%</b><small>reduction</small></div>
    </div>
    <div class="savings-body">
      <div class="lead">tokens saved · compressed context path</div>
      <div class="big"><em id="savedBig">0</em> tokens</div>
      <div class="flow">
        <div class="node before"><span>before</span><strong id="beforeTokens">0</strong></div>
        <div class="arrow">&rarr;</div>
        <div class="node after"><span>after</span><strong id="afterTokens">0</strong></div>
      </div>
    </div>
  </section>

  <div class="kpi-grid" id="stats"></div>

  <div class="cols">
    <section class="panel">
      <div class="panel-head"><div class="title">proxy log</div><div class="meta" id="logSource">no log yet</div></div>
      <div class="panel-body"><div class="log" id="log"></div></div>
    </section>
    <aside class="panel">
      <div class="panel-head"><div class="title">runtime coverage</div><div class="meta">same loop · different drive</div></div>
      <div class="panel-body"><div class="runtime-grid" id="runtimeGrid"></div></div>
    </aside>
  </div>

  <div class="footer">
    <span>simplicio-loop · headroom token monitor</span>
    <span id="runtimeCount">10 runtimes</span>
  </div>
</div>"""

SCRIPT = """<script>
const GAUGE_CIRC = 402;
function escapeHTML(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function fmt(v){return Number(v||0).toLocaleString();}

function card(label,value,color,sub,bar,barColor){
  label=escapeHTML(label); value=escapeHTML(value); sub=sub?escapeHTML(sub):'';  // safe by construction
  const accent={green:'var(--green)',amber:'var(--amber)',red:'var(--red)',blue:'var(--cyan)',purple:'var(--violet)'}[barColor||color]||'var(--green)';
  const fill=bar?`<div class="bar"><div class="fill ${barColor||color}" style="width:${Math.min(Math.max(bar,0),100)}%"></div></div>`:'';
  const subEl=sub?`<div class="sub">${sub}</div>`:'';
  return `<div class="card" style="--accent:${accent}"><div class="label">${label}</div><div class="value ${color}">${value}</div>${subEl}${fill}</div>`;
}
function runtimeCard(r){
  return `<div class="runtime">
    <div class="runtime-top"><span class="runtime-name">${escapeHTML(r.name)}</span><span class="pill ${escapeHTML(r.state)}">${escapeHTML(r.state)}</span></div>
    <div class="runtime-meta"><span class="k">load</span> ${escapeHTML(r.load)}<br><span class="k">drive</span> ${escapeHTML(r.loop)}</div>
  </div>`;
}

async function refresh(){
  try{
    const d=await (await fetch('/api/status')).json();

    const dot=document.getElementById('statusDot');
    if(d.proxy_running){dot.className='dot green live-dot';document.getElementById('statusLabel').textContent='proxy live';}
    else{dot.className='dot';document.getElementById('statusLabel').textContent='stopped';}
    document.getElementById('portLabel').textContent=d.port;
    document.getElementById('uptimeLabel').textContent=d.uptime;
    document.getElementById('ts').textContent=d.timestamp;

    const pct=Math.min(Math.max(d.savings_pct||0,0),100);
    document.getElementById('savingsPct').textContent=(d.savings_pct||0)+'%';
    document.getElementById('gaugeArc').style.strokeDashoffset=GAUGE_CIRC*(1-pct/100);
    document.getElementById('savedBig').textContent=fmt(d.tokens_saved);
    document.getElementById('beforeTokens').textContent=fmt(d.tokens_before);
    document.getElementById('afterTokens').textContent=fmt(d.tokens_after);

    const memPct=d.memories>0?Math.min(100,d.memories):0;
    document.getElementById('stats').innerHTML=[
      card('requests',fmt(d.requests),'purple','proxy PERF rows',0,'purple'),
      card('tokens before',fmt(d.tokens_before),'amber','raw prompt/output',d.tokens_before>0?Math.min(100,Math.round(d.tokens_before/50000*100)):0,'amber'),
      card('tokens after',fmt(d.tokens_after),'blue','compressed path',d.tokens_after>0?Math.min(100,Math.round(d.tokens_after/50000*100)):0,'blue'),
      card('tokens saved',fmt(d.tokens_saved),d.tokens_saved>0?'green':'amber',d.savings_pct+'% reduction',pct,'green'),
      card('cache hit',d.cache_hit_pct+'%',d.cache_hit_pct>50?'green':'amber','headroom reuse',d.cache_hit_pct,'green'),
      card('memories',fmt(d.memories),'purple','headroom memory',memPct,'purple'),
      card('runtimes',fmt((d.runtimes||[]).length),'green','covered adapters',100,'green'),
    ].join('');

    document.getElementById('runtimeGrid').innerHTML=(d.runtimes||[]).map(runtimeCard).join('');
    document.getElementById('runtimeCount').textContent=(d.runtimes||[]).length+' runtimes · '+fmt(d.ledger_events)+' ledger events';
    document.getElementById('logSource').textContent=d.log_source||'no log yet';

    const logEl=document.getElementById('log');
    const lines=d.log_lines||[];
    if(!lines.length){logEl.innerHTML='<div class="log-empty">awaiting proxy traffic…</div>';}
    else{
      logEl.innerHTML=lines.map(raw=>{
        const l=escapeHTML(raw);  // escaped first; capture groups below are \\d+/\\w+ only — safe for innerHTML
        let level='INFO';
        if(l.includes('WARNING'))level='WARNING';
        if(l.includes('UPSTREAM_ERROR')||l.includes('Error:'))level='ERROR';
        const ts=l.match(/^[\\d-]+ [\\d:,]+/)?.[0]||'';
        let msg=l.replace(ts,'').trim();
        msg=msg.replace(/tok_\\w+=(\\d+)/g,'<span class="hl">$1</span>');
        msg=msg.replace(/(\\d+)/g,'<span class="num">$1</span>');
        msg=msg.replace(/tok_\\w+=/g,'');
        return `<div class="log-line"><span class="ts">${ts}</span><span class="level ${level}">${level}</span><span class="msg">${msg}</span></div>`;
      }).join('');
      logEl.scrollTop=logEl.scrollHeight;
    }
  }catch(e){
    document.getElementById('stats').innerHTML=card('error',e.message,'red','',0,'red');
  }
}
setInterval(refresh,3000); refresh();
</script>"""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Simplicio Loop · Token Monitor</title>
<link rel="icon" href="__FAVICON__">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;700&display=swap" rel="stylesheet">
__STYLE__
</head>
<body>
__BODY__
__SCRIPT__
</body>
</html>"""


import base64 as _b64
import re as _re
_FAVICON = "data:image/svg+xml;base64," + _b64.b64encode(BADGE_SVG.encode()).decode()
# Single-pass substitution — atomic per token, so a slot value can never expand a later slot.
_SLOTS = {"__FAVICON__": _FAVICON, "__STYLE__": STYLE, "__BODY__": BODY, "__SCRIPT__": SCRIPT}
HTML = _re.sub(r"__(?:FAVICON|STYLE|BODY|SCRIPT)__", lambda m: _SLOTS[m.group(0)], HTML)


def get_status():
    proxy_running = False
    port = HEADROOM_PORT
    uptime = "—"
    requests = 0
    tok_before = 0
    tok_after = 0
    tok_saved = 0
    cache_hit = 0.0
    log_lines = []
    cache_count = 0
    log_source = ""

    r = _run(["lsof", "-i", f":{port}"], timeout=3)
    proxy_running = "LISTEN" in r.stdout

    text, log_source = _read_first_log()
    if text:
        lines = [line for line in text.strip().split("\n") if line.strip()]
        log_lines = lines[-36:]
        for line in lines:
            if "PERF" in line:
                requests += 1
                for part in line.split():
                    if part.startswith("tok_before="):
                        tok_before += _parse_int(part.split("=", 1)[1])
                    elif part.startswith("tok_after="):
                        tok_after += _parse_int(part.split("=", 1)[1])
                    elif part.startswith("cache_hit_pct="):
                        try:
                            cache_hit += float(part.split("=", 1)[1])
                            cache_count += 1
                        except ValueError:
                            pass
        tok_saved = tok_before - tok_after
        cache_hit = round(cache_hit / max(cache_count, 1), 1)

    if proxy_running:
        uptime = _proxy_uptime()

    mr = _run(["headroom", "memory", "stats"], timeout=5)
    mem = 0
    for hl in mr.stdout.split("\n"):
        if "Total Memories" in hl:
            try:
                mem = int(hl.split(":")[1].strip())
            except (IndexError, ValueError):
                pass

    ledger = REPO_ROOT / ".simplicio" / "ledger" / "savings-events.jsonl"
    lc = 0
    if ledger.exists():
        with ledger.open(errors="replace") as f:
            lc = sum(1 for _ in f)

    tok_saved = max(tok_saved, 0)
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
        "log_source": log_source,
        "runtimes": RUNTIMES,
        "timestamp": time.strftime("%H:%M:%S"),
    }


def _run(cmd, timeout=5):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (FileNotFoundError, subprocess.SubprocessError):
        return subprocess.CompletedProcess(cmd, 1, "", "")


def _read_first_log():
    for log in LOG_CANDIDATES:
        if log.exists():
            return log.read_text(errors="replace"), str(log)
    return "", ""


def _parse_int(value):
    try:
        return int(float(value))
    except ValueError:
        return 0


def _proxy_uptime():
    r = _run(["pgrep", "-f", "headroom proxy"], timeout=2)
    pids = [pid for pid in r.stdout.strip().split("\n") if pid.strip()]
    if not pids:
        return "running"
    r2 = _run(["ps", "-o", "etime=", "-p", pids[0]], timeout=2)
    return r2.stdout.strip() or "running"


def _fallback_logo_svg():
    """No-PNG fallback — the faithful inline badge framed on black."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 224" width="240" height="224">'
        '<rect width="240" height="224" fill="#03060a"/>' + BADGE_SVG.split(">", 1)[1]
    )


def _send_logo(handler):
    for logo in LOGO_CANDIDATES:
        if logo.exists():
            handler.send_response(200)
            handler.send_header("Content-Type", "image/png")
            handler.send_header("Cache-Control", "public, max-age=3600")
            handler.end_headers()
            handler.wfile.write(logo.read_bytes())
            return
    handler.send_response(200)
    handler.send_header("Content-Type", "image/svg+xml")
    handler.send_header("Cache-Control", "public, max-age=3600")
    handler.end_headers()
    handler.wfile.write(_fallback_logo_svg().encode())


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(json.dumps(get_status()).encode())
        elif path == "/assets/simplicio-logo.png":
            _send_logo(self)
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
