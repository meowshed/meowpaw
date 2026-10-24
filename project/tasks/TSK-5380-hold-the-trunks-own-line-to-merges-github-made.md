---
id: TSK-5380
artifact: task
status: done
revised: 2026-10-11
bug: BUG-1560
closes: []
issue: 1092
projected: 098b25a13e6d
tracked: 8557fec78a7b
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold the trunk's own line to merges GitHub made, in the gate

`tools/check_layers.py trunk` fails a commit on the trunk's own line, after the baseline, that GitHub did not make, and `mise run layers` runs it on the trunk. A commit made in GitHub's web interface has the same committer and isn't found. It restores REQ-2712 and closes no requirement, because
ADR-2450 addressed it and TSK-4905 closed it.

## Acceptance criteria

1. Given a fixture repository whose trunk has a commit made by a person after the baseline, when `check_layers.py trunk` runs, then it exits 1 naming the commit, and it exits 0 where every commit after the baseline is GitHub's. Closed by: `test_a_commit_on_the_trunk_that_github_did_not_make_fails` in `tools/test_check_layers.py`, seen failing first.
2. Given the unit's README, when a test reads the sentence for the hook, then
   it names `mise run layers`, which is a task of the gate. Closed by:
   `test_each_hook_with_a_gate_check_names_it` in
   `tools/test_hook_layering.py`.

## What to do

Write the check and its tests, wire it into the gate, and name it in the
hook's README sentence in place of the statement that no check holds the rule.

## Depends on

Nothing.

## Evidence

The test came first, in a commit of its own, where `test_a_commit_on_the_trunk_that_github_did_not_make_fails` in `tools/test_check_layers.py` failed for the missing check. It closes criterion 1, and `test_each_hook_with_a_gate_check_names_it` closes criterion 2. The baseline is the merge of pull request 1046, and where a clone doesn't hold it the check reports the trunk as unresolved and exits 3, so a shallow checkout fails the gate and doesn't pass it; the workflow checks out the whole history for that. `mise run all` passed with exit status 0.

## Left alone

The hook itself and the other rules of its unit.
