---
id: TSK-5085
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2560
closes: [REQ-2336]
issue: 994
projected: 5ee99999b028
tracked: 210f0ccf98a0
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Ship the Python pack

The language pack for Python, named in its own document, is detected from `pyproject.toml`, and resolves
the five verbs from what the repository commits, as SPC-1190 states under
"The supported packs". One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository of the language with its marker in a
   subdirectory, when the pack's `status` runs, then it reports for that
   directory and names the marker, and with no marker it prints
   `unresolved: not a Python repository` and exits 3 (REQ-2336). Closed by: a
   crate test naming REQ-2336, seen failing first.
2. Given a fixture repository of the language, when the pack's `bind` runs,
   then it prints all five verbs, each bound from what the fixture commits or
   printed as unresolved or unbound with a reason (REQ-2336). Closed by: a crate
   test naming REQ-2336.
3. Given the fixture, when the pack's tests run, then they hold the shared
   rules that apply to Python: the environment the project declares (REQ-2426), the tool the repository configured where several serve a verb (REQ-2420), documentation tests where the project runs them (REQ-2412) and output kept outside the tree (REQ-2442). Closed by: the crate tests naming
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

- TSK-5080 (blocking): the packs ship one at a time in the order SPC-1190
  states, so a mistake in one is fixed before the next repeats it.

## Evidence

Criterion 1 is closed by `status_reports_for_the_directory_holding_its_marker`,
`with_no_marker_every_command_is_unresolved` and
`status_reports_once_per_directory_and_names_a_part` in
`crates/meow/tests/python.rs`, which name REQ-2336. The test file named the
README the pack ships before it existed, so it failed to compile until the
pack did.

Criterion 2 is closed by `bind_prints_all_five_stages_from_what_the_fixture_commits`,
`bind_prints_an_unconfigured_stage_as_unbound` and
`a_broken_project_is_unresolved_and_bind_takes_a_directory`, which name
REQ-2336.

Criterion 3 is closed, for the environment the project declares (REQ-2426), by
`each_tool_runs_through_the_environment_the_project_declares`,
`two_environments_leave_the_stages_unresolved`,
`check_finds_a_tool_run_outside_the_declared_environment` and
`check_finds_two_environments`. It is closed, for the tool the repository
configured (REQ-2420), by `the_configured_type_checker_binds_and_the_other_is_named`
and `bind_turns_on_no_rule_group_and_applies_no_fix`. It is closed, for
documentation tests (REQ-2412), by `the_test_stage_says_whether_it_runs_documentation_examples`,
and for output kept outside the tree (REQ-2442) by
`check_finds_a_tool_writing_its_cache_into_the_tree` and
`check_finds_ruff_applying_fixes`. The generated files (REQ-2450) are held by
`the_page_states_the_generated_files`, and the settings behind the stages by
`check_finds_two_files_configuring_one_tool` and
`a_clean_check_names_what_it_covered` (REQ-2434, REQ-2432).

Criterion 4 is closed by `tools/check_docs.py`, which reads the `shipped` row
in `docs/README.md`.

Criterion 3's documentation-test clause rests on judgement: the pack reads no
source file, so it cannot tell a project with doctests from one without, and
it states in a comment under `test` that the stage doesn't run them unless the
pytest configuration's `addopts` asks for them. `check` reports no finding for
it, because a project without doctests is not at fault.

Every stage passed in pull request #1077.

## Left alone

The other languages in the order, each its own task, and any binding the
pack's own document doesn't state.
