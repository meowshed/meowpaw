---
id: TSK-5410
artifact: task
status: done
revised: 2026-10-11
bug: BUG-1563
closes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Fail a tracked file of a run's own state, in the gate

`tools/check_layers.py run-state` fails a tracked `run.toml` or `log.jsonl`, because a run's own state lives outside the repository. It restores REQ-2712 and closes no requirement, because
ADR-2450 addressed it and TSK-4905 closed it.

## Acceptance criteria

1. Given a fixture repository that tracks `runs/abc/run.toml`, when `check_layers.py run-state` runs, then it exits 1 naming the file, and this repository passes. Closed by: `test_a_tracked_run_state_file_fails` and `test_this_repository_passes_its_own_run_state_check` in `tools/test_check_layers.py`, seen failing first.
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

The tests came first, in a commit of their own, where `test_a_tracked_run_state_file_fails` failed for the missing check, and `test_this_repository_passes_its_own_run_state_check` closes the other half of criterion 1. `test_each_hook_with_a_gate_check_names_it` closes criterion 2. The check finds a tracked file named for a run's state and nothing else: a write into a run's state in a session leaves no file in the tree, which the hook alone stops. `mise run all` passed with exit status 0.

## Left alone

The hook itself and the other rules of its unit.
