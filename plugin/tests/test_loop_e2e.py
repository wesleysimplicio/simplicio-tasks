"""End-to-end test of the loop driver (`hooks/loop_stop.py`) — the contract that matters:

the loop stops on **evidence**, not on a bare promise, and not by accident. We drive the real hook
(no mocks) with the Cursor `text` schema and a real scratchpad on disk, and assert each exit path:

  • promise + evidence            → STOP (state cleaned up)        ← the success exit
  • promise WITHOUT evidence       → CONTINUE (re-feed, ignored)   ← the anti-false-done guard
  • promise + evidence, AC pending → CONTINUE (re-feed, ignored)   ← the anti-DRIFT anchor gate
  • promise + evidence, ACs done   → STOP                          ← anchor satisfied
  • no promise, under cap          → CONTINUE (iteration bumped)
  • iteration >= max_iterations    → STOP by cap                   ← distinct from the evidence exit
  • .orchestrator/STOP signal      → STOP immediately

This is the "stopped by evidence, not by cap" proof: cases 1 and 4 stop for *different* reasons,
and case 2 proves a promise alone never escapes the loop.
"""
import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(REPO, "hooks", "loop_stop.py")
JOURNAL = os.path.join(".orchestrator", "loop", "journal.jsonl")
HANDOFF = os.path.join(".orchestrator", "loop", "HANDOFF.md")

SCRATCHPAD = """---
iteration: {iteration}
max_iterations: {max_iter}
completion_promise: "SIMPLICIO_DONE"
evidence_required: true
started_at: "2026-06-24T00:00:00Z"
---
Implement the thing and prove it works.
"""


def _arm(root, iteration=1, max_iter=5):
    loop = os.path.join(root, ".orchestrator", "loop")
    os.makedirs(loop, exist_ok=True)
    with open(os.path.join(loop, "scratchpad.md"), "w", encoding="utf-8") as f:
        f.write(SCRATCHPAD.format(iteration=iteration, max_iter=max_iter))
    return loop


def _tick(root, response_text):
    """Run loop_stop.py exactly as the host would: cwd=root, stdin = {text:...}."""
    return subprocess.run([sys.executable, HOOK], input=json.dumps({"text": response_text}),
                          capture_output=True, text=True, cwd=root)


def _scratchpad(root):
    return os.path.join(root, ".orchestrator", "loop", "scratchpad.md")


def _iteration(root):
    with open(_scratchpad(root), encoding="utf-8") as f:
        for line in f:
            if line.startswith("iteration:"):
                return int(line.split(":", 1)[1])
    return None


def _append_attempt(root, record):
    with open(os.path.join(root, JOURNAL), "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def _install_runtime_scripts(root):
    scripts_dir = os.path.join(root, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    for name in ("cross_agent_wiki.py", "hierarchical_planner.py"):
        shutil.copy2(os.path.join(REPO, "scripts", name), os.path.join(scripts_dir, name))


def _write_watcher_pass(root):
    """Write a passing watcher state (Asolaria N-Nest Corrective Gate)."""
    loop = os.path.join(root, ".orchestrator", "loop")
    os.makedirs(loop, exist_ok=True)
    with open(os.path.join(loop, "watcher_state.json"), "w", encoding="utf-8") as f:
        json.dump({"match": True, "status": "MEASURED", "checked_at": "2026-07-01T00:00:00Z"}, f)


def _write_phase(root, phase="implement", strategy="Ship the smallest verified increment", guard="Do not refactor unrelated code"):
    loop = os.path.join(root, ".orchestrator", "loop")
    os.makedirs(loop, exist_ok=True)
    with open(os.path.join(loop, "phase.json"), "w", encoding="utf-8") as f:
        json.dump({
            "phase": phase,
            "strategy": strategy,
            "tactical_guard": guard,
            "iteration": 2,
        }, f)


def test_promise_with_evidence_stops(tmp_path):
    root = str(tmp_path)
    _arm(root)
    _write_watcher_pass(root)  # watcher-gate must pass before promise is honored
    r = _tick(root, "All green. <promise>SIMPLICIO_DONE</promise> tests pass ✓ "
                    "https://github.com/o/r/pull/9")
    assert r.returncode == 0
    assert r.stdout.strip() == "", "expected STOP (no re-feed), got: %s" % r.stdout
    assert not os.path.exists(_scratchpad(root)), "state should be cleaned up on a verified stop"


def test_bare_promise_without_evidence_continues(tmp_path):
    root = str(tmp_path)
    _arm(root, iteration=1, max_iter=5)
    r = _tick(root, "I think I'm done. <promise>SIMPLICIO_DONE</promise>")  # no evidence token
    assert r.returncode == 0
    # the loop must NOT stop on a bare promise — it re-feeds and bumps the iteration
    assert "followup_message" in r.stdout or "block" in r.stdout, \
        "a bare promise must be ignored, not honored:\n%s" % r.stdout
    assert os.path.exists(_scratchpad(root)), "loop wrongly stopped on a bare promise"
    assert _iteration(root) == 2


def _write_anchor(root, criteria):
    loop = os.path.join(root, ".orchestrator", "loop")
    os.makedirs(loop, exist_ok=True)
    with open(os.path.join(loop, "anchor.json"), "w", encoding="utf-8") as f:
        json.dump({"item": "1", "goal": "g", "goal_fp": "x", "criteria": criteria}, f)


def test_promise_with_evidence_but_pending_anchor_continues(tmp_path):
    # The mechanical anti-drift gate: even WITH evidence, a promise must NOT stop the loop while the
    # task anchor still has an unverified acceptance criterion — it re-feeds instead, naming the gap.
    root = str(tmp_path)
    _arm(root, iteration=1, max_iter=5)
    _write_anchor(root, [{"id": "AC1", "status": "done"}, {"id": "AC2", "status": "pending"}])
    r = _tick(root, "Looks done. <promise>SIMPLICIO_DONE</promise> tests pass ✓ "
                    "https://github.com/o/r/pull/9")
    assert r.returncode == 0
    assert "followup_message" in r.stdout or "block" in r.stdout, \
        "a promise with an open AC must be ignored, not honored:\n%s" % r.stdout
    assert os.path.exists(_scratchpad(root)), "loop wrongly stopped with an open AC"
    assert "AC2" in r.stdout, "re-feed should name the open acceptance criterion:\n%s" % r.stdout


def test_promise_with_evidence_all_acs_done_stops(tmp_path):
    # Once every anchored AC is verified, the evidence-backed promise stops the loop as before.
    root = str(tmp_path)
    _arm(root, iteration=1, max_iter=5)
    _write_watcher_pass(root)  # watcher-gate must pass
    _write_anchor(root, [{"id": "AC1", "status": "done"}, {"id": "AC2", "status": "done"}])
    r = _tick(root, "All green. <promise>SIMPLICIO_DONE</promise> tests pass ✓ "
                    "https://github.com/o/r/pull/9")
    assert r.returncode == 0
    assert r.stdout.strip() == "", "expected STOP (every AC verified), got: %s" % r.stdout
    assert not os.path.exists(_scratchpad(root)), "state should be cleaned up on a verified stop"


def test_no_promise_continues_and_bumps_iteration(tmp_path):
    root = str(tmp_path)
    _arm(root, iteration=2, max_iter=5)
    r = _tick(root, "Made progress; still working on the failing test.")
    assert "followup_message" in r.stdout
    assert _iteration(root) == 3


def test_continue_surfaces_phase_hint(tmp_path):
    root = str(tmp_path)
    _arm(root, iteration=2, max_iter=5)
    _write_phase(root, phase="implement", strategy="Ship the smallest verified increment", guard="Do not refactor unrelated code")
    r = _tick(root, "Still implementing; no promise yet.")
    assert r.returncode == 0
    assert "phase=implement" in r.stdout
    assert "guard=Do not refactor unrelated code" in r.stdout


def test_continue_runs_planner_and_refreshes_wiki(tmp_path):
    root = str(tmp_path)
    _arm(root, iteration=2, max_iter=5)
    _install_runtime_scripts(root)
    r = _tick(root, "Still implementing; no promise yet.")
    assert r.returncode == 0
    assert "phase=implement" in r.stdout, r.stdout
    phase = os.path.join(root, ".orchestrator", "loop", "phase.json")
    summary = os.path.join(root, ".orchestrator", "wiki", "SUMMARY.md")
    journal_dir = os.path.join(root, ".orchestrator", "wiki", "journal")
    assert os.path.exists(phase), "planner should materialize phase.json on first active turn"
    assert os.path.exists(summary), "continue path should refresh the cross-agent wiki summary"
    assert os.listdir(journal_dir), "continue path should capture at least one wiki journal entry"


def test_iteration_cap_stops(tmp_path):
    root = str(tmp_path)
    _arm(root, iteration=5, max_iter=5)  # at the cap
    r = _tick(root, "still going, no promise here")
    assert r.stdout.strip() == "", "cap reached must STOP, not re-feed:\n%s" % r.stdout
    assert not os.path.exists(_scratchpad(root)), "cap stop should clean up state"


def test_iteration_cap_handoff_carries_attempt_lineage(tmp_path):
    root = str(tmp_path)
    _arm(root, iteration=5, max_iter=5)
    _append_attempt(root, {
        "iteration": 4,
        "action": "split provider adapter",
        "gate": "blocked",
        "fingerprint": "deadbeef0001",
        "note": "needs a fixture",
        "execution_state": "authorized",
        "stage_id": "validate",
        "decision": "retry",
        "validator": "pytest",
        "retry_count": 2,
        "chunk_id": "audit:2",
        "source_artifact": "audit.md",
        "blocked_reason": "fixture missing",
        "next_action": "add fixture",
    })
    r = _tick(root, "still going, no promise here")
    assert r.stdout.strip() == "", "cap reached must STOP, not re-feed:\n%s" % r.stdout
    handoff = os.path.join(root, HANDOFF)
    assert os.path.exists(handoff), "cap stop should write HANDOFF.md"
    body = open(handoff, encoding="utf-8").read()
    assert "state=authorized" in body
    assert "stage=validate" in body
    assert "validator=pytest" in body
    assert "next=add fixture" in body
    assert "blocked=fixture missing" in body


def test_stop_signal_halts(tmp_path):
    root = str(tmp_path)
    _arm(root)
    open(os.path.join(root, ".orchestrator", "STOP"), "w").close()
    r = _tick(root, "anything")
    assert r.stdout.strip() == ""
    assert not os.path.exists(_scratchpad(root))


def test_done_flag_halts(tmp_path):
    root = str(tmp_path)
    loop = _arm(root)
    open(os.path.join(loop, "done.flag"), "w").close()
    r = _tick(root, "anything")
    assert r.stdout.strip() == ""
    assert not os.path.exists(_scratchpad(root)), "done.flag should stop and clean state"


def test_legacy_done_file_halts(tmp_path):
    root = str(tmp_path)
    loop = _arm(root)
    open(os.path.join(loop, "done"), "w").close()
    r = _tick(root, "anything")
    assert r.stdout.strip() == ""
    assert not os.path.exists(_scratchpad(root)), "legacy done file should still stop and clean state"


def test_gate_lock_fresh_allows_stop_without_consuming_iteration(tmp_path):
    root = str(tmp_path)
    loop = _arm(root, iteration=2, max_iter=5)
    open(os.path.join(loop, "gate.lock"), "w").close()
    r = _tick(root, "waiting on background verification")
    assert r.stdout.strip() == ""
    assert os.path.exists(_scratchpad(root)), "fresh gate lock should preserve loop state"
    assert _iteration(root) == 2, "fresh gate lock should not consume an iteration"


def test_gate_lock_stale_refeeds_again(tmp_path):
    root = str(tmp_path)
    loop = _arm(root, iteration=2, max_iter=5)
    lock = os.path.join(loop, "gate.lock")
    open(lock, "w").close()
    stale = __import__("time").time() - 1900
    os.utime(lock, (stale, stale))
    r = _tick(root, "background gate appears stale")
    assert "followup_message" in r.stdout or "block" in r.stdout
    assert _iteration(root) == 3, "stale gate lock should stop blocking and re-feed"


def test_budget_halted_writes_handoff_and_stops(tmp_path):
    root = str(tmp_path)
    _arm(root, iteration=2, max_iter=5)
    os.makedirs(os.path.join(root, ".orchestrator"), exist_ok=True)
    with open(os.path.join(root, ".orchestrator", "loop-budget.json"), "w", encoding="utf-8") as f:
        json.dump({"state": "halted"}, f)
    r = _tick(root, "budget exhausted")
    assert r.stdout.strip() == ""
    assert not os.path.exists(_scratchpad(root))
    assert os.path.exists(os.path.join(root, HANDOFF)), "budget halt should write HANDOFF.md"


def test_spindle_latched_writes_handoff_and_stops(tmp_path):
    root = str(tmp_path)
    loop = _arm(root, iteration=2, max_iter=5)
    with open(os.path.join(loop, "spindle_state.json"), "w", encoding="utf-8") as f:
        json.dump({"latch": True, "next_agent": "codex"}, f)
    r = _tick(root, "handoff in progress")
    assert r.stdout.strip() == ""
    assert not os.path.exists(_scratchpad(root))
    handoff = os.path.join(root, HANDOFF)
    assert os.path.exists(handoff), "latched spindle should write HANDOFF.md"
    assert "codex" in open(handoff, encoding="utf-8").read()


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _selfrun import run_module
    run_module(globals(), "test_loop_e2e")
