---
id: EPC-1530
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1560
checked-at: "#565"
---

# Evidence stays bound to its tree, and the evidence behind each claim is listed

Realises exactly one authorising record, ADR-1560. The epic is complete when a
dirty submodule leaves no result current, and `evidence --kept` lists the
evidence a change adds with its record identifiers.

## Acceptance criteria

Taken from ADR-1560, from its list of how I will know it was realised, before
the task below was written:

1. The task's evidence traces the `Ledger` and `Kept` fixtures that show a
   record's tree id and a stale record after any change. Fixtures show a
   result collected with a dirty submodule bound to nothing, and a result
   collected on a clean tree reading as bound to nothing, naming the
   submodule and exiting 3, once a submodule file is edited (REQ-0452,
   REQ-0454).
2. Fixtures show `evidence --kept` listing only the files a branch adds,
   committed or not, each with its record identifier and whether it matches
   `HEAD`; a superseded file listed and not counted; a failed result exiting
   1; an empty listing exiting 3; every kept file listed with a note where no
   trunk is declared; each marked bound to nothing outside git; and a record
   identifier a task cites found in the listing (REQ-0456).
3. Every requirement ADR-1560 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2380 bind no result to a dirty submodule, and list the
      evidence a change adds with `evidence --kept`
      closes: REQ-0452, REQ-0454, REQ-0456
      evidence: eight fixtures seen failing first, in #563.

## Verified

I checked this under #565 on `main` after #564, gathering the evidence there
rather than carrying it over from the task. `meow-verbs evidence --keep
format lint test` exits 0 on this change's own tree, each result kept in
`project/evidence/`, and `meow-verbs evidence --kept` lists those three files
as matching `HEAD`, as the pull request cites. The `Claims` and `Ledger`
fixtures pass. Every criterion is met:

| Criterion                                                                                                                                                      | Evidence on `main` after #564                                                             |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1. A record's tree id and staleness hold, a dirty submodule binds no result, and an edit in a submodule leaves no earlier result current                       | The two `Ledger` fixtures traced in TSK-2380 and the two submodule `Claims` fixtures pass |
| 2. `--kept` lists what the branch adds with each record and its match, handles superseded, failed, empty, no-trunk and non-git cases, and joins a cited record | The six listing `Claims` fixtures pass, and this change's own listing names each record   |
| 3. Every requirement lands in exactly one closed task                                                                                                          | `paw show` derives REQ-0452, REQ-0454 and REQ-0456 as closed by TSK-2380                  |

Two results kept within one second can still tie on a fresh clone, as
TSK-2380 records.

### Documentation

TSK-2380 stated the listing and the submodule rule on `meow-verbs`' page, at
0.7.0. The `test` verb checked it, running `tools/check_docs.py`.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1560 addresses 3 requirements, and all land in the one task above,
because they change the same few lines of the ledger.

## Not covered

Nothing ADR-1560 addresses. Matching the record identifiers tasks cite is left
to `paw`, as ADR-1560 says.
