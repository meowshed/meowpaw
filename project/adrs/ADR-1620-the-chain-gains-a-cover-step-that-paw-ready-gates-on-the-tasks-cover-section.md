---
id: ADR-1620
artifact: adr
status: draft
revised: 2026-09-28
addresses: [REQ-3200, REQ-3202, REQ-3203, REQ-3207, REQ-3216]
postpones: []
supersedes: []
---

# 1620. The chain gains a cover step that paw ready gates on the task's Cover section

## Decision

The method runs ten steps: research, requirements, design, spec, epic, cover,
implement, document, verify and review (REQ-3200). Cover sits between the
epic and the implementation, and runs once for each task: it writes the
task's checks, runs them, keeps the failing run and lands the checks before
any of the implementation. This amends ADR-1130, whose program and skill
carried nine steps, and keeps everything else ADR-1130 decided.

`crates/meow/src/record.rs` holds the steps as one list, and that list gains
`cover` between `epic` and `implement`. Everything that reads the list follows
it: `paw ready` names ten steps in its usage and in its refusal of an unknown
step, and a defect's `enters` accepts `cover`. A defect that enters at `cover`
names the requirement it violates, as one entering at `implement` or `design`
already must, because a check is written only against a requirement in force.

The task template gains a `## Cover` section, which the epic step writes as
`Not yet.` and the cover step fills with four lines:

```text
- Checks: <the path of each check it wrote, or none>
- Failing run: <the path of the kept run in which they failed, or none>
- Landed in: <the pull request, or the commit where nothing squashes, that carried them, or none>
- Judgement: <for each criterion no program can check, its number, a colon and the reason, separated by semicolons; or none>
```

The `Failing run` line keeps the run in which the checks failed, so a reader
can see afterwards that they did (REQ-3207). The `Judgement` line names each
criterion that rests on judgement with its reason, before any implementation,
so an unchecked criterion doesn't read as covered (REQ-3216).

The section is filled when `Landed in` names something, each path under
`Checks` exists, the path under `Failing run` exists, and each number under
`Judgement` carries a reason. It is also filled when `Checks` is `none` and
`Judgement` names every numbered criterion under `## Acceptance criteria`,
because a task whose every criterion rests on judgement has nothing to run.
`Failing run` and `Landed in` then read `none`, because nothing ran and
nothing landed. The program reads the four lines only. Whether the run really
failed, and whether the checks landed before the implementation, are for the
decision on REQ-3206 and REQ-3208.

`paw ready` gates the two steps a task passes through:

- `paw ready cover <task>` exits 0 when the task is approved, its epic or
  defect is approved, and each task under its `## Depends on` is done. That
  is today's gate for `implement`, moved one step earlier.
- `paw ready implement <task>` exits 0 when all of that holds and the task's
  `## Cover` section is filled. It exits 1 naming the missing Cover, or each
  missing line or path, on its own line.

`paw status` prints, for an approved epic with open tasks, `next: cover <task>`
for the first task whose dependencies are done and whose Cover isn't filled,
and `next: implement <task>` once it is. The rest of the line keeps its form,
`(<epic>, <n> of <m> tasks done)`.

`check frozen` treats `## Cover` in an approved task as it treats
`## Evidence`: a part that changes after approval. The cover step writes it
after the epic's approval by design, so without the exemption every cover run
would read as rewording an approved record.

The steps' prompts change with the list. A new file,
`plugins/meow-flow/skills/method/steps/cover.md`, carries the cover step: it
writes checks and never implementation code, runs them, keeps the failing run
with `meow-verbs evidence --keep`, lands them, and fills `## Cover`. The
content rules that REQ-3204, REQ-3206, REQ-3208, REQ-3210, REQ-3211 and
REQ-3213 state come with the decision that addresses them, as ADR-1160 added
each earlier step's rules.
`method/SKILL.md` names ten steps in its body and in its description, which
stays within `budget.toml`'s 500 characters. `steps/epic.md` names cover as
the step that picks it up. Step 3 of `steps/implement.md` changes from writing
the task's checks to running the checks the cover step wrote and seeing them
pass.

Each step's file names, in its role, the committed file its artifact lands in
(REQ-3203), using the kind's name and not a path, because a repository's
profile decides where its record lives:

| Step         | Its artifact lands in                                            |
| ------------ | ---------------------------------------------------------------- |
| research     | a research record's file                                         |
| requirements | one requirement record's file for each obligation                |
| design       | a decision record's file                                         |
| spec         | the specification's file                                         |
| epic         | the epic's file and each task's file                             |
| cover        | the check files, the kept failing run, and the task file's Cover |
| implement    | the changed files, the kept runs, and the task file's Evidence   |
| document     | each user-facing page it changed                                 |
| verify       | the epic's file, its verification and the evidence it cites      |
| review       | nothing in the repository (REQ-0544)                             |

The review step's role already says it writes nothing into the repository,
which REQ-0544 requires and REQ-3203 now leaves out of its obligation.

Cover ends without an approval gate of its own. The checks are reviewed in
the change that carries them, as an implementation is, and a gate here would
cost a person one more approval for every task.

`/meow-flow:run` keeps driving the chain from `paw status` (REQ-3202). Its
skill gains one step: where the step it ran ends without an approval gate, it
runs `paw status` again and continues. So one invocation takes an approved
task through cover and implement to the next gate. ADR-1130 already said the
driver stops at the next approval gate; the skill now says what it does at a
step that has none.

The obligation is new, so the method's rule M15 applies, and this decision
grandfathers where it could otherwise migrate. Nothing reads `## Cover` for a task its authorising
record marks `[x]` or `[~]`. `paw ready` and `paw status` look only at open
tasks, and no `paw check` rule asks a finished task for a Cover. So every task
finished before this decision stays valid without one, and no record is
migrated. An open task approved before this decision has no `## Cover`, and
enters cover before it can be implemented. On 2026-09-28 `paw status` exited
0, and the only `next:` line it printed was ADR-1600's `next: spec, then
epic`, so no approved epic had an open task caught between the two.

After this decision a person or `/meow-flow:run` runs cover for a task, and
`paw ready implement` refuses the task until its Cover names the checks, the
failing run and where they landed, and names each criterion resting on
judgement with its reason. Each step's file says which committed file
its artifact lands in, and the chain reads as ten steps in every prompt, the
specification and the constitution. What still doesn't work:

- Cover and implement run in one session when the driver runs both, so the
  implementing context sees the cover step's reasoning (REQ-3214, REQ-3215).
- Nothing stops the implementation changing a check the cover step wrote
  (REQ-3210, REQ-3212).
- The program checks that a failing run is kept, and not that it failed, and
  it doesn't check that the checks landed before the implementation (REQ-3206,
  REQ-3208).
- Where the cover step adds checks to a test file that already exists, the
  path under `Checks` exists before the step runs, so its existence proves
  nothing. The decision on REQ-3206 and REQ-3208 has to close that case.
- The cover step file carries the step's shape, and none of the labelled
  content rules REQ-3204, REQ-3206, REQ-3208, REQ-3210, REQ-3211 and REQ-3213
  state.

## Why

RES-0075 found that tests written after faulty code detect about half the
faults that tests written independently do, 14% against 25%, and that tests
given before the code improve the code. Its first conclusion is a step of its
own before the implementation, which REQ-3200 states. A step of its own gets
a gate of its own, because ADR-1130 put each step's readiness in a program.
RES-0064 found that a driver that remembers nothing needs the next step
computed from the record each time, so `paw status` has to name cover.

The gate reads a section of the task because the task is the unit the
criteria live on (RES-0075, conclusion 2). A section filled after approval
already exists for `## Evidence`, with its exemption from freezing.
The four lines give the program something it can settle without judging the
checks: a path exists or it doesn't, and a line is empty or it isn't.
REQ-2694 asks for a check wherever a program can settle a rule, and this is
as far as one can without reading history.

REQ-3201 asked that every step leave a committed artifact, and REQ-0544 says
review leaves none. Both were approved, so the design couldn't meet the two.
I withdrew REQ-3201 and wrote REQ-3203, which keeps the obligation for the
nine steps that produce something, names review as the exception with
REQ-0544's reason, and puts the obligation on what each step's instructions
name, because a static check can't observe that a step committed anything.

REQ-3207 and REQ-3216 are decided here and not later, because the program
gates on the four lines. A later decision that made the `Judgement` line
carry a reason would change the format `paw ready implement` parses, and
this decision would then be half of one.

REQ-3202 is met by the driver ADR-1130 built. The driver only has to find
cover in `paw status` and keep going past a step with no gate, so the change
to it is one step in its skill.

## Alternatives

| Option                                                | Better at                                                   | Why it lost                                                                                                                                                                                                              |
| ----------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| A cover step gated on the task's `## Cover` (chosen)  | A gate a program holds, on the unit the criteria live on    | Chosen                                                                                                                                                                                                                   |
| Cover as the first part of the implement step         | No tenth step, no new gate                                  | REQ-3200 names ten steps, a program can't see the order inside one step, and one step leaves REQ-3214 and REQ-3215 no boundary to split contexts at later                                                                |
| Cover ends at an approval gate of its own             | Someone reviews the checks before any implementation exists | It breaks the single invocation that takes a task from cover to implement, and the checks are already reviewed in the change that carries them                                                                           |
| One cover run for the whole epic, before any task     | One run and one commit for all the checks                   | Checks for a late task are written before earlier tasks change what it builds on, and the criteria live on the task, not the epic                                                                                        |
| The Cover recorded in the task's front matter         | A field is parsed without reading prose                     | Four values, two of them lists of paths, fit a section better, and `## Evidence` already sets how a part filled after approval is exempt from freezing                                                                   |
| A `check` rule asking every finished task for a Cover | The record shows at once which tasks were never covered     | Every task finished before the decision would be a finding, and M15 forbids changing an approved record to meet a later rule. As a draft rule it would ask only draft tasks, which `paw ready implement` already refuses |
| Do nothing                                            | No change to the program, the prompts or the templates      | REQ-3200 and REQ-3203 stay unmet, and a task's checks go on being written in the same step as its code                                                                                                                   |

## What it costs

Whoever maintains `crates/meow` changes the step list, `ready`, `status`,
the frozen exemption and a defect's `enters`, with fixtures for each.
`meow-flow` gains a step file and changes eight of the nine it has, every
one but review's, whose role already says it writes nothing into the
repository. It also changes `SKILL.md`, the task and bug templates, the run skill, its README and its version, a minor bump because the
unit gains a capability, and its `plugin.json` description, which the budget
counts, names ten steps.

Every task pays one more step: one more run of the checks, one more commit or
pull request, and four lines in the task. For a small task that is most of the
work's overhead, and RES-0075's case against the step names that cost. Every
turn pays about a dozen more characters of the method skill's description,
within the budget.

Every document naming the nine steps changes: SPC-1090's steps table, its gate
table and its state list, the `meow-flow` README and its `plugin.json`
description, the root README, `llms.txt`, `project/vision.md` in its two
places, and `CLAUDE.md`'s chain.

## What would reverse it

- A measurement showing checks written in the cover step catch no more faults
  than checks written in the implement step would remove the step, and
  REQ-3200 with it.
- A task whose checks can't exist before its implementation, such as one
  whose interface the implementation invents, would show that the gate
  refuses work a person would let through. Three such tasks, each recorded as
  a defect entering at `cover`, would move cover to a later point.

## Consequences

- `paw ready` has ten steps, and a new `cover` gate; `implement`'s gate adds
  the filled Cover.
- `paw status` names cover as the next step for an uncovered task.
- `check frozen` lets `## Cover` change in an approved task, and a defect may
  enter at `cover`.
- `plugins/meow-flow/skills/method/steps/cover.md` exists, and every step file
  names the committed file its artifact lands in.
- The task template has `## Cover`, and the bug template's `enters` names
  cover.
- `meow-flow` moves to a new minor version, and its README's `describes`
  matches it.
- SPC-1090, the root README, the unit's README and `plugin.json`, `llms.txt`,
  `project/vision.md` and `CLAUDE.md` read ten steps.

## How I will know it was realised

1. `paw ready bogus TSK-0001` exits 2 and names the ten steps in order.
2. On a fixture record, `paw ready cover` exits 0 on an approved task under an
   approved epic, and 1 on a draft task and on a task whose dependency isn't
   done.
3. `paw ready implement` exits 1 naming the missing Cover on an approved task
   with none, 1 naming the path on a Cover whose failing run doesn't exist, 1
   naming the path on a Cover with a check that doesn't exist, 1 naming the
   line on a Cover whose `Landed in` is `none` while `Checks` names a path, 1
   naming the criterion on a `Judgement` entry with no reason, 0 once the
   section is filled, and 0 on a task whose `Judgement` names every criterion
   with a reason and whose `Checks`, `Failing run` and `Landed in` are `none`.
4. On a fixture where a task is marked `[x]` with no `## Cover`, `paw check`
   reports nothing about it, and `paw check frozen` reports nothing on an
   approved task whose only change is a filled Cover.
5. On a fixture with an approved epic and an open task with no Cover,
   `paw status` prints `next: cover`; with the Cover filled it prints
   `next: implement`; run twice unchanged, its output is identical.
6. `paw check` accepts a defect with `enters: cover` that names what it
   violates, and reports one that names nothing.
7. A static fixture reads `method/SKILL.md`, finds the ten step names in order
   in its body and its description, and finds one file under `steps/` for
   each. The budget check passes on `meow-flow`.
8. A static fixture reads each step file's role and finds the committed file
   the table above gives, and for review finds that it writes nothing into
   the repository.
9. The next epic this repository implements keeps one run of
   `/meow-flow:run` whose output shows `next: cover <task>`, then
   `next: implement <task>`, and ends at a gate, and that task's Cover and
   Evidence were filled by the run.

## What this does not settle

- The content rules of the cover step: REQ-3204, REQ-3206, REQ-3208,
  REQ-3210, REQ-3211 and REQ-3213.
- Running cover and implement in separate contexts, and giving the
  implementation the checks without the reasoning: REQ-3214 and REQ-3215.
- Holding the cover step's checks read-only while a task is implemented:
  REQ-3212.
