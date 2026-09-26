---
id: TSK-1850
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1260
closes:
  [
    REQ-1540,
    REQ-1542,
    REQ-1544,
    REQ-1546,
    REQ-1548,
    REQ-1550,
    REQ-1552,
    REQ-1558,
    REQ-3092,
    REQ-3094,
  ]
issue: 330
---

# The onboard command recovers what a repository is and invents nothing

The onboard command recovers what a repository is and invents nothing, as ADR-1260 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given the command, when its front matter is read, then it carries `disable-model-invocation: true`. Closed by: a search.
2. Given the command, when the trace is read, then each requirement this task closes maps to a labelled rule that exists in it. Closed by: the trace table and a script finding each label.

## What to do

Write `skills/onboard/SKILL.md`, a command with `disable-model-invocation`, whose steps read the repository and write the recovered vision, specifications and missing constitution, and the report from its template, and whose rules carry the requirements this task closes. Record the trace under Evidence.

## Depends on

TSK-1840, whose report template the command writes from.

## Evidence

`skills/onboard/SKILL.md` carries `disable-model-invocation: true`, found
1 time, so only a person starts it. Each requirement this task closes is
carried by a labelled rule in it, and no rule names a requirement:

| Requirement | Carried by                       |
| ----------- | -------------------------------- |
| REQ-1540    | B1 in `skills/onboard/SKILL.md`  |
| REQ-1542    | B2 in `skills/onboard/SKILL.md`  |
| REQ-1544    | B3 in `skills/onboard/SKILL.md`  |
| REQ-1546    | B4 in `skills/onboard/SKILL.md`  |
| REQ-1548    | B5 in `skills/onboard/SKILL.md`  |
| REQ-1550    | B6 in `skills/onboard/SKILL.md`  |
| REQ-1552    | B7 in `skills/onboard/SKILL.md`  |
| REQ-1558    | B10 in `skills/onboard/SKILL.md` |
| REQ-3092    | B8 in `skills/onboard/SKILL.md`  |
| REQ-3094    | B9 in `skills/onboard/SKILL.md`  |

Its steps check for a profile first and send a repository without one to
`/meow-method:init`, run `meow-method check` over what they wrote, and stop at
the draft report. A script found all 10 traced labels. Whether the model
follows the rules is measured by evaluation, which is postponed.

## Left alone

Measuring whether a model recovers statements faithfully, which waits for
evaluation.
