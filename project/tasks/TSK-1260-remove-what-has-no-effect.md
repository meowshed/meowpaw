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

Postponed by the owner on 2026-09-24, before any run, for two reasons. As
written, the task runs one removal candidate per instruction: about 85 across
the style, the skill, the reviewer and the gate, and about 18,000 sessions for
the skill alone. And the case sets cannot yet see most single instructions:
the overall delta moves by 0.05 to 0.12 through noise, a single rule touches
one or two of fifteen cases, and three of `meow-core`'s four cases score the
same in both arms on Opus 5.5. A removal that "holds the delta" would then
mean a rule the cases cannot see, not a rule with no effect, and REQ-1138
would remove most of the standard.

The plan proposed for when it resumes, which amends this task and so needs
its own approval: remove one rule group at a time, ten runs per arm, and look
rule by rule only inside a group whose removal holds on both models; give
`meow-core` cases that discriminate on Opus 5.5 before its ten rules are
removed one at a time; and measure, alongside, whether the skill should load
its patterns for every text, the question TSK-1180 left open.

## Left alone

Adding instructions. A gap this finds is a candidate for the task that owns
the prompt.
