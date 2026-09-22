---
id: TSK-1260
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1020
closes: [REQ-1138]
issue: 69
---

# Remove every instruction the loop shows has no effect

One task, one branch, one pull request, one review.

## What to do

Run every shipped prompt through the loop with a candidate per instruction
that removes it, on Sonnet 5 and Opus 5.5 (REQ-1138). An instruction whose
removal holds the delta on both models and lowers the token cost goes. The
rest stay, and the table shows why.

## Depends on

TSK-1230, TSK-1240 and TSK-1250, because it measures the prompts in the form
those tasks leave them.

## Evidence

Not yet. The task closes on one table per prompt, a row per removal
candidate, each with its delta on both models, its token cost and whether it
landed.

## Left alone

Adding instructions. A gap this finds is a candidate for the task that owns
the prompt.
