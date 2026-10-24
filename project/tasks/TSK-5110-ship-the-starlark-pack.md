---
id: TSK-5110
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2560
closes: [REQ-2348]
issue: 999
projected: ed8dcd428677
tracked: 2594ccf60ee5
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Ship the Starlark pack

The language pack for Starlark, named in its own document, is detected from a Bazel or Buck workspace file, and resolves
the five verbs from what the repository commits, as SPC-1190 states under
"The supported packs". One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository of the language with its marker in a
   subdirectory, when the pack's `status` runs, then it reports for that
   directory and names the marker, and with no marker it prints
   `unresolved: not a Starlark repository` and exits 3 (REQ-2348). Closed by: a
   crate test naming REQ-2348, seen failing first.
2. Given a fixture repository of the language, when the pack's `bind` runs,
   then it prints all five verbs, each bound from what the fixture commits or
   printed as unresolved or unbound with a reason (REQ-2348). Closed by: a crate
   test naming REQ-2348.
3. Given the fixture, when the pack's tests run, then they hold the shared
   rules that apply to Starlark: the build system detected before it binds, Bazel or Buck (REQ-2446), output kept outside the tree (REQ-2442) and results kept in the build system's machine-readable format (REQ-2416). Closed by: the crate tests naming
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

- TSK-5105 (blocking): the packs ship one at a time in the order SPC-1190
  states, so a mistake in one is fixed before the next repeats it.

## Evidence

Criterion 1 is closed by `status_reports_for_the_directory_holding_the_marker`
and `a_work_tree_with_no_marker_is_not_a_starlark_repository` in
`crates/meow/tests/pack_starlark.rs`, seen failing first against a stub
(REQ-2348, REQ-3048). Criterion 2 is closed by
`bind_prints_every_stage_bound_from_the_fixture`,
`buildifier_binds_only_where_the_repository_configured_it` and
`two_workspaces_bind_one_command_that_runs_each_in_its_directory` (REQ-2348).
Criterion 3 is closed by `the_build_system_is_detected_before_any_stage_binds`
and `a_buck_project_binds_no_build_or_test` (REQ-2446),
`check_reports_bazel_symlinks_written_into_the_tree` and
`a_buck_project_binds_no_build_or_test` (REQ-2442), and
`check_reports_a_buildifier_stage_that_passes_whatever_it_finds` with the
`--build_event_json_file` assertion in
`bind_prints_every_stage_bound_from_the_fixture` (REQ-2416).
`status_names_the_generated_files_to_commit_and_to_ignore` and the crate test
`tsk_5135_criterion_3_every_language_pack_states_its_generated_files` close
REQ-2450. Criterion 4 is closed by `tools/check_docs.py`. No criterion rests on
judgement.

`paw ready implement TSK-5110` refused only because TSK-5105, the earlier pack
in the chain, isn't done on this branch.

Every stage passed in pull request #1077.

## Left alone

The other languages in the order, each its own task, and any binding the
pack's own document doesn't state.
