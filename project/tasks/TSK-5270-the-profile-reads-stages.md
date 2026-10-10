---
id: TSK-5270
artifact: task
status: done
revised: 2026-10-10
epic: EPC-2760
closes: [REQ-4202, REQ-4204]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The profile reads `[stages]` and reports `[verbs]` as deprecated

The profile reader takes the five from a `[stages]` table, and from a
`[verbs]` table where `[stages]` is absent, and reports `[stages]` as the table
to use whenever it read `[verbs]`.

## Acceptance criteria

1. Given a profile with a `[stages]` table that binds `test`, when a stage
   resolves, then `test` resolves to that command and the report names no
   deprecation. Closed by: a test in `crates/meow`.
2. Given a profile with a `[verbs]` table that binds `test` and no `[stages]`
   table, when a stage resolves, then `test` resolves to that command and the
   report names `[stages]` as the table to use. Closed by: a test in
   `crates/meow`.
3. Given a profile with both tables that bind `test` to different commands,
   when a stage resolves, then `[stages]` wins and the report names the
   duplicate. Closed by: a test in `crates/meow`.

## What to do

Read the table in the one place the profile is read, and make every consumer of
the profile's stages (`meow-checks`, the markdown pack and the profile report)
go through it, so no consumer reads `[verbs]` on its own. Keep the report
line's wording in the style of the existing deprecation reports.

## Depends on

Nothing.

## Evidence

Pull request 875. The tests are in `crates/meow/src/profile.rs` and
`crates/meow/src/verbs.rs`:

- Criterion 1: `a_stages_table_is_the_declaration_and_names_no_deprecation`
  and `a_stage_resolves_from_either_table`.
- Criterion 2: `a_verbs_table_declares_the_stages_and_names_the_table_to_use`
  and `a_stage_resolves_from_either_table`.
- Criterion 3: `with_both_tables_stages_wins_and_the_report_names_the_duplicate`.

Three Python tests asserted the old table name in a bind output and in the
undeclared stage hint, and a commit of its own corrects them. `meow-checks run
build format lint check test` passed on every stage, `test` at 319.6 seconds
after the corrected expectations.

## Left alone

The Rust module and directory names that say "verbs", this repository's own
`.meowpaw/profile.toml` (TSK-5271 moves it), and the command-line arguments of
`meow-checks run`.
