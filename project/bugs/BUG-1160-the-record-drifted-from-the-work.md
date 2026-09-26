---
id: BUG-1160
artifact: bug
status: approved
severity: minor
violates: REQ-0239
found: 2026-09-26
revised: 2026-09-26
issue: 209
---

# The record drifted from the work in four places

## Reproduction

At the revision #193 merged, run `meow-method status`. It leads with four
tasks waiting for approval whose work is merged and verified, shows EPC-1080
with a task open that closed, and shows ADR-1030, ADR-1040 and ADR-1060 at
"next: spec, then epic".

## What the system does

TSK-1360 to TSK-1390 are stored as `draft`, although EPC-1080 approved them
and they closed with evidence. EPC-1080 marks T-005 `[+]`, which says the task
was added after approval but not that it is done. ADR-1030, ADR-1040 and
ADR-1060 each said it added no task, because another epic's task made the
change, so no epic realises them, and REQ-0077 is closed by no task at all.

## What it should do, and why

REQ-0239 asks each decision addressing a requirement for its own epic and
tasks, because an epic is how anyone can tell whether the decision was
realised. A task's stored status and an epic's marks are what `status` and
`ready` read, so a stale one reports work as waiting that is done.

## Triage

Implementation, in the record. The task statuses and the mark are corrected,
and each of the three decisions gets an epic of its own with a task that runs
the decision's probes against the merged work.

## Closed by

`meow-method status` places ADR-1030, ADR-1040 and ADR-1060 as realised, and
leads with no task that is done. EPC-1120's second criterion, a measurement on
both models, stays unmet and named, because evaluation is postponed.
