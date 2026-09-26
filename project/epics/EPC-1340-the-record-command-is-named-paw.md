---
id: EPC-1340
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1350
checked-at: "#404"
---

# The record's command is `paw`

Realises exactly one authorising record, ADR-1350. The epic is complete when
a person runs the record's command as `paw`, and `meow-method` still works for
one release while saying it is deprecated.

## Acceptance criteria

Taken from ADR-1350, from its list of how I will know it was realised, before
the tasks below were written:

1. `plugins/meow-method/bin/paw check` checks the record, and every message
   and usage line it prints names `paw`.
2. `plugins/meow-method/bin/meow-method check` prints to standard error that
   the command is `paw` and that 0.31.0 removes the alias, and its standard
   output and exit status equal `paw`'s.
3. No skill, hook, template, specification, documentation page, `CLAUDE.md`
   or the profile runs `meow-method` as a command.
4. REQ-3166 lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-2020 the record's command is `paw`, with `meow-method` as a deprecated alias
      closes: REQ-3166
      evidence: three fixtures in `Named`, seen failing first, and the `test` verb passing.

## Verified

Checked under issue 404 on the trunk after #403, with evidence gathered there
and not carried over from the task. Every criterion is met:

| Criterion                                                                                                | Evidence on the trunk after #403                                                                                                                                                                                                      |
| -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. `bin/paw check` checks the record, and every message and usage line names `paw`                       | `paw check` exits 0 with 0 findings in every check; `paw show` prints `usage: paw show <id>` and `paw check nothing` prints `paw check: no check is named nothing`, both exit 2; `test_every_usage_line_and_message_names_paw` passes |
| 2. `bin/meow-method check` names `paw` and 0.31.0 on standard error, with `paw`'s output and exit status | Both exit 0, `cmp` finds their standard output identical, and standard error reads "this command is now paw, and 0.31.0 removes the name meow-method"; `test_the_alias_says_it_is_deprecated_and_runs_paw` passes                     |
| 3. Nothing runs `meow-method` as a command                                                               | `grep` over the skills, the hook, the templates, the specifications, `docs/`, `CLAUDE.md` and the profile finds only the two index markers ADR-1350 keeps; `test_nothing_the_unit_ships_runs_the_old_name` passes                     |
| 4. REQ-3166 lands in exactly one closed task                                                             | `paw check coverage` reports 0 findings, and `paw show REQ-3166` names TSK-2020, done in EPC-1340                                                                                                                                     |

Each of the three fixtures failed against the tree before the change, so each
would fail if its requirement were broken. `python3 -m unittest discover -s
plugins/meow-method/tests` ran 126 tests, OK.

Postponed and revisited here: ADR-1340 postpones 8 requirements for version
control tools other than git, until a repository using the harness adopts one
or the owner asks for one. Nothing in this epic bears on that condition, and
whether it holds is the owner's to say.

## Coverage

ADR-1350 addresses 1 requirement, which lands in the one task above. That
task is the smallest set that tests the decision.

## Not covered

The task removing the alias in 0.31.0, which ADR-1350 leaves to be written
when 0.30.0 is released.
