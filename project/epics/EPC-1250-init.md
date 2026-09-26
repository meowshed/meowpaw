---
id: EPC-1250
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1250
checked-at: "#326"
---

# A repository is brought into the harness by `/meow-method:init`

Realises exactly one authorising record, ADR-1250. The epic is complete when
the init command and its template exist with their rules, and an empty record
reports its coverage as zero.

## Acceptance criteria

Taken from ADR-1250, from its list of how I will know it was realised, before
the tasks below were written:

1. `meow-method template profile` prints a template that names no language,
   build tool or package manager, and `/meow-method:init` carries
   `disable-model-invocation`.
2. Each rule ADR-1250 places in the command maps to its requirement in the
   task that closes it.
3. A fixture shows `check coverage` and `status` on an empty record reporting
   zero requirements and coverage as zero.
4. Every requirement ADR-1250 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1810 the init command and the profile template
      closes: REQ-1560, REQ-1563
      evidence: the template, the command and a fixture, in #319.

- [x] T-002 TSK-1820 the init command reports before it writes and chooses nothing
      closes: REQ-1554, REQ-1561, REQ-1562, REQ-1564
      evidence: 4 requirements traced to four rules, in #320.

- [x] T-003 TSK-1830 an empty record reports its coverage as zero
      closes: REQ-3098, REQ-3180
      evidence: two fixtures, and every write the program makes accounted for,
      in #321.

## Verified

Checked under issue 326 at revision `2636f4b`, with evidence gathered there
and not carried over from the tasks. Every criterion is met:

| Criterion                                                                                                                                             | Evidence at `2636f4b`                                                                                                                                                   |
| ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. `template profile` prints a template naming no language, build tool or package manager, and `/meow-method:init` carries `disable-model-invocation` | `test_the_profile_template_names_no_language` passes, and `disable-model-invocation: true` is found once in `skills/init/SKILL.md`                                      |
| 2. Each rule in the command maps to its requirement in the task that closes it                                                                        | N1 to N5 are each found once in `skills/init/SKILL.md`; TSK-1810 traces N1 and TSK-1820 traces N2 to N5                                                                 |
| 3. `check coverage` and `status` on an empty record report zero requirements and coverage as zero                                                     | `test_an_empty_record_reports_its_coverage_as_zero` and `test_coverage_counts_the_requirements_that_land_in_a_task` pass, `Ran 3 tests`, `OK` with the template fixture |
| 4. Every requirement lands in exactly one closed task                                                                                                 | `meow-method check coverage` reports 0 findings, and the three tasks are marked `[x]` with evidence                                                                     |

## Coverage

ADR-1250 addresses 8 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. TSK-1820 follows TSK-1810; TSK-1830 runs
alongside.

## Not covered

Nothing ADR-1250 addresses.
