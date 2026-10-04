---
id: EPC-1420
artifact: epic
status: done
revised: 2026-09-27
realises: ADR-1440
---

# A defect authorises work directly, and enters the chain where its triage says

Realises exactly one authorising record, ADR-1440. The epic is complete when a
task can be authorised by a defect with no epic, the record says where each
defect enters the chain, and the step files carry the rules on a defect.

## Acceptance criteria

Taken from ADR-1440, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures show a task naming `bug:` whose defect marks it done derived as
   done, `paw ready implement` passing for it once the defect is approved, and
   `paw status` counting tasks by the kind that authorised them.
2. Fixtures show each rule `paw check` holds here failing on a draft that
   breaks it, and the defects approved before this decision passing.
3. The implement and verify step files carry the rules on a defect, traced in
   the task's evidence.
4. Every requirement ADR-1440 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2170 let a defect authorise a task directly, and count work by
      its authority
      closes: REQ-0352, REQ-0354, REQ-0374
      evidence: six fixtures and `status` counting tasks by authority, in #475.

- [x] T-002 TSK-2180 hold a defect's triage, reproduction and closing in
      `paw check`
      closes: REQ-0356, REQ-0358, REQ-0360, REQ-0362, REQ-0364, REQ-0368,
      REQ-0370, REQ-0372
      evidence: eight fixtures and the rules on this record, in #476.
      depends: TSK-2170 - the rules read the `bug` field and the defect's
      tasks it adds

- [x] T-003 [P] TSK-2190 carry the rules on a defect in the implement and
      verify steps
      closes: REQ-0348, REQ-0350, REQ-3170, REQ-3174
      evidence: rules I13 to I15 and V14, traced, in #477.

## Coverage

ADR-1440 addresses 15 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001: once it lands, a one-task
fix needs no epic. T-003 changes only step files, so it can run beside the
other two.

## Not covered

Nothing ADR-1440 addresses. Projecting a defect's own tasks onto a tracker is
left out, as ADR-1440 says.
