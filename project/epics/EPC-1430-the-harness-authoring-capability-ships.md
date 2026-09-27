---
id: EPC-1430
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1450
checked-at: "#490"
---

# An authoring unit ships how the harness's own material is written, and a check any repository runs

Realises exactly one authorising record, ADR-1450. The epic is complete when
`meow-author` ships its check and its skill, and this repository's gate runs
the shipped check in place of its own script.

## Acceptance criteria

Taken from ADR-1450, from its list of how I will know it was realised, before
the tasks below were written:

1. `meow-author check` passes on this repository's units, and fixtures show it
   failing on each condition it lists.
2. `meow-author check .claude` runs on a repository's own skills, shown by a
   fixture holding a skill outside any unit.
3. The skill's rules carry each requirement ADR-1450 addresses, traced in the
   task's evidence, and the check passes on the skill.
4. The skill's description loads it before a skill is written in at least
   four of five sessions on each of Sonnet 5 and Opus 5.5, and on no more than
   one of five near misses that change code.
5. Every requirement ADR-1450 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2200 ship `meow-author check`, run it in this repository's
      gate, and retire `tools/check_prompts.py`
      closes: REQ-1110, REQ-1111, REQ-1112, REQ-1114, REQ-1120, REQ-1122,
      REQ-1124, REQ-1128, REQ-1142, REQ-1672, REQ-1678, REQ-2688
      evidence: thirteen fixtures, and the shipped check passing on this
      repository in the `prompts` task, in #485.

- [x] T-002 TSK-2210 give `meow-author` the skill that carries the rules a
      program can't settle
      closes: REQ-1116, REQ-1118, REQ-1126, REQ-2680, REQ-2682, REQ-2684,
      REQ-2686, REQ-2690, REQ-2692, REQ-2706, REQ-2708
      evidence: seventeen rules, and the skill loading in ten of ten writes and
      none of ten near misses, in #486.
      depends: TSK-2200 - the skill ships in the unit T-001 creates

## Verified

I checked this under #490 on `main` after #489, gathering the evidence there
rather than carrying it over from the tasks. Every criterion is met:

| Criterion                                                                                                                 | Evidence on `main` after #489                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. The check passes on this repository, and fixtures fail it on each condition                                            | `meow-author check` reports 56 files and 0 failures, and the unit's 13 fixtures pass, one per condition ADR-1450 lists                                                     |
| 2. The check reads a repository's own `.claude`                                                                           | `test_a_repositorys_own_skills_are_checked` passes, holding a skill outside any unit                                                                                       |
| 3. The skill carries every rule, traced, and the check passes on it                                                       | The skill carries 17 labelled rules; TSK-2200 and TSK-2210 trace the 23 requirements, the program holding ten of them, and the check passes on the skill                   |
| 4. The skill loads before the first write in at least four of five per model, and in no more than one of five near misses | Asked to write an agent definition, with only the unit installed: Sonnet 5 loaded it first in 5 of 5, Opus 5.5 in 5 of 5. Asked to change a line of code: 0 of 3 per model |
| 5. Every requirement lands in exactly one closed task                                                                     | `paw show` derives all 23 requirements ADR-1450 addresses as closed and not yet verified                                                                                   |

The sessions here asked for an agent definition, where the tasks asked for a
skill, so the skill routed on a second kind of material too.

### Documentation

The tasks wrote `meow-author`'s page, and SPC-1080 names the new subcommand.
The `test` verb checked the pages, running `tools/check_docs.py`, which
reports 15 pages and 0 failures.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1450 addresses 23 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001: once it lands, a repository
can check its own material with the shipped program.

## Not covered

Nothing ADR-1450 addresses. Context cost and loading are a later decision, as
ADR-1450 says.
