---
id: TSK-2280
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1460
closes: [REQ-0148]
issue: 514
projected: 61f4dbb663ed
---

# `meow-verbs:verify` and the implement step cite records and check them before calling work done

The skill runs `format` first, cites a result as `meow-verbs evidence` prints
it, and calls the work done only on its exit 0 or a person's acceptance; the
method's implement step asks for the same citation where `meow-verbs` is
installed. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the `verify` skill, when it is read, then it carries the order, the
   citation and the check before done, each traced to REQ-0148 in this task's
   evidence. Closed by: the trace.
2. Given the implement step, when it is read, then it asks for the recorded
   citation where `meow-verbs` is installed, and for the command, its exit
   status and its output where it isn't. Closed by: the trace.
3. Given the changed skill, when `meow-author check` and `meow-author cost`
   run, then both exit 0. Closed by: their output.

## What to do

Change `plugins/meow-verbs/skills/verify/SKILL.md` and
`plugins/meow-flow/skills/method/steps/implement.md`, and move each unit to its
next patch version.

## Depends on

TSK-2270, whose command the skill names.

## Evidence

Closes REQ-0148. `meow-verbs evidence format lint test` exits 0:

```text
format: passed, record 784e35964dd9, current at tree 2d628eaf70ea
lint: passed, record d9dc014f742f, current at tree 2d628eaf70ea
test: passed, record 2c46ec863f7f, current at tree 2d628eaf70ea
```

The committed tree differs from `2d628eaf70ea` by the SPC-1090 paragraph, this
section and the epic's mark, written after the run. `lint` runs
`meow-author check`, 0 authoring failures, and `meow-author cost`, 0 budget
failures, with `meow-verbs` at 331 of 450 characters. The trace:

1. The `verify` skill: step 2 and V4 run `format` first; step 5 and V3 cite a
   result as `evidence` prints it; step 5 and V1 call the work done only on
   `evidence` exiting 0 or the person's acceptance; V5 reports a result bound
   to no tree with its command, exit status and output (REQ-0148).
2. The implement step: step 4 cites the record and tree id where `meow-verbs`
   is installed and the command, exit status and output where it isn't, and
   I7 asks for the record and tree id (REQ-0148). SPC-1090 states it.
3. The checks above.

`meow-verbs` stays at 0.4.0, unreleased since TSK-2270, and `meow-flow` moves
to 0.32.1.

## Left alone

The program, which TSK-2270 changes.
