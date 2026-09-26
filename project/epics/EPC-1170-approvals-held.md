---
id: EPC-1170
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1170
checked-at: "#249"
---

# Approvals held frozen, and pending ones reported first

Realises exactly one authorising record, ADR-1170. The epic is complete when
the frozen check reports a change that invalidates an approval, a session
opens with what waits for approval, and the skill never infers one.

## Acceptance criteria

Taken from ADR-1170, from its list of how I will know it was realised, before
the tasks below were written:

1. Rewording an approved requirement fails `check frozen --base HEAD`, and the
   same change with an added `**Amended by ADR-NNNN.**` line passes.
2. Adding evidence to an approved task and marks to an unverified epic passes.
3. A session started in this repository with a draft waiting opens with it,
   and one started with nothing waiting adds nothing to context.
4. Every requirement ADR-1170 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1590 the frozen check
      closes: REQ-0396, REQ-0398, REQ-0622, REQ-0626, REQ-0630, REQ-0634, REQ-0635
      evidence: nine fixtures, and the check run on this repository's history,
      in #242.

- [x] T-002 TSK-1600 report what waits for approval when a session starts
      closes: REQ-0392, REQ-0394, REQ-0402
      evidence: three fixtures, and a fresh session opening with the draft,
      in #243.

- [x] T-003 TSK-1610 the method skill stops at approval and never infers one
      closes: REQ-0390, REQ-0400
      evidence: M5 and M6 in the skill, in #244.

## Verified

Checked under issue 249 at revision `dc77c1f`, with evidence gathered there
and not carried over from the tasks. Every criterion is met:

| Criterion                                                                                                  | Evidence at `dc77c1f`                                                                                                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Rewording an approved requirement fails `check frozen`, and the same change naming its authority passes | `test_rewording_an_approved_requirement_invalidates_it` and `test_a_change_naming_its_authority_passes` run `OK`; against the revision before BUG-1110's fix the check found the eight requirements that fix edited          |
| 2. Evidence on an approved task and marks on an unverified epic pass                                       | `test_a_task_may_gain_evidence_and_an_unverified_epic_marks` runs `OK`, and `test_a_verified_epic_is_frozen` shows the other side                                                                                            |
| 3. A session with a draft waiting opens with it, and one with nothing waiting adds nothing                 | A fresh `claude -p` session with this unit, in a scratch record whose decision is a draft, opened "ADR-0001 is waiting for your approval at the design gate"; with the decision approved, `status --waiting` printed 0 bytes |
| 4. Every requirement in one closed task                                                                    | `meow-method check coverage` reports 0 findings, and all seven checks and `check frozen` report 0                                                                                                                            |

## Coverage

ADR-1170 addresses thirteen requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. The three tasks can run in parallel, and
T-001 alone tests the decision. Measurable before the work finishes: the
frozen check run against this repository's own history.

## Not covered

Running the frozen check in continuous integration, as ADR-1170 says.
