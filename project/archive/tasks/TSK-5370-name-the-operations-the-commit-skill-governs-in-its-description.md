---
id: TSK-5370
artifact: task
status: done
revised: 2026-10-11
bug: BUG-1550
closes: []
issue: 1091
projected: 713bf348241d
tracked: a35e5d0e25ee
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

The tests came first, in a commit of their own, where
`test_the_description_names_each_operation_the_rules_bound` in
`plugins/meow-scm/tests/test_scm.py` failed. It closes criterion 1
(REQ-1146), and `test_the_description_keeps_the_message_obligation_and_the_closing_sentence`
holds the earlier obligation and the closing sentence. `mise run budget`
failed at 397 of 380 characters, and passed once the budget was raised to 450,
which closes criterion 2. `mise run all` passed with exit status 0.

## Left alone

The rules T1 to T7, which TSK-4370 wrote, and any other unit's description.

A review by a separate agent found the description naming neither `worktree`,
a bare merge nor deletion, and the check matching a word anywhere in the
description. The description now says "a branch is merged or rebased, or a
worktree or working tree is created, removed or deleted" in the sentence that
says the skill MUST be loaded, at 419 characters under the ceiling of 450, and
the test anchors each verb to that sentence. The bug now violates REQ-1146
alone, because REQ-2610 and REQ-2618 are what goes unheld and not what was
broken.

Two gaps stay. Whether the longer description over-triggers on Sonnet 5 or
Opus 5.5 is unmeasured, and ADR-1050 asks for that measurement before a
description ships, so it falls to the owner's next evaluation run. The Pi
package under `packages/meow-scm` mirrors the unit and was already behind
before this change; syncing it is the release's work under ADR-2820.
