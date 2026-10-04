---
id: TSK-3870
artifact: task
status: done
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

## Evidence

`tools/test_marketplace.py` holds the three checks, one for each criterion.
All three failed at the pull request's first commit and pass after it, and
`meow-verbs run format lint check test` passed all four verbs. The pull request
removes `plugins/meow-method/`, its marketplace entry, its line in the `test`
verb and its row in `docs/README.md`. Criteria 2 and 3 name `test -e` and
`tools/test_verb_bindings.py` as what closes them; one test file holds all
three instead, so the checks for one task sit together and run in the gate.

## Left alone

Nothing beyond what the epic leaves.
