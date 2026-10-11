---
id: BUG-1610
artifact: bug
status: approved
severity: major
enters: requirements
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A run cannot start from a Pi session

On Claude Code a person types `/meow-loop:run` and the run starts in the
session. On Pi the same typing is an unknown command: the `meow-loop`
extension registers only its guards, so a run can start only from a terminal
outside the session, and the session where the person works cannot hold one.

## Reproduction

Seen with Pi 1.1.0, `@meowshed/meow-loop` 0.15.0, at revision `a42e16d2` on
macOS (arm64).

1. Open a Pi session on a repository whose record holds open work.
2. Type `/meow-loop:run --iterations 5`.

## What the system does

Pi reports no such command. The package's extension
(`packages/meow-loop/extensions/loop.ts`) registers no command; its hooks
table in SPC-1300 maps no `UserPromptSubmit` and no `Stop` event, so the
runner's `prompt` and `stop` subcommands are unreachable from a session. The
only Pi path is the `loop` skill, which writes a prompt file and hands the
person a `meow-loop start` command for a terminal outside the session.

## What it should do, and why

The person who types the start command is the person REQ-0894 asks for, so
starting from a session violates nothing — but no requirement covers the Pi
start path, because SPC-1300's hook table predates the in-session run. That
is a gap in the requirements, so the defect enters at requirements and
REQ-4616 states the missing behaviour.

## Triage

It enters at requirements, where REQ-4616 is written, and its fix implements
that requirement. Severity is major: the runner's whole purpose is a run a
person starts where they work, and on Pi it cannot happen there.

## Closed by

`tools/test_pi_extensions.py` passes once the extension registers the
command, feeds every submitted input to the runner's `prompt` subcommand and
continues the session at the settle boundary on the runner's `stop` answer,
and REQ-4616 carries TSK-5450 as its closing task.

## Tasks

- [ ] T-001 TSK-5450 register the `meow-loop:run` command on Pi and carry a
      run with the runner's `prompt` and `stop` subcommands, in
      `packages/meow-loop/extensions/loop.ts`
      closes: REQ-4616