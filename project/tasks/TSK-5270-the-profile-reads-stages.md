---
id: TSK-5270
artifact: task
status: approved
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

Not yet.

## Left alone

The Rust module and directory names that say "verbs", this repository's own
`.meowpaw/profile.toml` (TSK-5271 moves it), and the command-line arguments of
`meow-checks run`.
