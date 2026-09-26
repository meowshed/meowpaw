---
id: EPC-1290
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1290
checked-at: "#362"
---

# A GitHub pack reads a repository's history

Realises exactly one authorising record, ADR-1290. The epic is complete when
`meow-github history` prints a repository's whole history and the unit ships
like the others.

## Acceptance criteria

Taken from ADR-1290, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixtures with a stand-in `gh` show `history` printing issues, pull requests
   with `merged`, and both kinds of comment, reading every page, requesting
   the cache, and failing by name on a missing field.
2. A fixture shows a refused read reported as unread, naming the listing,
   with no document printed.
3. `meow-github` installs alone: `check_standalone.py` passes, and its
   launcher runs its binary.
4. Every requirement ADR-1290 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1910 the GitHub pack reads a repository's history
      closes: REQ-2556, REQ-2558, REQ-2560, REQ-2564, REQ-2826, REQ-2832, REQ-2906
      evidence: the pack, four fixtures and a read of this repository, in
      #359.

## Verified

Checked under issue 362 at revision `b799b73`, with evidence gathered there
and not carried over from the tasks. Every criterion is met:

| Criterion                                                                                                                                                            | Evidence at `b799b73`                                                                                                                      |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. `history` prints issues, pull requests with `merged`, and both kinds of comment, reading every page, requesting the cache, and failing by name on a missing field | `test_history_reads_every_listing_and_page` and `test_a_missing_field_fails_by_name` pass                                                  |
| 2. A refused read is reported as unread, naming the listing, with no document                                                                                        | `test_a_refused_listing_leaves_the_history_unread` passes; the pack's four fixtures report `Ran 4 tests`, `OK`                             |
| 3. `meow-github` installs alone, and its launcher runs its binary                                                                                                    | `check_standalone.py` reports `88 unit files, 0 paths leaving their unit`, and the fixtures run the unit's launcher, which runs its binary |
| 4. Every requirement lands in exactly one closed task                                                                                                                | `meow-method check coverage` reports 0 findings, and TSK-1910 is marked `[x]` with evidence                                                |

## Coverage

ADR-1290 addresses 7 requirements, and all land in the one task above,
because the program, its unit and its packaging are one reviewable change.

## Not covered

Nothing ADR-1290 addresses.
