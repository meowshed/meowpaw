---
id: REQ-3320
artifact: requirement
topic: the-forge
class: functional
status: approved
revised: 2026-09-28
elaborates: RES-0289
verification: static
---

# REQ-3320

The harness MUST NOT write any grouping of a task other than the epic that realises its authorising record or the defect that carries it, in the record or on a tracker, where a milestone, a project, a label and a parent issue are each a grouping even when it stands for the task's epic or defect, the epic's or the defect's own issue as a parent included.

RES-0289 found that a defect carries its own tasks, so a task already sits
under one of two records, and that GitHub offers four more groupings, a
milestone, a parent issue, a project and a label. A grouping the record
doesn't hold is a second plan the tracker keeps, which RES-0022 names as the
failure to avoid, and a parent issue also leaves its sub-issues open when a
closing keyword closes the parent. A grouping field inside the record, such
as a `milestone:` in a task's front matter, does the same harm from the other
side: the task then answers to two plans, and whoever reads its status has to
reconcile them.

## Open review findings

- The agent reviewer, round 1, finding 3 (preference): list RES-0022 beside
  RES-0289 in `elaborates:`. I left it, because every requirement in the
  record names one research document there, and RES-0289 elaborates RES-0022,
  so the claim reaches RES-0022 through it.
- The agent reviewer, round 1, finding 4 (preference): state only the tracker
  half. I kept both halves, because the record half is what stops a grouping
  field being added to a task later, and ADR-1800's forbidden fields check it.
- The agent reviewer, round 2, finding 3 (preference): name in the statement
  that a static search can't see a grouping built at runtime or written by an
  agent following a prompt. I left it, because the statement forbids the
  write whoever makes it, and a gap in how one check reaches it belongs to
  the check and not to the obligation.
