---
id: SPC-1300
artifact: spec
status: live
revised: 2026-10-04
states:
  [
    REQ-4100,
    REQ-4102,
    REQ-4104,
    REQ-4106,
    REQ-4108,
    REQ-4110,
    REQ-4112,
    REQ-4114,
    REQ-4116,
    REQ-4118,
    REQ-4120,
    REQ-4122,
    REQ-4124,
    REQ-4126,
    REQ-4128,
  ]
---

# The Pi packages

## Scope

This covers how the meowpaw harness ships as Pi packages: the package
structure, the extension that each layer provides, how each Claude Code plugin
component maps to its Pi analogue, and the principle that every new plugin is
developed for both platforms. It states the mapping, the package layout, the
event handlers, the commands, the tools, the binary dispatch and the
dual-platform contract.

It leaves the implementation of each extension to its task, the eval runner
design to a later decision (REQ-4124), and per-user configuration to a later
decision. A Pi package that exploits dynamic tool registration, virtual models
or structured output has no specification yet, because no decision asks for
one.

ADR-2780 decides this part.

## Boundary

| Surface | What it is |
|---|---|
| `packages/meow-core/` | The kernel Pi package |
| `packages/meow-flow/` | The method Pi package |
| `packages/meow-code/` | The practice Pi package |
| `packages/meow-mise/`, `packages/meow-gotask/`, `packages/meow-markdown/` | The pack Pi packages |
| `packages/meow-core/extensions/kernel.ts` | The kernel extension |
| `packages/meow-flow/extensions/method.ts` | The method extension |
| `packages/meow-code/extensions/practice.ts` | The practice extension |
| `plugins/<name>/` | The existing Claude Code plugins, unchanged |
| `project/research/RES-0340-pi-as-a-platform.md` | The platform research |
| `project/research/RES-0341-mapping-each-plugin-to-pi.md` | The per-plugin mapping |

## The dual-platform contract

Every new plugin is developed for both Claude Code and Pi. A plugin that
introduces a skill carries the same `SKILL.md` on both platforms. A plugin
that introduces a hook carries both a `hooks.json` entry (for Claude Code) and
a corresponding event handler in the Pi extension (for Pi). A plugin that
introduces a command carries both a skill with `disable-model-invocation: true`
(for Claude Code) and a `pi.registerCommand()` call (for Pi). A plugin that
introduces an agent carries both an `agents/<name>.md` (for Claude Code) and
a registered tool with a nested model call (for Pi).

The existing plugins are the baseline. The Pi packages adapt them; they do not
replace them. The `plugins/` directory remains the source of truth for skills,
agents and output styles. The `packages/` directory adds the Pi-specific
extensions and package plumbing.

## The package structure

Each Pi package has this layout:

```text
packages/<name>/
├── package.json          name, pi key, peerDependencies
├── extensions/
│   └── <layer>.ts        registers event handlers, commands and tools
├── skills/               symlinked or copied from plugins/<name>/skills/
├── bin/                  platform-specific native binaries
├── budget.toml           documented permanent character cost
└── README.md             the package's page
```

`package.json` declares:

```json
{
  "name": "@meowshed/pi-<layer>",
  "keywords": ["pi-package"],
  "pi": {
    "extensions": ["extensions/<layer>.ts"],
    "skills": ["skills"]
  },
  "peerDependencies": {
    "@earendil-works/pi-coding-agent": "*",
    "@earendil-works/pi-ai": "*",
    "@earendil-works/pi-agent-core": "*",
    "@earendil-works/pi-tui": "*",
    "typebox": "*"
  }
}
```

No host package appears in `dependencies`. The `"*"` range accepts whatever
Pi supplies at runtime (REQ-4114).

## The mapping

### Skills

Each `plugins/<name>/skills/<skill>/SKILL.md` is the same file the Pi package
carries in `skills/<skill>/SKILL.md` (REQ-4102). Pi discovers it by the same
progressive-disclosure mechanism: the description appears in the system prompt,
and the full instructions load on invocation.

Where a skill uses Claude Code–specific frontmatter (`model`, `effort`,
`arguments`, `argument-hint`, `user-invocable`), the Pi extension provides the
equivalent at runtime:

| Claude Code field | Pi equivalent |
|---|---|
| `model`, `effort` | Session control before invocation |
| `arguments`, `argument-hint` | A `pi.registerCommand()` that parses arguments |
| `user-invocable: false` | The command is not registered |

### Hooks

Each `hooks.json` entry maps to an event handler registered with `pi.on()`
(REQ-4104):

| Claude Code event | Pi event | Handler returns |
|---|---|---|
| `SessionStart` | `session_start` | nothing (side effect only) |
| `PreToolUse` on Bash | `user_bash` | `{ block: true, reason }` or `undefined` |
| `PreToolUse` on tools | `tool_call` | `{ block: true, reason }` or `undefined` |
| `PostToolUse` | `tool_result` | modified result or `undefined` |

The handler shells out to the same native binary the Claude Code hook runs
(REQ-4106). It invokes the binary with `child_process.execFile`, interprets
the exit code: 0 is pass-through, 2 is feedback to the model, and non-zero
with output is a block.

Where two extensions intercept the same event, the extension that must run
first loads first (REQ-4126). The load order is: kernel, then method, then
practice, then packs. This ensures the prose gate blocks before the git
convention check on `git commit`.

### Output style

The kernel extension reads `plugins/meow-core/output-styles/meow.md` and
injects it into `event.systemPromptOptions.guidelines` on every
`before_agent_start` (REQ-4108). This replaces Claude Code's
`force-for-plugin: true`.

Where a tool makes a nested model call, the extension includes the reply
shape in the nested call's messages (REQ-4112). This enforces rule R10 by
construction: a dispatched agent receives the reply shape even though it runs
its own system prompt.

### Agents

The router agent (`plugins/meow-flow/agents/router.md`) becomes a tool
registered by the method extension (REQ-4110):

```typescript
pi.registerTool("meow-router", {
  description: "Route a request to change the repository before work starts",
  parameters: RouterParametersSchema,
  execute: async (args, ctx) => {
    const result = await ctx.modelRegistry.streamSimple({
      model: "sonnet",
      messages: [
        { role: "system", content: replyShape },
        { role: "user", content: routerPrompt(args.request) },
      ],
      tools: ["Read", "Grep", "Glob"],
    });
    return { content: result.text, details: undefined };
  },
});
```

The skeptic agent follows the same pattern.

### The two-judge prose gate

The prose gate's `user_bash` handler runs the judge twice with
`ctx.modelRegistry.streamSimple()` (REQ-4116). It passes the judge prompt
from `plugins/meow-prose-gate/fragments/judge.md` and the text to judge. It
blocks only where both judgements agree on a span the text holds, preserving
the two-judge semantics.

### Commands

The method extension registers a command for each step and driver
(REQ-4122):

| Command | Loads skill |
|---|---|
| `/meow-flow:research` | `skills/research/SKILL.md` |
| `/meow-flow:requirements` | `skills/requirements/SKILL.md` |
| `/meow-flow:design` | `skills/design/SKILL.md` |
| `/meow-flow:spec` | `skills/spec/SKILL.md` |
| `/meow-flow:epic` | `skills/epic/SKILL.md` |
| `/meow-flow:implement` | `skills/implement/SKILL.md` |
| `/meow-flow:review` | `skills/review/SKILL.md` |
| `/meow-flow:run` | `skills/method/SKILL.md` |
| `/meow-flow:init` | `skills/init/SKILL.md` |
| `/meow-flow:onboard` | `skills/onboard/SKILL.md` |

### Binaries and templates

The native binaries ship in the package's `bin/` directory as
platform-specific executables (REQ-4118). The extension resolves each binary's
path relative to the package root at `session_start`.

The record templates ship in the package alongside `paw` (REQ-4128). The
command `paw template <kind>` reads them from the same relative path it uses
in the Claude Code plugin.

### Budgets

Each package carries a `budget.toml` that states the permanent character cost
its skills and commands add to the system prompt (REQ-4120). The values are
the same as the Claude Code plugins state. Pi does not enforce the budget; the
file documents the cost for the package author and the installer.

### Evals

Eval suites remain in the `plugins/` directory and are not carried in the Pi
packages (REQ-4124). A future extension may register a `paw eval` command
that runs them.

## The layer packages

### `@meowshed/meow-core`

Kernel extension registers:

- `before_agent_start` handler: injects the reply shape into guidelines.
- `session_start` handler: resolves binary paths.
- `user_bash` handler: prose gate check on commit, PR, issue and release
  commands; two-judge nested model call for idioms.

Skills: `writing` (from meow-prose).

Binaries: `meow-prose-gate`.

### `@meowshed/meow-flow`

Method extension registers:

- `session_start` handler: `paw status --waiting`.
- `user_bash` handler: git commit guard, git push guard, governance guard.
- `tool_call` handler: loop guard on Bash, Edit, Write.
- `meow-router` tool: nested model call with Read, Grep, Glob.
- Commands: research, requirements, design, spec, epic, implement, review,
  run, init, onboard.

Skills: method, route, init, onboard, run, verify, commit, loop and the seven
step skills (from meow-flow, meow-checks, meow-scm, meow-loop).

Binaries: `paw`, `meow-git`, `meow-github`, `meow-loop`, `meow-scm`,
`meow-checks`, `meow-unattended`.

### `@meowshed/meow-code`

Practice extension registers:

- `session_start` handler: resolves binary paths.

Skills: change, debug (meow-code), write (meow-author), header (meow-licence).

Binaries: `meow-author`, `meow-licence`.

### Pack packages

Each pack is its own package with a thin extension that resolves its binary
and carries its skill:

- `@meowshed/meow-mise`: skill `tasks`, binary `meow-mise`.
- `@meowshed/meow-gotask`: skill `tasks`, binary `meow-gotask`.
- `@meowshed/meow-markdown`: skill `markdown`, binary `meow-markdown`.

## What this does not cover

- Whether to port any native binary to TypeScript or WASM.
- The eval runner design.
- Whether the Pi packages are published to npm or distributed as a git
  repository.
- How per-user configuration is handled on Pi.
- Exploiting Pi's dynamic tool registration, virtual models or structured
  output.
- Language packs beyond Rust, TypeScript, Python, Go, C#, Lua, Neovim,
  Godot, Starlark and Scheme.
