---
id: TSK-5095
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2560
closes: [REQ-2340]
issue: 996
projected: a6013dc934d1
tracked: cfa1afe2a050
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Ship the C# pack

The language pack for C#, named in its own document, is detected from a `.sln` or `.csproj` file, and resolves
the five verbs from what the repository commits, as SPC-1190 states under
"The supported packs". One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository of the language with its marker in a
   subdirectory, when the pack's `status` runs, then it reports for that
   directory and names the marker, and with no marker it prints
   `unresolved: not a C# repository` and exits 3 (REQ-2340). Closed by: a
   crate test naming REQ-2340, seen failing first.
2. Given a fixture repository of the language, when the pack's `bind` runs,
   then it prints all five verbs, each bound from what the fixture commits or
   printed as unresolved or unbound with a reason (REQ-2340). Closed by: a crate
   test naming REQ-2340.
3. Given the fixture, when the pack's tests run, then they hold the shared
   rules that apply to C#: a build prerequisite performed explicitly, such as a restore (REQ-2448), a pinned SDK (REQ-2428), the analysis level it ran at (REQ-2444) and output kept outside the tree (REQ-2442). Closed by: the crate tests naming
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

- TSK-5090 (blocking): the packs ship one at a time in the order SPC-1190
  states, so a mistake in one is fixed before the next repeats it.

## Evidence

Criterion 1 is closed by `status_reports_for_the_directory_holding_the_marker`
and `a_work_tree_with_no_marker_is_not_a_c_sharp_repository`
(REQ-2340, REQ-3048), and by `a_project_under_a_solution_is_covered_by_the_solution`.
Criterion 2 is closed by `bind_prints_every_stage_bound_from_the_fixture`,
`bind_names_the_reason_for_each_stage_it_leaves_unbound` and
`two_solutions_in_one_directory_bind_no_stage` (REQ-2340, REQ-2420, REQ-2422).
Criterion 3 is closed by `every_build_restores_explicitly_first` (REQ-2448),
`a_pinned_sdk_is_read_and_compared_with_the_installed_ones` (REQ-2428),
`the_analysis_level_it_runs_at_is_stated` and
`check_reports_each_setting_that_decides_whether_lint_means_anything`
(REQ-2444), and `output_goes_outside_the_working_tree` (REQ-2442), all in
`crates/meow/tests/pack_csharp.rs`. Criterion 4 is closed by
`tools/check_docs.py`, with the `meow-csharp` row of `docs/README.md` reading
`shipped`. The pack is built on `pack.rs` and `detect.rs`, and the shared
`pack::across` joins the stages of several directories (REQ-3048).

Every stage passed in pull request #1077.

## Left alone

The other languages in the order, each its own task, and any binding the
pack's own document doesn't state.
