---
id: SPC-1300
artifact: spec
status: live
revised: 2026-10-04
states:
  [
    REQ-4100,
    REQ-4104,
    REQ-4106,
    REQ-4108,
    REQ-4110,
    REQ-4112,
    REQ-4114,
    REQ-4120,
    REQ-4122,
    REQ-4124,
    REQ-4126,
    REQ-4128,
    REQ-4130,
    REQ-4132,
    REQ-4134,
    REQ-4136,
    REQ-4138,
    REQ-4144,
    REQ-4146,
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

ADR-2780 decides this part, and ADR-2790 decides what a package does at
install time and how it finds its own files, added after four defects
(BUG-1400 to BUG-1403) showed the packages working only beside a checkout of
this repository.

## Boundary

| Surface                                                                   | What it is                                                |
| ------------------------------------------------------------------------- | --------------------------------------------------------- |
| `packages/meow-core/`                                                     | The kernel Pi package                                     |
| `packages/meow-flow/`                                                     | The method Pi package                                     |
| `packages/meow-code/`                                                     | The practice Pi package                                   |
| `packages/meow-mise/`, `packages/meow-gotask/`, `packages/meow-markdown/` | The pack Pi packages                                      |
| `packages/meow-core/extensions/kernel.ts`                                 | The kernel extension                                      |
| `packages/meow-flow/extensions/method.ts`                                 | The method extension                                      |
| `packages/meow-code/extensions/practice.ts`                               | The practice extension                                    |
| `packages/<name>/prompts/`                                                | The prompt files each extension loads, bundled (REQ-4130) |
| `packages/<name>/install-meow.mjs`                                        | The installer that downloads the meow binary (REQ-4136)   |
| `plugins/<name>/`                                                         | The existing Claude Code plugins, unchanged               |
| `project/research/RES-0340-pi-as-a-platform.md`                           | The platform research                                     |
| `project/research/RES-0341-mapping-each-plugin-to-pi.md`                  | The per-plugin mapping                                    |

## Behaviour

### The dual-platform contract

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

### The package structure

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

### The mapping

### Skills

Each `plugins/<name>/skills/<skill>/SKILL.md` is carried in the Pi package
as `skills/<skill>/SKILL.md`, adapted in one phrasing alone: a binary is
named by its plain command and a supporting file by its path relative to
the skill's own directory, never through `${CLAUDE_SKILL_DIR}` or
`${CLAUDE_PLUGIN_ROOT}`, which Pi never sets (REQ-4132). The
package's extension puts its `bin/` directory on the session's PATH at
load, so the plain command resolves the wrapper, which resolves the
platform meow binary. Claude Code puts a plugin's `bin/` on PATH natively,
so the same phrasing serves both platforms once the plugins adopt it.

A skill's name is unique across the units, and it names the tool or the
capability it teaches, never a kind of record the method already claims:
Pi loads every unit's skills into one flat namespace, where two units
claiming one name silently keep the first and drop the rest, and a name
the record tree already uses misnames the skill against it (BUG-1412).

Pi discovers each skill by the same progressive-disclosure mechanism: the
description appears in the system prompt, and the full instructions load on
invocation.

Where a skill uses Claude Code–specific frontmatter (`model`, `effort`,
`arguments`, `argument-hint`, `user-invocable`), the Pi extension provides the
equivalent at runtime:

| Claude Code field            | Pi equivalent                                  |
| ---------------------------- | ---------------------------------------------- |
| `model`, `effort`            | Session control before invocation              |
| `arguments`, `argument-hint` | A `pi.registerCommand()` that parses arguments |
| `user-invocable: false`      | The command is not registered                  |

### Hooks

Each `hooks.json` entry maps to an event handler registered with `pi.on()`
(REQ-4104):

| Claude Code event     | Pi event        | Handler returns                          |
| --------------------- | --------------- | ---------------------------------------- |
| `SessionStart`        | `session_start` | nothing (side effect only)               |
| `PreToolUse` on Bash  | `user_bash`     | `{ block: true, reason }` or `undefined` |
| `PreToolUse` on tools | `tool_call`     | `{ block: true, reason }` or `undefined` |
| `PostToolUse`         | `tool_result`   | modified result or `undefined`           |

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

The gate binary holds the judge itself, as it does for the Claude Code
hook: it spawns the judge twice with a bounded deadline, keeps only what
both judgements agree on, and exits 2 with the agreed findings (REQ-4106).
The extension never re-implements the judge; it pipes the hook JSON to the
binary and relays the verdict, so an extension cannot weaken what the
program holds.

### Commands

The method extension registers a command for each step and driver
(REQ-4122):

| Command                   | Loads skill                    |
| ------------------------- | ------------------------------ |
| `/meow-flow:research`     | `skills/research/SKILL.md`     |
| `/meow-flow:requirements` | `skills/requirements/SKILL.md` |
| `/meow-flow:design`       | `skills/design/SKILL.md`       |
| `/meow-flow:spec`         | `skills/spec/SKILL.md`         |
| `/meow-flow:epic`         | `skills/epic/SKILL.md`         |
| `/meow-flow:implement`    | `skills/implement/SKILL.md`    |
| `/meow-flow:review`       | `skills/review/SKILL.md`       |
| `/meow-flow:run`          | `skills/method/SKILL.md`       |
| `/meow-flow:init`         | `skills/init/SKILL.md`         |
| `/meow-flow:onboard`      | `skills/onboard/SKILL.md`      |

### Binaries and templates

The shell wrappers ship in the package's `bin/` directory as committed
source; the platform meow binary is not committed. Each package's
`install-meow.mjs` runs after install, downloads the meow-full release
archive — the one meow binary built once with every unit's feature, because
a unit's own release carries only its unit's feature and a package bundles
several — extracts the binary for the machine it runs on into
`bin/<cpu>-<system>/meow`, removes the archive and exits 0 on any failure
(REQ-4136). A failed download breaks no install, because the
wrappers report each check as unrun, which is the designed behaviour for a
missing binary. The repository ignores `packages/*/bin/*-*/`, so no
download is ever committed (REQ-4138).

Every prompt, fragment and supporting file an extension or skill loads is
bundled inside the package that loads it, and no resolved path walks above
the package root (REQ-4130). Where a file is missing, the extension
reports it and carries on with the behaviour it can hold.

The record templates ship in the package alongside `paw` (REQ-4128). The
command `paw template <kind>` reads them from the same relative path it uses
in the Claude Code plugin.

### The reply shape

The `@meowshed/meow-core` extension alone injects the reply shape into the
system prompt guidelines on `before_agent_start` (REQ-4108, REQ-4134). No
other package's extension injects it. A package that makes a nested model
call — the method's router, the prose gate's judge — carries its own
bundled copy of the reply shape into that call's messages, because a nested
call runs its own prompt and never sees the session's.

### Budgets

Each package carries a `budget.toml` that states the permanent character cost
its skills and commands add to the system prompt (REQ-4120). The values are
the same as the Claude Code plugins state. Pi does not enforce the budget; the
file documents the cost for the package author and the installer.

### Evals

Eval suites remain in the `plugins/` directory and are not carried in the Pi
packages (REQ-4124). A future extension may register a `paw eval` command
that runs them.

### The install sources

A package installs from npm, which is the distribution install:
`pi install npm:@meowshed/<unit>`. The core tarball carries the
all-features meow binary for every platform the build workflow builds,
placed in the package's `bin/` before packing, so an npm install copies
the whole package and makes no request at install or load time. The other
five tarballs carry no binary: their launchers fall back to `meow` on
PATH, which the core extension resolves, so the core package is the
install every other layer sits beside (REQ-4144). A tag named
`<unit>-pi-v<version>` publishes that one package; the workflow run by
hand publishes every one whose version npm does not hold yet. The
`postinstall` runs for a git-source install of the core package, where
the clone obeys `.gitignore` and the platform directories are absent, and
is absent from the other packages, which download nothing.

A local path is the development install: it loads the package in place
from a checkout, runs no lifecycle script, and tracks that checkout. The
person installing the core package that way runs `node install-meow.mjs`
by hand, because the checkout ignores the platform directories it fills.
The GitHub release archives stay as the record of what shipped and as the
download source the core installer names (RES-0342).

### The packages

Each Pi package mirrors one unit (REQ-4146): `@meowshed/<unit>` carries
that unit's skills, launcher, extension and budget, and its manifest
states the version the unit's `.claude-plugin/plugin.json` states. A tag
named `<unit>-v<version>` releases the unit to both registries, and each
side skips what it already holds. The guards live in the units that own
them: the prose gate's handlers in `meow-prose-gate`, the git guards in
`meow-git`, the governance guard in `meow-github`, the loop guard in
`meow-loop`. The reply-shape injection stays in `meow-core`, and the
router and the step commands in `meow-flow`.

The meow binary still ships with `meow-core` alone (REQ-4144), and every
other package's launcher falls back to `meow` on PATH. The prose gate's
fragments sit in its package at `fragments/`, where the binary resolves
them from its own unit root.

## Failure paths

Where the meow binary is missing, the shell wrappers report each check as
unrun and let the command through, because blocking every command for a
missing binary would punish the person for something the package cannot
check (ADR-1600). Where a download fails, the installer exits 0 and the
wrappers answer the same way.

Where a bundled prompt file is missing, the extension reports it through a
session notification and carries on with the behaviour it can hold, and
never reads a neighbouring package's or a checkout's files (REQ-4130).

Where the governance guard asks and no person can answer — print mode, JSON
mode, a session with no UI — the command is denied, because a governance
change nobody approved is the outcome the guard exists to prevent.

Where the router tool is invoked with no model available, it answers that
the router is unavailable rather than raising, because a tool that fails
loudly on a machine with no credentials blocks the method it serves.

The build runs in the Rust Tool workflow alone, started by a change to
`crates/**`, by hand or by a `meow-full-v<version>` tag; the release
workflows fetch its artifacts and never build (ADR-2810). A plugin
release without a successful Rust Tool run on the trunk fails and names
that workflow.

What this specification does not cover: porting a native binary to
TypeScript or WASM; the eval runner design; npm publication versus a git
source; per-user configuration on Pi; Pi's dynamic tool registration,
virtual models or structured output; language packs beyond the ten the
marketplace ships.
