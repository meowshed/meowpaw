---
id: TSK-4300
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2320
closes: [REQ-2940, REQ-2942, REQ-2948, REQ-2950]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Print the profile's state and name each unknown key from one table of keys

Every command that reads `.meowpaw/profile.toml` prints `profile: absent`,
`profile: unparseable` or `profile: parsed`, and names each key the tool's
table of keys doesn't list, as SPC-1080 states under "The profile". One task,
one branch, one pull request, one review: the tests first, then the change,
its documentation and its marks.

## Acceptance criteria

1. Given a fixture with `.meowpaw/profile.toml` in the parent of the
   repository root and none in the root, when `meow-checks status` runs in
   the root, then it prints `profile: absent` and every verb as `no profile`
   (REQ-2940). Closed by: a crate test naming REQ-2940, seen failing first.
2. Given a fixture whose profile holds `[verbs` on line 3, when
   `meow-checks status` and `meow-checks run test` run, then each prints
   `profile: unparseable` with the parser's message and line 3, all five
   verbs are unresolved as `profile unparseable`, and nothing runs (REQ-2948).
   Closed by: a crate test naming REQ-2948.
3. Given a fixture with `tset = "true"` and `test = "true"` under `[verbs]`,
   when `meow-checks run test` runs, then the output names `verbs.tset` once
   as unknown, `test` passes, and the exit status is 0, as it is with the key
   removed (REQ-2942). Closed by: a crate test naming REQ-2942.
4. Given the table of keys, when a test reads every entry, then each carries
   a non-empty reason, and a test entry added with an empty reason fails it
   (REQ-2950). Closed by: a crate test naming REQ-2950.
5. Given this repository's own `.meowpaw/profile.toml`, when
   `meow-checks status` runs, then it names no unknown key. Closed by: the
   `test` verb's run in the pull request.

## What to do

Return the parsed table together with its unknown keys from the profile reader
in `crates/meow/src/profile.rs`, and add the table of keys there: one list, an
entry per key path a unit reads, each with its reason. Seed it with every key
a unit reads today, `[verbs]`, `[commits]`, `[git]`, `[tracker]`, `[record]`,
`[docs]`, `[markdown]`, `[licence]`, `[unattended]`, `[prose]` and
`[method]` among them, by reading each feature's code rather than this list.

Print the state line and the unknown keys from every subcommand that reads the
profile: `meow-checks status` and `run`, `meow-scm convention` and
`check-message`, `paw` wherever it reads `[record]`, and every other unit's
subcommand that reads a table. Replace each unit's own "listed as ignored"
report with the shared one, so a key is named once. Keep each exit status as
it is, because ADR-2370 makes the report information and never a failure.

Update each affected unit's README where it describes the report, and the
profile template's comments in `plugins/meow-flow/templates/` if it names the
ignored keys.

## Depends on

Nothing.

## Evidence

The tests came first, in the pull request's first commit, where all three
fixtures in `crates/meow/tests/profile_states.rs` failed and the unit tests in
`crates/meow/src/profile.rs` didn't compile.
`a_profile_above_the_root_is_absent` closes criterion 1 (REQ-2940).
`an_unparseable_profile_names_the_parser_message_and_line_and_runs_nothing`
closes criterion 2 (REQ-2948). `an_unknown_key_is_named_once_and_changes_no_exit_status`
closes criterion 3 (REQ-2942), and
`every_subcommand_that_reads_the_profile_names_each_unknown_key_once` holds the
same rule for fifteen subcommands across ten units.
`every_key_in_the_table_carries_a_reason` closes criterion 4 (REQ-2950), and
`this_repositorys_profile_names_no_unknown_key` closes criterion 5 in the
`test` verb's run.

The review agent found that the first tests matched the parser's message by
its first line and pinned the state lines for `meow-checks` alone. A commit of
its own rewrote both tests, and the second one then failed on `meow-git
push-guard`, which returned before it printed the state when nothing was
left to publish, and on `paw check`, which printed nothing when its layout was
missing. Both now print the state first. `paw status --waiting` prints it on
standard error, and SPC-1080 states why `meow-loop`'s guard prints none.

`mise run all` exits 0, `meow-checks run format lint check test build`
reports all five verbs passed and `paw check` reports 0 findings, on pull
request #818.

## Left alone

The personal profile, which TSK-4310 adds, and the commit types, which
TSK-4320 changes. A profile below the root (REQ-3040) and the comments rule
(REQ-2954) stay out, because ADR-2370 leaves both open.
