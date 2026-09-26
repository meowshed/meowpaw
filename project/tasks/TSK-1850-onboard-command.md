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

Not yet.

## Left alone

Measuring whether a model recovers statements faithfully, which waits for
evaluation.
