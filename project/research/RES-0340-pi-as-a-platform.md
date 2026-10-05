---
id: RES-0340
artifact: research
status: approved
revised: 2026-10-04
---

# Pi as a platform

## Summary

Pi is a coding agent with its own extension, skill, package and event system
that differs structurally from Claude Code's plugin system. Where Claude Code
plugins are directory trees with a manifest, skills, hooks and native binaries,
Pi extensions are TypeScript modules loaded into the Pi process that register
tools, commands, event handlers and model providers through an `ExtensionAPI`.
Pi skills are Markdown files with frontmatter, discovered and loaded by
description, identical in shape to Claude Code skills but loaded from Pi's own
directory structure and packages. The mapping is not one-to-one: each Claude
Code plugin component has a Pi analogue, but the analogue works differently and
some components have no direct equivalent.

Sources: the Pi extension reference, skill reference, package reference and
extension examples, read 2026-10-04 from the installed release at
`/Users/retran/.pi/agent/install/releases/1.0.2/node_modules/@earendil-works/pi-coding-agent/`.

## Method

The Pi documentation was read in full on 2026-10-04: extensions.md,
skills.md, packages.md, and the example extensions directory. The installed
release is `1.0.2`. Each page is living documentation, so each finding
carries the date and the release it was observed on.

Nothing was measured. Claims about capability come from the documentation and
the example code.

## What Pi provides

### Extensions

A Pi extension is a TypeScript module exporting a default factory that receives
`ExtensionAPI`. The factory registers capabilities for the session. Extensions
run inside the Pi process with the same operating-system permissions.

Capabilities registered through `ExtensionAPI`:

| Capability                    | API                                          | Claude Code analogue                          |
| ----------------------------- | -------------------------------------------- | --------------------------------------------- |
| Observe or modify lifecycle   | `pi.on()`                                    | `hooks/hooks.json`                            |
| Add a model-callable tool     | `pi.registerTool()`                          | `skills/<name>/SKILL.md` with `allowed-tools` |
| Add a `/` command             | `pi.registerCommand()`                       | `commands/<name>.md` / skills                 |
| Add a shortcut or CLI flag    | `pi.registerShortcut()`, `pi.registerFlag()` | no equivalent                                 |
| Send messages                 | `pi.sendUserMessage()`, `pi.sendMessage()`   | no equivalent                                 |
| Persist session data          | `pi.appendEntry()`                           | `${CLAUDE_PLUGIN_DATA}`                       |
| Change tools, model, thinking | session control methods                      | no equivalent                                 |
| Add a model provider          | `pi.registerProvider()`                      | no equivalent                                 |
| Add an MCP server             | `pi.registerMcpServer()`                     | `.mcp.json`                                   |
| Add a virtual model           | `pi.registerVirtualModel()`                  | no equivalent                                 |
| Terminal rendering            | renderer registration, `ctx.ui`              | `output-styles/`                              |
| Extension communication       | `pi.events`                                  | no equivalent                                 |

Events cover resource discovery, sessions, agent and message lifecycle,
providers, tools and raw input. The events most relevant to meowpaw:

| Pi event             | Triggers               | Claude Code analogue        |
| -------------------- | ---------------------- | --------------------------- |
| `session_start`      | Session begins         | `SessionStart` hook         |
| `before_agent_start` | Before a model call    | `Setup` hook                |
| `tool_call`          | Before a tool executes | `PreToolUse` hook           |
| `tool_result`        | After a tool completes | `PostToolUse` hook          |
| `user_bash`          | Before a Bash command  | `PreToolUse` matcher `Bash` |
| `turn_end`           | After a turn           | no equivalent               |

A `tool_call` handler can mutate input or block execution, which is what
meowpaw's `PreToolUse` hooks do. A `tool_result` handler can replace a result,
which is what the prose gate's PostToolUse feedback relies on.

A `user_bash` handler returning `undefined` passes the command to the next
handler and then to local execution. Returning `operations` or `result` stops
propagation. This is the mechanism for the git commit guard, the git push
guard and the governance guard.

### Skills

Pi skills follow the Agent Skills specification (`agentskills.io`). A skill is
a directory containing `SKILL.md` with YAML frontmatter (`name`,
`description`, optional fields) followed by instructions. Pi scans skill
locations at startup, adds each skill's name and description to the system
prompt, and loads full instructions only when invoked.

This is the same progressive-disclosure pattern Claude Code uses. The
frontmatter fields overlap:

| Field                        | Pi                 | Claude Code    |
| ---------------------------- | ------------------ | -------------- |
| `name`                       | required           | directory name |
| `description`                | required, max 1024 | required       |
| `allowed-tools`              | experimental       | supported      |
| `disable-model-invocation`   | supported          | supported      |
| `model`, `effort`            | not in spec        | supported      |
| `argument-hint`, `arguments` | not in spec        | supported      |
| `user-invocable`             | not in spec        | supported      |

Claude Code skills can declare `model`, `effort`, `argument-hint`, `arguments`
and `user-invocable`. Pi skills cannot. Pi skills are instruction-only; the
extension provides the executable behaviour that commands and tool overrides
require.

### Packages

Pi packages distribute extensions, skills, prompt templates and themes as one
unit. A package is an npm package or git repository with a `package.json` and
conventional directories (`extensions/`, `skills/`, `prompts/`, `themes/`).

```text
my-pi-package/
├── package.json
├── extensions/
├── skills/
├── prompts/
└── themes/
```

Installed with `pi install npm:@example/pi-tools@1.0.0` or
`pi install git:github.com/example/pi-tools@v1`. Personal installs go to
`~/.pi/agent/settings.json`; project installs to `.pi/settings.json` (loaded
after project trust).

This replaces Claude Code's marketplace mechanism:
`claude plugin marketplace add <url>` / `claude plugin install <name>@<marketplace>`.

Pi supplies host packages to extensions as `peerDependencies`:
`@earendil-works/pi-ai`, `@earendil-works/pi-agent-core`,
`@earendil-works/pi-coding-agent`, `@earendil-works/pi-tui`, `typebox`.

### Agents and subagents

Pi has no direct equivalent of Claude Code's `agents/<name>.md` subagent
definitions. Instead, an extension can:

1. Use `ctx.modelRegistry.streamSimple()` for provider-neutral nested model
   calls from within a tool.
2. Register a tool that calls another tool via `ctx.executeTool()`.
3. Use `pi.sendMessage()` to inject a user message that triggers the model.

The router agent (`meow-flow:router`) and the skeptic agent have no direct
structural analogue in Pi. They would become tools registered by an extension
that make nested model calls with constrained prompts and tool sets.

## What a Claude Code plugin maps to in Pi

### The manifest

Claude Code's `plugin.json` carries `name`, `version`, `description`,
`author`, `license`, `keywords`, `dependencies` and `userConfig`. Pi packages
carry the same metadata in `package.json`, plus the `pi` key for resource
paths. `dependencies` maps to npm `dependencies` (or `peerDependencies` for
host packages). `userConfig` has no Pi equivalent; per-user configuration
would need its own mechanism inside the extension.

### Skills

Claude Code skills map directly to Pi skills with the same `SKILL.md` format.
The content is portable. The differences are in frontmatter fields that Pi
does not support (`model`, `effort`, `arguments`, `argument-hint`,
`user-invocable`). A skill that uses these fields needs adaptation:

- `model` and `effort`: the extension sets these via session control methods
  before invoking the skill.
- `arguments` and `argument-hint`: the extension registers a command that
  parses arguments and constructs the prompt.
- `user-invocable`: the extension registers or withholds the command.

### Hooks

Claude Code hooks map to Pi event handlers registered with `pi.on()`. The
mapping:

| Claude Code hook             | Pi event                              |
| ---------------------------- | ------------------------------------- |
| `SessionStart`               | `session_start`                       |
| `Setup`                      | `before_agent_start`                  |
| `PreToolUse` (matcher, `if`) | `tool_call` or `user_bash`            |
| `PostToolUse`                | `tool_result`                         |
| `UserPromptSubmit`           | `before_agent_start` (prompt section) |
| `PermissionRequest`          | no direct equivalent                  |

Claude Code hooks run external commands (`type: "command"`) with exit codes.
Pi event handlers are async TypeScript functions that return structured results.
This is the largest structural difference: every native binary that a Claude
Code hook invokes must be replaced by TypeScript logic in the extension, or the
extension must shell out to the binary itself and interpret its exit code.

The native binaries in `bin/` (`paw`, `meow-git`, `meow-prose-gate`,
`meow-loop`, `meow-github`, `meow-scm`, `meow-checks`, `meow-licence`) remain
usable from Pi — an extension can shell out to them with `Bash` or
`child_process`. The question is whether to shell out or to port their logic
into TypeScript.

### Output styles

Claude Code output styles are Markdown files in `output-styles/` that replace
the default system prompt section for reply shape. Pi has no output-style
mechanism. The equivalent is an extension that modifies the system prompt via
`before_agent_start`:

```typescript
pi.on("before_agent_start", async (event, ctx) => {
  event.systemPromptOptions.guidelines.push(outputStyleContent);
});
```

Or a prompt template in the package's `prompts/` directory.

### Agents

Claude Code agents (`agents/<name>.md`) define subagents with frontmatter
(`model`, `effort`, `maxTurns`, `tools`, `skills`, `background`,
`isolation`). Pi has no agent-definition files. The equivalent is a tool
registered by the extension that makes a nested model call:

```typescript
pi.registerTool("router", {
  description: "Route a request before work starts",
  parameters: /* TypeBox schema */,
  execute: async (args, ctx) => {
    const result = await ctx.modelRegistry.streamSimple({
      model: "sonnet",
      messages: [{ role: "user", content: routerPrompt(args) }],
      tools: ["Read", "Grep", "Glob"],
    });
    return { content: result.text, details: undefined };
  },
});
```

### Budgets

Claude Code `budget.toml` states the permanent character cost a plugin adds to
every turn. Pi has no budget mechanism. An extension that registers skills or
commands adds their descriptions to the system prompt, and the cost is implicit
in the string length. A Pi package could carry a `budget.toml` for its own
accounting, but Pi would not enforce it.

### Evals

Claude Code evals (`evals/` directories with prompts, graders and results) use
`claude plugin eval`. Pi has no eval mechanism. An extension could register a
command that runs evals, but the infrastructure (prompt-runner, grader
protocol, result aggregation) would need to be built.

## What Pi provides that Claude Code does not

1. **In-process extensions.** An extension shares the Pi process and can
   inspect prompts, tool calls, files, credentials and session history. Claude
   Code plugins share no runtime; every contract is a file format or a command.
   An in-process extension can implement cross-cutting concerns (routing,
   gate logic, state derivation) without shelling out.

2. **Dynamic tool registration.** An extension can register and unregister
   tools at runtime (`pi.setActiveTools()`), choose exposure (`direct`,
   `model-only`, `codemode`, `deferred`, `hidden`), and adjust tool
   descriptions per loadout. Claude Code's tool set is static per session.

3. **Event composition.** Multiple extensions' event handlers compose in
   load order. A `tool_result` handler sees prior changes. Claude Code hooks
   from different plugins merge but do not compose; each runs independently.

4. **Virtual models.** `pi.registerVirtualModel()` routes requests to
   different models based on content. Claude Code has no routing mechanism;
   meowpaw implements routing as a dispatched agent.

5. **Structured tool output.** Tools declare `outputSchema` and return
   `structuredContent` that scripts and other tools can consume
   programmatically. Claude Code tool results are text.

6. **Nested tool execution.** A tool can call `ctx.executeTool()` to run
   other tools with full validation and event handling. The session keeps a
   bounded record of nested calls.

7. **Terminal UI.** Extensions can register renderers, custom components,
   overlays and status widgets. Claude Code has output styles only.

8. **Session state.** `pi.appendEntry()` persists data outside model context
   but inside the session. Claude Code uses `${CLAUDE_PLUGIN_DATA}` on the
   filesystem.

## What Claude Code provides that Pi does not

1. **Hook merging.** Claude Code merges hooks from multiple plugins by event
   type. Pi event handlers compose in extension load order, but an extension
   that returns a blocking result prevents later handlers from running. This
   means Pi extensions must coordinate where Claude Code plugins need not.

2. **Native binary hooks.** Claude Code hooks can run any executable with
   exit-code semantics. Pi event handlers are TypeScript; shelling out is
   possible but not idiomatic.

3. **Agent definitions.** Claude Code's `agents/<name>.md` with frontmatter
   for model, tools, turns and isolation is a declarative subagent. Pi has
   no equivalent; subagents are programmatic (nested model calls from tools).

4. **Marketplace.** Claude Code's marketplace is a JSON index at a URL, with
   `plugin marketplace add` and `plugin install`. Pi uses npm or git packages
   with `pi install`.

5. **Evals.** Claude Code's `claude plugin eval` runs prompt suites with
   graders. Pi has no built-in eval mechanism.

6. **Plugin data directory.** `${CLAUDE_PLUGIN_DATA}` is a per-plugin
   persistent directory managed by the platform. Pi extensions use
   `pi.appendEntry()` or manage their own storage.

7. **`userConfig` with keychain.** Claude Code's `userConfig` with
   `sensitive` values stored in the OS keychain. Pi has no equivalent.

## Conclusions

1. Every Claude Code plugin component has a Pi analogue, but the analogue
   works differently. Skills are the most portable component. Hooks require
   the most adaptation, because they change from external commands to
   in-process TypeScript handlers.

2. The native binaries (`paw`, `meow-git`, etc.) remain the right
   implementation for record checking, commit guarding and prose gating. An
   extension shells out to them or ports their logic. Shelling out preserves
   the existing test coverage; porting gives in-process integration and
   structured output. The decision is recorded separately.

3. Pi's in-process extensions enable capabilities Claude Code plugins cannot
   match: dynamic tool registration, event composition, virtual models,
   structured output, nested tool execution and terminal UI. These
   capabilities can strengthen meowpaw's routing, gating and reporting.

4. Pi lacks capabilities Claude Code provides: hook merging (extensions must
   coordinate), native binary hooks (TypeScript is idiomatic), declarative
   agents (programmatic only), marketplace (npm/git instead), evals, plugin
   data directory and userConfig with keychain. Each gap needs a design
   decision.

5. A Pi package is the distribution unit, replacing the Claude Code
   marketplace. The package carries extensions, skills, prompts and themes.
   The native binaries ship alongside the package, either as bundled
   executables or as a dependency that installs them.

6. The `budget.toml` mechanism has no Pi equivalent. The cost of skill and
   command descriptions in the system prompt is implicit. A Pi package could
   carry a `budget.toml` for documentation, but it would not be enforced by
   the platform.

7. The router and skeptic agents, currently Claude Code agent definitions,
   become tools registered by the meow-flow extension. Their constrained
   prompts and tool sets translate to nested model calls with session control.

## Sources

All read 2026-10-04 from Pi release 1.0.2 installed at
`/Users/retran/.pi/agent/install/releases/1.0.2/node_modules/@earendil-works/pi-coding-agent/`.
Every page is living documentation that changes under the same address, so each
finding is something to re-check.

- `docs/extensions.md` — ExtensionAPI, events, tools, commands, state, UI,
  MCP, rendering, lifecycle, error handling.
- `docs/skills.md` — SKILL.md format, frontmatter, progressive disclosure,
  loading, validation.
- `docs/packages.md` — Package structure, installation, sources,
  dependencies, resource selection.
- `examples/extensions/` — Concrete extension examples covering tools,
  events, commands, flags, shortcuts, state, rendering, providers, OAuth,
  remote execution, terminal components.
