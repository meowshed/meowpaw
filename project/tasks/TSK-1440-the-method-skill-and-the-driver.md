---
id: TSK-1440
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1100
closes:
  [
    REQ-0190,
    REQ-0192,
    REQ-0194,
    REQ-0196,
    REQ-0202,
    REQ-0204,
    REQ-0208,
    REQ-0532,
    REQ-2630,
    REQ-2632,
  ]
issue: 191
---

# The method skill and the command that drives the chain

One task, one branch, one pull request, one review.

## What to do

Write `plugins/meow-method/skills/method/SKILL.md` with what every step shares, and `steps/<step>.md` for each of the nine steps: its input, its gate command, what it writes from which template, and the step that picks it up. Write `plugins/meow-method/skills/run/SKILL.md`, a command a person types, which runs `status`, runs the next step and stops at the next gate, reporting where it stopped and what the next invocation does. State the caps: three clarifying questions and two rounds of self-review. Raise the unit's budget by the `method` skill's description and add the skills to `docs/meow-method.md`.

## Depends on

TSK-1420 and TSK-1430, because the steps call the program and write from the templates.

## Evidence

Not yet.

## Left alone

Measuring whether the skill routes on its description, which waits for evaluation.
