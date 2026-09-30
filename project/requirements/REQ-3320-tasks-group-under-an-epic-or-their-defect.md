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
