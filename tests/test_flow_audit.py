import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOW = os.path.join(REPO, "scripts", "flow_audit.py")


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip(), encoding="utf-8")


def _run(args, cwd):
    return subprocess.run([sys.executable, FLOW] + args, capture_output=True, text=True, cwd=cwd)


def test_flow_audit_fails_on_frontend_call_without_endpoint(tmp_path):
    _write(tmp_path / "frontend" / "Checkout.tsx", """
export function Checkout() {
  return <button onClick={() => fetch("/api/checkout", { method: "POST" })}>Pay</button>
}
""")
    _write(tmp_path / "backend" / "routes.py", """
@app.get("/api/health")
def health():
    return {"ok": True}
""")

    r = _run(["audit", str(tmp_path), "--fail-on", "high"], cwd=REPO)
    assert r.returncode == 1, r.stdout
    assert "frontend_call_without_backend_endpoint" in r.stdout, r.stdout


def test_flow_audit_detects_backend_stub(tmp_path):
    _write(tmp_path / "frontend" / "Login.tsx", """
export function Login() {
  return <button onClick={() => fetch("/api/login", { method: "POST" })}>Login</button>
}
""")
    _write(tmp_path / "backend" / "routes.py", """
@app.post("/api/login")
def login():
    raise NotImplementedError("TODO")
""")

    r = _run(["audit", str(tmp_path), "--fail-on", "high"], cwd=REPO)
    assert r.returncode == 1, r.stdout
    assert "backend_endpoint_stub" in r.stdout, r.stdout


def test_flow_audit_passes_matched_non_stub_flow(tmp_path):
    _write(tmp_path / "frontend" / "Login.tsx", """
export function Login() {
  return <button onClick={() => fetch("/api/login", { method: "POST" })}>Login</button>
}
""")
    _write(tmp_path / "backend" / "routes.py", """
@app.post("/api/login")
def login():
    return {"ok": True}
""")

    r = _run(["audit", str(tmp_path), "--fail-on", "high"], cwd=REPO)
    assert r.returncode == 0, r.stdout
    assert "flow-audit: PASS" in r.stdout, r.stdout


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _selfrun import run_module
    run_module(globals(), "test_flow_audit")
