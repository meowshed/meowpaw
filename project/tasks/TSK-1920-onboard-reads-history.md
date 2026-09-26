---
id: TSK-1920
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1300
closes: [REQ-3110, REQ-3112, REQ-3128]
issue: 365
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

Each requirement this task closes is carried by a labelled rule in the onboard
command, and no rule names a requirement:

| Requirement | Carried by                       |
| ----------- | -------------------------------- |
| REQ-3110    | B13 in `skills/onboard/SKILL.md` |
| REQ-3112    | B14 in `skills/onboard/SKILL.md` |
| REQ-3128    | B15 in `skills/onboard/SKILL.md` |

Step 2 runs `meow-github history` where the command exists, as a bare command
found 1 time, never by a path into that unit, and step 3 writes the
recovered drafts. A script found all 3 traced labels. Whether the model
follows the rules is measured by evaluation, which is postponed.

```text
$ python3 tools/check_standalone.py
88 unit files, 0 paths leaving their unit
```

## Left alone

Measuring whether a model recovers statements faithfully, which waits for
evaluation.
