---
id: TSK-5115
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2560
closes: [REQ-2350]
issue: 1000
projected: 67c3606b4a50
tracked: 80221cf53f3f
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Ship the Scheme pack

The language pack for Scheme, named in its own document, is detected from a Scheme project file, and resolves
the five verbs from what the repository commits, as SPC-1190 states under
"The supported packs". One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository of the language with its marker in a
   subdirectory, when the pack's `status` runs, then it reports for that
   directory and names the marker, and with no marker it prints
   `unresolved: not a Scheme repository` and exits 3 (REQ-2350). Closed by: a
   crate test naming REQ-2350, seen failing first.
2. Given a fixture repository of the language, when the pack's `bind` runs,
   then it prints all five verbs, each bound from what the fixture commits or
   printed as unresolved or unbound with a reason (REQ-2350). Closed by: a crate
   test naming REQ-2350.
3. Given the fixture, when the pack's tests run, then they hold the shared
   rules that apply to Scheme: the implementation detected before it binds (REQ-2446) and the tool the repository configured where several serve a verb (REQ-2420). Closed by: the crate tests naming
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

- TSK-5110 (blocking): the packs ship one at a time in the order SPC-1190
  states, so a mistake in one is fixed before the next repeats it.

## Evidence

Criterion 1 is closed by `status_reports_for_the_directory_holding_the_marker`
and `a_directory_of_scm_files_is_not_a_scheme_repository` in
`crates/meow/tests/pack_scheme.rs`, seen failing first against a stub
(REQ-2350, REQ-3048). Criterion 2 is closed by
`bind_prints_every_stage_for_a_racket_collection`, `chicken_binds_no_command`
and `two_collections_bind_one_command_that_runs_each_in_its_directory`
(REQ-2350). Criterion 3 is closed by
`the_implementation_is_detected_before_any_stage_binds` (REQ-2446) and by
`bind_prints_every_stage_for_a_racket_collection`, which holds that the only
tool bound is the one `info.rkt` configures (REQ-2420). The
`check_reports_a_stage_that_writes_bytecode_into_the_tree` test closes REQ-2442,
and `status_names_the_generated_files_and_the_test_discovery`,
`check_reports_bytecode_nobody_ignores_or_a_repository_tracks` and the crate
test `tsk_5135_criterion_3_every_language_pack_states_its_generated_files`
close REQ-2450. Criterion 4 is closed by `tools/check_docs.py`. No criterion
rests on judgement.

`paw ready implement TSK-5115` refused only because TSK-5110, the earlier pack
in the chain, isn't done on this branch.

Every stage passed in pull request #1077.

## Left alone

The other languages in the order, each its own task, and any binding the
pack's own document doesn't state.
