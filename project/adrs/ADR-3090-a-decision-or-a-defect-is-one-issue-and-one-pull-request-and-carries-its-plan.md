---
id: ADR-3090
artifact: adr
status: approved
revised: 2026-10-31
issue: 1134
addresses:
  [
    REQ-3666,
    REQ-3668,
    REQ-3670,
    REQ-3672,
    REQ-3674,
    REQ-3676,
    REQ-3678,
    REQ-3680,
    REQ-3682,
    REQ-3684,
    REQ-3686,
    REQ-4002,
    REQ-5300,
    REQ-5302,
    REQ-5304,
    REQ-5306,
    REQ-5308,
    REQ-5310,
    REQ-5312,
    REQ-5314,
  ]
supersedes: [ADR-2860]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 3090. A decision or a defect is one issue and one pull request, and carries its plan

## Decision

Epics and tasks retire. A decision or a defect is the one unit of work: one
record, one issue, one branch and one pull request (REQ-3668). A defect stays a
record of its own, on the same level as a decision. The chain becomes six steps
(REQ-3666):

```text
research -> requirements -> design -> spec -> implement -> review
```

The record carries its own plan. A decision that addresses a requirement holds a
`## Plan` of ordered steps, and so does a defect that enters at implement
(REQ-3672, REQ-3674). "How I will know it was realised" stays where a task's
acceptance criteria were. A record too large for one pull request is split
before its work starts (REQ-3670). The plan stays editable until the record is
done, because the work corrects it, and it freezes then (REQ-3676). Each step
keeps the order a task had: tests that fail in a commit of their own, then the
change, its documentation and its record marks (REQ-3682).

Decisions and defects store `done`, which `paw done <record> --pr <number>`
sets in the pull request that completes the work, adding `pr:` to the front
matter (REQ-3678). A requirement closes when a done decision addresses it or a
done archived task closes it, and no approved decision still in work addresses
it (REQ-3680). A postponed requirement closes only with a decision later than the
one that postponed it, or an earlier decision would read as closing it. `paw ready implement`, `paw brief` and `paw status` take a
decision or a defect. `meow-github project` and `sync` map one record to one
issue, with `issue:`, `projected:` and `tracked:` on the record (REQ-4002), and
the pull request closes that issue.

A requirement that states the old decomposition is withdrawn in this pull
request and names its replacement. One that says task or epic in passing, and is
still true, reads as the decision or defect carrying the work (REQ-3686).

### The upgrade

`/meow-flow:upgrade` sits beside init and onboard (REQ-5300). `paw upgrade`
previews, and `paw upgrade --write` changes the tree (REQ-5302):

1. It moves `epics/` and `tasks/` under `archive/`, each file unchanged
   (REQ-5304). `paw` reads the archive so `TSK-` and `EPC-` still resolve, and it
   refuses a new one (REQ-3684).
2. It stores `done` on each decision and defect the old marks derive as complete
   (REQ-5310), because nothing can compute that once the marks are archived.
3. It adds each open task as a step of the `## Plan` of its live authority,
   naming the archived task, and writes `folded-into:` on the archived copy
   (REQ-5306).
4. It leaves an open task with no live authority in the archive with no
   `folded-into:`, and reports it as needing a decision (REQ-5308).
5. It removes `epic` from `[unattended] gates` (REQ-5312).

An upgrade run on a record already in that form says so and changes nothing
(REQ-5314). Every other `paw` command on a record in the old form reports one
finding that names the upgrade, because a second working form would never retire.
A template the repository overrides under `.meowpaw/templates/` for a retired
kind is reported and left alone, because it is the repository's own file.

### Open tasks and issues

Issues change after the record's pull request merges, so an issue never points at
a plan that isn't on the trunk. `meow-github upgrade` runs then, previews with
`--check`, and reads the archive. It writes one call for each issue, prepending
the notice to the body and setting the state together, so an interrupted run
leaves no issue half changed:

| Archived task                     | Its issue is open                                                                          | Its issue is closed            |
| --------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------ |
| Done                              | Closed as `completed`                                                                      | Left alone                     |
| Withdrawn, rejected or superseded | Closed as `not_planned`                                                                    | Left alone                     |
| Open, with `folded-into:`         | The record's issue is created first, then this one is closed as `not_planned`, naming it   | Left alone, and reported       |
| Open, with no `folded-into:`      | Left open, and reported as needing a decision                                              | Reported as needing a decision |

An issue that maps to no task is the repository's own and stays as it is. A
defect's issue stays open and stays its issue. The command lists each open pull
request whose title or body names a folded task and changes none of them, because
those branches are somebody's work: they rebase, and move their plan to the
record by hand.

Once this is accepted, a person gets one decision or defect, one issue and one
pull request, and an existing repository has one supported way to get there.
What still doesn't work: parallel work inside one decision. Two parallel streams
are two decisions.

## Why

Every epic has been one pull request since ADR-2860, 114 of 115 epics are stored
done, and 75 of 394 tasks already skip the epic, so these records divide no work
and repeat the decision (RES-0369). A defect already has the target shape, with
its own issue on its own record (RES-0369). Archiving keeps closure and citations
true with no write to a frozen record, where deleting would leave 138 citing
records dangling and reopen twelve closed requirements (RES-0369).

The issue step follows the merge because a closed issue naming a plan that was
never merged is a dead end, and `not_planned` is used so that a task nobody did
never reads as done on GitHub (RES-0369). The owner asked for the removal and for
a defect to stay separate from a decision.

## Alternatives

| Option                                    | Better at                                | Why it lost                                                            |
| ----------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------- |
| Do nothing                                | Costs nothing, and parallel tasks stay   | Three records for one review, and the method keeps growing exceptions  |
| Drop only the epic                        | Smallest change                          | One pull request still closes several issues                           |
| Delete the old records                    | Nothing to carry                         | 138 citing records dangle, and history leaves the record               |
| Keep both forms working                   | No forced upgrade                        | Every rule runs twice, and nothing retires                             |
| Archive, and upgrade by command           | Citations and closure stay true          | `paw` keeps a read of two retired kinds                                |
| Close issues in the upgrade pull request  | One step for the person                  | The issue can name a plan that is never merged                         |

## What it costs

A repository has to run the upgrade before the release's `paw` will pass, and the
release breaks anyone who ignores it, so the unit's release notes carry it. A plan
inside a decision moves design and procedure into one file, and the plan is the
one editable part of an approved decision, so `paw check frozen` no longer holds
it until the record is done. Parallel work inside a decision is gone. `paw` keeps
the archive's read for as long as a repository has an archive, and the upgrade
keeps a small copy of the old marks' rules.

This pull request is large. REQ-3670 would split it, and I accept that once,
because the retirement can't land in halves: each half leaves the record failing
its own check.

## What would reverse it

- Two decisions in a row that a person splits only to run work in parallel.
- A plan that a person reports as unusable because editing it after approval
  changed the decision's meaning.

## Consequences

- ADR-2860 is superseded. ADR-1310, ADR-2300, ADR-2310, ADR-2880 and ADR-2890
  each gain a line naming this decision.
- The requirements step 1 of the plan lists are withdrawn.
- `CLAUDE.md` and 23 specifications change, and `meow-prose` loses its epic and
  task record types.

## How I will know it was realised

1. `paw count` on this repository shows no draft or approved epic or task, the
   same counts of each kind before and after the move, and the same closed
   requirements, with the withdrawals accounted for.
2. `paw new task` and `paw new epic` exit non-zero, and `paw show TSK-2310` prints
   the archived task.
3. A fixture with an open task, an orphan and a closed defect comes out of
   `paw upgrade --write` as this decision says, and a second run changes nothing.
4. `meow-github upgrade --check` over a fixture reports each row of the table, and
   no fixture records a write to an issue with no mapping.
5. `paw ready implement ADR-3090` passes, and `paw ready implement` refuses a
   decision that addresses work and has no plan.
6. `mise run all` exits 0, and `tools/check_unit_copies.py` shows `packages/`
   aligned.

## What this does not settle

- Which repository outside this one upgrades first: no open-task case exists here,
  so that path has only fixtures behind it.
- Generating `packages/` from `plugins/`, which stays a separate question.
- Whether requirements themselves are worth keeping.

## Plan

Issue and pull request are one each, on the branch
`feat/one-record-one-pull-request`. Each step lands tests first where a program
can check it. I chose to keep requirements and the spec step, because the owner
named only epics and tasks.

1. Records: this decision, its requirements and RES-0369, the `Amended by` lines,
   and these withdrawals:
   - REQ-3666 replaces REQ-3638, REQ-4122.
   - REQ-3668 replaces REQ-0239, REQ-0252, REQ-0262, REQ-0264, REQ-0538, REQ-0546, REQ-0660, REQ-0662, REQ-0664, REQ-1360, REQ-3630, REQ-3650, REQ-4400, REQ-4402, REQ-4404, REQ-4408, REQ-4410, REQ-4412, REQ-4414.
   - REQ-3670 replaces REQ-0258, REQ-4406.
   - REQ-3672 replaces REQ-0256, REQ-0260, REQ-0263, REQ-0265, REQ-0301, REQ-0303, REQ-0309, REQ-0323, REQ-2892, REQ-2894, REQ-2896, REQ-2897, REQ-2898, REQ-2900, REQ-2902, REQ-2904, REQ-3106, REQ-3902.
   - REQ-3674 replaces REQ-0354, REQ-0356, REQ-2926, REQ-4000.
   - REQ-3676 replaces REQ-0634, REQ-0635, REQ-0698, REQ-0700, REQ-0702.
   - REQ-3678 replaces REQ-0583, REQ-0585, REQ-0595, REQ-0596, REQ-0692, REQ-3604, REQ-3606, REQ-4600.
   - REQ-3680 replaces REQ-0254, REQ-3600, REQ-3608, REQ-3646, REQ-3648.
   - REQ-3682 replaces REQ-3616, REQ-3618, REQ-3626, REQ-3628, REQ-3640, REQ-3642.
   - REQ-3684 replaces REQ-3652, REQ-4128.
   - REQ-4002 replaces REQ-1350, REQ-1352, REQ-1364, REQ-1376, REQ-1382, REQ-1386, REQ-3320, REQ-4706.
2. Tests: write the failing tests for the archive, closure, `paw done`, `ready`,
   `status`, `brief`, the plan rules and `paw upgrade`, in `crates/meow/tests`, and
   remove the tests of what retires.
3. `paw`: move the two kinds in `plugins/meow-flow/lib/layout.toml` to archived
   ones, add `## Plan` to decisions and defects and `done` to defects, retarget
   closure, `done`, `ready`, `status` and `brief`, replace the task rules with the
   plan rules, and add `crates/meow/src/record/upgrade.rs` holding `paw upgrade`
   and the one copy of the old marks' rules.
4. `meow-github`: map `project` and `sync` to the record itself, add `upgrade`, and
   test it against a fixture of the table above. Retarget the loop's step list.
5. Prompts: rewrite the method skill and its steps, remove `steps/epic.md`, add
   `skills/upgrade`, update route, run, init, onboard, the commit skill, the
   templates and `meow-prose`, in `plugins/` and `packages/` both.
6. This repository: run `paw count`, `paw upgrade --write` as a commit of its own,
   `paw count` again, and regenerate the indexes.
7. Living text: `CLAUDE.md`, `project/README.md`, the specifications, `docs/` and
   the unit READMEs.
8. Close: `mise run all`, an agent's review of the code, then `paw done ADR-3090
   --pr <number>` and the pull request. The merge is the approval.
