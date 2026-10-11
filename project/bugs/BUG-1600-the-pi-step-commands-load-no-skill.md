---
id: BUG-1600
artifact: bug
status: approved
severity: major
violates: REQ-4122
enters: implement
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Pi step commands tell the person to load a skill and load nothing

Every command the `meow-flow` Pi extension registers — the seven step
commands, the driver, the initialiser and the onboarding command — does
nothing but show a notification, and the notification names the command
itself as the skill to load, so following it repeats the same nothing.

## Reproduction

Seen with Pi 1.1.0, `@meowshed/meow-flow` 0.51.0, at revision `a42e16d2` on
macOS (arm64).

1. Open a Pi session on a repository whose record holds open work.
2. Type `/meow-flow:run`.

## What the system does

A notification reads "Load the skill /meow-flow:run and follow its
instructions". Nothing enters the conversation: no skill loads, the model
sees nothing, and the session does no work. Typing the command again shows
the same notification, because it names the command that shows it, and the
skill command Pi actually exposes is `/skill:run`, a name the notification
never states.

## What it should do, and why

REQ-4122 says each command loads the corresponding skill and runs the step.
A handler that only notifies loads nothing, and a notification pointing at
the command itself can never be followed.

## Triage

It enters at implement, because REQ-4122 covers the behaviour and the
extension does something else. Severity is major: all ten commands of the
method unit are inert on Pi, so a person who installs the packages for the
method gets no method.

## Closed by

`tools/test_pi_extensions.py` fails while any command's handler stops at a
notification, and passes once each handler sends its skill's instructions
into the session, naming the skill file the command maps to.

## Tasks

- [x] T-001 TSK-5440 (done: pull request 1053)
      closes: REQ-4122 send each command's skill into the session instead of a
      notification, in `packages/meow-flow/extensions/flow.ts`
