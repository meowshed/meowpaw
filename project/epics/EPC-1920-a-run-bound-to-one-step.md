---
id: EPC-1920
artifact: epic
status: approved
revised: 2026-09-30
realises: ADR-2020
---

# A run is bound to one step, finishes on that step's work at the current tree, and ends when it crosses a gate

Realises exactly one authorising record, ADR-2020. The epic is complete when
a person starts `meow-loop start --step <step> --inputs <ids>` over an
approved input, and the run ends `finished` only when the runner has seen the
step's work in the record and the named verbs pass at the tree that stands,
and ends `crossed` or `off-step`, naming the cause, the call after a model
decides a status, changes an approved record or writes another step's files.

**Amended by ADR-2300.** ADR-2300 removed the cover and verify steps and `checked-at`, so the `verify` half of criterion 10, criterion 11 in both halves (`checked-at` and the Cover lines) and `--step document` in criterion 6 no longer apply; TSK-3440's criterion 2 tests an input left failing the start test in criterion 11's place, and each task's tests land first in its own pull request.

## Acceptance criteria

Taken from ADR-2020, from its list of how I will know it was realised, before
the tasks below were written. Each check runs the runner with a stand-in
`claude` on the path, as EPC-1910's checks do, in a scratch git repository
holding a small record the fixture builds, so no check depends on this
repository's record. Each check clears `CLAUDECODE` from the runner's
environment, because the gate often runs inside a Claude Code session.

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
   the run `finished`; one that marks it `x` with text in its Evidence
   section, while the verb passes, ends it `finished` after that call
   (REQ-0884).
6. `start` without `--step`, with `--step document`, `--step review` or an
   unknown step, with `--inputs` on `research` or without it on `design`,
   exits 2 and leaves no run directory. `start` over a draft requirement, with
   the record root ignored by git, with the record root missing, or with the
   record root outside the work tree, exits 3, prints the reason and leaves no
   run directory. A started run's `run.toml` holds `step` as one string and
   `inputs` as a list (REQ-0888).
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
    marks the input task `x` in that epic, changing nothing else there,
    doesn't (REQ-0888). In a `verify` run, a stand-in that rewords an
    acceptance criterion ends the run `crossed`, and one that writes
    `## Verified` and sets `checked-at` doesn't (REQ-0888). In an `implement`
    run of a task an approved defect authorises, a stand-in that marks the
    task `x` in the defect, changing nothing else there, doesn't end the run
    `crossed`, and one that rewords the defect's reproduction does
    (REQ-0888).
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
15. In a `design` run whose verb is criterion 3's formatter, set to rewrite an
    approved requirement and a file outside the record root on its first run,
    a stand-in that writes only the decision ends the run `finished`, and
    neither `crossed` nor `off-step` (REQ-0888).
16. Every recorded call's preamble names the step and its inputs and is byte
    identical across calls (REQ-0888).
17. Each check above counts what it matched, and a count of zero where one
    was expected fails it.
18. Every requirement ADR-2020 addresses lands in exactly one closed task.

Criterion 17 is added here, as EPC-1910 added its criterion 13, because a
check that matched nothing reports a pass with nothing behind it. ADR-2020's
criterion 17 is criterion 18 here.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number, as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-3410 bind `start` to `--step` and `--inputs`, hold a copy of
      the record, and finish a run only when the step's test and the verbs
      pass at one tree, in `plugins/meow-loop/` and the `loop` feature of
      `crates/meow`
      closes: REQ-0884
      evidence: the `Step` checks pass after failing first in their own
      commits, and the five verbs pass. TSK-3410 carries the rest.
      depends: TSK-3360 (blocking) - the preamble this task extends
      depends: TSK-3370 (blocking) - the condition and the meter checks
      depends: TSK-3390 (blocking) - the held verb commands and hash checks

- [x] T-002 [P] TSK-3420 end a run `crossed` when a call or an evaluation
      decides a status, or changes or removes an approved record
      evidence: the `Crossed` checks that guard a crossing failed first in
      their own commits, and the five verbs pass.
      depends: TSK-3410 (blocking) - the step and the copy held at start

- [x] T-003 [P] TSK-3430 add the hook's status rule, active when
      `MEOW_LOOP_RUN` is set, and set that variable in every call
      evidence: `Hook.test_status_rule`, `Hook.test_status_rule_on_write` and
      `Step.test_run_id_in_every_call` pass after failing first in their own
      commit, and the five verbs pass.
      depends: TSK-3410 (blocking) - the record code naming living kinds
      depends: TSK-3400 (blocking) - the last change to the hook it joins

- [ ] T-004 TSK-3440 end a run `off-step` when a call writes another step's
      records or paths, or leaves its input unready
      closes: REQ-0888
      depends: TSK-3420 (blocking) - `crossed` is checked before `off-step`
      depends: TSK-3430 (blocking) - REQ-0888 closes here, after every guard

TSK-3420 and TSK-3430 can run in parallel once TSK-3410 has landed, because
one adds a check after the call and the other adds a hook rule and an
environment variable, and neither reads what the other adds. TSK-3440 waits
for both.

## Coverage

ADR-2020 addresses two requirements, and each lands in one task:

| Requirement | Task     | Why there                                                                       |
| ----------- | -------- | ------------------------------------------------------------------------------- |
| REQ-0884    | TSK-3410 | The step's test and the verbs at one tree are the evidence a run finishes on    |
| REQ-0888    | TSK-3440 | `off-step` lands last and cites the evidence of TSK-3410, TSK-3420 and TSK-3430 |

The criteria split between the tasks as follows. TSK-3410 closes 1 to 6, 14
and 16, and the `finished` half of 13. Criteria 6 and 16 bear on REQ-0888,
and TSK-3440 cites TSK-3410's evidence for them when it closes REQ-0888.
TSK-3420 closes 7 and 10, the `crossed` half of 12 and of 13. TSK-3430
closes 9. TSK-3440 closes 8, 11 and 15, and the `off-step` half of 12.
Criterion 17 binds every check in every task, and criterion 18 is this epic's
own.

TSK-3420 and TSK-3430 close no requirement, because REQ-0888 is one
obligation met only when a run can neither cross a gate nor leave its step,
and it closes once, in the task that lands last. Each still has observable
behaviour: an ending and a denied edit.

The smallest set that tests the decision is TSK-3410 and TSK-3420, because
together they show a run that finishes on its step's work and not on a
phrase, and stops the call after it approves a record. Once EPC-1910 has
landed and before TSK-3410 does, criteria 1 and 2 can be measured against
EPC-1910's runner: both already end without `finished` there, because its
condition is the verbs alone, and TSK-3410 must keep them so.

The cover step keeps each task's failing run from the tree the task starts
on. TSK-3410's failing run is taken on the tree EPC-1910 leaves, where
`start` has no `--step`, so its checks fail on the flag. Each later task's
failing run is taken on the tree of the tasks it depends on, where the checks
fail only on what the task adds.

## Not covered

- Runs in the document and review steps, which have no test a program can
  read (ADR-2020, "What this does not settle").
- A run approving a record through a separate judge, marked as the harness's
  (REQ-2382, REQ-2384).
- Stopping a run and what an interrupted iteration leaves (REQ-0890,
  REQ-0892).
- Whether `paw ready` should exit 3 for a missing record, which the runner
  doesn't depend on, because it applies the test itself.
- Keeping a run's final results as evidence files in the repository; the run
  records them in the ledger and the person keeps them.
- Whether a hook fires in a `claude -p` call and sees `MEOW_LOOP_RUN`, which a
  stand-in can't show and the first real run will.
- The reversal triggers ADR-2020 names, which count the first ten real runs
  and so can't be measured before the runner ships.
- The user-facing pages outside the unit, which the document step updates
  once every task is done.
