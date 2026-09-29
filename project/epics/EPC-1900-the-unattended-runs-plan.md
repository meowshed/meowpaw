---
id: EPC-1900
artifact: epic
status: approved
revised: 2026-09-29
realises: ADR-2000
checked-at: "#626"
---

# An unattended run is planned from an authority the repository declares

Realises exactly one authorising record, ADR-2000. The epic is complete when
`meow-unattended plan` reads a repository's `[unattended]` table, refuses
every state ADR-2000 refuses, prints the command that would start the run
with its posture and each unit named, and writes the snapshot that holds the
run's authority, as SPC-1200 states. It starts nothing.

## Acceptance criteria

Taken from ADR-2000, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixture repositories with no `[unattended]` table, and with a table lacking
   each required key in turn, each give `unresolved` naming what's missing and
   exit status 3. A table naming `bypassPermissions`, a gate outside the list,
   a folder of units, a URL, and `merge_protected = true` without `merge` in
   `gates` is each refused the same way.
2. A fixture declaring `dontAsk` prints `--permission-mode dontAsk`, and the
   printed command line holds `--bare`, `--permission-prompts none`,
   `--disallowed-tools AskUserQuestion`, `--max-budget-usd` with the declared
   value, and exactly one `--plugin-dir` for each of three declared units.
3. A fixture repository with a `.mcp.json` server and a hook in
   `.claude/settings.json` gets a command line and snapshot naming neither,
   and one with an `env` block gets `unresolved` naming the file and its keys.
4. The snapshot denies `Edit` on `.meowpaw/**`, `.claude/**` and the folder
   that holds it. Changing the profile after `plan` leaves the snapshot's
   content and its hash unchanged.
5. With `merge_protected` absent, the snapshot holds the three push rules for
   the declared trunk. With it `true`, it holds none.
6. With `amend_approved` absent, a fixture record of two approved and one
   draft requirement and one approved and one draft decision gives exactly
   three deny rules on record files, one for each approved file. With it
   `true`, it gives none. A fixture profile with no `[record]` gets output
   saying there is no record to protect.
7. With `MEOWPAW_STATE=off`, `plan` writes no file and says so, and
   `plan --purge` removes every snapshot of the work tree.
8. `plan`'s output states each of the four limits of the deny rules, that the
   command needs `ANTHROPIC_API_KEY`, and that a record approved later needs a
   new plan.
9. Each check above counts what it matched, and a count of zero where one was
   expected fails it.
10. Every requirement ADR-2000 addresses, REQ-2388 and REQ-2392, lands in
    exactly one closed task.

Criterion 4 reads "the folder that holds it" where an earlier draft of
ADR-2000 read "its own path". I changed both while ADR-2000 was a draft,
because the snapshot's file name is the hash of its content, and content
can't hold a rule naming its own hash.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-3300 add `meow-unattended` with `plan`, which reads the
      `[unattended]` table, prints the command line with its posture, and
      writes the snapshot with its deny rules, in `plugins/meow-unattended/`
      and a feature `unattended` in `crates/meow`
      closes: REQ-2388
      evidence: 13 checks seen failing at the cover commit f9e8b4e, and
      passing unchanged in #663.

- [x] T-002 TSK-3310 make `plan` load each unit by name: refuse a URL, a
      folder of units and a project `env` block, and name each unit with its
      version in the output and the snapshot
      closes: REQ-2392
      depends: TSK-3300, because it extends the program, the table reader and
      the snapshot that task adds
      evidence: 4 checks seen failing at the cover commit fa22b5f, and
      passing unchanged in #668.

Neither task can run in parallel with the other, because TSK-3310 changes the
code TSK-3300 writes.

## Verified

I checked this under #626 on `main` after #668, gathering the evidence there
rather than carrying it over from the tasks. `crates/meow/build-units` rebuilt
the units and exited 0. The 17 fixtures in
`plugins/meow-unattended/tests/test_unattended.py` run 17, OK, exit 0, against
that build, and `meow-verbs evidence --keep format lint check test build`
keeps each verb's result in `project/evidence/`, as the pull request cites.
Every criterion is met:

| Criterion                                                                                                                                             | Evidence on `main` after #668                                                                                                                                                                                                        |
| ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. No table, each missing key, `bypassPermissions`, an unknown gate, a folder, a URL and an unguarded `merge_protected` are each `unresolved`, exit 3 | `Refusals.test_no_table`, `test_no_profile`, `test_each_required_key_missing` (4 subtests) and `test_refused_values` (4), and `Units.test_url_and_folder_refused` (2) pass, each asserting exit 3, one matching line and no snapshot |
| 2. `dontAsk` and the posture flags are printed, with exactly one `--plugin-dir` for each of three units                                               | `Plan.test_command_line_states_the_posture` passes, and `Units.test_one_plugin_dir_for_each_unit` asserts one `--bare` and the three `--plugin-dir` values equal to the declared units in order                                      |
| 3. Neither a `.mcp.json` server nor a hook is named, and an `env` block is refused naming file and keys                                               | `Units.test_repository_hooks_and_servers_not_named` and `Refusals.test_env_block_refused` (2 subtests, one line naming both keys) pass                                                                                               |
| 4. The snapshot denies its own authority, and a later profile change leaves it unchanged                                                              | `Snapshot.test_denies_its_own_authority` and `Snapshot.test_unchanged_after_the_profile_changes` pass                                                                                                                                |
| 5. Three push rules with `merge_protected` absent, none with it `true`                                                                                | `Snapshot.test_push_rules` passes                                                                                                                                                                                                    |
| 6. Exactly three deny rules on approved records, none with `amend_approved`, and no record to protect                                                 | `Snapshot.test_approved_records_are_denied` passes, comparing the rules on record files to the three approved files for equality                                                                                                     |
| 7. `MEOWPAW_STATE=off` writes nothing and says so, and `--purge` removes every snapshot                                                               | `State.test_state_off` and `State.test_purge` pass                                                                                                                                                                                   |
| 8. The output states the four limits, `ANTHROPIC_API_KEY` and that a later approval needs a new plan                                                  | `Plan.test_output_states_the_limits` passes, and each of its six patterns matches one sentence in `crates/meow/src/unattended.rs` and nothing else there                                                                             |
| 9. Each check counts what it matched, and zero where one was expected fails it                                                                        | Every check above asserts a count or an exact list; each check expecting zero also asserts a non-zero count on the same output, such as three `--plugin-dir` values or at least three `Edit` rules, so an empty run fails            |
| 10. REQ-2388 and REQ-2392 each land in exactly one closed task                                                                                        | `paw show` derives REQ-2388 as closed by TSK-3300 and REQ-2392 as closed by TSK-3310, each in EPC-1900                                                                                                                               |

Each check would fail if its requirement were violated, which I judged by
reading it: every assertion names the exact line, rule or flag value, and
none passes on empty output. One check is weaker than the others, and TSK-3310
says so: `Units.test_repository_hooks_and_servers_not_named` passed before
that task, because nothing names a repository server or hook, so it guards
against a regression and never saw one fail.

I also read `claude --help` from the installed Claude Code, which is 2.1.280
and not the 2.1.283 that `requires.toml` names. It exits 0 and lists every flag
`plan` prints, with `dontAsk` among the modes and `none` among the prompt
targets. That is a judgement on a third party's program, as in TSK-3300, and a
flag changed between the two versions wouldn't show. Run in this repository,
which declares no `[unattended]` table, `meow-unattended plan` prints
`unresolved: no [unattended] table in .meowpaw/profile.toml` and exits 3.

### Documentation

`plugins/meow-unattended/README.md` states what `plan` accepts, what it writes
and the four limits, and its `describes:` names `meow-unattended@0.2.0`, which
`plugin.json` holds. The documentation index lists the page, and the `test`
verb checked the pages. `docs/README.md` still lists unattended runs under
Planned, which stays true, because nothing starts a run yet.

### Postponements

ADR-2000 postpones REQ-2372, REQ-2376, REQ-2390 and REQ-2406 until the
decision that starts a run shows their behaviour, and REQ-2376 also until the
sandbox and the credential removal exist. No such decision is recorded, so the
condition doesn't hold, and `paw show` derives each as postponed by ADR-2000.

## Coverage

ADR-2000 addresses two requirements, and each lands in one task. REQ-2388
lands in TSK-3300, because the declared posture reaches the run through what
that task builds: the table, the `--permission-mode` and `--max-budget-usd`
flags, and the snapshot passed as `--settings`. REQ-2392 lands in TSK-3310,
because a unit is loaded by name only once `plan` refuses every entry that
would load by discovery or from an address that can change, and the checks
that show it are that task's.

The criteria split between the tasks as follows. TSK-3300 closes criteria 1
except the URL and folder cases, 2 except the `--plugin-dir` count, and 4 to 8. TSK-3310 closes the URL and folder cases of 1, the `--plugin-dir` count of
2, and 3. Criterion 9 binds every check in both tasks, and criterion 10 is
this epic's own.

The smallest set that tests the decision is both tasks, because REQ-2388 and
REQ-2392 are the only requirements it addresses and each rests on one of
them. Before either task is finished, one thing can be measured:
`meow-unattended` doesn't exist, so every check in both tasks fails, which is
what the cover step keeps as each task's failing run.

## Not covered

- REQ-2372, REQ-2376, REQ-2390 and REQ-2406, which ADR-2000 postpones because
  their checks need a started run. The decision that starts a run closes them
  with the evidence ADR-2000 names.
- Starting, repeating and stopping a run, crossing a declared gate, the
  sandbox and the credential removal, which ADR-2000 names as not settled.
- The user-facing pages outside the unit, `docs/README.md`'s list of units
  among them, which the document step updates once both tasks are done, from
  ADR-2000's consequences.
