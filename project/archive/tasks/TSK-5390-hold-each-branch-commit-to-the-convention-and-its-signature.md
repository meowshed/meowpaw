---
id: TSK-5390
artifact: task
status: done
revised: 2026-10-11
bug: BUG-1561
closes: []
issue: 1093
projected: 8da3b1f72e45
tracked: 725696452f2e
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold each branch commit to the convention and its signature, in the gate

`tools/check_layers.py commits` runs `meow-scm check-message` on each commit a branch adds, with the commit's own author, and verifies its signature against `.github/allowed_signers` where the profile requires one. It restores REQ-2712 and closes no requirement, because
ADR-2450 addressed it and TSK-4905 closed it.

## Acceptance criteria

1. Given a fixture branch with a commit whose message breaks the convention, or whose signature doesn't verify where signatures are required, when `check_layers.py commits` runs, then it exits 1 naming the commit. Closed by: `test_a_branch_commit_whose_message_breaks_the_convention_fails` and `test_an_unsigned_branch_commit_fails_where_signatures_are_required` in `tools/test_check_layers.py`, seen failing first.
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

The tests came first, in a commit of their own, where the two in `tools/test_check_layers.py` failed for the missing check. They close criterion 1, and `test_each_hook_with_a_gate_check_names_it` closes criterion 2. The check runs `meow-scm check-message` with the commit's own author as the identity, so a sign-off is compared with who wrote the commit and not with whoever runs the gate. `mise run all` passed with exit status 0.

## Left alone

The hook itself and the other rules of its unit.
