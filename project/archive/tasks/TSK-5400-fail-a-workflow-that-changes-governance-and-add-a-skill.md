---
id: TSK-5400
artifact: task
status: done
revised: 2026-10-11
bug: BUG-1562
closes: []
issue: 1094
projected: 3a189c3ddf62
tracked: b67c9cb3f861
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Fail a workflow that changes governance, and say why in a skill

`tools/check_workflows.py` fails a workflow step that runs a `gh` command the governance guard asks about, and `meow-github` ships the `governance` skill that says why. It restores REQ-2712 and closes no requirement, because
ADR-2450 addressed it and TSK-4905 closed it.

## Acceptance criteria

1. Given a workflow whose step runs `gh api -X PUT` on branch protection, a ruleset, `gh repo edit` or `gh secret set`, when the check runs, then it names the line and exits 1, and the unit ships a skill whose description states the obligation. Closed by: `test_a_step_that_changes_governance_fails_naming_its_line` in `tools/test_check_workflows.py` and `GovernanceSkill` in `plugins/meow-github/tests/test_skill.py`, seen failing first.
2. Given the unit's README, when a test reads the sentence for the hook, then
   it names `mise run test-tools`, which is a task of the gate. Closed by:
   `test_each_hook_with_a_gate_check_names_it` in
   `tools/test_hook_layering.py`.

## What to do

Write the check and its tests, wire it into the gate, and name it in the
hook's README sentence in place of the statement that no check holds the rule.

## Depends on

Nothing.

## Evidence

The tests came first, in a commit of their own, where `test_a_step_that_changes_governance_fails_naming_its_line` in `tools/test_check_workflows.py` and the three tests of `GovernanceSkill` in `plugins/meow-github/tests/test_skill.py` failed. They close criterion 1, and `test_each_hook_with_a_gate_check_names_it` and `test_the_governance_guard_names_a_skill_in_its_unit` close criterion 2. The skill's description is 394 characters and the unit's budget is 440. A review found the first rule matching a few spellings, so the check now asks the guard itself, which also learned to read a `gh -R owner/name` before its subcommand. `mise run all` passed with exit status 0.

## Left alone

The hook itself and the other rules of its unit.
