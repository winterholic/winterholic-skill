# Global Rules

These rules are the portable, public-safe version of my personal harness ruleset. Reuse them selectively instead of copying them blindly.

## Core Principles

- Respond to the user in Korean.
- Be explicit about uncertainty. Mark unverified commands, versions, and numbers inline with `확인 필요`.
- If a step is blocked, denied, or impossible, say so directly with the reason and propose an alternative.
- Stay focused on the requested task. Ask once when scope is genuinely ambiguous.
- Default to discussion. Modify code or files only on a clear imperative.
- Never without explicit request: `git push`, reading `.env` or secret stores, or writing obviously unsafe security-sensitive code.
- Comments should explain why, not what.
- When receiving review or correction, verify before agreeing or pushing back.

## Verification Rules

- Before using completion language for code or file work, include the command just run and 1-3 lines of fresh output in the same response.
- Do not reuse old output when claiming a fix.
- If execution is impossible, say `미실행: <reason>` instead of pretending verification happened.
- For repeated bug attempts, switch from quick fixes to root-cause debugging: callstack, business logic, environment, logs.

## Git

- `push`: only when explicitly requested.
- In a git repo: branch first, then commit in meaningful units.
- For code review work: read-only unless the user asks for edits.
- In a non-git project: do not use git commands.
- Do not amend or rewrite history unless explicitly requested.

## Large File Strategy

When producing a long file:

1. Create the file or skeleton first so progress survives interruption.
2. Add sections incrementally.
3. If interrupted, resume from the existing file.
4. Signal continuation explicitly.

## Handoff

- Default handoff directory: `~/.claude/handoffs/`
- Filename pattern: `YYYY-MM-DD-HHmm-topic-kebab.md`
- If the user asks for handoff, read the handoff skill first and decide whether this is create vs resume from context.
- Keep handoff files as short operational documents, not full journals.

## Context Hygiene

- Suggest handoff when context usage becomes high.
- Prefer one relevant skill over many overlapping skills.
- Keep rarely used skills outside the always-loaded path.
- Preserve important operational rules in files, not only in chat context.

## Knowledge Vault

- If you use a knowledge vault, define its root explicitly in your local setup.
- Before vault read/write, check the vault-specific guide file first if one exists.
- HTML reports should stay outside the vault by default.
- Treat the vault as a downstream artifact store, not your only source of harness truth.

## Skill Check Before Starting

- Check whether one skill clearly fits before starting work.
- If multiple fit, prefer one by this order: file-extension match, specialized skill, then general category skill.
- Keep global always-loaded skills small and high leverage.
- Move bulky or niche instructions to `sub-skills/` or `workflows-skills/`.

## Skill Layout

Recommended structure:

- `~/.claude/skills/`: always-loaded global skills
- `~/.claude/sub-skills/`: non-auto-loaded specialty skills
- `~/.claude/workflows-skills/`: multi-step or orchestration-heavy skills
- `~/.claude/imported-sub-skills/`: externally sourced or experimental skills
- `~/.claude/agents-archive/`: archived agent definitions kept for manual reuse

## Agent Modes

- Default: respond directly from the main context.
- Use a subagent only when explicitly requested.
- Use an agent team only when explicitly requested for cross-domain work.
- If both a narrow subagent trigger and a team trigger appear, prefer the narrower scope unless the user explicitly asks for a team.
- Prefer skills over persistent agent hierarchies when the value is really procedural, not identity-based.

## Work History

- Work-history can be handled by a stop hook or external summarizer.
- Keep format ownership in one place only.
- Avoid manually duplicating automated history unless explicitly requested.
- If automation is asynchronous, accept one-turn lag as normal.

## Completion Checklist

- If you changed files inside a git repo, commit them in meaningful units after verification.
- Confirm any project-local agent instructions were followed before closing the task.
- If you intentionally skipped a normal step because the user asked you to, say so explicitly.

## RTK

- If you use RTK in your environment, prefer `rtk <command>` for compact output.
- Keep RTK instructions local if your setup depends on it; they are optional for portable sharing.
