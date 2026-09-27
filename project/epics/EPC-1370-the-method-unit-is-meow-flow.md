---
id: EPC-1370
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1390
checked-at:
---

# The method's unit is `meow-flow`, and `meow-method` stays one release as a stub

Realises exactly one authorising record, ADR-1390. The epic is complete when
the unit ships as `meow-flow` under that name everywhere outside the approved
records, the indexes carry the new marker, and a stub under the old name tells
an installed copy where the unit went.

## Acceptance criteria

Taken from ADR-1390, from its list of how I will know it was realised, before
the tasks below were written:

1. `claude plugin install meow-flow@meowpaw` installs the unit from the
   committed catalogue, and `/meow-flow:run` and `paw check` run.
2. No shipped file, specification, page, the constitution or the profile names
   `meow-method`, apart from the stub, the old marker `paw` still reads, and
   approved records.
3. `paw index` writes `<!-- meow-flow index -->`, a fixture shows it reading an
   index with the old marker, and this repository's indexes carry the new one.
4. The stub's `SessionStart` hook prints that `meow-method` is now
   `meow-flow`, with the two commands that move it, in a fixture.
5. REQ-3004, REQ-3168 and REQ-3190 land in exactly one closed task each.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2090 rename the unit to `meow-flow` everywhere outside the
      approved records, and migrate the index markers
      closes: REQ-3168, REQ-3190
      evidence: the unit at `plugins/meow-flow/`, validated, and two marker
      fixtures, in #436.

- [x] T-002 TSK-2100 ship `meow-method` 0.30.0 as a stub that says where the
      unit went
      closes: REQ-3004
      evidence: the stub at 0.30.0 and its notice fixture, in #437.
      depends: TSK-2090 - the stub names the unit T-001 creates, and takes
      over the directory T-001 empties

## Coverage

ADR-1390 addresses 3 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001: once it lands, a person
installs and runs `meow-flow`.

## Not covered

Nothing ADR-1390 addresses. Removing the stub and the old marker is a task
written when 0.31.0 is released, as ADR-1390 says.
