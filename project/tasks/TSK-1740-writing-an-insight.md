---
id: TSK-1740
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1220
closes: [REQ-0570, REQ-0572, REQ-0577, REQ-0578, REQ-0580]
issue: 292
---

# The method says when to write an insight and how to find one

The method says when to write an insight and how to find one, as ADR-1220 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given the skill and the implement step, when the trace is read, then each requirement this task closes maps to a labelled rule that exists in the file named. Closed by: the trace table and a script finding each label.

## What to do

Add rules to the `method` skill: write an insight only when something was learned, never on a schedule, with nothing learned an ordinary outcome; keep activity in the history; find an insight with `find` when the work needs it, never loaded by default. Add a rule to `steps/implement.md`, and a line to the task template, recording a prediction under Acceptance criteria before the work that tests it. Record the trace under Evidence.

## Depends on

Nothing. ADR-1220 is approved.

## Evidence

Each requirement this task closes is carried by a labelled rule in the file
named, and no rule names a requirement:

| Requirement | Carried by                  |
| ----------- | --------------------------- |
| REQ-0570    | M12 in `SKILL.md`           |
| REQ-0572    | M11 in `SKILL.md`           |
| REQ-0577    | M11 in `SKILL.md`           |
| REQ-0578    | I12 in `steps/implement.md` |
| REQ-0580    | M13 in `SKILL.md`           |

The task template's Acceptance criteria now asks for the predicted number
before the work, beside I12, and `check frozen` holds an approved task's
criteria. The session's only hook runs `meow-method status --waiting`, which
reads no insight, so nothing loads insights by default. A script found all
5 traced labels in their files. Whether the model follows the rules is
measured by evaluation, which is postponed.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
