---
id: RES-0369
artifact: research
status: approved
revised: 2026-10-31
elaborates: RES-0346
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A decision or a defect can carry its own plan, so epics and tasks can retire into an archive

## Summary

Of 115 epics and 394 tasks, none is open, and since ADR-2860 every epic has
already been one pull request, so the epic and the task no longer divide any
work: they repeat what the decision says. The owner asked to remove both, make
a decision or a defect the one unit of work, with one issue and one pull
request, and move the plan into the record. The record can take this, with
three catches. Twelve closed requirements have no done decision behind them, so
closure can't move to decisions alone. The closure of a defect is derived from
task marks, so a defect needs a stored `done`. A repository with open tasks has
open issues, so an upgrade has to place that work and may not close it silently.

The document covers the record, `paw`, `meow-github` and how a repository
moves to the new form. It doesn't cover the wording of each step's prompt.

## The question

Can the decision and the defect replace the epic and the task as the unit of
work, and what happens to the records and the issues that exist?

The assumption behind the question is that the task carries nothing a decision
can't. A task holds acceptance criteria, a dependency order, its own issue and
evidence. "How I will know it was realised" already holds the criteria, an
ordered plan holds the order, and the merged pull request holds the evidence,
because ADR-2300 keeps no verification in the record. What has no replacement
is parallel work inside one decision: a plan is one branch. A decision too big
for one branch is two decisions, which is the valve REQ-4406 already names for
an epic.

## Method

I counted the record with `paw count`, `paw status --brief` and a script over
the front matter of `project/` as of pull request 1133 on 2026-10-31. I read
`crates/meow/src/record.rs`, `crates/meow/src/github/project.rs`,
`crates/meow/src/github/sync.rs`, `crates/meow/src/runloop.rs` and
`plugins/meow-flow/lib/layout.toml`, the onboard and init skills, and the
decisions ADR-2300, ADR-2310 and ADR-2860. I listed the repository's open issues
and pull requests with `gh`, and read GitHub's description of the update call. I
tested no repository other than this one, so the open-work path below is
reasoned from the code and has no measured case here.

## Findings

### The epic and the task divide nothing any more

The record holds 115 epics, 114 done and one stored `approved` with every task
finished, and 394 tasks, 384 done and 10 withdrawn (`paw count`). RES-0346 put
the mean at 2.7 tasks to an epic, and ADR-2860 made all of them one pull
request, so a task is a group of commits in the review of its epic. 28 of the
394 tasks already skip the epic through `realises`, and 47 sit directly on a
defect (front matter count), so the method has been dropping this level one
case at a time.

### Every task has a mapping and almost no issue is open

All 394 tasks carry `issue:`, 268 carry `projected:` and 179 carry `tracked:`.
Three issues are open on the repository: the dependency dashboard (748), a
free-form report (599) and BUG-1360 (716). No open issue maps to a task, and
82 of 83 defects already name their issue on the defect. A defect is therefore
already one record, one issue, and its reference shape holds for a decision.

### Closing a requirement can't move to decisions alone

1,105 of the 1,141 requirements in force are closed through a task's `closes`.
Twelve of those are addressed by no done decision: REQ-1364, REQ-1366, REQ-1370,
REQ-1390, REQ-1398, REQ-2562, REQ-2570, REQ-2584, REQ-2586, REQ-2588, REQ-2824
and REQ-3183. If closure read only decisions, these twelve would reopen though
their work landed. The archived tasks have to keep counting.

### A defect's closure and a decision's state hang on task marks

`defect_open` reads the marks under a defect's `## Tasks` and the wording of
`## Closed by`, and a defect has no stored `done` status. ADR-1600 is stored
`approved` while its one epic is finished, so its completion is only derived.
With the marks gone, both need a stored state, and only code that still reads
the old marks can compute it once.

### Moving the files breaks nothing frozen

Links to `tasks/` and `epics/` paths appear 113 times in `project/README.md` and
3 times in `plugins/meow-flow/README.md`, both living. No frozen record links to
those paths, though a few name them in prose. Identifiers are cited from 69
defects, 34 decisions, 23 specifications and 12 research documents, so `paw`
must go on resolving `TSK-` and `EPC-` or every citation dangles.

### The reach of the change is one program, two modules and the method's text

`record.rs` names epic or task about 270 times and `github/project.rs` and
`github/sync.rs` about 80 times, while `runloop.rs` names them only in a list of
what a step may write. The hits in `gotask.rs`, `mise.rs` and `runner.rs` are
task runners, which share the word and stay. Forty-three test files, seven
skills, five templates and 23 specifications name epic or task, and `packages/`
repeats the method's skills and templates for Pi.

### 139 requirements mention the words, and 79 contradict the new form

Of the 139 requirements in force that use "task" or "epic", about 30 are about
task runners. I read each remaining one: 79 state the old decomposition itself, such as
REQ-0252, and the others use the word in passing, such as REQ-1026.

### The profile names the epic step

`.meowpaw/profile.toml` lists `epic` under `[unattended] gates`, so a repository
that upgrades its record and keeps that line declares a gate that doesn't exist.

### GitHub distinguishes a closed issue that wasn't done

The update call takes `state_reason` with `completed` or `not_planned`, and the
call also takes the body, so one write can both explain and close. The request
layer already allows that call.

## Comparison

| Option                                      | Better at                                  | Why it falls short                                                      |
| ------------------------------------------- | ------------------------------------------ | ----------------------------------------------------------------------- |
| Keep epics and tasks                        | Parallel work, per-task issues             | Two records for one review, and a third file for one plan               |
| Drop only the epic                          | Smallest change                            | Tasks keep their issues, so one pull request still closes several       |
| Delete the old records                      | Least to carry                             | History moves to git, and 138 citing records dangle                     |
| Archive them, read-only and citable         | Keeps closure and citations with no writes | `paw` keeps a small read of two retired kinds for as long as they exist |
| Keep the old form working beside the new    | No forced upgrade                          | Every rule runs twice, and nothing retires                              |

## The case against one record for everything

A plan inside the decision mixes what was decided with how it gets done, and
REQ-2904 kept those apart so a design wasn't moved into a plan unreviewed. A
plan also changes as the work teaches, where a decision freezes. So the plan
has to be the one section of an approved decision that stays editable until
the decision is done. Without that, the first wrong step forces an amendment,
and people stop writing plans that say anything.

## Conclusions

1. The method has six steps, research, requirements, design, spec, implement
   and review, because the decision carries the plan (Findings: the epic and
   the task divide nothing).
2. A decision or a defect is the one unit of work, and each maps to one issue,
   one branch and one pull request, because a defect already has that shape
   (Findings: every task has a mapping).
3. A decision that addresses work, and a defect that enters at implement, carry
   an ordered plan an implementer can follow with no conversation, and the plan
   stays editable until the record is done (The case against one record).
4. A decision or defect too large for one reviewable pull request is split
   before its work starts (The question).
5. No new epic or task can be written, and the existing ones stay readable and
   citable in an archive under the record's root, unchanged (Findings: moving
   the files breaks nothing frozen; Comparison).
6. A requirement closes when a done decision addresses it or a done archived
   task closes it, so that closed work stays closed (Findings: closing a
   requirement can't move to decisions alone).
7. Decisions and defects store `done`, and the upgrade computes that state once
   from the old marks, because nothing else can afterwards (Findings: a
   defect's closure hangs on task marks).
8. A command beside init and onboard moves a repository to the new form,
   previews first, and can be run again with nothing to do (Findings: the
   profile names the epic step).
9. The upgrade folds each open task into the `## Plan` of the decision or
   defect that authorises it, and an open task with no live authority is
   archived and reported, never dropped (Findings: every task has a mapping).
10. Issue changes run after the record's pull request merges, so an issue never
    points at a plan that isn't on the trunk yet. A done or dropped task's open
    issue closes as completed or not planned, a folded task's closes as not
    planned and names its successor, and an orphan's and an unmapped issue stay
    open (Findings: GitHub distinguishes a closed issue).
11. A repository in the old form gets one finding naming the upgrade from every
    check, because a second working form would never retire (Comparison).
12. Requirements that state the old decomposition are withdrawn and replaced in
    the same change, and one that uses the word in passing reads as the decision
    or defect carrying the work, so the record stops contradicting itself
    (Findings: 139 requirements mention the words).

## Sources

- `project/` as of pull request 1133, counted 2026-10-31 - every count of records, fields and citations.
- `crates/meow/src/record.rs` as of pull request 1133, read 2026-10-31 - closure, marks, frozen parts and `paw done`.
- `crates/meow/src/github/project.rs` and `crates/meow/src/github/sync.rs` as of pull request 1133, read 2026-10-31 - the mapping of a task to an issue.
- `plugins/meow-flow/lib/layout.toml` as of pull request 1133, read 2026-10-31 - the kinds and their rules.
- `plugins/meow-flow/skills/init/SKILL.md` and `plugins/meow-flow/skills/onboard/SKILL.md` as of pull request 1133, read 2026-10-31 - what the upgrade sits beside.
- `gh issue list` and `gh pr list` on the repository, read 2026-10-31 - the three open issues.
- [REST API endpoints for issues](https://docs.github.com/en/rest/issues/issues#update-an-issue), read 2026-10-31 - `state_reason` and its values.
