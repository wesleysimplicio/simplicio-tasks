# CLAUDE.md — simplicio-tasks (Claude Code)

This repo ships the **simplicio-tasks** skill for Claude Code.

## Install

```bash
cp -r .claude/skills/simplicio-tasks  <your-repo>/.claude/skills/
# or copy into your user skills dir to make it global
```

## Use

```
/simplicio-tasks finish all the open issues
```

Claude Code loads `.claude/skills/simplicio-tasks/SKILL.md` on invocation. The skill
runs the full orchestration loop with Claude's native tools (Bash, Edit, Read, Grep,
git, gh, the Agent/Task sub-agent fabric, Workflow). Claude's sub-agents satisfy the
`execute` extension point; its file tools satisfy `deterministic_edit`; its scheduler
satisfies `watcher`.

See [`AGENTS.md`](AGENTS.md) for the runtime-agnostic contract and the full list of
43 extension points (or read the Step 1b table in the skill directly).
