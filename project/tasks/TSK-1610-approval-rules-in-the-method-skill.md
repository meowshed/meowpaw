---
id: TSK-1610
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1170
closes: [REQ-0390, REQ-0400]
issue: 244
---

# The method skill stops at approval and never infers one

The method skill stops at approval and never infers one, as ADR-1170 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given the `method` skill, when the prompt check runs, then it passes, and its rules block carries both rules. Closed by: the prompt check's output and the rule labels.
2. Given the unit's budget, when `check_budget` runs, then meow-method stays within 500 characters. Closed by: its output.

## What to do

Add to the `method` skill's rules that a step stops after producing an artifact needing approval, and that silence, a change of subject or an unrelated instruction is never approval, each with its reason. Keep within the unit's budget, because the rules sit in the body, not the description.

## Depends on

Nothing. ADR-1170 is approved.

## Evidence

Not yet.

## Left alone

Running the frozen check in continuous integration, which ADR-1170 leaves.
