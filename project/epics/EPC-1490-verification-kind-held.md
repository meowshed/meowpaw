---
id: EPC-1490
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1510
checked-at: "#537"
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

## Verified

I checked this under #537 on `main` after #536, gathering the evidence there
rather than carrying it over from the task. `meow-verbs evidence format lint
test` exits 0, each current at tree `3b9d49e82385`. Every criterion is met:

| Criterion                                                                                                | Evidence on `main` after #536                        |
| -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| 1. `paw check rules` fails on a kind outside the four, draft or approved, and passes on each of the four | The two `VerificationKind` fixtures pass             |
| 2. `paw check` passes on the project record                                                              | The `test` verb runs it, 0 findings                  |
| 3. REQ-1664 lands in exactly one closed task                                                             | `paw show REQ-1664` derives it as closed by TSK-2320 |

### Documentation

TSK-2320 named the rule on `meow-flow`'s page, at 0.33.1. The `test` verb
checked it, running `tools/check_docs.py`.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1510 addresses 1 requirement, and it lands in the one task above.

## Not covered

Nothing ADR-1510 addresses. REQ-1662, which ADR-1510 leaves open, is not
addressed here.
