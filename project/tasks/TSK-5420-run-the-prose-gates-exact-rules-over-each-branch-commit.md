---
id: TSK-5420
artifact: task
status: done
revised: 2026-10-11
bug: BUG-1564
closes: []
issue: 1095
projected: b40cc7a7c121
tracked: e9406fe214f8
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Run the prose gate's exact rules over each branch commit, in the gate

`tools/check_layers.py commits` feeds each commit's message to `meow-prose-gate check` as a commit command, with the judge's model call switched off, and fails a message that breaks an exact rule. It restores REQ-2712 and closes no requirement, because
ADR-2450 addressed it and TSK-4905 closed it.

## Acceptance criteria

1. Given a fixture branch with a commit whose message holds a banned phrase, when `check_layers.py commits` runs, then it exits 1 naming the commit and no model is called. Closed by: `test_a_branch_commit_that_breaks_a_prose_rule_fails` in `tools/test_check_layers.py`, seen failing first.
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

The test came first, in a commit of its own, where `test_a_branch_commit_that_breaks_a_prose_rule_fails` in `tools/test_check_layers.py` failed for the missing check. It closes criterion 1, and `test_each_hook_with_a_gate_check_names_it` closes criterion 2. The judge is switched off with `MEOW_PROSE_GATE_JUDGE`, so the check runs the gate's exact rules and makes no model call; the judged rules stay with the hook and the review. `mise run all` passed with exit status 0.

## Left alone

The hook itself and the other rules of its unit.
