---
id: TSK-1160
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes: [REQ-1050, REQ-1056, REQ-1057, REQ-1058, REQ-1060]
issue: 53
---

# State a size budget for every unit, and measure it

One task, one branch, one pull request, one review.

## What to do

Give `meow-core`, `meow-prose` and `meow-prose-gate` a stated size budget each
(REQ-1056). The budget covers what loads on every turn: the description and
anything else permanently in context. Nothing permanent goes beyond what a
model needs to decide whether the unit is relevant (REQ-1050).

Set each number from the first measurement of the unit as it ships, and record
the measurement beside the number. ADR-1010 leaves the numbers open because a
number guessed before measuring is arbitrary.

Write a check that reads every shipped unit, measures it against its stated
budget, and fails naming the unit and the overrun. It also fails on a
description longer than the platform's cap of 1,536 characters (REQ-1060). An
overrun is a defect and not a judgement call (REQ-1058). Run the check in the
gate, and see it fail first on a unit given a budget smaller than itself
(REQ-2072).

Material over a budget moves into supporting files, where it loads when it is
needed (REQ-1057). The check never passes a unit that met its budget by
dropping an obligation, which is why the budget covers the permanent load and
not the whole unit.

## Depends on

TSK-1120 and TSK-1140, because a budget covers what a unit loads, and the three
units have to exist before anything can be measured against one.

## Evidence

`tools/check_budget.py` runs in the gate as `mise run budget`, and every unit
states its budget in `budget.toml`, with the measurement beside the number.
`meow-core` and `meow-prose` landed theirs in #96, and `meow-prose-gate` lands
its own with the unit in #93:

```text
$ python3 tools/check_budget.py
meow-core: 3945 of 4200 characters on every turn
meow-prose: 576 of 700 characters on every turn
meow-prose-gate: 0 of 0 characters on every turn
3 units, 0 budget failures

$ python3 tools/check_budget.py      # meow-prose given a budget of 500
meow-prose: loads 576 characters on every turn, 76 over its budget of 500
2 units, 1 budget failures
```

Before the budgets existed the check failed both units for stating none. The
permanent load is counted in characters, because that needs no model and gives
the same number twice. The gate is a prompt hook, which loads only when it
fires, so its budget is 0. REQ-1050, REQ-1056, REQ-1057, REQ-1058 and REQ-1060
are closed.

## Left alone

What a unit says. The check counts size and reads no prose, so it never becomes
the pattern over the text that REQ-3186 forbids.
