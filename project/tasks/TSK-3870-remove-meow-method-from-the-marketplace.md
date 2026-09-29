---
id: TSK-3870
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-2200
closes: [REQ-3654]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Remove the `meow-method` stub from the marketplace

`plugins/meow-method/` and its marketplace entry are gone, and the test verb no longer runs its tests. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the marketplace, when `.claude-plugin/marketplace.json` is read, then it has no `meow-method` entry. Closed by: a `tools/` test.
2. Given the repository, when `test -e plugins/meow-method` runs, then it exits 1. Closed by: that command.
3. Given `.meowpaw/profile.toml`, when the `test` verb is read, then it names no `plugins/meow-method`. Closed by: `tools/test_verb_bindings.py`.

## What to do

Delete `plugins/meow-method/`, its marketplace entry, its line in the profile's `test` verb, and its row in every page listing the units. Frozen records keep the name.

## Depends on

Nothing.

## Cover

Not yet. The cover step replaces this line with four, `Checks`,
`Failing run`, `Landed in` and `Judgement`, and `paw ready implement` refuses
the task until they are filled.

## Evidence

Not yet.

## Left alone

Nothing beyond what the epic leaves.
