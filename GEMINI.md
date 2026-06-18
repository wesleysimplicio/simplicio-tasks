# GEMINI.md — simplicio-tasks (Gemini / other runtimes)

The **simplicio-tasks** skill is runtime-agnostic. Gemini, Codex, Copilot, Grok, or
any local agent can run it from the same source file.

## Load

Point your agent at:

```
.claude/skills/simplicio-tasks/SKILL.md
```

The folder name is `.claude/` for convention, but nothing in the skill is
Claude-specific — it uses only shell, git, gh, file edit, and web.

## Use

```
simplicio-tasks: finish all the open issues
```

## Binding

Where your runtime exposes native capabilities (a repo mapper, a deterministic file
writer, a local model fan-out, a durable scheduler), bind them to the matching
extension points in the Step 1b table so the steps become deterministic and
near-zero-token. Otherwise the LLM fallbacks cover 100% of the work.

See [`AGENTS.md`](AGENTS.md) for the full contract.
