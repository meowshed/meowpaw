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

`plugins/meow-method/skills/method/SKILL.md` holds what every step shares and
the three caps and rules, and `steps/<step>.md` holds each of the nine steps:
its input, the template it writes from, its content rules and the step that
picks it up. `plugins/meow-method/skills/run/SKILL.md` is the driver, marked
`disable-model-invocation: true`, so only a person invokes it and the platform
doesn't list it on every turn.

`tools/check_budget.py` counted the driver's description, which the platform
doesn't load: its skills documentation says such a skill's "Description not in
context". That was a false positive in the check, and the check now skips a
skill marked so.

```text
$ python3 tools/check_prompts.py
50 shipped prompts, 0 failures
$ python3 tools/check_budget.py
meow-method: 385 of 500 characters on every turn
7 units, 0 budget failures
```

`docs/meow-method.md` describes the steps, the driver, `status`, `ready` and
`template`, and `meow-method` is 0.2.0. Whether the skill routes on its
description is left for evaluation, as ADR-1130 says.

## Left alone

Measuring whether the skill routes on its description, which waits for evaluation.
