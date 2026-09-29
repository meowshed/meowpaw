---
id: ADR-2020
artifact: adr
status: approved
revised: 2026-09-29
addresses: [REQ-0884, REQ-0888]
supersedes: []
---

# 2020. A run is bound to one step, finishes when the runner sees that step's work done at the current tree, and ends when it crosses a gate

## Decision

This decision amends ADR-2010's `start` command and its refusals, its
`run.toml`, its preamble, its condition, the checks after a call, its hook and
its endings table, and adds a copy of the record the runner reads at start and
compares after each call. Each is stated below, and the rest of ADR-2010
holds.
ADR-2010 is approved, and pull request #710 carried it to `main`. An approved
record is frozen, so this decision amends ADR-2010 as a record of its own and
doesn't edit it.

`meow-loop start` takes the step and its input, and refuses a run without
them (REQ-0888):

```text
meow-loop start --step <step> [--inputs <id>[,<id>...]]
                --until verbs=<verb>[,<verb>...] ...
```

`--step` names one of the eight steps in the table below, and `--inputs` names
the identifiers that step reads. A missing `--step`, a step outside the table,
`--inputs` given to `research` or left out of any other step each exit 2 and
write nothing, because the command as typed can't start a run. `document` and
`review` are outside the table, because neither has a test of its work a
program can read, and a run with no such test ends `finished` before its first
call wherever the verbs pass, as ADR-2010's evaluation before the first call
does.

The runner then applies the test `paw ready <step> <inputs>` applies, and
exits 3 with each line it would print, writing nothing, when an input isn't
ready. It exits 3 as well when the record's root is missing, or is ignored by
git or lies outside the work tree. Exit 3 is right because the same command
starts once a person approves the input, and a record the tree id leaves out
would leave the step's test bound to no tree. The runner compiles in the
`record` feature's code to apply the test, as it compiles in the `verbs`
feature's, for two reasons. The `standalone` gate refuses a unit whose file
runs a path outside its own directory. And `paw ready` exits 1 for a missing
record exactly as for an input that isn't ready (RES-0301), so a runner reading
its status would call a missing record an unapproved input.

`run.toml` gains `step`, one string, and `inputs`, a list, beside the other
terms, and the runner holds both in memory with them. The fixed preamble names
the step, its inputs, what the step writes, and the three things that end the
run early: a decided status, a change to an approved record, and a change to
another step's files. It tells the model to record a defect as a draft where
the work shows an approved artifact is wrong, because every step may write
one and none may change the approved artifact. The preamble is the same text
on every call, so REQ-0880 still holds.

At start the runner reads the whole record and holds it in memory: each
record's identifier, kind, stored status and text. RES-0301 measured that
reading 2146 files takes 0.23 seconds, so the runner can compare against this
copy after every call. The runner takes the copy after its evaluation before
the first call, and not before it, because a verb that writes, such as
`format`, can rewrite a record or a path in that evaluation, and a copy taken
earlier would blame that rewrite on the first call. "The copy held at start"
below means this copy.

### Completion

The condition is now two terms, and it holds only when both hold at the same
tree: the verbs the person named with `--until`, and the step's test below.
The runner evaluates the condition whenever ADR-2010 says it does: before the
first call, and after each call that changed the tree. A `cover`, `implement`
or `verify` run whose work is already done therefore ends `finished` with no
call, because nothing is left for the run to do. The five record steps' tests
count only a record new or changed since the copy held at start, so their run
always makes at least one call.

| Step           | Its test holds when                                                                                               | The step may write                                                        |
| -------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `research`     | A research record exists that wasn't in the record at start                                                       | research records                                                          |
| `requirements` | Each input research record is in the `elaborates` of some requirement new or changed since start                  | requirements                                                              |
| `design`       | Each input requirement is in the `addresses` or `postpones` of some decision new since start                      | decisions                                                                 |
| `spec`         | Each requirement the input decision addresses is in the `states` of some specification new or changed since start | specifications                                                            |
| `epic`         | An epic new since start names the input in `realises`                                                             | epics and tasks                                                           |
| `cover`        | Each input task passes the Cover test `paw ready implement` applies                                               | tasks, and any path outside the record root                               |
| `implement`    | Each input task is marked `x` by the record that authorises it, and its `## Evidence` holds text                  | tasks, the task marks of epics and defects, and any path outside the root |
| `verify`       | Each input epic's `checked-at` is set                                                                             | epics' `## Verified` and `checked-at`                                     |

A draft counts, because a step's artifact waits for a person as a draft. The
five record steps count only a record new or changed since start, because a
record that already answered the input before the run is no work of the run's.
A design run that amends or supersedes a decision, over requirements an earlier
decision already addresses, finishes only on the new decision, and so does a
spec run over a decision a specification already states, which adds or
changes a specification. The `design` and `epic` rows count only a new record,
because an approved decision or epic can't be changed without crossing, and a
draft left from before the run is a person's work in progress. The
`requirements` and `spec` rows count a changed record as well, because a
draft requirement or a living specification may gain the input in a run.
The `implement` test reads the `x` mark alone, because the record counts `~`,
dropped, as finished, and a run could otherwise finish by dropping its work
(RES-0301). The `cover` test is the one `paw ready implement` already applies,
and the `verify` test is the one `paw ready review` applies.

Every term of the condition is evidence the runner obtains itself, at the tree
that stands when the run ends (REQ-0884):

1. The runner reads the tree id, applies the step's test to the record in the
   work tree, runs each verb through the `verbs` code, and reads the tree id
   again.
2. The condition holds only when the test passes, every verb exits 0, and the
   two tree ids are equal and identified. A verb that writes to the tree, such
   as `format`, passed at a tree that no longer stands, so where the two ids
   differ the runner repeats the evaluation once, at once, and that second
   result stands. The repeat is bounded, so a verb that rewrites the tree on
   every run can't hold the runner in a loop; a verb that settles only after
   two passes leaves the condition unmet, and the next call runs. A tree it
   can't identify, such as one with a dirty submodule, binds no result, so the
   condition doesn't hold there.
3. The runner records each verb's result in the ledger through the `verbs`
   code, with the tree before and after, so the person can keep and cite the
   run's final results with `meow-verbs evidence --keep`.

The runner reads no pass back from the ledger. A line there shows that some
process appended it, not that the runner saw the command pass (RES-0301), and
the runner has run the verbs itself at that tree. It reads nothing the model
printed, so a result whose text claims the work is done changes nothing, and no option
takes a completion phrase.

### One step

After each call the runner checks the record and the changed paths, and the
first check that fails ends the run. The paths come from the tree id the
runner reads immediately before the call, after its own evaluation of the
condition, and the tree id after the call, so a path a verb rewrote in that
evaluation is never counted as the call's. The record is compared with the
copy held at start. The checks come after ADR-2010's hash check and its two
meter checks, and before the condition, because a success reached
by crossing a gate can't be trusted, for the reason ADR-2010 puts a changed
term first. They run after every call, unless the tree ids before and after
it are both identified and equal. Equal identified ids show the call changed
no record and no path, because `start` refused a record the tree id leaves
out. Where either id is unidentified, as with a dirty submodule, the runner
can't tell whether the call changed anything, so it compares the record.

A decided status, in this decision, is any stored status except `draft`, and
except `live` in a kind the record declares living, such as a specification,
because a specification's status is `live` from its first draft and never
marks an approval. The run ends as `crossed` when the record, compared with
the copy held at start, shows any of four changes:

- a record's stored status became a decided status;
- a record new since start carries a decided status;
- an approved record is gone from the path it had at start, deleted or
  renamed;
- an approved record changed outside what a run may change in it.

A run may change an approved task only outside its frozen part, as the
record's frozen comparison allows. A run may change an approved epic or an
approved defect only in its task marks in an `implement` run, because a task a
defect authorises is closed by the defect's mark, and the frozen comparison
grants a defect no change at all. A run may change an approved epic only in
its `## Verified` section and `checked-at` in a `verify` run, and may change
an approved defect in no other way. Any other change to an approved epic,
such as a reworded acceptance criterion, crosses, because rewording an
approved record to match what was built is the failure the constitution
names. The frozen comparison lets an epic change freely while its
`checked-at` is empty, and the runner doesn't take that allowance. Nor does
it take the comparison's two exemptions, a status now `withdrawn` or
`superseded` and a line naming an authority. RES-0301 observed `paw check
frozen` passing both, and each is a decision the method leaves to a person
(REQ-0888). The frozen comparison reads only the records that still exist,
which is why the runner names a removed record itself. The ending names each
record that crossed.

The run ends as `off-step` when a call did any of three things:

- created or changed a record of a kind the table doesn't let its step write.
  A defect or an insight, as a draft, is allowed in every step, and so is a
  file under the record root that is no record, such as an index, because
  `paw index --write` regenerates those;
- changed a path outside the record root in a step whose row doesn't allow
  it. `git diff-tree -r --name-only` between the tree ids before and after
  the call lists the paths (RES-0301). Where either id is unidentified, the
  runner can't list them, and it ends a run of a step that writes only
  records as `off-step` for that reason;
- left an input failing the test that `start` applied, or, in an `implement`
  run, set an epic's `checked-at`, which is the verify step's work.

The ending names each record or path that took the run off its step. The
runner checks for `crossed` before `off-step`, so a call that does both ends
`crossed`, because a crossed gate is the graver of the two.

The runner also compares the record after each of its own evaluations that
changed the tree, because a verb the person named can rewrite a record too.
A decided status or a change to an approved record found there ends the run
`crossed`, naming the evaluation and the verb, and not a call. The verbs
already ran over every record before the copy was taken, so this fires only
where a verb doesn't settle, or rewrites a record a call left changed and
the check after that call allowed.

The unit's hook gains a rule of its own, active only when `MEOW_LOOP_RUN` is
set. The runner sets that variable to the run's id in every call's
environment, and the hooks reference says a hook inherits Claude Code's
environment (RES-0301). The rule denies an Edit whose `new_string`, or a Write
whose `content`, would change the stored status of a file under the record
root to a decided status, as defined above, reading the kind from the file's
directory, so it allows `live` in a specification as the comparison does. It reads the file
on disk to tell a change from a status that is already there, so an Edit of an
approved task's Evidence section passes. Outside a run the rule allows the
edit, because in a session the model writes an approval a person gave. The
hook is the first line, so the model hears the refusal before it spends the
iteration; the comparison after the call decides, because a hook that doesn't
fire, or a Bash command that writes the file, leaves the change for the
comparison to find.

The endings table in ADR-2010 gains two rows, both with exit status 1, because
the condition didn't hold:

| Ending     | Means                                                                              | Exit status |
| ---------- | ---------------------------------------------------------------------------------- | ----------- |
| `crossed`  | A call or an evaluation decided a status, or changed or removed an approved record | 1           |
| `off-step` | A call wrote another step's files, or the step's input stopped being ready         | 1           |

After this decision a person starts a run for one step over its approved
input, such as `--step implement --inputs TSK-3350`. The run ends `finished`
when the runner has seen that step's work in the record and the named verbs
pass at the tree that stands. It ends `crossed` or `off-step`, naming the
cause, the call after a model approves a record, changes an approved one, or
starts on another step's files. What still doesn't work:

- A run can't work in the document or review step.
- A cover or implement run may change any path outside the record root, so
  one that edits the user-facing pages, which is the document step's work,
  stays on its step, because the harness names no language and can't tell a
  page from code.
- The record steps' tests count only a record new or changed since start. A
  record step's run over an input a record already answers finishes
  only once the run writes or changes one, which is the work an amendment
  needs, so a person can't use a run merely to confirm that the record
  already answers the input.
- The step's test reads front matter and marks the model writes. A design run
  finishes on a decision that names each input in `addresses`, whatever its
  body says, wherever the named verbs don't judge the record. The draft still
  waits at the gate for a person, so the worst outcome is a poor draft waiting
  and never an approved one.
- Whether a hook fires in a `claude -p` call and sees `MEOW_LOOP_RUN` is
  unobserved, as ADR-2010 lists. Until the first real run shows it, the
  comparison is the only guard that holds in a run.
- The run keeps no evidence file. It records its results in the ledger, and
  the person keeps them.
- A run's approval of a record, through a separate judge and marked as the
  harness's, isn't possible, so an unattended run crosses no gate at all
  (REQ-2382, REQ-2384).

## Why

RES-0024 and RES-0059 found that a loop completes on evidence at the current
revision, including the plan's tasks marked with what closed them, and never
on a phrase, and that a loop stays inside one step and never crosses an
approval gate. RES-0301 found what a program can read to hold those two rules:
`paw ready` passes before and after a step's work alike, so the step needs a
test of its own work; the frozen check passes an approval, a withdrawal and a
line naming an authority, so a run needs a stricter comparison; a dropped task counts as
finished; a task's evidence is text bound to no tree; a ledger line is a file
any process can append to; and two tree ids name the paths a call changed.

ADR-2010's condition, the verbs alone, holds before a record step does any
work, so a design run on a clean tree ends `finished` with no call. A test of
the step's own artifact is what makes the condition mean the step is done, and
the verbs run at the same tree are what make it evidence.

## Alternatives

| Option                                                                 | Better at                                                                        | Why it lost                                                                                                                                                                                               |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Read a pass at the current tree from the ledger, as the plan proposed  | No verb runs in the runner after a call                                          | A ledger line shows a process appended it, and a call can append one (RES-0301); ADR-2010's runner already runs the verbs                                                                                 |
| A condition `tasks=<epic>` over every task of an epic                  | One run closes a whole epic                                                      | The implement step reads tasks, so the run's inputs already name them, and a test through the record's `finished` counts a dropped task as done (RES-0301)                                                |
| End the run as `at-gate` the call a draft appears                      | Stops the earliest                                                               | The first draft seldom passes the checks, and fixing its own draft is the same step; the step's test and the verbs end the run the call the draft passes                                                  |
| Run `paw check frozen` after each call to find a crossing              | No second comparison in the code                                                 | It passes an approval, a withdrawal and an authority line, three changes a run must not make, and spent 47 seconds of CPU on this record (RES-0301)                                                       |
| Bind a run to the step's own artifact paths, which the step files name | Names the exact files, so a design run can't write a second decision's directory | For the record steps the paths are one directory per kind, which the kinds already bind; for `cover` and `implement` the step files name "the changed files", which binds nothing outside the record root |
| Run `paw ready` and `paw status` as programs                           | The runner's code stays small                                                    | The `standalone` gate refuses a unit running another unit's path, and `paw ready` exits 1 for a missing record as for an unready input (RES-0301)                                                         |
| Rely on the hook alone                                                 | Refuses before the write                                                         | A hook firing in a `-p` call is unobserved, and a Bash command that edits the file passes it                                                                                                              |
| Do nothing                                                             | No new ending, no record read after each call                                    | A record step's run ends `finished` before its first call, and a run can approve its own draft or start the next step unattended                                                                          |

## What it costs

The person running the loop names the step and its input, and a chain of
steps is one run per step with a person between them. That is the point of REQ-0888, and it is also
the price: a run can't carry a requirement through design and spec overnight.
The document and review steps can't run at all.

The person running the loop pays in time on each call for a read of the
whole record and a `git diff-tree`, about a quarter of a second on this
repository, and for running the verbs twice in each evaluation where a verb
writes to the tree. A repository whose record
root is ignored by git, or lies outside the work tree, can't run a loop. A run
ends `crossed` where the work shows an approved artifact is wrong and the
model corrects it in place, as this repository's constitution tells it to; the
preamble's instruction to record a defect instead is the only thing between
the two. A Write that rewrites a whole approved record is refused inside a run
whenever it would change the status, so the model uses Edit for those files.

The `loop` feature compiles in the `record` feature's code, so the unit's
program grows by the record's parser. The unit's maintainers pay for that: a
change to the record's rules reaches the runner only on the next build and
release of `meow-loop`, and each such change needs the loop's fixtures run
again.

## What would reverse it

- Of the first ten real runs, more end `crossed` or `off-step` on work a
  person would have approved than end `finished`. The person who started each
  run makes that judgement when they read its ending, and records it, with
  the run's id, in the insight that reports the count. The binding then moves from
  kinds and paths to the step's own artifact paths, which the step files
  already name.
- Of the first ten design or requirements runs that finish, the person
  refuses the draft at the gate in more than five. The step's test then moves
  from front matter to the judge the unattended decisions will add (REQ-2382).
- The record gains a machine-readable test of whether a step is done. The
  runner then applies that test in place of the table, so the two can't
  drift.

Two unobserved behaviours would amend the decision and not reverse it, if the
first real run shows them false:

- A hook in a `claude -p` call doesn't see `MEOW_LOOP_RUN`. The hook's rule
  then denies nothing inside a run, and the comparison is the only guard.
- A hook in a `claude -p` call doesn't fire at all, which ADR-2010 already
  lists. The same holds.

## Consequences

- ADR-2010 gains a line naming this decision as its amendment, once this
  decision is on `main`.
- `crates/meow`'s `loop` feature compiles in the `record` feature, and the
  record's code exposes its step test, its frozen comparison with the
  exemptions switchable, and each kind's allowance after approval to it.
- `meow-loop`'s hook gains the status rule, and its skill's start command
  names `--step` and `--inputs`. The unit's version rises by a minor.
- SPC-1201 gains the step, the inputs, the step's test and the two endings, at
  the spec step.
- Fixtures build a small record in a scratch repository, so no fixture
  depends on this repository's record.

## How I will know it was realised

Each fixture runs the runner with a stand-in `claude` on the path, as
ADR-2010's do, in a scratch repository holding a small record.

1. A stand-in whose result text says "DONE, all tests pass", while the verb's
   command exits 1 at the current tree, runs to the ceiling, and the run ends
   `ceiling` (REQ-0884).
2. A stand-in that appends a passing ledger line for the verb at the current
   tree, while the verb's command exits 1, doesn't end the run `finished`
   (REQ-0884).
3. A verb whose command reformats a tracked file on its first run and exits 0
   ends the run `finished` after the repeated evaluation, and a verb that
   changes the tree on every run never ends it `finished` (REQ-0884).
4. With a dirty submodule the condition never holds, and the log records the
   tree as unidentified (REQ-0884).
5. In an `implement` run, a stand-in that marks the input task `~` doesn't end
   the run `finished`; one that marks it `x` with text in its Evidence section,
   while the verb passes, ends it `finished` after that call (REQ-0884).
6. `start` without `--step`, with `--step document`, `--step review` or an
   unknown step, with `--inputs` on `research` or without it on `design`,
   exits 2 and leaves no run directory. `start` over a draft requirement,
   with the record root ignored by git, with the record root missing, or with
   the record root outside the work tree, exits 3, prints the reason and
   leaves no run directory. A started run's `run.toml` holds `step` as one
   string and `inputs` as a list (REQ-0888).
7. A stand-in that sets a draft decision's status to `approved` ends the run
   `crossed` after that call, naming the decision. So does one that sets an
   approved requirement to `withdrawn`, one that appends to an approved
   requirement a line naming an amendment, in the form the frozen check
   accepts, and one that deletes or renames an approved requirement
   (REQ-0888).
8. In a `design` run, a stand-in that writes a draft decision addressing the
   input and a specification ends the run `off-step`, naming the
   specification, and so does one that writes a file outside the record root.
   One that writes only the decision, while the verb passes, ends it
   `finished` (REQ-0888).
9. A hook fixture with `MEOW_LOOP_RUN` set denies an Edit changing a record's
   `status: draft` to `status: approved` and allows an Edit of an approved
   task's Evidence section; without the variable it allows both (REQ-0888).
10. In an `implement` run, a stand-in that rewords an acceptance criterion of
    the approved epic ends the run `crossed`, naming the epic, and one that
    marks the input task `x` in that epic, changing nothing else there, doesn't
    (REQ-0888). In a `verify` run, a stand-in that rewords an acceptance
    criterion ends the run `crossed`, and one that writes `## Verified` and
    sets `checked-at` doesn't (REQ-0888). In an `implement` run of a task an
    approved defect authorises, a stand-in that marks the task `x` in the
    defect, changing nothing else there, doesn't end the run `crossed`, and
    one that rewords the defect's reproduction does (REQ-0888).
11. In an `implement` run, a stand-in that sets the epic's `checked-at` ends
    the run `off-step`, naming the epic, and so does one that empties the
    input task's `## Cover` lines, naming the task (REQ-0888).
12. In a `design` run with a dirty submodule, a stand-in that writes the
    decision ends the run `off-step`, and the log records the tree as
    unidentified; with the same submodule, a stand-in that sets a draft
    decision to `approved` ends it `crossed` (REQ-0888).
13. In a `spec` run, a stand-in that writes a new specification with status
    `live` stating each requirement the input decision addresses, while the
    verb passes, ends the run `finished`, not `crossed`; one that sets a draft
    requirement's status to `live` ends it `crossed` (REQ-0888).
14. In a `design` run over a requirement an approved decision already
    addresses, the run makes a call. A stand-in that writes a new draft
    decision addressing it, which names in its own text the decision it
    amends and changes nothing in that decision, ends the run `finished`
    (REQ-0884).
15. In a `design` run whose verb is fixture 3's formatter, set to rewrite an
    approved requirement and a file outside the record root on its first run,
    a stand-in that writes only the decision ends the run `finished`, and
    neither `crossed` nor `off-step` (REQ-0888).
16. Every recorded call's preamble names the step and its inputs and is byte
    identical across calls (REQ-0888).
17. Every requirement ADR-2020 addresses lands in exactly one closed task.

## What this does not settle

- Tests of the document and review steps' work, and so runs in those steps.
- A run approving a record through a separate judge, and marking the approval
  as the harness's (REQ-2382, REQ-2384).
- Stopping a run and what an interrupted iteration leaves (REQ-0890,
  REQ-0892).
- Whether `paw ready` should exit 3 for a missing record. SPC-1090 specifies
  exit 1, the same as for an input that isn't ready (RES-0301), and the runner
  doesn't depend on it, because it applies the test itself.
- Keeping the run's final results as evidence files in the repository.
- A run that confirms, without writing a record, that the record already
  answers its input, because the record steps' tests count only a record new
  or changed since start.

## Strongest objection

The step's test trusts front matter the model writes, so REQ-0884's evidence
is weaker for the record steps than for implement: a decision that names the
requirement in `addresses` passes the test whatever its reasoning. I keep the
decision because the evidence REQ-0884 asks for is that the run's claim holds
at the current tree, and the runner checks that claim at that tree with the
checks the person named. Whether the reasoning is good is a judgement, and the
gate the run stops at is where a person makes it.

## Premortem

A night's implement run ended `crossed` on its second call. The task showed
that an approved requirement named the wrong exit status, and the model
corrected the requirement in place, because the constitution says to fix a
wrong artifact. The work the first call did was left in the tree, the ending
named the requirement, and the morning went on writing the defect record the
run should have written. The preamble's instruction to record a defect as a
draft is there for this case, and the count of runs ending this way is the
first signal to read.
