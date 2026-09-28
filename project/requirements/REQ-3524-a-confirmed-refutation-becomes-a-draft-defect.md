---
id: REQ-3524
artifact: requirement
topic: the-method
class: functional
status: approved
revised: 2026-09-28
elaborates: RES-0309, RES-0063
verification: evaluation
---

# REQ-3524

A refutation that verification confirms MUST be recorded as a draft defect
record that names in `violates` the requirement it shows unmet, records its
`severity`, records as its reproduction the input or condition that broke the
requirement, what verification ran or read to confirm it and the revision it
was confirmed at, and leaves its triage unwritten: the `## Triage` section and
the `enters` field stay empty. Where an open defect record already names the
same requirement and a reproduction that fails for the same cause,
verification cites that defect in the epic's `## Verified` section and writes
no second one.

A confirmed refutation is the evidence a defect record exists to hold. Triage
decides whether the work or the requirement is wrong, and so where the defect
enters, and that judgement belongs to a person, so verification records the
evidence and doesn't answer it. Severity is different: REQ-0372 makes it a
property of the observation and requires it on every defect, so the
verification that observed the break records it. A defect without its
reproduction leaves that person nothing to run, and evidence from before an
edit doesn't survive the edit, so the reproduction names its revision. A
second record for a finding already open would split one defect across two
records that each have to be closed, and the citation lands in `## Verified`
because a citation left in a report is lost with the conversation. REQ-3520
permits the write, and this requirement obliges it.

## Open review findings

- Round 1 suggested splitting the obligation into three: record the defect,
  name the requirement, leave triage unwritten. I kept one requirement,
  because all three are properties of the one record an evaluation checks
  together, and the triage clause has no reason to change on its own.
