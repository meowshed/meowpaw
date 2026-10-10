---
id: RES-0346
artifact: research
status: approved
revised: 2026-10-10
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# An epic holds 2.7 tasks on average, and a pull request for each task and each stage multiplies the gate

## Summary

Of 105 epics, 80 hold two or more tasks and the mean is 2.72, so the rule
"one task, one pull request" opens about three pull requests where one would
carry the same commits. On 2026-10-10 the epic EPC-2760 took four pull requests
and about 25 minutes of gate time. No program holds the rule today, and the
readiness check already treats a dependency marked done in the working tree as
done, so tasks of one epic can be worked on one branch with no change to the
tool. The cost is review size, which the commit skill already bounds by
splitting a branch that has grown past one reviewable change.

The document covers the unit of a pull request, from an epic's research to the
merge of its completed work. ADR-2310 stops that path at the records and holds
the implementation until they merge, and this document asks what that stop is
worth.

## The question

Should one epic, or one defect that carries its tasks, be one pull request,
where today one task is?

The assumption behind the question is that fewer, larger pull requests are
cheaper without being less reviewed. A larger change can be approved with less
reading, which is the reason the commit skill gives for splitting one. The rule
has to keep that bound, or it trades one cost for the other.

## Method

I counted the task lines of every epic in `project/epics/`, as the lines that
begin `- [ ] T-NNN` or another mark, on 2026-10-10. I read where the rule is
stated in `CLAUDE.md`, the method unit's templates and steps, the commit skill
and SPC-1060, and I searched the crate, the hooks and `tools/` for code that
enforces it. I read `unready` and `task_finished` in `crates/meow/src/record.rs`
for how a dependency is judged. I took the gate durations of pull requests 874
to 877 from `gh pr checks`. I did not measure review time, which no tool here
records.

## Findings

### Epics hold 2.7 tasks on average

The 105 epics hold 286 tasks. One epic has none, 24 have one, 30 have two, 26
have three, 14 have four, and 11 have between five and eleven. Eighty epics
hold two or more tasks, and those hold 262 of the tasks.

### The rule costs a gate run for each task

EPC-2760 took the records pull request (874) and three implementation pull
requests (875, 876, 877). Their `gate` jobs took 7:15, 6:19, 6:07 and 5:57, about
25 minutes in sequence, and each needed its own merge before the next task was
ready. One pull request would have run the gate once on the same commits.

### Nothing enforces the rule

Searching the crate, the hooks, `tools/` and the workflows for a check that
refuses a pull request carrying more than one task found none. The rule is
stated in `CLAUDE.md` (the layout table and the principle `own_method_first`),
`plugins/meow-flow/templates/task.md`, the implement step, SPC-1060 and the
commit skill's rule B1.

### A dependency inside the branch is already ready, and an approval is not

`paw ready implement` reports a task's blocking dependency as not done unless
the dependency's mark in the working tree is done, so a second task of the same
epic is ready on the branch once the first is marked. The task's own approval is
read from the trunk: `off_trunk` refuses a task whose record isn't approved
there (REQ-3660), and `paw status` says the task waits on its merge. That
guard is what keeps an epic's implementation out of the pull request that
carries its records, so a full cycle in one pull request has to lift it.

### The commit skill already bounds a large branch

Rule B6 of the commit skill says to split a branch that has grown past one
reviewable change, because review turns into approval past a size. TSK-5271
alone changed 99 files, so an epic of three such tasks could pass that size.

## Comparison

| Option                               | Better at                                            | Why it falls short                                                           |
| ------------------------------------ | ---------------------------------------------------- | ---------------------------------------------------------------------------- |
| One task, one pull request           | Smallest reviews, each task merges and closes alone  | A gate run and a merge for each task, 2.7 times on average                   |
| One epic or defect, one pull request | One gate run, one review of the whole change, atomic | A large epic is approved and not read, and one failing task holds the others |
| Stacked pull requests per task       | Small reviews and the tasks stay ordered             | Tooling for stacks (ADR-2550), and a merge for each, which is the cost above |
| One pull request per step            | Mirrors the chain                                    | Splits one task's tests from its change, which review needs to see together  |

## The case against one pull request for an epic

A reviewer reads a change of three tasks with less care than three of one, and
the commit skill's own reason for B6 says so. A failing task also holds the
other two back, where today they would have merged. The rule therefore needs a
valve: an epic that would not be one reviewable change is split into smaller
epics before its work starts, so that the unit of a pull request stays the unit
of review.

## Conclusions

1. One epic, from its research to the merge of its completed work, is one
   branch, one pull request and one review, with each task a group of commits
   on that branch (Findings: epics hold 2.7 tasks; the rule costs a gate run for
   each task).
2. One defect that carries its tasks, and one task that realises a decision
   with no epic, follow the same rule from its record to the merge of its fix
   (Findings: epics hold 2.7 tasks).
3. An epic whose pull request would not be one reviewable change is split into
   smaller epics before its work starts, and its pull request is never split in
   its place (Findings: the commit skill already bounds a large branch).
4. An epic or a defect with no unmerged dependency opens its pull request
   against the trunk (Findings: nothing enforces the rule).
5. A person who asks for an epic gets its records written through to the tasks
   and implemented on the same branch, with one stop at the pull request, whose
   merge is the one approval, and the work done before that merge is at risk of
   rejection with the decision. A person who asks for the work of an epic whose
   records are already approved gets its tasks implemented on one branch and one
   pull request, and a person who asks only for a decision still gets the
   records alone (Findings: a dependency inside the branch is already ready,
   and an approval is not).
6. The readiness check reads a task's approval from the working tree, so a task
   approved on the epic's own branch is ready to implement (Findings: a
   dependency inside the branch is already ready, and an approval is not).

## Sources

- `CLAUDE.md`, layout table and the principle `own_method_first`, as of pull request 879, read 2026-10-10 - where the rule is stated.
- `plugins/meow-scm/skills/commit/SKILL.md`, rules B1 and B6, as of pull request 879, read 2026-10-10 - the rule and the bound on a large branch.
- `crates/meow/src/record.rs`, `unready` and `task_finished`, as of pull request 879, read 2026-10-10 - how a dependency is judged.
- `project/epics/`, 105 files, as of pull request 879, counted 2026-10-10 - tasks for each epic.
- `gh pr checks` for pull requests 874 to 877, read 2026-10-10 - gate durations.
