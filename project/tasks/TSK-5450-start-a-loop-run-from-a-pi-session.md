---
id: TSK-5450
artifact: task
status: approved
revised: 2026-10-11
bug: BUG-1610
closes: [REQ-4616]
issue:
---

# Start a loop run from a Pi session

`packages/meow-loop/extensions/loop.ts` registers the `meow-loop:run`
command, feeds every submitted input to the runner's `prompt` subcommand and
asks the runner's `stop` subcommand at the settle boundary, so a run a person
starts in Pi behaves as SPC-1201 states. One task, one branch, one pull
request, one review: the tests first, then the change, its documentation and
its marks.

## Acceptance criteria

1. Given `packages/meow-loop/extensions/loop.ts`, when
   `tools/test_pi_extensions.py` reads it, then it registers `meow-loop:run`,
   and that handler runs the bundled `meow-loop prompt` with
   `hook_event_name`, the submitted start command, the session id and the
   working directory, and sends the returned `additionalContext` into the
   session as a user message. Closed by: `tools/test_pi_extensions.py`, seen
   failing first (BUG-1610).
2. Given a submitted input that is not the start command, when the handler
   runs, then it feeds the same subcommand, so the runner ends an active run
   `cancelled`. Closed by: the same test.
3. Given a settled turn while a run is active, when the extension runs, then
   it runs `meow-loop stop` with the session id and working directory, and
   continues the session once with the frozen prompt the `block` answer
   names; an answer that reports an ending or an unresolved state continues
   nothing. Closed by: the same test.
4. Given the installed unit's wrapper and a scratch work tree with a small
   record, when `prompt` and `stop` run with the extension's event JSON, then
   each answers in a shape the extension parses. Closed by: the run's output
   in the task's pull request, since it drives the real binary.

## What to do

Reuse the guard's `runGuard` for the two subcommands, parse `say_only`'s
`systemMessage` and the `block` answer's `decision` and `reason`, and at the
settle boundary append the frozen prompt as a `custom_message` entry with
`continue: true`, skipping it when the outcome is `aborted`, so an escaped
turn reads as an interrupted run and not a continued one. State the Pi start
path in `packages/meow-loop/README.md`, and raise `@meowshed/meow-loop` and
the `meow-loop` plugin to 0.16.0 together (REQ-4614).

## Depends on

Nothing.

## Left alone

The `loop` skill, which keeps preparing a run for a terminal outside the
session until the runner's `start` subcommand leaves, as SPC-1201 states.
A Pi skill named `run` would collide with `meow-flow`'s in Pi's flat
namespace, so the session path carries through the command and not a skill.

## Evidence

Not yet.