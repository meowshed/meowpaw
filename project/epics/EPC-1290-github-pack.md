---
id: EPC-1290
artifact: epic
status: draft
revised: 2026-09-26
realises: ADR-1290
checked-at:
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

- [ ] T-001 TSK-1910 the GitHub pack reads a repository's history
      closes: REQ-2556, REQ-2558, REQ-2560, REQ-2564, REQ-2826, REQ-2832, REQ-2906

## Coverage

ADR-1290 addresses 7 requirements, and all land in the one task above,
because the program, its unit and its packaging are one reviewable change.

## Not covered

Nothing ADR-1290 addresses.
