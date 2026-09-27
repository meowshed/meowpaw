---
id: TSK-2280
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1460
closes: [REQ-0148]
issue:
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

Not yet.

## Left alone

The program, which TSK-2270 changes.
