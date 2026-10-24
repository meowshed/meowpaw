---
id: TSK-5020
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2550
closes: [REQ-0080, REQ-0086, REQ-0088]
issue: 984
projected: 845934bba1d2
tracked: 355e4a896dbf
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Run the method's steps on a repository with no pack installed

A fixture repository with only the kernel and the method units installed runs
`paw ready`, `paw check` and `meow-checks status` to a result, every verb
reported unresolved and nothing waiting on a pack, as SPC-1080 states under
"What stays optional" and SPC-1090 under "The steps". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository with a profile declaring no verb and no pack's plugin directory reachable, when `meow-checks status` runs, then all five verbs are reported unresolved with their kind and nothing is reported passed (REQ-0086, REQ-0088). Closed by: a test under `plugins/meow-flow/tests/` naming REQ-0088, seen failing first.
2. Given the same fixture with an approved decision, when `paw ready spec` and `paw ready epic` run, then each exits as it would with every pack installed (REQ-0088). Closed by: a test naming REQ-0088.
3. Given a fixture task that produces only a specification change, when `paw ready implement` and `paw check` run, then the task passes through the same gate as one that changes code (REQ-0080). Closed by: a test naming REQ-0080.

## What to do

Build the fixture from the units' own files under a temporary directory, with
no pack's directory on any path the launchers search. Read the method's step
files and confirm none names a pack's command as required, fixing any that
does in the same change.

## Depends on

Nothing.

## Evidence

Criteria 1 to 3 are closed by `plugins/meow-flow/tests/test_no_pack.py`, run
by the `test-flow` task against a fixture installation under a temporary
directory that holds the kernel, the method and `meow-checks` and no pack:
`test_every_verb_is_unresolved_with_its_kind_and_none_passes` for REQ-0086 and
REQ-0088, `test_the_ready_gates_answer_as_they_do_beside_every_pack` for
REQ-0088, and
`test_a_task_that_changes_only_a_specification_passes_the_same_gate` for
REQ-0080. `test_no_step_file_requires_a_pack_command` was seen failing first,
on the two rules of `implement.md` that told a step to run `meow-github sync`
whether or not the command existed. Both trees now say that where the command
doesn't exist the step reports the tracker as unsynced and goes on. The
driven programs are `paw` and `meow-checks`, and a run with a model is left
out, as the task says.

Every stage passed in pull request #PR.

## Left alone

A run with a model, which this repository keeps out of CI, so the fixture
drives the programs the steps call and not the steps' prose.
