---
id: EPC-2830
artifact: epic
status: done
revised: 2026-10-11
realises: ADR-2980
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The harness measures no prompt

Realises exactly one authorising record, ADR-2980. The epic is complete when
the runners, the `eval` task and the four case sets are gone, the twenty
withdrawn requirements carry the decision's name, REQ-2750 carries the
reviewed move, and the living specifications name review where they named
measurement.

## Acceptance criteria

Taken from ADR-2980's list of how it will be known realised:

1. `find plugins tools -name "loop.py" -o -name "measure_gate.py"` matches
   nothing, and `mise.toml` names no `eval` task.
2. `plugins/meow-core/evals`, `plugins/meow-author/evals`,
   `plugins/meow-flow/evals` and `plugins/meow-prose/evals` don't exist, and
   `plugins/meow-prose-gate/evals/hand_run.py` still does.
3. The twenty requirements carry `status: withdrawn`, each naming ADR-2980,
   and REQ-2750 carries the reviewed move.
4. SPC-1020 states that no prompt is measured, and SPC-1000, SPC-1010,
   SPC-1030 and SPC-1090 name review where they named measurement.
5. The twelve postponed requirements are named under Postponed in `paw
   status`, with ADR-2980's condition.
6. REQ-5100 states the workflow prohibition, and SPC-1210 states it.
7. Every requirement ADR-2980 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [x] T-001 TSK-5560 withdraw the twenty measurement requirements, write REQ-2750 and REQ-5100 in their places, and regenerate the indexes, in `project/requirements/`
      closes: REQ-2750, REQ-5100

- [x] T-002 [P] TSK-5570 delete the runners and the `eval` task, in `tools/loop.py`, `tools/measure_gate.py`, `tools/test_loop.py` and `mise.toml`
      closes: none
      depends: TSK-5560 (not blocking) - the requirements go in the same pull request, and nothing here reads them

- [x] T-003 [P] TSK-5580 delete the four units' case sets, the reviewer's coverage test and the terms entry that excepts them, in `plugins/meow-core/evals/`, `plugins/meow-author/evals/`, `plugins/meow-flow/evals/`, `plugins/meow-prose/evals/`, `plugins/meow-prose/tests/test_rule_cases.py` and `tools/check_terms.py`
      closes: none
      depends: TSK-5560 (not blocking) - the requirements go in the same pull request

- [x] T-004 [P] TSK-5590 remove the eval tests from the route unit's static test and update the prose-gate unit's page that names the hand run, in `plugins/meow-flow/tests/test_route.py` and `plugins/meow-prose-gate/README.md`
      closes: none
      depends: TSK-5580 (blocking) - the evals it reads are deleted by the other task

- [x] T-005 TSK-5600 update the living specifications and the authoring skill, and run the gate, across `project/specs/SPC-1020`, `SPC-1000`, `SPC-1010`, `SPC-1030`, `SPC-1090` and `plugins/meow-author/skills/write/SKILL.md`
      closes: none
      depends: TSK-5570 (blocking), TSK-5580 (blocking) - the specifications describe the tree the other tasks leave

## Coverage

REQ-2750 and REQ-5100, the requirements ADR-2980 addresses, land in TSK-5560. The
twenty withdrawn requirements are named by TSK-5560, which writes their
withdrawals; a withdrawal closes nothing, so they name no task's `closes`.
TSK-5570 and TSK-5580 are the smallest set that tests the decision, because
the runners gone and the case sets gone are its two checkable claims.
TSK-5570, TSK-5580 and TSK-5590 run in parallel where their files allow;
TSK-5600 waits on both and runs the gate.

## Not covered

The prose gate and its pre-release hand run, which ADR-2980 leaves in force.
The published results inside `plugins/meow-core/evals/results/`, which go
with their cases' directory because no case set survives to explain them;
their numbers are quoted in the frozen records that cite them. The frozen
records citing a measurement, which keep the rules they were approved under.
The twelve evaluation-verified obligations, postponed by ADR-2980 until the
redesign, which no task re-verifies now.
