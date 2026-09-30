---
id: TSK-2900
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1710
closes: [REQ-1358]
issue: 641
projected: 524fab72b02e
---

# Make `paw` wait only on a blocking dependency, and ask a draft to say which kind each one is

Each line under a task's `## Depends on` says `(blocking)` or
`(not blocking)`, `paw` waits only on the blocking ones, and a draft task that
leaves the marker out is reported. So an author declares a dependency that
exists only for convenience and never leaves it out, as REQ-1358 asks. One
task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a draft task whose dependency line reads
   `- TSK-NNNN (not blocking): shares a helper`, when `paw check` runs, then
   it reports nothing on the line; given the same draft with a bare
   `- TSK-NNNN` line, or a line naming two identifiers, then it reports that
   line by number under `dependency-declared`. Closed by:
   `Dependencies.test_a_declared_dependency_passes`,
   `Dependencies.test_a_bare_dependency_in_a_draft_is_reported` and
   `Dependencies.test_a_line_naming_two_tasks_is_reported` in
   `plugins/meow-flow/tests/test_record.py`.
2. Given an approved task with a bare dependency line on an open task, when
   `paw check` and `paw ready implement` run, then `check` reports nothing on
   the line and `ready implement` exits 1 naming the dependency. Closed by:
   `Dependencies.test_an_approved_bare_dependency_still_blocks`.
3. Given an approved task whose only open dependency is marked
   `(not blocking)`, when `paw ready cover` and `paw ready implement` run,
   then each exits 0 past the dependency, and `paw status` names that task as
   next; with the same dependency marked `(blocking)`, each exits 1 naming it.
   Closed by: `Dependencies.test_a_not_blocking_dependency_leaves_the_task_ready`,
   `Dependencies.test_a_blocking_dependency_makes_the_task_wait` and
   `Dependencies.test_status_names_a_task_whose_only_dependency_does_not_block`.
4. Given a defect's epic whose only order between tasks is a task's
   dependency line marked `(not blocking)`, and one whose only order is an
   epic entry's `depends:` marked `(not blocking)`, when `paw check` runs,
   then `defect-epic-ordered` reports each; with the marker `(blocking)`, or
   an unmarked `depends:`, it reports neither. Closed by:
   `Dependencies.test_a_not_blocking_order_does_not_order_a_defects_epic` and
   `Dependencies.test_a_blocking_order_orders_a_defects_epic`.
5. Given `paw template task`, `paw template epic` and
   `skills/method/steps/epic.md`, when they are read, then the task template
   shows `(blocking)` and `(not blocking)`, the epic template's entry shows
   `depends: TSK-NNNN (not blocking) - why`, neither says a convenience isn't
   a dependency, and the epic step holds a rule beside E6 to declare a
   convenience as not blocking with its reason. Closed by:
   `Dependencies.test_the_templates_and_the_epic_step_show_both_markers`.
6. Given `plugins/meow-prose/skills/writing/types/record/task.md` and
   `epic.md`, when they are read, then each shows both markers and neither
   says a convenience isn't a dependency. Judgement: `meow-prose` ships no
   test directory, and a check in `meow-flow` reading another unit's files
   would cross the boundary the `standalone` check holds, so the reviewer
   reads the two files.
7. Given this change's tree, when `meow-verbs run format lint check test build`
   runs, then each passes. Closed by: the kept evidence of that run.

## What to do

In `crates/meow/src/record.rs`, `depends_on()` returns only the blocking
dependencies, as SPC-1090's section "The gate" states: a line saying
`(blocking)`, or naming a `TSK-` identifier with neither marker, blocks, and
a line saying `(not blocking)` doesn't. `ready cover`, `ready implement` and
`status` read it, so they change with it. `defect-epic-ordered` counts a task's
line only when it blocks, and an epic entry's `depends:` only when it says
`(blocking)` or neither marker.

Add the draft rule `dependency-declared` on the task kind, in the program and
in `plugins/meow-flow/lib/layout.toml`'s `draft_rules`. It reports each line
under a draft task's `## Depends on` that names a `TSK-` identifier without
either marker, and each line naming more than one identifier, with the line's
number. It is a draft rule because the approved tasks naming a dependency
keep the meaning they were approved with (ADR-1140), and none is migrated.
The pattern matches the two markers exactly; a variant such as
`(non-blocking)` is reported as undeclared.

`templates/task.md` shows both forms under `## Depends on`, and
`templates/epic.md`'s entry reads `depends: TSK-NNNN (not blocking) - why` in
place of "a convenience isn't a dependency". `skills/method/steps/epic.md`
gains a rule beside E6: declare a dependency that exists only for convenience
as not blocking, with its reason, and never leave it out. Follow
`meow-author:write` for the step file. The task and epic types in
`plugins/meow-prose/skills/writing/types/record/` say the same.

Raise `meow-flow`'s and `meow-prose`'s minor versions in `plugin.json` and
each README's `describes`, because what an author is told changes. If the
other task of EPC-1710 landed first, take the next minor above it. Write the
checks first, in a commit of their own, and see them fail.

## Depends on

Nothing. ADR-1800 and EPC-1710 are approved.

## Evidence

- Before this change, the test verb's run of
  `plugins/meow-flow/tests/test_record.py` exited 1 with 200 tests and
  `FAILED (failures=10)`, the ten `Dependencies` checks, kept in
  the run under #662, whose output is no longer kept.
- After it, `python3 -m unittest plugins/meow-flow/tests/test_record.py -k Dependencies`
  exits 0 with `Ran 10 tests` and `OK`, and the whole file exits 0 with
  `Ran 200 tests` and `OK`.
- `git diff` of `plugins/meow-flow/tests/test_record.py` against the commit
  that added the checks prints nothing, so the checks are the ones the cover
  step wrote.
- `plugins/meow-flow/bin/paw check` exits 0 with 0 findings under every rule.
- `meow-verbs run format lint check test build` passes each verb, in the
  evidence kept with this change.
- Criterion 6 rests on judgement: the reviewer reads
  `plugins/meow-prose/skills/writing/types/record/task.md` and `epic.md`,
  which show both markers and no longer say a convenience isn't a dependency.
- The Cover's Checks line named the class in prose, and `paw ready implement`
  read each word as a path; the line now names the file alone.
- The change landed in #662, closing REQ-1358.

## Left alone

The grouping fields and the `meow-github` test, which the other task of
EPC-1710 carries. GitHub's blocked-by relation, the `[P]` mark and the
agreement between an epic entry's marker and the task's own line, which
ADR-1800 leaves unsettled. Every approved task's bare dependency line, which
keeps blocking and isn't rewritten. SPC-1090 and SPC-1070, already updated
with the epic. The user-facing pages beyond the two READMEs' `describes`,
which the document step updates.
