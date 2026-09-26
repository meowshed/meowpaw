---
id: TSK-1760
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1230
closes: [REQ-0530, REQ-0552, REQ-0554, REQ-0555]
issue:
---

# Withdrawn statements are collected and nothing is archived

Withdrawn statements are collected and nothing is archived, as ADR-1230 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a specification citing a withdrawn requirement in its body, when `check shape` runs, then it reports the line, and passes once the citation sits under Withdrawn. Closed by: a fixture.
2. Given a directory named `archive` under the root, when `check shape` runs, then it reports it. Closed by: a fixture.
3. Given REQ-0530 and REQ-0554, when their evidence is gathered, then the task records the file and line that shows each holds. Closed by: the evidence table.

## What to do

In `check shape`, report a living document citing a withdrawn requirement outside a section headed Withdrawn, and a directory under the record's root whose name contains `archive`. Record the evidence that the constitution outranks every artifact and that a superseded record names what replaced it.

## Depends on

Nothing. ADR-1230 is approved.

## Evidence

Not yet.

## Left alone

Splitting approved requirements that carry two obligations, which ADR-1230
leaves to the amendment path.
