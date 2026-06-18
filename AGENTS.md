# AGENTS.md — simplicio-tasks

This repository ships **one runtime-agnostic skill**: the Universal Looping AI
Orchestrator. Any agent runtime that reads `AGENTS.md` / skill folders can run it.

## What to load

The skill lives at:

```
.claude/skills/simplicio-tasks/SKILL.md
```

That single file IS the protocol. Load it and follow it end-to-end. It uses only
standard tools (shell, git, gh, file edit, web) so it works on any strong LLM.

## Activation

The user invokes it with a target body of work:

```
/simplicio-tasks finish all the open issues
/simplicio-tasks clear the CI queue
/simplicio-tasks drain the Jira board
```

If no argument is given, default to "all open work-items in the default source" and
confirm scope in one line only if ambiguous.

## Extension points (bind native, else fall back)

The skill defines **43 named extension points** (see the Step 1b table in `SKILL.md`).
For each point, if this runtime exposes a faster native capability, **bind it** —
the step becomes deterministic and near-zero-token. If not, perform the documented
LLM fallback. The skill never requires a specific runtime; the binding lives here in
the host, not in the skill.

## Non-negotiables

- Run commands for real — never simulate output.
- Never mark an item done without green gates + evidence ("works, not just compiles").
- Secret-scan every diff; route irreversible ops through the human gate.
- Unattended 24/7 runs require a cost kill-switch (`ceiling > 0`).
- Report an honest token-savings line, credited only on a passing quality gate.
