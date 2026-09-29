---
id: TSK-2540
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1580
closes: [REQ-3202]
issue: 617
projected: 0529a56555d2
---

# Make `paw status` name cover before implement, and let the driver continue past a step with no gate

`paw status` prints `next: cover <task>` for an open task whose Cover isn't
filled and `next: implement <task>` once it is, and `/meow-flow:run` runs
`status` again after a step that ends with no approval gate. So one
invocation takes an approved task through cover and implement to the next
gate, which is what REQ-3202 asks of the one command that drives the chain.
One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the fixture record with an approved epic and an open task with no
   Cover, when `paw status` runs, then it prints
   `next: cover TSK-0001 (EPC-0001, 0 of 1 task done)`. Closed by:
   `Chain.test_status_names_cover_for_an_uncovered_task` in
   `plugins/meow-flow/tests/test_record.py`.
2. Given the same record with the task's Cover filled, when `paw status`
   runs, then it prints the same line with `next: implement` in place of
   `next: cover`. Closed by: `Chain.test_status_names_implement_once_covered`.
3. Given either record, when `paw status` runs twice with nothing changed,
   then both outputs are identical. Closed by:
   `Chain.test_status_prints_the_same_state_twice`, extended to a record
   with an uncovered open task.
4. Given `plugins/meow-flow/skills/run/SKILL.md`, when it is read, then a
   step says that where the step it ran ends without an approval gate, it
   runs `paw status` again and continues, and step 5 still stops at an
   approval gate. Closed by:
   `RunSkill.test_the_driver_continues_past_a_step_with_no_gate`,
   a static fixture reading the skill.
5. Given the driver run on a task, when it reaches the task's implement step,
   then it reached it in the same invocation that ran cover. Judgement,
   because no fixture runs a model session; criterion 9 of EPC-1580 observes
   it on the next epic.
6. Given this change's tree, when `meow-verbs run format lint test` runs,
   then each passes. Closed by: the kept evidence of that run.

## What to do

In `crates/meow/src/record.rs`, the `status` branch for an approved decision
whose epic has open tasks picks the first task whose dependencies are done,
as now, and prints `cover` or `implement` by reading the task's Cover with
the function TSK-2530 added. The rest of the line keeps its form. A task
under a defect's `## Tasks` follows the same rule. SPC-1090's section "The
state" states the output.

Change the existing status test that expects `next: implement TSK-0001` to
the new line.

In `plugins/meow-flow/skills/run/SKILL.md`, add the step ADR-1620 gives: where
the step just run ends without an approval gate, run `paw status` again and
continue. Keep the skill's other steps, and follow `meow-author:write` for the
prompt.

Raise `meow-flow`'s minor version in `plugin.json` and its README's
`describes`. Write the checks first, in a commit of their own, and see them
fail.

## Depends on

TSK-2530, because `status` decides between cover and implement with the
Cover reading that task adds, and names a step `ready` must already know.

## Cover

- Checks: plugins/meow-flow/tests/test_record.py
- Failing run: project/evidence/0c16e63f1816.txt
- Landed in: #658
- Judgement: 5: no fixture runs a model session, so whether one invocation reaches implement after cover is observed on the next epic, as criterion 9 of EPC-1580 says

The checks are `Chain.test_status_names_cover_for_an_uncovered_task` for
criterion 1, `Chain.test_status_names_implement_once_covered` for criterion 2,
`Chain.test_status_prints_the_same_state_twice` for criterion 3 and
`RunSkill.test_the_driver_continues_past_a_step_with_no_gate` for criterion
4, all for REQ-3202. `Chain.test_status_leads_with_drafts_and_places_each_decision`
now expects `next: cover TSK-0001`, as What to do asks. Criterion 6 is the
kept run of the verbs at the revision that merges.

### Cover returned

Two checks were wrong, and I corrected them after the failing run. The two
status checks compared the expected line with whole output lines, and `paw
status` indents each decision's position by four spaces, so they now compare
stripped lines. The covered fixture gave the task no numbered criterion, which
`ready implement` refuses since BUG-1261, so it now carries the criteria the
Cover fixtures use.

## Evidence

`position` in `crates/meow/src/record.rs` reads the first doable task's Cover
with `cover_gaps`, the function `ready implement` uses, and prints
`next: cover <task>` while the Cover has gaps and `next: implement <task>`
once it has none. `/meow-flow:run` gains a step that runs `paw status` again
and continues where the step it ran ends without an approval gate. SPC-1090's
sections "The state" and "The driver" no longer mark the behaviour as not yet,
and `meow-flow` goes to 0.36.0.

The five checks failed first: `meow-verbs run test` exited 1 with
`FAILED (failures=5)`, kept as `project/evidence/0c16e63f1816.txt`, in the
commit that held the checks alone. They pass now:

```text
$ python3 -m unittest test_record    # in plugins/meow-flow/tests
Ran 193 tests
OK                                   # exit 0
```

`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

The method skill and the step files, which TSK-2550 changes. `paw status
--waiting`, whose output doesn't name a next step. The driver's context
split between cover and implement, REQ-3214 and REQ-3215, which ADR-1620
leaves open.
