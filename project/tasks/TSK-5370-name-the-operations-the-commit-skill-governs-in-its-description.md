---
id: TSK-5370
artifact: task
status: approved
revised: 2026-10-11
bug: BUG-1550
closes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Name the operations the commit skill governs in its description

The `commit` skill's description states the obligation for every operation its
rules bound, so a request to merge, rebase or remove a working tree loads it.
It restores REQ-1146, REQ-2610 and REQ-2618 and closes none, because ADR-2420
and ADR-1050 addressed them and their tasks closed them.

## Acceptance criteria

1. Given `plugins/meow-scm/skills/commit/SKILL.md`, when a test reads its
   description, then it says the skill MUST be loaded before a composite
   command such as `wt merge` is run, before a branch is rebased and before a
   working tree is created or removed, and it keeps the closing sentence that
   the skill MUST NOT be skipped (REQ-1146). Closed by: a test in
   `plugins/meow-scm/tests/test_scm.py` naming REQ-1146, seen failing first.
2. Given `plugins/meow-scm/budget.toml`, when `mise run budget` runs, then it
   exits 0 with the longer description counted. Closed by: the command's
   output.

## What to do

Extend the description by one sentence naming those operations, in the third
person and with the verbs a request uses (merge, rebase, remove, delete,
create a working tree), and raise `permanent_characters` to what
`mise run budget` measures, updating the comment above it and the figure in
the README.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The rules T1 to T7, which TSK-4370 wrote, and any other unit's description.
