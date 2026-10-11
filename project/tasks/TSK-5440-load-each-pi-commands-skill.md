---
id: TSK-5440
artifact: task
status: done
revised: 2026-10-11
bug: BUG-1600
closes: []
issue:
---

# Load each Pi command's skill, and answer nothing else

Each of the ten commands `packages/meow-flow/extensions/flow.ts` registers
sends its skill's instructions into the session as a user message, so the
step runs; no handler stops at a notification. One task, one branch, one pull
request, one review: the tests first, then the change, its documentation and
its marks.

## Acceptance criteria

1. Given `packages/meow-flow/extensions/flow.ts`, when
   `tools/test_pi_extensions.py` reads it, then every registered command's
   handler sends a user message carrying the SKILL.md text of the skill the
   command maps to, with the command's arguments beside it, and no handler
   ends at `ctx.ui.notify` alone. Closed by: `tools/test_pi_extensions.py`,
   seen failing first (BUG-1600).
2. Given the skill file each command names, when the test resolves it under
   `packages/meow-flow/skills/`, then each exists. Closed by: the same test.
3. Given this change's tree, when `meow-checks run format lint check test
build` runs, then each passes. Closed by: each verb's outcome in the task's
   pull request.

## What to do

Map the seven step commands and the driver, initialiser and onboarding
command to the skill files that exist — the seven steps and the driver load
`skills/method/SKILL.md` and `skills/run/SKILL.md`, `init` and `onboard`
their own — send the file's text with the arguments, and correct the command
table in SPC-1300, which names skill files no unit ships. Raise
`@meowshed/meow-flow` and the `meow-flow` plugin to 0.52.0 together
(REQ-4614), and carry the README change to both sides.

## Depends on

Nothing.

## Left alone

The `route` command, which the flow commands' list does not carry, because
routing is a tool the model invokes and not a step a person drives.

## Evidence

The tests came first, in a commit of their own, c22f6679, where every command's handler still notified. `tools/test_pi_extensions.py` closes criteria 1 and 2: `FlowCommands.test_each_command_sends_its_skill_into_the_session` and `FlowCommands.test_each_command_maps_to_a_skill_that_exists` pass on this tree, `Ran 14 tests` and `OK`. Criterion 3 is closed by the verbs' outcomes in pull request 1053. SPC-1300's command table names the skills that exist, and both manifests carry 0.52.0 (REQ-4614).
