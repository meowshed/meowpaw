---
id: EPC-1370
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1390
checked-at: "#441"
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

## Verified

I checked this under #441 on `main` after #440, gathering the evidence there
rather than carrying it over from the tasks. Every criterion is met, the first
by validation, as the table says:

| Criterion                                                                                      | Evidence on `main` after #440                                                                                                                                                                                                                                                                                      |
| ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. `meow-flow` installs from the committed catalogue, and `/meow-flow:run` and `paw check` run | `claude plugin validate` passes on the catalogue, whose entry names `meow-flow` at `./plugins/meow-flow`, and `plugins/meow-flow/bin/paw check` exits 0. I didn't install the unit into the owner's Claude Code, which would change their configuration, so the skill's invocation rests on the validated manifest |
| 2. Nothing outside the stub, the old marker and approved records names `meow-method`           | A search outside the approved records finds it in the stub's catalogue entry, page, tests and troubleshooting entry, in the old marker the program, a fixture and SPC-1100 name, and in approved records' titles quoted by the indexes                                                                             |
| 3. `paw index` writes the new marker, reads the old, and the indexes carry the new one         | The two index files carrying a block carry `<!-- meow-flow index -->` and none the old form, and `test_an_index_with_the_old_markers_is_read_and_moved_to_the_new` passes                                                                                                                                          |
| 4. The stub's hook prints the rename and the two commands, in a fixture                        | `hooks/notice` prints "meow-method is now meow-flow" and both commands, and the stub's three fixtures pass                                                                                                                                                                                                         |
| 5. Each requirement lands in exactly one closed task                                           | `paw show` derives REQ-3004 in TSK-2100 and REQ-3168 and REQ-3190 in TSK-2090, all closed and not yet verified                                                                                                                                                                                                     |

### Documentation

The epic's tasks changed every page naming the unit: `meow-flow`'s own page,
the stub's page, the introduction, the troubleshooting page and `llms.txt`.
The `test` verb checked them, running `tools/check_docs.py`, which reports 12
pages and 0 failures.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1390 addresses 3 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001: once it lands, a person
installs and runs `meow-flow`.

## Not covered

Nothing ADR-1390 addresses. Removing the stub and the old marker is a task
written when 0.31.0 is released, as ADR-1390 says.
