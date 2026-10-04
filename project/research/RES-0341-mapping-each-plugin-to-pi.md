---
id: RES-0341
artifact: research
status: approved
elaborates: RES-0340
---

# Mapping each meowpaw plugin to Pi

## Summary

Each of the sixteen meowpaw plugins mapped to its Pi equivalent, component by
component. Skills are the most portable (same `SKILL.md` format). Hooks are the
least (TypeScript event handlers instead of command hooks). Native binaries
remain usable from extensions. The mapping produces one Pi package per layer
(kernel, method, practice) with extensions for the executable behaviour and
skills for the instructional content.

Source: the plugin directories under `plugins/`, read 2026-10-04.

## Method

Each plugin directory was examined for its `plugin.json`, skills, hooks,
agents, output styles, native binaries, budgets and evals. The Pi analogue
for each component was determined from RES-0340.

## Plugin-by-plugin mapping

### meow-core (kernel)

| Component | Claude Code | Pi |
|---|---|---|
| Output style | `output-styles/meow.md` | Extension: `before_agent_start` adds the reply shape to `guidelines` |
| Evals | `evals/` (error-report, gap-list-kept, no-preamble-no-recap, one-line-keeps-the-gap) | No Pi equivalent; would need a custom eval runner |
| Budget | `budget.toml` (4200 chars) | Not enforced by Pi |
| Native binary | none | — |

The output style is the kernel's core contribution. In Pi, an extension
injects it into the system prompt on `before_agent_start`. The content of
`meow.md` is portable as a string; the extension reads it from the package's
skill directory or embeds it.

### meow-prose (kernel)

| Component | Claude Code | Pi |
|---|---|---|
| Skills | `skills/writing/SKILL.md` (25 evals, 1 agent) | Same `SKILL.md`, loaded by Pi's skill discovery |
| Agent | `agents/reviewer.md` | Tool registered by extension: nested model call with constrained prompt |
| Evals | 25 pattern/corrected pairs | No Pi equivalent |
| Budget | 700 chars + ~5000 tokens on invocation | Not enforced by Pi |

The writing skill is fully portable. The reviewer agent becomes a tool.

### meow-prose-gate (kernel)

| Component | Claude Code | Pi |
|---|---|---|
| Hook | `PreToolUse` matcher `Bash` for commit/PR/issue/release commands | Extension: `user_bash` handler that shells out to `meow-prose-gate check` or ports the check logic |
| Fragment | `fragments/judge.md` | Loaded by the extension as a prompt template for the judge call |
| Native binary | `bin/meow-prose-gate` | Shelled out to, or ported |
| Budget | 0 chars permanent | — |

The prose gate is a pre-commit hook that checks text before it is published.
In Pi, a `user_bash` event handler intercepts the relevant `git` and `gh`
commands. The handler either shells out to the existing binary or implements
the check in TypeScript. The two-judge model call (for idioms not caught by
the programmatic check) becomes a nested model call from the handler.

### meow-checks (method)

| Component | Claude Code | Pi |
|---|---|---|
| Skill | `skills/verify/SKILL.md` | Same `SKILL.md` |
| Native binary | `bin/meow-checks` | Shelled out to, or ported |
| Budget | 450 chars | Not enforced by Pi |

The verify skill is portable. The binary runs the five verbs (format, lint,
check, test, build) from the profile declaration.

### meow-flow (method)

| Component | Claude Code | Pi |
|---|---|---|
| Skills | 12 skills (method, route, init, onboard, run, steps/*) | Same `SKILL.md` files |
| Agent | `agents/router.md` | Tool: nested model call with Read, Grep, Glob |
| Hook | `SessionStart`: `paw status --waiting` | Extension: `session_start` handler |
| Templates | `templates/` (7 record kinds) | Carried in the package; loaded by `paw template <kind>` |
| Native binary | `bin/paw` | Shelled out to, or ported |
| Budget | 820 chars | Not enforced by Pi |

meow-flow is the largest plugin. Its skills are portable. The router agent
becomes a tool. The session-start hook becomes an event handler. The templates
ship in the package and are read by `paw`.

### meow-scm (method)

| Component | Claude Code | Pi |
|---|---|---|
| Skill | `skills/commit/SKILL.md` | Same `SKILL.md` |
| Native binary | `bin/meow-scm` | Shelled out to, or ported |
| Budget | 380 chars | Not enforced by Pi |

Fully portable skill. The binary checks commit messages against the convention.

### meow-git (method)

| Component | Claude Code | Pi |
|---|---|---|
| Hook | `PreToolUse` matcher `Bash` for `git commit` and `git push` | Extension: `user_bash` handler |
| Native binary | `bin/meow-git` (commit-guard, push-guard) | Shelled out to, or ported |
| Budget | 0 chars permanent | — |

The git guards intercept commit and push commands. In Pi, `user_bash` handlers
shell out to the binary or port the logic.

### meow-github (method)

| Component | Claude Code | Pi |
|---|---|---|
| Hook | `PreToolUse` matcher `Bash` for governance guard | Extension: `user_bash` handler |
| Native binary | `bin/meow-github` | Shelled out to, or ported |
| Budget | 0 chars permanent | — |

Same pattern as meow-git: governance guard becomes a `user_bash` handler.

### meow-loop (method)

| Component | Claude Code | Pi |
|---|---|---|
| Hook | `PreToolUse` matcher `Bash|Edit|Write` for guard | Extension: `tool_call` handler |
| Skill | `skills/loop/SKILL.md` | Same `SKILL.md` |
| Native binary | `bin/meow-loop` | Shelled out to, or ported |
| Budget | 0 chars permanent | — |

The loop guard intercepts write operations to keep a run inside its step. In
Pi, a `tool_call` handler for `Bash`, `Edit` and `Write` tools replaces the
`PreToolUse` hook.

### meow-unattended (method)

| Component | Claude Code | Pi |
|---|---|---|
| Native binary | `bin/meow-unattended` | Shelled out to, or ported |
| Budget | 0 chars permanent | — |

No skills or hooks. The binary plans an unattended run from the profile
declaration.

### meow-code (practice)

| Component | Claude Code | Pi |
|---|---|---|
| Skills | `skills/change/SKILL.md`, `skills/debug/SKILL.md` | Same `SKILL.md` files |
| Budget | 600 chars | Not enforced by Pi |

Fully portable skills.

### meow-author (practice)

| Component | Claude Code | Pi |
|---|---|---|
| Skill | `skills/write/SKILL.md` | Same `SKILL.md` |
| Native binary | `bin/meow-author` | Shelled out to, or ported |
| Budget | 400 chars | Not enforced by Pi |

Fully portable skill. The binary checks authoring compliance.

### meow-licence (practice)

| Component | Claude Code | Pi |
|---|---|---|
| Skill | `skills/header/SKILL.md` | Same `SKILL.md` |
| Native binary | `bin/meow-licence` | Shelled out to, or ported |
| Budget | 380 chars | Not enforced by Pi |

Fully portable skill.

### meow-mise (pack)

| Component | Claude Code | Pi |
|---|---|---|
| Skill | `skills/tasks/SKILL.md` | Same `SKILL.md` |
| Native binary | `bin/meow-mise` | Shelled out to, or ported |
| Budget | 380 chars | Not enforced by Pi |

Fully portable skill.

### meow-gotask (pack)

| Component | Claude Code | Pi |
|---|---|---|
| Skill | `skills/tasks/SKILL.md` | Same `SKILL.md` |
| Native binary | `bin/meow-gotask` | Shelled out to, or ported |
| Budget | 380 chars | Not enforced by Pi |

Fully portable skill.

### meow-markdown (pack)

| Component | Claude Code | Pi |
|---|---|---|
| Skills | `skills/markdown/SKILL.md`, review skill | Same `SKILL.md` files |
| Native binary | `bin/meow-markdown` | Shelled out to, or ported |
| Budget | 380 chars | Not enforced by Pi |

Fully portable skills.

## Layer grouping

The sixteen plugins fall into four layers. A Pi package per layer keeps the
dependency direction and lets a repository install only what it needs.

| Layer | Plugins | Pi package |
|---|---|---|
| Kernel | meow-core, meow-prose, meow-prose-gate | `@meowshed/meow-core` |
| Method | meow-checks, meow-flow, meow-scm, meow-git, meow-github, meow-loop, meow-unattended | `@meowshed/meow-flow` |
| Practice | meow-code, meow-author, meow-licence | `@meowshed/meow-code` |
| Packs | meow-mise, meow-gotask, meow-markdown | `@meowshed/meow-markdown`, `@meowshed/meow-mise`, `@meowshed/meow-gotask` |

Packs stay as separate packages because a repository installs only the packs
its toolchain needs. The kernel, method and practice layers could be one
package, but separating them lets a repository take the kernel's reply shape
without the method's seven-step chain.

## Conclusions

1. Skills are the most portable component: every `SKILL.md` works in Pi
   unchanged. Twelve of sixteen plugins carry at least one skill.

2. Hooks require the most adaptation: five plugins use `hooks.json` with
   command hooks, and each maps to a TypeScript event handler. The handler
   either shells out to the existing native binary or ports the logic.

3. The router agent is the only Claude Code agent definition. It becomes a
   tool registered by the meow-flow extension that makes a nested model call.

4. Output styles have no Pi mechanism. The kernel extension injects the reply
   shape into the system prompt via `before_agent_start`.

5. Native binaries remain the right implementation for record checking, commit
   guarding and prose gating. The decision to shell out or port is per-binary
   and is recorded separately.

6. A Pi package per layer preserves the dependency direction and the
   install-only-what-you-need property.

7. Evals have no Pi equivalent. The existing eval infrastructure would need
   a custom runner registered as a Pi command.

## Sources

The plugin directories under `plugins/`, read 2026-10-04. Each `plugin.json`,
`hooks.json`, `budget.toml`, `requires.toml`, skill, agent and output-style
file was examined directly.
