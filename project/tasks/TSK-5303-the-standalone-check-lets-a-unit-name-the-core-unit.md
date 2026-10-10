---
id: TSK-5303
artifact: task
status: done
revised: 2026-10-10
epic: EPC-2790
closes: [REQ-4502]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The standalone check lets a unit name the core unit

`tools/check_standalone.py` accepts the core unit under a unit's `dependencies`
and reports any other unit named there.

## Acceptance criteria

1. Given a unit whose manifest lists `meow-core`, when the check runs, then it
   passes. Closed by: a test in `tools/test_check_standalone.py`.
2. Given a unit whose manifest lists another unit, when the check runs, then it
   fails naming that unit. Closed by: a test in the same file.

## What to do

Change the check and its tests, and say the rule in SPC-1080's section on
adoption in part.

## Depends on

- TSK-5302 (not blocking): either can land first.

## Evidence

Pull request 881. The tests are in `tools/test_check_standalone.py`:

- Criterion 1: a unit that names `meow-core` under `dependencies` may climb to it.
- Criterion 2: climbing to it without declaring it, or to any other unit, is a
  path leaving the unit.

## Left alone

The Pi packages.
