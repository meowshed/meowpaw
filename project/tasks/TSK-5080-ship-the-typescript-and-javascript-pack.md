---
id: TSK-5080
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2560
closes: [REQ-2338]
issue: 993
projected: 96d74475b423
tracked: 62e3fda83aef
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Ship the TypeScript and JavaScript pack

The language pack for TypeScript and JavaScript, named in its own document, is detected from `package.json`, and resolves
the five verbs from what the repository commits, as SPC-1190 states under
"The supported packs". One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository of the language with its marker in a
   subdirectory, when the pack's `status` runs, then it reports for that
   directory and names the marker, and with no marker it prints
   `unresolved: not a TypeScript and JavaScript repository` and exits 3 (REQ-2338). Closed by: a
   crate test naming REQ-2338, seen failing first.
2. Given a fixture repository of the language, when the pack's `bind` runs,
   then it prints all five verbs, each bound from what the fixture commits or
   printed as unresolved or unbound with a reason (REQ-2338). Closed by: a crate
   test naming REQ-2338.
3. Given the fixture, when the pack's tests run, then they hold the shared
   rules that apply to TypeScript and JavaScript: the package manager the project declares (REQ-2426), the tool the repository configured where several serve a verb (REQ-2420), output kept outside the tree (REQ-2442) and the generated files to commit and to ignore (REQ-2450). Closed by: the crate tests naming
   each requirement.
4. Given `docs/README.md`, when the pack ships, then its row reads `shipped`.
   Closed by: `tools/check_docs.py`.

## What to do

Before implementing, check that the pack's own specification exists beside
SPC-1190, written through the spec step, with `paw ready implement` on this
task; where it doesn't, stop and report it, because this task decides
nothing the pack's document states: its bindings, its findings and its
settings table. Build the pack as a feature of `crates/meow/` on EPC-2565's
shared layer, with a program carrying `status`, `bind` and `check`, a skill
and a page, as SPC-1190's Boundary states. The pack binds each verb from the
tool the repository configured, and never from what is installed. Add a
fixture repository of the language to the crate's tests. The pack's README
states the toolchain versions it is current as of.

## Depends on

- TSK-5075 (blocking): the packs ship one at a time in the order SPC-1190
  states, so a mistake in one is fixed before the next repeats it.

## Evidence

Criterion 1 is closed by `status_reports_for_the_directory_holding_its_marker`,
`with_no_marker_every_command_is_unresolved` and
`status_reports_once_per_directory_and_names_a_part` in
`crates/meow/tests/typescript.rs`, which name REQ-2338. The test file named the
README the pack ships before it existed, so it failed to compile until the
pack did.

Criterion 2 is closed by `bind_prints_all_five_stages_from_what_the_fixture_commits`,
`bind_prints_an_unconfigured_stage_as_unbound` and
`bind_without_a_package_manager_leaves_every_stage_unresolved`, which name
REQ-2338.

Criterion 3 is closed, for the package manager the project declares
(REQ-2426), by `each_tool_runs_through_the_manager_the_project_declares`,
`a_manager_that_cannot_be_told_leaves_the_stages_unresolved`,
`check_finds_a_tool_run_outside_the_declared_manager` and
`check_finds_two_lockfiles`. It is closed, for the tool the repository
configured (REQ-2420), by `the_configured_linter_binds_and_the_installed_one_never_does`
and `an_eslintrc_binds_nothing_and_is_named`. It is closed, for output kept
outside the tree (REQ-2442), by `tsc_writes_nothing_into_the_tree`, and for the
settings behind the stages by `check_finds_eslint_settings_that_have_no_effect`
and `check_finds_oxlint_passing_on_warnings` (REQ-2434), and
`a_clean_check_names_what_it_covered` (REQ-2432). It is closed, for the
generated files to commit and to ignore (REQ-2450), by
`the_page_states_the_generated_files`, which reads both READMEs.

Criterion 4 is closed by `tools/check_docs.py`, which reads the `shipped` row
in `docs/README.md`.

No criterion rests on judgement. One finding came with the work: Biome's
documentation states no exit status for `biome format` without `--write`
(RES-0362), so the pack binds no format command to Biome alone and says so.

Every stage passed in pull request #1077.

## Left alone

The other languages in the order, each its own task, and any binding the
pack's own document doesn't state.
