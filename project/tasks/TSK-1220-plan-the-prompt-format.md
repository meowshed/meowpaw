---
id: TSK-1220
artifact: task
status: draft
revised: 2026-09-22
epic:
closes: []
issue: 62
---

# Plan the amendment: the format and loading of every prompt

Planning is work, so it is a task, and this record authorises the artifacts it
merges with. It has no epic, because it is the step that produces the decision
an epic would realise.

## What to do

Run steps 1 to 5 of the method over the findings in RES-0270, and produce the
preparatory pull request that closes issue #62:

- Record the guides at their primary source in RES-0270.
- Write REQ-1130 to REQ-1140 where no requirement covered a finding.
- Write ADR-1020, which amends ADR-1010, and mark ADR-1010 as amended.
- Change SPC-1010 and SPC-1020 to state the amendment.
- Write EPC-1020 with acceptance criteria taken from the decision, and one
  task record per task, filed as issues only after the epic is approved.

REQ-0259 keeps the amendment apart from TSK-1110 (#48), which is rebuilt on
top of it.

## Depends on

EPC-1010 approved, because ADR-1020 amends the decision it realises.

## Evidence

Not yet. The task closes on the preparatory pull request merging, with
`tools/check_coverage.py` reporting every requirement ADR-1020 addresses in
exactly one task, and the other checks over the record passing.

## Left alone

The drafts of `meow-prose` on the branch for #48, which are rewritten to this
decision in TSK-1110.
