---
id: EPC-1470
artifact: epic
status: done
revised: 2026-09-27
realises: ADR-1490
---

# A record is reviewed by an agent that didn't write it, and its verdict is labelled as an agent's

Realises exactly one authorising record, ADR-1490. The epic is complete when
`meow-flow` ships `record-reviewer`, the method skill dispatches it before
every gate with the record's path alone and records what stays open, and the
review step dispatches a review of the session's own work.

## Acceptance criteria

Taken from ADR-1490, from its list of how I will know it was realised, before
the tasks below were written:

1. `meow-author check` passes on the agent, which declares `Read`, `Grep` and
   `Glob` as its only tools, and its body carries each question set and the
   two every kind gets, traced in the task's evidence.
2. Evaluation cases run by hand through the loop SPC-1020 states, with no
   model call in CI, show the agent reporting a draft decision with a rule
   given no reason and no cost section, opening with its label, and reporting
   a clean record as clean.
3. Evaluation cases show the method skill dispatching the agent with the path
   alone, stopping after the second round with the open findings written into
   the record, and reporting a record as unreviewed where no agent can be
   dispatched.
4. The review step carries the dispatch and the label, traced in the task's
   evidence.
5. Every requirement ADR-1490 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2290 ship `meow-flow:record-reviewer`, with its questions per
      kind and read-only tools, and its evaluation cases
      closes: REQ-0132, REQ-0147, REQ-0819, REQ-2828, REQ-2830
      evidence: the trace, and both cases at 1.00 on Sonnet 5 and Opus 5.5, in
      #521.

- [x] T-002 TSK-2300 dispatch the reviewer before each gate, bound the repair
      and label the verdict, in the method skill and the review step
      closes: REQ-0149, REQ-0151, REQ-0157, REQ-0822, REQ-0823, REQ-2202
      evidence: the trace, and both dispatch cases at 1.00 on Sonnet 5 and
      Opus 5.5, in #522.

## Coverage

ADR-1490 addresses 11 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001. T-002 dispatches the agent
T-001 ships, so it follows it.

## Not covered

Nothing ADR-1490 addresses. What the review step asks of code and
documentation, and the check on `verification` values, are left out, as
ADR-1490 says.
