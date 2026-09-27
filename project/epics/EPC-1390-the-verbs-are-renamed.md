---
id: EPC-1390
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1410
checked-at: "#455"
---

# The verbs are `format`, `lint`, `check`, `test` and `build`, and the old names are read one release

Realises exactly one authorising record, ADR-1410. The epic is complete when
`meow-verbs` names the new verbs everywhere it ships and reads the old two for
one release with a notice.

## Acceptance criteria

Taken from ADR-1410, from its list of how I will know it was realised, before
the tasks below were written:

1. `meow-verbs status` lists `format`, `lint`, `check`, `test` and `build`,
   and `meow-verbs run format` runs the command declared under `format`.
2. A fixture shows a profile declaring `fmt` resolving `format` with a notice
   naming 0.4.0, and `meow-verbs run typecheck` running `check` with the same
   notice.
3. No shipped file, page or specification names `fmt` or `typecheck` as a
   verb, apart from the program's reading of the old names and its fixtures.
4. REQ-2908 lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2140 rename the verbs in `meow-verbs` and everywhere they are
      named, reading the old two for one release
      closes: REQ-2908
      evidence: seven fixtures and the verbs run under their new names, in
      #451.

## Verified

I checked this under #455 on `main` after #454, gathering the evidence there
rather than carrying it over from the task. Every criterion is met:

| Criterion                                                                                        | Evidence on `main` after #454                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. `status` lists the five new names, and `run format` runs its command                          | `meow-verbs status` lists `format`, `lint`, `check`, `test` and `build`, and `test_the_verbs_are_named_as_decided` runs `format`'s command                                                             |
| 2. An old key resolves with a notice naming 0.4.0, and `run typecheck` runs `check`              | `test_an_old_key_resolves_its_new_verb_with_a_notice`, `test_an_old_name_on_the_command_line_runs_the_new_verb` and `test_a_new_key_wins_over_its_old_name` pass, with the rest of the unit's fixtures |
| 3. Nothing shipped names `fmt` or `typecheck` as a verb, apart from the reading of the old names | A search finds them in the program's table of old names, its fixtures, and SPC-1040's paragraph describing that reading; `fmt-check` names this repository's own task                                  |
| 4. REQ-2908 lands in exactly one closed task                                                     | `paw show REQ-2908` derives it closed in TSK-2140                                                                                                                                                      |

### Documentation

The task renamed the verbs in every page that names them: `meow-verbs`'s
page, the introduction, the tutorial and the troubleshooting page, restamped
at 0.3.0. The `test` verb checked them, running `tools/check_docs.py`, which
reports 13 pages and 0 failures.

### Postponements

ADR-1360's condition for REQ-1138 and ADR-1340's for its 8 requirements are
untouched by this epic. The owner decides whether either condition holds.

## Coverage

ADR-1410 addresses 1 requirement, which lands in the one task above. That task
is the smallest set that tests the decision.

## Not covered

Nothing ADR-1410 addresses. Removing the old names is a task written when
0.3.0 is released, as ADR-1410 says.
