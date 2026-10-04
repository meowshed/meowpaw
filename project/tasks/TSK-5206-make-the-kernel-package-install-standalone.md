---
id: TSK-5206
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2710
closes: [REQ-4108, REQ-4130, REQ-4134]
issue: 848
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Make the kernel package install standalone

The kernel extension loads the reply shape from a file bundled inside the
package, injects it into the system prompt as the one extension that does,
puts the package's bin wrappers on PATH, and holds the prose gate over every
publish command by relaying the gate binary's verdict. Fixes BUG-1400 and
BUG-1402.

## Acceptance criteria

1. Given `@meowshed/meow-core` installed from a copy with no `plugins/`
   directory anywhere above it, when a Pi session starts, then the reply
   shape is injected into the prompt guidelines and the model can quote its
   rules. Closed by: installing from a copied package directory in `/tmp`
   and asking the model which rules R1, R2 and R10 state.
2. Given the kernel and any other layer installed together, when a session
   starts, then the reply shape appears in the system prompt once. Closed
   by: reading the extensions — only `kernel.ts` pushes into
   `promptGuidelines` — and a session with both packages loaded.
3. Given a publish command with a prose defect, when the model or the
   person runs it, then the gate binary blocks it with its finding relayed.
   Closed by: a session test committing `Lets circle back` through the
   Bash tool.

## What to do

Bundle the reply shape in `packages/meow-core/prompts/`; load it in the
extension's factory, because print mode fires no `session_start` before its
one request; push it into `event.systemPromptOptions.promptGuidelines`,
which the normalised shape always carries. Prepend the package's `bin/` to
`process.env.PATH` at load. Pipe the hook JSON
(`{tool_name, tool_input: {command}}`) to the gate wrapper and relay exit 2
as a block, both for the model's `tool_call` on bash and for a person's
`user_bash`.

## Depends on

Nothing.

## Evidence

`paw check` reports no finding; the repository gate passes. A Pi session
with `packages/meow-core` copied to `/tmp` (no `plugins/` anywhere above
it) quotes rules R1, R2 and R10 of the reply shape, proving the injection;
`grep -rn 'readPluginFile\|\.\./\.\./plugins' packages/` reports no match;
only `kernel.ts` pushes into `promptGuidelines`, so the kernel and any
other layer inject the shape once; the same session's `git commit -m "Lets
circle back on this later"` is blocked with `P1 | "circle back"` relayed
from the gate binary, proving the hook-JSON relay in both directions.

## Left alone

The other five packages' extensions, which TSK-5207 and TSK-5208 hold;
the Claude Code plugins' skills, which keep their `${CLAUDE_SKILL_DIR}`
phrasing until their own next version, because rewording a released unit's
prompt is a release of its own.
