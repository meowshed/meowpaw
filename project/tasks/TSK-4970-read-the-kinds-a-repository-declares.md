---
id: TSK-4970
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2535
closes: [REQ-0666, REQ-0668, REQ-0670]
issue: 974
projected: d21283c4b556
tracked: 3ddc10d6c002
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Read the kinds a repository declares, and hold each to every general obligation

`paw check` reads each `[record.kinds.<name>]` table in the profile, checks
its `prefix`, `lifetime` and `template`, and checks files of that kind as it
checks a built-in kind's, as SPC-1070 states under "Kinds a repository
declares". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture profile declaring `[record.kinds.narrative]` with `prefix = "NAR"`, `lifetime = "record"` and a template that exists, and a file `narrative/NAR-0001-<slug>.md` under the record's root missing its `status`, when `paw check` runs, then it reports the missing field as it would for a built-in kind and exits 1 (REQ-0666, REQ-0670). Closed by: a crate test naming REQ-0666, seen failing first.
2. Given the same declaration with no `template`, or a `template` path that doesn't exist, when `paw check` runs, then it reports a finding naming the kind and the missing key or file (REQ-0668). Closed by: a crate test naming REQ-0668.
3. Given a declaration carrying a key that would turn an obligation off, such as `frozen = false`, when any command reads the profile, then the key is reported as unknown and the approved `NAR` file is still held frozen by `paw check frozen` (REQ-0670). Closed by: a crate test naming REQ-0670.
4. Given a profile with `[record.kinds]`, when any command reads it, then `record.kinds` isn't reported as an unknown key. Closed by: the profile's test of its table of keys.

## What to do

Read `[record.kinds]` in the `record` feature of `crates/meow/` and add each
declared kind beside the built-in kinds the layout in
`plugins/meow-flow/lib/layout.toml` names, so every existing check runs over it
unchanged. `prefix`, `lifetime` (`record` or `living`) and `template` are
required, and `template` is a path under `.meowpaw/templates/`. Add
`record.kinds` to the table of keys in `crates/meow/src/profile.rs` with its
reason, as SPC-1080 states under "The profile". Document the table on
`plugins/meow-flow/README.md`.

## Depends on

Nothing.

## Evidence

Every criterion is closed by a test seen failing before the change, all in
`crates/meow/tests/record_kinds.rs` unless named otherwise.

1. `a_declared_kinds_file_missing_its_status_is_reported_like_a_built_in_kinds`
   (REQ-0666, REQ-0670), with `a_well_formed_declared_file_is_not_reported`
   as its counterpart.
2. `a_declaration_without_a_template_is_a_finding`,
   `a_template_that_does_not_exist_is_a_finding` and
   `a_declaration_without_a_prefix_or_a_lifetime_is_a_finding` (REQ-0668).
3. `a_key_that_would_opt_out_is_unknown_and_the_file_stays_frozen`
   (REQ-0670), and `a_declared_kinds_keys_are_known_and_an_opt_out_is_not`
   in `crates/meow/src/profile.rs`.
4. `the_kinds_table_is_not_an_unknown_key` and the profile test above.

The template must sit under `.meowpaw/templates/`, as SPC-1070 states, and a
kind that reuses a built-in kind's name or prefix is a finding; the task
states neither, so both are choices made here. `docs/interface.md` is
regenerated for the new profile key.

Every stage passed in pull request #PR.

## Left alone

`outranks`, which TSK-4975 reads, and an index for a declared kind, which
ADR-2600 leaves to a later decision.
