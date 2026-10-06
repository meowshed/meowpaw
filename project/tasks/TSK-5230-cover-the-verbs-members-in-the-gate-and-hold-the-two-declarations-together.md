---
id: TSK-5230
artifact: task
status: done
revised: 2026-10-05
bug: BUG-1510
closes: [REQ-1754]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Cover the verbs' members in the gate, and hold the two declarations together

`mise run all` runs every member the profile's verbs run: the test chain
moves into `[tasks.test]`, which the profile's `test` verb names, the two
unit checks the `lint` verb names directly gain their own tasks, and
`[tasks.all]`'s depends lists a task for each remaining member, so CI's gate
and a local verb run execute the same commands (REQ-1754).
`tools/check_gate_covers_verbs.py` reads both declarations and fails naming
any member the gate lacks, so they cannot drift apart silently again. One
task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the profile's verbs and `mise.toml` as they stood, when the cover
   check runs, then it exits 1 naming 26 members the gate lacks, and given
   the fixed declarations, then it exits 0 (REQ-1754). Closed by: the check
   seen failing first, in the commit that holds it alone.
2. Given this repository's tree, when `mise run all` runs, then it exits 0
   with the full composition. Closed by: the gate's output in the pull
   request.

## What to do

Add `[tasks.test]` carrying the chain the profile's `test` verb held, and
point that verb at it, so the chain is declared once. Add
`[tasks.mise-check]` and `[tasks.markdown]` for the two direct commands the
`lint` verb runs, and extend `[tasks.all]`'s depends to cover every member.
Write the cover check, and register it in the test chain.

## Depends on

Nothing. BUG-1510 is approved.

## Evidence

`python3 tools/check_gate_covers_verbs.py` exits 1 with 26 gate-coverage
failures on the tree the check was written on, and exits 0 after the
declarations moved. `meow-mise check` reports 0 findings, `paw check`
exits 0, and `mise run all` exits 0 on the change's tree, as the pull
request cites.

## Left alone

`[tasks.measure]`, which costs money on real models and is run by hand, and
the per-part gates a repository declares beside its own verbs.
