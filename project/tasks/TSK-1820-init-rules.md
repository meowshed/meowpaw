---
id: TSK-1820
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1250
closes: [REQ-1554, REQ-1561, REQ-1562, REQ-1564]
issue: 320
---

# The init command reports before it writes and chooses nothing

The init command reports before it writes and chooses nothing, as ADR-1250 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given the command, when the trace is read, then each requirement this task closes maps to a labelled rule that exists in it. Closed by: the trace table and a script finding each label.

## What to do

Give the command its rules: report which verbs resolve first; report an inconsistent convention as its variants with their counts; record the existing layout and templates; and on a second run show what would change in an existing profile and write nothing without agreement. Record the trace under Evidence.

## Depends on

TSK-1810, which writes the command these rules join.

## Evidence

Each requirement this task closes is carried by a labelled rule in the init
command, and no rule names a requirement:

| Requirement | Carried by                   |
| ----------- | ---------------------------- |
| REQ-1554    | N2 in `skills/init/SKILL.md` |
| REQ-1561    | N3 in `skills/init/SKILL.md` |
| REQ-1562    | N4 in `skills/init/SKILL.md` |
| REQ-1564    | N5 in `skills/init/SKILL.md` |

Step 3 now stops at a diff where a profile exists, and step 5 reports the
verbs first, so the steps follow N2 and N5. A script found all 4 traced
labels. Whether the model follows the rules is measured by evaluation, which
is postponed.

## Left alone

Onboarding from existing documents, which ADR-1250 leaves to the next
decision.
