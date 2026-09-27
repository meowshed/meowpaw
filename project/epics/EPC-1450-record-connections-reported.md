---
id: EPC-1450
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1470
checked-at: "#506"
---

# The record reports deep coverage, suspect citations and unconnected artifacts

Realises exactly one authorising record, ADR-1470. The epic is complete when
`paw check` fails on a chain resting on a draft and on a suspect citation a
change can clear, and `paw status` reports the frozen cases, the unconnected
artifacts and the share of the requirement set resting on judgement.

## Acceptance criteria

Taken from ADR-1470, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures show `check coverage` failing on an approved artifact over a draft
   provider two steps up and passing once the provider is approved, failing on
   a draft over a withdrawn provider, and `status` listing an approved artifact
   over a rejected one.
2. Fixtures show `check relations` failing on a draft citing a target revised
   later, and passing on an approved record doing the same, which `show` marks
   and `status` counts.
3. A fixture shows a citation of an epic revised later passing, and one of a
   withdrawn epic reported as suspect.
4. `status` on the project record lists the five unconnected artifacts, the
   three suspect citations and the share resting on judgement with judgement
   split by verifier, matching the counts in ADR-1470.
5. `paw check` passes on the project record after the change.
6. Every requirement ADR-1470 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2240 check each chain and each citation's date with
      `paw check`, and mark a suspect citation in `paw show`
      closes: REQ-0139, REQ-0141
      evidence: five fixtures seen failing first, and `paw check` passing on
      the project record, in #502.

- [x] T-002 TSK-2250 report unconnected artifacts, frozen suspect citations
      and the share resting on judgement in `paw status`
      closes: REQ-0143, REQ-0161
      evidence: three fixtures seen failing first, and `paw status` on the
      project record matching ADR-1470's counts, in #503.

## Verified

I checked this under #506 on `main` after #505, gathering the evidence there
rather than carrying it over from the tasks. `meow-verbs run format lint test`
exits 0 with `summary: format passed, lint passed, test passed`, and the nine
fixtures in `Connections` and `Reported` pass. Every criterion is met:

| Criterion                                                                                                                | Evidence on `main` after #505                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. `check coverage` fails over a draft two steps up and a draft over a withdrawn provider; `status` lists a rejected one | `Connections` covers the draft chain and the withdrawn provider, and `Reported` the rejected provider in `status`                                                            |
| 2. `check relations` fails on a draft citing a later revision, and passes on an approved one, which `show` marks         | The two `Connections` fixtures on a later revision pass                                                                                                                      |
| 3. An epic revised later passes, and a withdrawn epic is suspect                                                         | `Connections.test_an_epic_is_suspect_by_its_status_and_not_its_date` passes                                                                                                  |
| 4. `status` lists the five unconnected artifacts, the three suspect citations and the share by verifier                  | `paw status` lists BUG-1130, BUG-1150, TSK-1000, TSK-1100 and TSK-1220, the citations from ADR-1020, ADR-1350 and TSK-2020, and 61 of 1091, with judgement split by verifier |
| 5. `paw check` passes on the project record                                                                              | The `test` verb runs `paw check`, which reports 0 findings in every check                                                                                                    |
| 6. Every requirement lands in exactly one closed task                                                                    | `paw show` derives REQ-0139, REQ-0141, REQ-0143 and REQ-0161 as closed, by TSK-2240 and TSK-2250                                                                             |

Each fixture was seen failing before its code, except the one for a living
artifact over a rejected provider, which TSK-2250 wrote after its code. It
would fail if that provider went unreported, because it asserts the finding's
exact text.

### Documentation

TSK-2240 and TSK-2250 described the new findings and reports on `meow-flow`'s
page, at 0.32.0. The `test` verb checked it, running `tools/check_docs.py`.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1470 addresses 4 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001. T-002 builds on the chain
walk and the suspect test T-001 adds, so it follows it.

## Not covered

Nothing ADR-1470 addresses. Clearing a suspect citation in an approved record
without a new record is left out, as ADR-1470 says.
