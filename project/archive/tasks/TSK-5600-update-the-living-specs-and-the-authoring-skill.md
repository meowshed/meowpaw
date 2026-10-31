---
id: TSK-5600
artifact: task
status: done
revised: 2026-10-11
epic: EPC-2830
closes: []
issue: 1111
projected: f15c8c65e071
tracked: f8e13db77491
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Update the living specifications and the authoring skill

The living specifications state what the tree now does, and the authoring
skill's rule on moving explanation names review. This task runs last and runs
the gate.

## Acceptance criteria

1. Given `project/specs/SPC-1020-measuring-the-harness.md`, when read, then it
   states that the harness measures no prompt and keeps none of the
   measurement rules. Closed by: reading it in the pull request.
2. Given SPC-1000, SPC-1010, SPC-1030 and SPC-1090, when read, then each names
   review where it named measurement, and SPC-1010 no longer states the
   reviewer's case set. Closed by: reading them in the pull request.
3. Given the changed tree, when `mise run all` runs, then it passes as far as
   its pre-existing findings allow, and `paw check` reports no finding this
   epic's change introduced. Closed by: the gate's output in the pull request.

## What to do

SPC-1020: rewrite to a short statement of the absence, keeping its identity
and what ADR-2980 and ADR-2840 name. SPC-1000: the measurement paragraph
becomes review wording. SPC-1010: the reviewer's case-set section and its
REQ-4800/4802/4804 citations go. SPC-1030: the lines citing the loop and the
routing measurement name review. SPC-1090: the route paragraph's case
sentence names review. The `write` skill's C6 names review.

## Depends on

- TSK-5570 (blocking): the specifications describe the tree the runner task
  leaves.
- TSK-5580 (blocking): the specifications describe the tree the case-set task
  leaves.

## Evidence

SPC-1020 states the absence and carries a Behaviour section (criterion 1).
SPC-1000, SPC-1010, SPC-1030 and SPC-1090 name review where they named
measurement, SPC-1010's case-set section is gone, and SPC-1210 and SPC-1300
lost their withdrawn citations (criterion 2). The `write` skill's C6 names
review. `paw check` reports only the pre-existing REQ-4110 finding, and `mise
run all` fails only where `main`'s does (criterion 3).

## Left alone

SPC-1070's verification-kinds row, which keeps `evaluation` for the frozen
records, and the frozen records citing a measurement.
