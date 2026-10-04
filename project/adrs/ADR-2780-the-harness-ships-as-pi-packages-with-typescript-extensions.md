---
id: ADR-2780
artifact: adr
status: done
revised: 2026-10-04
addresses: [REQ-4100, REQ-4102, REQ-4104, REQ-4106, REQ-4108, REQ-4110, REQ-4112, REQ-4114, REQ-4116, REQ-4118, REQ-4120, REQ-4122, REQ-4124, REQ-4126, REQ-4128]
supersedes: []
---

# 2780. The harness ships as Pi packages with TypeScript extensions

## Decision

Each meowpaw layer ships as a Pi package containing TypeScript extensions,
skills and supporting files. The mapping from Claude Code plugins to Pi
packages is:

1. **Skills are carried unchanged.** Every `SKILL.md` a Claude Code plugin
   provides goes into the Pi package's `skills/` directory. Pi loads it by
   the same progressive-disclosure mechanism.

2. **Hooks become TypeScript event handlers.** Each `hooks.json` entry maps
   to a handler registered with `pi.on()`: `SessionStart` to
   `session_start`, `PreToolUse` with a Bash matcher to `user_bash`,
   `PreToolUse` with a tool matcher to `tool_call`, `PostToolUse` to
   `tool_result`.

3. **Handlers shell out to the existing native binaries.** The handler
   invokes `paw`, `meow-git`, `meow-prose-gate`, `meow-loop` or
   `meow-github` with `child_process`, interprets the exit code the same way
   the Claude Code hook mechanism does, and returns the corresponding block,
   feedback or pass-through.

4. **The output style is injected by `before_agent_start`.** The kernel
   extension reads `meow.md` and adds it to
   `event.systemPromptOptions.guidelines` on every model call, replacing
   Claude Code's `force-for-plugin: true`.

5. **Agent definitions become registered tools.** The router and the skeptic
   are tools whose `execute` functions make nested model calls via
   `ctx.modelRegistry.streamSimple()`, constraining the model, effort and
   tool set as the agent frontmatter declares.

6. **The kernel extension carries the reply shape to every nested call.**
   Where a tool makes a nested model call, the extension includes the reply
   shape in the messages, enforcing rule R10 by construction.

7. **The prose gate's two-judge call is a nested model call.** The
   `user_bash` handler runs the judge twice with
   `ctx.modelRegistry.streamSimple()` and blocks only where both agree.

8. **Each layer is one Pi package.** The kernel is `@meowshed/meow-core`,
   the method is `@meowshed/meow-flow`, the practice is
   `@meowshed/meow-code`, and each pack is its own package. Host packages
   are `peerDependencies` with `"*"` ranges.

9. **Native binaries ship alongside the package.** The compiled Rust binaries
   are platform-specific executables in the package or a shared dependency
   package. The extension resolves each binary's path relative to the package
   root.

10. **The method extension registers a command per step.** Each of the seven
    steps, plus `run`, `init` and `onboard`, is a `pi.registerCommand()`
    that loads the corresponding skill.

11. **Hook ordering is by extension load order.** Where multiple extensions
    intercept the same event (the prose gate and the git guard both intercept
    `git commit`), the extension that must run first loads first.

12. **Templates ship in the package.** `paw template <kind>` resolves them
    from the package root, unchanged.

13. **Evals are deferred.** Pi has no eval mechanism; the suites remain in
    the repository for a future runner.

14. **budget.toml is carried for documentation.** Pi does not enforce it,
    but the cost is real and recording it prevents unnoticed growth.

The packages are distributed through npm or a git repository, installed with
`pi install npm:@meowshed/meow-flow` or
`pi install git:github.com/meowshed/meowpaw-pi`.

## Why

RES-0340 found that every Claude Code plugin component has a Pi analogue, but
the analogue works differently. Skills are the most portable (same format,
same loading). Hooks require the most adaptation (TypeScript instead of
commands). Native binaries are the right implementation for record checking,
commit guarding and prose gating; porting them to TypeScript would duplicate
tested logic.

RES-0341 mapped all sixteen plugins component by component and found that the
mapping is consistent: no plugin requires a capability Pi lacks, and no
plugin's behaviour is lost in the translation. The gaps (evals, userConfig,
marketplace) have acceptable workarounds.

Pi's in-process extensions enable capabilities Claude Code plugins cannot
match — dynamic tool registration, event composition, virtual models,
structured output, nested execution — but this decision does not exploit them
yet. It establishes the structure so that future work can.

The strongest objection is that shelling out to native binaries from
TypeScript event handlers is less idiomatic than porting the logic. The
objection loses because the binaries carry Rust performance, deterministic
behaviour and test coverage that a TypeScript port would need to reproduce.
Shelling out is the minimum viable mapping; porting is a later optimisation.

## Alternatives

| Option | Better at | Why it lost |
|---|---|---|
| Pi packages with extensions shelling out to native binaries | Preserves tested binaries, fastest to ship | Chosen |
| Pi packages with extensions porting all binary logic to TypeScript | In-process, structured output, no child process overhead | Duplicates tested Rust, second implementation to maintain, prose gate and git guard are performance-sensitive |
| Pi packages with skills only, no extensions | Simplest, no TypeScript at all | Cannot implement hooks, output-style injection, commands or nested model calls; loses the guards and the method driver |
| One monolithic Pi package instead of one per layer | One install command | Cannot install kernel without method, loses the install-only-what-you-need property, bundle size grows with every pack |
| Pi packages plus a Claude Code compatibility shim | Runs on both platforms from one source | The shim would need to translate every event handler back to a command hook, which is the inverse problem with the same cost |

## What it costs

Each extension is a TypeScript module that the package must build and test.
The extension code is thin — it registers handlers that shell out — but it is
a new artifact that did not exist in the Claude Code plugins. The package
structure (`package.json`, `extensions/`, `skills/`, `bin/`) is additional
plumbing.

Hook ordering between extensions is by load order, which is less robust than
Claude Code's independent hook merging. The meowpaw extensions must document
their ordering constraint and the installer must respect it.

Evals are unavailable until a custom runner is built. The Claude Code eval
suites remain in the repository but cannot run under Pi.

The `budget.toml` is documentation only; Pi does not enforce it, so the cost
of skill descriptions could grow unnoticed without the check.

## What would reverse it

- Pi adds a hook mechanism that runs external commands with exit-code
  semantics, making the TypeScript event handlers unnecessary.
- Pi adds an output-style mechanism equivalent to Claude Code's, making the
  `before_agent_start` injection unnecessary.
- The native binaries are ported to a Pi-compatible language (WASM, a Pi
  codemode script) and the child-process overhead becomes a measurable cost.
- Pi packages prove too fragile to distribute (version conflicts, dependency
  hell) and a different distribution mechanism is needed.

## Consequences

- The harness runs on both Claude Code (via the existing plugins) and Pi (via
  the new packages) from the same repository.
- Skills are shared: the same `SKILL.md` files serve both platforms.
- Extensions are Pi-only: the event handlers, commands and tool registrations
  have no Claude Code equivalent and live in the Pi package.
- The native binaries are shared: the same compiled Rust executables serve
  both platforms.
- The kernel, method and practice layers install independently on Pi, as they
  do on Claude Code.
- Hook ordering between meowpaw extensions is explicit and documented, where
  Claude Code left it unsupportable.
- Future work can exploit Pi's dynamic tool registration, virtual models and
  structured output without changing the package structure.

## How I will know it was realised

1. `pi install npm:@meowshed/meow-core` loads the kernel package, and a Pi
   session shows the reply shape in the system prompt.
2. `pi install npm:@meowshed/meow-flow` loads the method package, and
   `/meow-flow:run` drives the seven-step chain.
3. A `git commit` with a prose defect is blocked by the prose gate extension.
4. A `git commit` on the declared trunk is blocked by the git guard
   extension.
5. A `git push` with an unsigned commit is blocked by the push guard
   extension.
6. The router tool returns a route for a request, and the model follows it.
7. The skeptic tool refutes a verified claim and produces a defect.
8. Skills load by description on both platforms and produce the same
   behaviour.
9. `paw check` runs from the Pi package and reports the same findings as from
   the Claude Code plugin.

## What this does not settle

- Whether to port any native binary to TypeScript or WASM.
- The eval runner design and whether it registers as a Pi command.
- Whether packs beyond mise, gotask and markdown ship as Pi packages.
- Whether the Pi packages are published to npm or distributed only as a git
  repository.
- How per-user configuration (`userConfig` with keychain) is handled on Pi.
- Whether Pi's dynamic tool registration, virtual models or structured output
  are exploited in a later increment.
