---
id: BUG-1412
artifact: bug
status: approved
severity: minor
violates:
enters: requirements
found: 2026-10-04
revised: 2026-10-04
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Both task-runner packs claim the skill name tasks

The mise pack and the go-task pack each ship a skill named `tasks`. Pi
loads every unit's skills into one flat namespace, so with both packs
installed Pi silently keeps the first and drops the rest, and the session
reports the collision at startup. The name also misnames the skill
against the method's own vocabulary, where `tasks` is the record kind the
`project/tasks/TSK-NNNN` files hold.

## Reproduction

Pi 1.0.2 on macOS 15, the packages installed from npm with both
task-runner packs:

1. `pi install npm:@meowshed/meow-mise && pi install npm:@meowshed/meow-gotask`.
2. Start a session.
3. The startup report names the collision: `"tasks" collision: kept
npm:@meowshed/meow-mise (user), skipped npm:@meowshed/meow-gotask`.

## What the system does

Which pack's skill survives depends on load order, not on the repository
the session works in, and nothing tells the model the other pack's skill
was dropped.

## What it should do, and why

A skill's name is unique across the units, and it names the tool or the
capability it teaches, never a kind of record the method already claims:
a name two packs share is a collision the loader resolves silently, and a
name the record tree already uses misnames the skill. The two skills are
renamed for their tools, `mise` and `gotask`, and SPC-1300 states the
rule the rename follows.

## Triage

Enters at implement, because the rule the rename follows is one sentence
in the specification the packs already live under, and the rename touches
two skills and their budgets. Minor, because each pack installs alone in
every repository that uses its runner, so the collision needs both packs
on one machine and only misroutes which instructions load.

## Closed by

The rename to `mise` and `gotask`, shipped in meow-mise 0.2.2 and
meow-gotask 0.2.2.
