---
id: TSK-1920
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1300
closes: [REQ-3110, REQ-3112, REQ-3128]
issue:
---

# The onboard command reads the forge history and recovers what it states

The onboard command reads the forge history and recovers what it states, as ADR-1300 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given the onboard command, when the trace is read, then each requirement this task closes maps to a labelled rule that exists in it. Closed by: the trace table and a script finding each label.
2. Given the repository, when `check_standalone.py` runs, then it passes. Closed by: its output.

## What to do

Add a step to `/meow-method:onboard` reading `meow-github history` where the command exists, and rules recovering stated requirements and decisions as drafts citing their addresses, and reporting the history as unread, naming `meow-github`, where it isn't installed. Record the trace under Evidence.

## Depends on

Nothing. ADR-1300 is approved.

## Evidence

Not yet.

## Left alone

Measuring whether a model recovers statements faithfully, which waits for
evaluation.
