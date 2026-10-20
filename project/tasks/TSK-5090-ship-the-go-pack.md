---
id: TSK-5090
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2560
closes: [REQ-2334]
issue: 995
projected: 19f24e67ba4d
tracked: 50010c67404d
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Ship the Go pack

The language pack for Go, named in its own document, is detected from `go.mod`, and resolves
the five verbs from what the repository commits, as SPC-1190 states under
"The supported packs". One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository of the language with its marker in a
   subdirectory, when the pack's `status` runs, then it reports for that
   directory and names the marker, and with no marker it prints
   `unresolved: not a Go repository` and exits 3 (REQ-2334). Closed by: a
   crate test naming REQ-2334, seen failing first.
2. Given a fixture repository of the language, when the pack's `bind` runs,
   then it prints all five verbs, each bound from what the fixture commits or
   printed as unresolved or unbound with a reason (REQ-2334). Closed by: a crate
   test naming REQ-2334.
3. Given the fixture, when the pack's tests run, then they hold the shared
   rules that apply to Go: the race detector on in `test` (REQ-2414), documentation examples run as tests (REQ-2412), a pinned toolchain (REQ-2428) and a supply-chain check that states its reach (REQ-2436). Closed by: the crate tests naming
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

- TSK-5085 (blocking): the packs ship one at a time in the order SPC-1190
  states, so a mistake in one is fixed before the next repeats it.

## Evidence

Criterion 1 is closed by `tsk_5090_criterion_1_status_reports_the_directory_and_names_the_marker` and `tsk_5090_criterion_1_with_no_marker_the_repository_is_not_go` in `crates/meow/tests/go_pack.rs` (REQ-2334). Criterion 2 is closed by `tsk_5090_criterion_2_bind_prints_all_five_stages_bound_or_with_a_reason` and `tsk_5090_criterion_2_a_module_below_the_root_is_reached_with_cd`, which check that each of the five stages is bound or printed unresolved or unbound with a reason, on a bare module, a module with golangci-lint formatters, a module below the root and two modules (REQ-2334).

Criterion 3 is closed, one requirement at a time, by `tsk_5090_criterion_3_the_race_detector_is_on_and_turning_it_off_is_recorded` (REQ-2414), `tsk_5090_criterion_3_only_the_configured_linter_is_bound` (REQ-2420), `tsk_5090_criterion_3_a_pinned_toolchain_is_compared_with_the_installed_one` (REQ-2428), `tsk_5090_criterion_3_a_supply_chain_check_states_its_reach` (REQ-2436), `tsk_5090_criterion_3_a_v1_configuration_is_a_finding` (REQ-2434, REQ-2432) and `tsk_5090_criterion_3_the_page_states_its_generated_files` with the shared layer's `tsk_5135_criterion_3_every_language_pack_states_its_generated_files` (REQ-2450). Criterion 4 is closed by `tools/check_docs.py`, which finds the Go row `shipped` and the unit present.

Part of criterion 3 rests on judgement. REQ-2412, documentation examples run as tests, is held by the same test that checks `test` binds `go test`, and that `go test` runs an example stating its output is a fact of the Go toolchain (RES-0364) that no test here can run without installing Go. The tests were written before the module, and run with the `go` subcommand left out of the dispatch, nine of the ten failed.

Every stage passed in pull request #PR.

## Left alone

The other languages in the order, each its own task, and any binding the
pack's own document doesn't state.
