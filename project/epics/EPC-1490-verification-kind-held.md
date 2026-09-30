---
id: EPC-1490
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1510
---

# A requirement declares one of four kinds of check, and the record holds it

Realises exactly one authorising record, ADR-1510. The epic is complete when
`paw check rules` fails on a requirement whose `verification` isn't one of
the four kinds, on approved requirements as well as drafts.

## Acceptance criteria

Taken from ADR-1510, from its list of how I will know it was realised, before
the task below was written:

1. A fixture shows `paw check rules` failing on a requirement whose
   `verification` is outside the four, on an approved one as well as a draft,
   and passing on each of the four.
2. `paw check` passes on the project record.
3. REQ-1664 lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2320 add the `verification-kind` rule to `paw check rules`
      closes: REQ-1664
      evidence: two fixtures, the first seen failing, and `paw check` passing
      on the project record, in #535.

## Coverage

ADR-1510 addresses 1 requirement, and it lands in the one task above.

## Not covered

Nothing ADR-1510 addresses. REQ-1662, which ADR-1510 leaves open, is not
addressed here.
