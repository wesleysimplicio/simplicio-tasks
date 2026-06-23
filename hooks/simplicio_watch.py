#!/usr/bin/env python3
"""Simplicio Token Monitor (CLI watch) — proxy + savings status for simplicio-loop.

The compression proxy is powered by headroom-ai (a third-party accelerator Simplicio
integrates); its binary is still invoked as `headroom`, so those command names stay.

Usage:
    python3 hooks/simplicio_watch.py status    # show proxy + savings status
    python3 hooks/simplicio_watch.py start     # start the compression proxy
    python3 hooks/simplicio_watch.py stop      # stop the compression proxy
"""
import json
import os
import subprocess
import sys

HOME = os.path.expanduser("~")
LOGS = os.path.join(HOME, ".hermes", "logs")
PROXY_SERVICE = "ai.simplicio.proxy"


def log(msg):
    print(msg)


def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), -1


def status():
    out, rc = run(["lsof", "-i", ":8787"])
    if "headroom" in out:  # external proxy process name
        log("✅ Simplicio proxy — RUNNING (port 8787)")
    else:
        log("❌ Simplicio proxy — NOT RUNNING")
    out2, _ = run(["headroom", "memory", "stats"])  # external accelerator binary
    for line in out2.split("\n"):
        if "Total" in line or "Database" in line:
            log(f"  {line.strip()}")
    out3, _ = run(["headroom", "output-savings"])  # external accelerator binary
    if "No output-savings data yet" in out3:
        log("  📊 Output savings: no data yet (seed with `headroom learn`)")
    else:
        log(f"  📊 Output savings: {out3[:80]}")
    # Savings ledger
    ledger = os.path.join(HOME, "projetos", "ai", "simplicio-loop",
                          ".simplicio", "ledger", "savings-events.jsonl")
    if os.path.isfile(ledger):
        total = sum(1 for _ in open(ledger))
        log(f"  💰 Savings ledger: {total} events")
    log(f"  🪵 Logs: {LOGS}/simplicio-proxy.log")
    return 0 if "RUNNING" in out2 else 1


def start():
    log("Starting Simplicio compression proxy on port 8787...")
    log("  Use: headroom proxy --port 8787")  # external accelerator binary
    log(f"  Then: launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/{PROXY_SERVICE}.plist")
    return 0


def stop():
    log("Stopping Simplicio compression proxy...")
    run(["launchctl", "bootout", f"gui/{os.getuid()}/{PROXY_SERVICE}"])
    log("  Stopped.")
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    dispatch = {"status": status, "start": start, "stop": stop}
    if cmd in dispatch:
        sys.exit(dispatch[cmd]())
    print(f"Usage: {sys.argv[0]} {{status|start|stop}}")
    sys.exit(1)


if __name__ == "__main__":
    main()
