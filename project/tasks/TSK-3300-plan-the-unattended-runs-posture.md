---
id: TSK-3300
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1900
closes: [REQ-2388]
issue:
---

# Add `meow-unattended plan`, which prints a run's declared posture and writes the snapshot that holds its authority

A new method-layer unit, `meow-unattended`, ships `plan`: it reads the
`[unattended]` table in `.meowpaw/profile.toml`, refuses a table that is
missing or wrong, prints the command that would start the run with the
declared posture and budget, and writes the snapshot, holding the deny rules,
that the command passes as `--settings`. So an unattended run's posture is
declared by the repository and never inherited from a session's default,
which is what REQ-2388 asks. One task, one branch, one pull request, one
review.

## Acceptance criteria

Every check below lives in `plugins/meow-unattended/tests/test_unattended.py`,
runs the built unit against a fixture repository in a temporary directory,
and counts what it matched, failing on a count of zero where one was expected
(EPC-1900 criterion 9).

1. Given a fixture repository whose profile has no `[unattended]` table, when
   `meow-unattended plan` runs, then it prints `unresolved` naming the table
   and exits 3, and writes no snapshot. Closed by: `Refusals.test_no_table`.
2. Given a table lacking each of `permission_mode`, `budget_usd`, `gates` and
   `units` in turn, when `plan` runs, then it prints `unresolved` naming the
   missing key and exits 3. Closed by:
   `Refusals.test_each_required_key_missing`, which runs four fixtures.
3. Given a table naming `bypassPermissions`, a table naming a gate outside
   the list, a `budget_usd` of 0, and `merge_protected = true` without
   `merge` in `gates`, when `plan` runs on each, then it prints `unresolved`
   naming the value and exits 3. Closed by: `Refusals.test_refused_values`.
4. Given a table with `gates = []`, when `plan` runs, then it exits 0.
   Closed by: `Plan.test_empty_gates_is_a_declaration`.
5. Given a table declaring `dontAsk` and a budget of 2.5, when `plan` runs,
   then the command line holds `-p`, `--bare`, `--permission-mode dontAsk`,
   `--permission-prompts none`, `--disallowed-tools AskUserQuestion`,
   `--output-format stream-json`, `--verbose`, `--max-budget-usd 2.5` and
   `--settings` followed by the snapshot's path, one argument per line.
   Closed by: `Plan.test_command_line_states_the_posture`.
6. Given a fixture plan, when the snapshot is read, then it denies `Edit` on
   `//<work tree>/.meowpaw/**`, `//<work tree>/.claude/**` and the folder
   that holds it, its file name is the SHA-256 of its content, and it holds
   no `apiKeyHelper`. Given the profile then changed, the earlier snapshot's
   content and hash are unchanged. Closed by:
   `Snapshot.test_denies_its_own_authority` and
   `Snapshot.test_unchanged_after_the_profile_changes`.
7. Given `merge_protected` absent and `[git] trunk = "main"`, when `plan`
   runs, then the snapshot holds `Bash(git push *main*)`, `Bash(git push)`
   and `Bash(git push *HEAD*)`; given `merge_protected = true` with `merge`
   in `gates`, it holds none of the three. Closed by:
   `Snapshot.test_push_rules`.
8. Given `amend_approved` absent and a fixture record of two approved and one
   draft requirement and one approved and one draft decision, when `plan`
   runs, then the snapshot holds exactly three `Edit` rules on record files,
   one for each approved file; given `amend_approved = true`, it holds none;
   given a profile with no `[record]`, the output says there is no record to
   protect. Closed by: `Snapshot.test_approved_records_are_denied`.
9. Given `MEOWPAW_STATE=off`, when `plan` runs, then it writes no file and
   says no snapshot was kept; given two plans kept, when `plan --purge` runs,
   then neither file remains. Closed by: `State.test_state_off` and
   `State.test_purge`.
10. Given a fixture plan, when its output is read, then it states the four
    limits of the deny rules, that the command needs `ANTHROPIC_API_KEY`, and
    that a record approved later needs a new plan. Closed by:
    `Plan.test_output_states_the_limits`.
11. Given Claude Code 2.1.283 installed, when `claude --help` is read, then
    it lists every flag criterion 5 names. Judgement, because the check reads
    a third party's installed program, which no fixture pins and CI doesn't
    have; the implementer keeps the help text as evidence and names the
    version read, and says so where it isn't 2.1.283.
12. Given this change's tree, when `meow-verbs run format lint check test
build` runs, then each passes. Closed by: the kept evidence of that run.

## What to do

Build the unit as SPC-1200 states, except what TSK-3310 adds. The unit's
directory holds a launcher in `bin/`, `.claude-plugin/plugin.json` at version
0.1.0, a README whose `describes:` matches it, a `budget.toml` of zero
characters, since it ships no skill, a `requires.toml` naming Claude Code
2.1.283, and its tests. Add the unit to `.claude-plugin/marketplace.json`, a
feature `unattended` to `crates/meow/Cargo.toml` and its subcommand to
`crates/meow/src/main.rs`, the unit's pair to `crates/meow/build-units`, and
its test directory to the `test` verb in `.meowpaw/profile.toml`. Read the
table through the profile reader in `crates/meow/src/profile.rs`.

In this task `plan` passes each `units` entry to `--plugin-dir` as written.
Find the state directory and the key as the evidence ledger does
(SPC-1040). Write the snapshot through a temporary file renamed into place.
The README states the four limits, and that the command needs
`ANTHROPIC_API_KEY`, as SPC-1200 gives them.

Write the checks first, in a commit of their own, and see them fail.

## Depends on

Nothing: the profile reader, the state directory and the record reader
already exist.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

Checking that each unit is a unit's own directory, refusing a URL or a folder
of units, refusing a project `env` block, and naming each unit's version,
which TSK-3310 adds, so between the two tasks `plan` passes a unit entry
unchecked. Starting a run, which ADR-2000 leaves to a later decision.
`docs/README.md` and the root `README.md`, which the document step updates.
