---
id: EPC-1710
artifact: epic
status: approved
revised: 2026-09-28
realises: ADR-1800
checked-at: "#625"
---

# A task's dependency says whether it blocks, and only an epic or a defect groups tasks

Realises exactly one authorising record, ADR-1800. The epic is complete when
`paw` waits only on a blocking dependency, reports a draft task whose
dependency line doesn't say whether it blocks, reports a grouping field on a
task, an epic or a defect, and `meow-github project` is shown to group an
issue nowhere.

## Acceptance criteria

Taken from ADR-1800, from its list of how I will know it was realised, before
the tasks below were written:

1. A `paw` fixture shows a draft task whose dependency line reads
   `- TSK-NNNN (not blocking): shares a helper` passing `paw check`, and the
   same draft with a bare `- TSK-NNNN` line, or a line naming two identifiers,
   reported by line under `dependency-declared`.
2. A fixture shows an approved task with a bare dependency line not reported,
   and `paw ready implement` still waiting on it.
3. A fixture shows `paw ready implement` and `paw ready cover` reporting a
   task ready when its only open dependency is marked `(not blocking)`, and
   waiting when the same dependency is marked `(blocking)`; `paw status` names
   the task whose only dependency is not blocking as next.
4. Fixtures show `defect-epic-ordered` reporting a defect's epic whose only
   order between tasks is a task's dependency line marked `(not blocking)`,
   and one whose only order is an epic entry's `depends:` marked
   `(not blocking)`, and accepting each when the marker is `(blocking)`.
5. A fixture shows a task carrying `milestone:` and an epic carrying `parent:`
   each reported by `paw check`, and a task naming `epic:` or `bug:` passing.
6. A `meow-github` test with a stand-in `gh` shows `project` passing no
   `--milestone`, `--parent`, `--project` or `--label` argument, and an issue
   body carrying `(not blocking)` where the task's line does.
7. The task and epic templates in `meow-flow` and the task and epic types in
   `meow-prose` show `(blocking)` and `(not blocking)` and no longer say a
   convenience isn't a dependency, the epic step holds the new rule beside E6,
   SPC-1090 states that readiness waits only on blocking dependencies, and
   SPC-1070 names `dependency-declared`.
8. A fixture shows a defect carrying `milestone:` reported by `paw check`.
9. Every requirement ADR-1800 addresses, REQ-1358 and REQ-3320, lands in
   exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 [P] TSK-2900 make `paw` wait only on a blocking dependency, add
      `dependency-declared`, count only a blocking order in
      `defect-epic-ordered`, and show both markers in the templates, the epic
      step and the `meow-prose` record types
      closes: REQ-1358

- [x] T-002 [P] TSK-2910 forbid the grouping fields on the task, epic and
      defect kinds in `plugins/meow-flow/lib/layout.toml`, and show in a
      `meow-github` test that `project` groups an issue nowhere
      closes: REQ-3320

Neither task waits on the other. Both raise `meow-flow`'s minor version and
its README's `describes`, so whichever lands second takes the next minor
version above the first. That shared version is a convenience, and `paw`
can't yet record it as one: until TSK-2900 lands, every `TSK-` identifier
under a task's `## Depends on` blocks, so neither task names the other there.

## Verified

I checked this under #625 on `main` after #670, gathering the evidence there
rather than carrying it over from the tasks. `meow-verbs run format lint check
test build` exits 0 on this change's own tree, each verb passed, and the
results are kept in `project/evidence/`, as the pull request cites.
`python3 -m unittest test_record` in `plugins/meow-flow/tests` runs 209, OK,
and `python3 -m unittest test_github` in `plugins/meow-github/tests` runs 14,
OK. The ten `Dependencies` and six `Grouping` fixtures run 16, OK. Every
criterion is met:

| Criterion                                                                                                                                     | Evidence on `main` after #670                                                                                                                                                                                                                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. A declared line passes, and a bare line or one naming two tasks is reported under `dependency-declared`                                    | `Dependencies.test_a_declared_dependency_passes`, `test_a_bare_dependency_in_a_draft_is_reported` and `test_a_line_naming_two_tasks_is_reported` pass                                                                                                                                                        |
| 2. An approved task's bare line isn't reported and still blocks                                                                               | `Dependencies.test_an_approved_bare_dependency_still_blocks` passes                                                                                                                                                                                                                                          |
| 3. `ready implement` and `ready cover` pass a `(not blocking)` dependency and wait on a `(blocking)` one, and `status` names the task as next | `Dependencies.test_a_not_blocking_dependency_leaves_the_task_ready`, `test_a_blocking_dependency_makes_the_task_wait` and `test_status_names_a_task_whose_only_dependency_does_not_block` pass                                                                                                               |
| 4. `defect-epic-ordered` counts only a blocking order                                                                                         | `Dependencies.test_a_not_blocking_order_does_not_order_a_defects_epic` and `test_a_blocking_order_orders_a_defects_epic` pass                                                                                                                                                                                |
| 5. `milestone:` on a task and `parent:` on an epic are reported, and `epic:` or `bug:` on a task passes                                       | `Grouping.test_a_task_with_a_milestone_is_reported`, `test_an_epic_with_a_parent_is_reported` and `test_a_task_under_its_epic_or_defect_passes` pass                                                                                                                                                         |
| 6. `project` passes no grouping argument and the body carries `(not blocking)`                                                                | `Project.test_project_groups_an_issue_nowhere` passes against the stand-in `gh`                                                                                                                                                                                                                              |
| 7. The templates, the epic step, the `meow-prose` types and both specifications show the markers                                              | `Dependencies.test_the_templates_and_the_epic_step_show_both_markers` passes; `grep` finds both markers in `plugins/meow-prose/skills/writing/types/record/task.md` and `epic.md`, rule E7 in the epic step, the rule in SPC-1090's section "The gate", and `dependency-declared` in SPC-1070's layout table |
| 8. `milestone:` on a defect is reported                                                                                                       | `Grouping.test_a_defect_with_a_milestone_is_reported` passes                                                                                                                                                                                                                                                 |
| 9. REQ-1358 and REQ-3320 each land in one closed task                                                                                         | `paw show` derives REQ-1358 as closed by TSK-2900 and REQ-3320 as closed by TSK-2910, each done in EPC-1710                                                                                                                                                                                                  |

### Judgement

Criterion 7's `meow-prose` half rests on reading the two record types, because
`meow-prose` ships no test directory and a check in `meow-flow` reading its
files would cross the `standalone` boundary. `Project.test_project_groups_an_issue_nowhere`
passed before TSK-2910's work, because `project` already sent only a title and
a body, so it guards against a regression rather than having been seen to
fail; it would fail if a call carried any of the four flags. Every other
check named above failed first, in `project/evidence/9c59e364c42a.txt` and
`project/evidence/27c4d319f7ce.txt`.

### Postponements

ADR-1800 postpones no requirement.

## Coverage

ADR-1800 addresses two requirements, and each lands in one task. REQ-1358
lands in TSK-2900, because the marker, the program reading it and the rule
asking a draft for it are what let an author declare a convenience as not
blocking, and the templates and prompts are where the author is told to.
REQ-3320 lands in TSK-2910, because the forbidden fields hold the record half
of the obligation and the `meow-github` test holds the tracker half.

Criteria 1 to 4 and 7 close in TSK-2900, and criteria 5, 6 and 8 in TSK-2910.
Criterion 6's body marker needs no change to `meow-github`: `project` copies
the task's `## Depends on` section into the body as the task writes it, so
the test holds whichever task lands first. Criterion 7's specification half
is already met, because SPC-1090 and SPC-1070 were updated in the change that
approved this epic. Criterion 9 is the verify step's.

The smallest set that tests the decision is TSK-2900 alone: with it, a task
whose only open dependency is marked `(not blocking)` is ready, which is what
REQ-1358 changes in practice. Before either task is finished, one thing can
be measured: `paw ready implement` on a fixture task whose only open
dependency reads `(not blocking)` exits 1 today and must exit 0.

## Not covered

- Projecting a blocking dependency onto GitHub's blocked-by relation, and the
  epic onto a tracker grouping (REQ-1364), which ADR-1800 leaves to a tracker
  decision.
- Checking the `[P]` mark against the dependencies, and an epic entry's
  marker against the task's own line, which ADR-1800 names as still not
  working.
- A grouping written under a field name the forbidden list doesn't hold, such
  as `group:`, which ADR-1800 leaves unreported.
- The user-facing pages beyond each unit's README `describes`: the document
  step updates them once both tasks are done, from ADR-1800's consequences.
