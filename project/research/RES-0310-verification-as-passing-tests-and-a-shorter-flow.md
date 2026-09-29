---
id: RES-0310
artifact: research
status: approved
revised: 2026-09-29
elaborates: RES-0309
---

# The flow spends its effort writing records, and verification repeats in prose what the checks already settle

## Summary

The method's cost is the volume of records a session writes, not the time a
pull request waits: 150 merged pull requests took a median of 3.5 minutes from
opening to merge, while the cover step's eleven pull requests added 8,677
lines over 28 hours, 4,044 of them in two record changes before any code. In
the last 100 commits, authored records outgrew code by 1.4 to 1, and kept
evidence added as many lines again. Verification then stalled on a criterion
nobody could meet, and a reviewer found four defects in a record `paw check`
had passed. The owner asked for no verification record at all: a requirement
is closed when the task or epic that names it closes, and the gate's tests are
what a task has to pass to close. This note compares four ways to shorten the
flow, names what each would have to replace, and lists the approved records
that closing requirements with their tasks would withdraw. It also compares names for `meow-verbs`, which the owner finds
unclear. It doesn't decide between the options, and it doesn't cover how the
steps from research to the decision could shrink.

## The question

Which parts of the flow can go, or become a program's work, while the trace
from a requirement to its check survives?

The question assumes that the flow is slow because of its gates. The first
findings test that assumption, and they don't support it: a pull request
merges in minutes, so the cost sits in what is written before it opens. The
second assumption is that verification, review and kept evidence each earn
what they cost, which the later findings test.

## Method

I ran each command below on 2026-09-29 at `main` after #586, and read
each file named. I read no measurement from another repository.

- `git log -100 --numstat --format= origin/main`, summing added lines by path,
  with `project/**/README.md` counted as generated, because `paw index --write`
  writes their index blocks, and `project/evidence/` counted apart.
- `git log --since=2026-09-22 --format=%s origin/main`, counting commit types.
- `gh pr list --state merged --limit 150 --json title,createdAt,mergedAt`, for
  the time from opening to merge. The 150 span 2026-09-27 to 2026-09-29.
- `gh pr view` on #593, #615, #619, #620, #629, #647, #653, #658, #678, #744
  and #745, for the cover step's timeline and size.
- `wc -l` on ADR-1620, EPC-1580 and its three tasks.
- `paw status`, `paw ready verify EPC-1580` and `meow-verbs status`.
- A loop over `project/evidence/*.txt` running `git cat-file -e <tree>`.
- A count of tasks under each epic, and of records carrying
  `## Open review findings`.
- `paw find`, and a read of each requirement and decision cited below.
- `crates/meow/src/record.rs`, lines 2518 to 2580, for how `paw ready
implement` reads a Cover's failing run.

I couldn't obtain how long a session spends writing a record before its pull
request opens, because nothing records when a session starts one. The
timeline of the cover step's pull requests stands in for it. The reviews the
method dispatches are not kept, so I couldn't count them. The 27 records
carrying `## Open review findings` are a floor, since a review that found
nothing leaves no section.

## Findings

### A pull request merges in minutes

The 150 most recent merged pull requests took a median of 3.5 minutes from
opening to merge, and 90% took under 18.6 minutes. By type the medians are
1.1 minutes for `spec`, 1.3 for `chore`, 4.2 for `feat` and 9.5 for `fix`.
Waiting on a gate is not where the flow spends its time.

### The cover step took eleven pull requests and 8,677 lines over 28 hours

The cover step's pull requests ran from #593, opened 2026-09-28 14:08 UTC,
to #745, merged 2026-09-29 18:36 UTC. They added 8,677 lines:

| Pull request | Change                             | Lines added |
| ------------ | ---------------------------------- | ----------- |
| #593         | `spec`: the requirements           | 1,885       |
| #615         | `spec`: the decision and the epic  | 2,159       |
| #619         | `chore`: the issues                | 169         |
| #620         | `feat`: the gate                   | 966         |
| #629         | `feat`: the prompts                | 736         |
| #647         | `fix`: a Cover path                | 540         |
| #653         | `fix`: an unnamed criterion        | 572         |
| #658         | `feat`: status and the driver      | 442         |
| #678         | `fix`: a criterion naming no check | 1,203       |
| #744         | `docs`: the README                 | 4           |
| #745         | `docs`: `llms.txt`                 | 1           |

The two record changes before any code, #593 and #615, added 4,044 lines,
which is 47% of the total. Three of the eleven fix the change itself. The
record that plans it is 895 lines: ADR-1620 at 280, EPC-1580 at 133, and
TSK-2530, TSK-2540 and TSK-2550 at 210, 127 and 145. Its verification hasn't
landed.

### Authored records outgrow code, and kept evidence doubles them

In the last 100 commits, `crates/`, `plugins/` and `tools/` gained 18,224
lines. `project/` gained 61,602: 25,011 authored, 5,239 generated into the
index READMEs and 31,352 of kept evidence. Authored records alone come to 1.4
lines for each line of code. Counts are added lines only.

### Two commits in five are `spec`

Since 2026-09-22 the trunk took 362 commits: 152 `spec`, 131 `feat`, 48 `fix`,
25 `chore`, 4 `docs` and 2 `feat!`, so 42% of them moved the record and
shipped no capability.

### `paw status` can't see the document step done

After #744 and #745 merged, `paw status` still printed `next: document, then
verify EPC-1580`, and `paw ready verify EPC-1580` exited 0 with `ready`. The
document step writes no record, so nothing tells `status` it ran, and the line
names a step already done for as long as verification waits.

### A criterion that broke an existing rule stopped verification

Criterion 9 of EPC-1580 asks for a kept run of `/meow-flow:run` "on the next
epic this repository implements". Epics implemented after #658 went through
cover and implement without keeping one, so the criterion could no longer be
met, and a session found that by attempting verification. The record already
requires that an acceptance criterion state something the project itself can
bring about, and no program checks it.

### Review found four defects in a record `paw check` passed

`paw check` reported 0 findings on the draft verification of EPC-1580. The
`meow-flow:record-reviewer` agent, given the path alone, reported seven
findings, four marked `fix` and three `preference`. Of the four, two were
mechanical: a table that cites no kept run, and a stale line in
`project/README.md`. A program could hold both. The report isn't kept in the
repository, so the count rests on this session's reading.

### Every record the method writes is reviewed by an agent

Step 7 of the method skill dispatches `meow-flow:record-reviewer` on each
record written, and rules M19 to M23 run up to two rounds and write what stays
open into the record. So research, each requirement, each decision, each epic
and each task passes a review, and 27 records carry `## Open review findings`.

### Kept evidence still resolves, and the cover gate depends on it

All 577 tree ids named in `project/evidence/*.txt` resolve with `git cat-file
-e` in this clone. This clone keeps its branches, so a fresh one might lose
trees from deleted branches, which I didn't test. Rule V12 in
`steps/verify.md` speaks of commit hashes, not trees. `paw ready implement`
refuses a Cover whose `Failing run` isn't a file kept in the repository
(`record.rs` line 2525 on), as the record requires: "The run in which the
cover step's checks fail MUST be kept". Removing kept evidence removes what
the cover gate reads.

### The record keeps a verified state apart from a closed one

The record requires that a requirement whose status is verified have at least
one passing check naming its identifier, and that checking the record report
one that has none. `paw status` counts 765 requirements verified and 19
"closed and not yet verified", so a requirement moves through two states after
its task is done, and the second needs the epic's `## Verified` section with
its `checked-at`, which a session writes by hand.

### Postponed requirements are revisited only at verification

ADR-1330 says a deferred requirement is revisited when its epic is
verified, and rule V13 in `steps/verify.md` carries that out. `paw status`
reports 23 postponed requirements. Nothing else in the chain looks at them.

### A passing check can leave a requirement unmet

RES-0309 records four of 755 requirements derived as verified that later
defect records found unmet, each because the check couldn't fail or an input
went unexercised. It found those four through ordinary work and says the case
for a second reader rests on the bias of a model judging its own output. I
haven't re-read RES-0309's own sources.

### A quarter of the requirements have no check

`paw status` reports 1,107 requirements in force: 495 declare a static check,
548 a behavioural one, 22 an evaluation and 42 a judgement, 30 of those by an
agent. 273 are checked by nothing. Kinds are declared per ADR-1510, so a
static check, a program reading files, counts as a check as much as a test.

### Seventeen of 70 epics group one task

The count over `project/epics/` gives 70 epics, 17 of them with a single task.
A task's front matter names an `epic:` or a `bug:`, the record forbids any
other grouping, and ADR-1310 projects an epic's tasks onto issues. So a decision one
task realises still gets an epic to hold that task.

### The cover step's checks already land on the task's branch

The record requires the cover checks to land in a commit of their own before
any commit that implements the task, and each to be seen to fail first. Neither requires a pull request of its own. The lanes in this session
committed the failing checks as the first commit of the task's branch, for
example `chore: add the failing checks for TSK-2950` on
`feat/tsk-2950-budgets-cover`. So a commit on the branch, where the checks fail
and the implementation is absent, can show what a kept run file shows today.
`paw status` still names `cover` and `implement` as two steps.

### Two pages disagreed with the chain after it changed

After the cover step landed, the root `README.md` named nine steps in three
places and `llms.txt` once, and `plugins/meow-flow/README.md` named ten. The
epic listed the pages by hand, and nothing checks a step count.

### The unit that runs the checks is named for its grammar

`meow-verbs` runs the commands a repository declares for `format`, `lint`,
`check`, `test` and `build`, and reports an undeclared one as unresolved. Its
page and its plugin description call these "verification verbs", and the
profile holds them in a `[verbs]` table. "Verb" describes how the commands are
named, not what the unit does for a reader, who wants their checks run. The
name appears 1,693 times in the repository, 577 of them in kept evidence and
most of the rest in frozen records, and in about 20 live files: the unit
itself, the crate, four tools and their tests, the marketplace, the profile,
two pages under `docs/` and three other units' pages. The harness has renamed
a unit before, `meow-method` to `meow-flow` under ADR-1390, with a stub that
stayed one release, and renamed the verbs themselves under ADR-1410, reading
the old names for one release.

### The owner's instructions of 2026-09-29

The owner said that verification and review of records stall the flow; that
verification is tests, so passing tests mean verified; that no evidence
belongs in the repository; that the verified claim and the skeptic go; that a
requirement is closed by closing the tasks and epics that name it, with no
verification record; that the pull request carrying a task closes the task,
its epic when that was the epic's last open task, and each requirement no open
task or epic still names; that filing a defect against a requirement reopens it;
and
that a decision one task can realise needs one task and no epic; that the
cover step's checks live in the same pull request as the rest of the task; and
that an agent's code review also runs inside the task's pull request, records
nothing, and has its findings fixed in that pull request; that `meow-verbs`
needs a better name; that cover is writing the tests before the code; that a
task or an epic closes any number of requirements and a requirement is closed
by any number of them; that research, requirements, the decision, the epic
and its tasks land in one pull request; that plugins the new chain doesn't
need are removed; and that existing records are rewritten to the new shape,
since that is a change of format and not of data. These come from a
person and not from a finding, and a requirement built on them names
the instruction as its outside source.

## Options

### How to shorten the flow

Each option is put in the terms of the person who would choose it.

1. **Trim the ceremony and keep every step.** Documentation, record marks and
   verification land in the implementing pull request, and derived text is
   generated. It is better at costing nothing in policy. It leaves the prose
   verification and the review of every record, the two costs the owner
   named.
2. **Close a requirement with its task, and keep no verification.** A
   requirement is closed when the task or epic naming it closes, and a task
   closes only by merging with the gate passing. No verdict, `checked-at`,
   kept run or second state after closed is written or derived. It is better
   at removing the stalled step and half of the record's growth, and at
   needing no store for a pass, since the gate runs before the merge. It drops
   the second reader RES-0309 measured, and it trusts that each task's checks
   exercise the requirements it names.
3. **Let a task realise a decision directly.** The decision stays, and a task
   names it with `realises:`; an epic exists only where several tasks need an
   order. It is better at the cost the 17 single-task epics carry, and it
   changes the grouping rule and the tracker projection in ADR-1310.
4. **Review the change, not the record.** An agent reviews the task's code
   inside its pull request, the findings are fixed there, and the review writes
   nothing into the record. Records aren't reviewed by an agent. It is better
   at the effort in M19 to M23 and at keeping a review finding next to its
   fix, and it moves the judgement on records to the person approving the
   pull request.

Doing nothing is better at nothing the findings show, since verification of
EPC-1580 can't pass as the record stands. Dropping the method and keeping only
tests would be fastest, and it loses the trace from requirement to check, the
project's claim, so I drop it.

Options 2, 3 and 4 fit the owner's instructions and each finding, and I lead
with them together.

### What to call the unit that runs the checks

Each name is put in the terms of the person who would pick it.

1. **`meow-checks`.** It says what a reader gets: their checks, run as
   declared. It is better at being understood without the page. It collides
   with the `check` verb, with `paw check` and with `meow-author check`, so
   "check" would name a unit, one of its five commands and two other
   programs.
2. **`meow-gate`.** The constitution already calls `mise run all` the gate,
   and CI runs a job named `gate`, and under option 2 a passing gate is what
   lets a task close. It is better at naming the unit's role in the
   shorter flow. It collides with the method's approval gate, "a gate is a
   stop", which is a different thing in the same documents.
3. **`meow-run`.** It is short and names the act. It collides with
   `/meow-flow:run`, the driver, and says nothing about checking.
4. **Keep `meow-verbs`.** It costs nothing, and "verb" is the term the profile
   contract and the decisions already use. It is better at stability, and it
   keeps the name the owner dislikes.

The concept and the unit can be renamed apart: the `[verbs]` table and the
five names can stay while the unit takes a new name, as `meow-method` became
`meow-flow` without its steps changing. This choice is left to the design
step, which has to weigh the collisions above.

### The case against closing a requirement with its task

RES-0309 found that a check closing a requirement can be one that couldn't
fail, and closing on the task calls such a requirement closed with no reader
to notice. The four unmet requirements were found by ordinary work, so the
loss is a defect found later, not one never found. A defect names the
requirement it violates in `violates:`, so reopening the requirement while the
defect is open puts that finding back in the requirement's state. Closing also says nothing about a requirement whose
task named no check for it, so the cover step, which writes the checks first,
carries the whole weight of the trace from requirement to check.

### The case against letting a task realise a decision

An epic states acceptance criteria before its tasks are written, and a task
realising a decision directly has to carry them itself, so the task template
grows. The tracker projection today groups by epic, so a task with no epic
needs its own projection rule.

## What the options would withdraw or supersede

Options 2 to 4 contradict approved records, which the requirements step has to
withdraw or supersede, and research names none of them by identifier because
it cites no requirement. By what they say, they are:

- the rules that the verification step verifies each task and each epic, and
  that an epic isn't verified merely because its tasks are done;
- the rules that a verified requirement has a passing check naming it, and
  that checking the record reports one that hasn't;
- the rule that documentation comes before verification;
- the rule that a deferred requirement is revisited at verification, and
  ADR-1330;
- the rule that an epic may close with a recorded defect;
- the rules naming ten steps and a committed artifact for each step;
- the rule that the cover step's failing run is kept;
- the rule that a task groups only under an epic or a defect, and ADR-1310;
- the three rules for the skeptic, and ADR-2200;
- ADR-1490, which reviews every record with an agent;
- ADR-1530, ADR-1550 and ADR-1560, which keep evidence in the repository.

## Conclusions

1. A requirement is closed when no open task or epic names it and at least
   one closed one does, and it has no state after closed, because the
   verification written by hand stalled the flow and the owner's instruction
   removes it.
2. The pull request carrying a task closes that task, closes its epic when
   the task was the epic's last open one, and so closes each requirement
   neither still leaves open, with no later pull request, because the cover
   step spent its last pull requests on closing work already done. The
   owner's instruction imposes this.
3. A task closes only when its pull request merges with the gate passing, so
   the tests that settle a requirement run before the requirement closes and
   nothing has to store their result.
4. A requirement no open or closed task names reports as open, because 273
   requirements have no check today and closing must come from a task, never
   from silence.
5. A requirement that an open defect names in `violates:` reports as open
   until the defect's task closes, because a defect is evidence the
   requirement isn't met. The owner's instruction imposes this.
6. The harness reports a check that names a requirement and can't fail, where
   a program can tell, because the four unmet requirements in RES-0309 each
   had one.
7. The repository holds no kept run output, because kept evidence added as
   many lines as every authored record together. The owner's instruction
   imposes this too.
8. The cover step's checks land in the task's own pull request, as its first
   commit, and that commit is where they are seen to fail, without a kept run
   file, because the implement gate reads a kept file that conclusion 7
   removes, and the record already orders the commits. The owner's instruction imposes
   the single pull request.
9. A change lands its code, its documentation and its record marks in one
   pull request, because the cover step spent two of eleven pull requests on
   four changed lines of documentation.
10. A step that writes no record leaves `paw status` able to tell it ran,
    because `status` named the document step after it was done.
11. Postponed requirements are revisited at a point the chain still reaches,
    because verification was the only one and 23 are postponed.
12. No agent reviews a record, because every record the method writes is
    reviewed today and the owner named that review as a stall. The owner's
    instruction imposes this.
13. An agent reviews a task's change inside its pull request, and its findings
    are fixed in that pull request and written nowhere else, because a finding
    kept beside its fix needs no record. The owner's instruction imposes
    this.
14. A requirement settled by judgement names the person or agent who judges,
    because 30 name an agent today and conclusion 12 removes the review that
    judged them.
15. A program refuses an acceptance criterion that names work the project
    can't yet bring about, at approval, because the record required it and
    criterion 9 of EPC-1580 broke it unnoticed.
16. A decision one task realises has that task and no epic, because 17 of 70
    epics group one task. The owner's instruction imposes this.
17. A number a living page states about the chain, such as the step count,
    comes from one source or is checked against it, because two pages carried
    the old count after the chain changed.
18. A unit's name says what it does for the reader
    without its page, and a rename keeps the old name working for one release,
    because the owner finds `meow-verbs` unclear and the harness renamed
    `meow-method` and the verbs that way before. The owner's instruction
    imposes the rename.

## Sources

- Read 2026-09-29: `git log -100 --numstat` and `git log --since=2026-09-22`
  on `origin/main` after #586 - record, evidence, code and commit-type
  volume.
- Read 2026-09-29: `gh pr list --state merged --limit 150` and `gh pr view` on
  the eleven pull requests named - merge times and the cover step's timeline.
- Read 2026-09-29: ADR-1620, EPC-1580 and its three tasks - the cover step's
  footprint and criterion 9.
- Read 2026-09-29: `paw status`, `paw ready verify EPC-1580` and `meow-verbs
status` - the gate outputs and the counts.
- Read 2026-09-29: `project/evidence/*.txt` with `git cat-file -e` - the 577
  trees.
- Read 2026-09-29: `crates/meow/src/record.rs` after #586, lines 2518 to
  2580 - how the implement gate reads a Cover's failing run.
- Read 2026-09-29: `plugins/meow-flow/skills/method/SKILL.md` and
  `steps/verify.md` in `meow-flow` 0.39.5 - step 7, M19 to M23, V12 and V13.
- Read 2026-09-29: the requirements in `project/requirements/` on verified
  status, closing, grouping, acceptance criteria and the cover step - the rules in
  force.
- Read 2026-09-29: ADR-1310, ADR-1330, ADR-1390, ADR-1410, ADR-1490,
  ADR-1530, ADR-1550, ADR-1560 and ADR-2200 - the decisions affected and the
  earlier renames.
- Read 2026-09-29: `plugins/meow-verbs/README.md` and its `plugin.json`, and
  `grep -rIo meow-verbs` over the repository - the unit's name and footprint.
- Read 2026-09-29: RES-0309 - the unmet requirements and the case for a
  second reader.
