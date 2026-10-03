---
id: TSK-4710
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2440
closes: [REQ-2738, REQ-2740]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Keep the method out of an initialised constitution, and ask the design step for rules that pull against each other

`/meow-flow:init` writes a repository's constitution from the template and
what the repository holds, with no step, rule or template of the method in
it, and the design step asks of each decision adding a constitution rule
whether it pulls against one already there, as SPC-1220 states. One task, one
branch, one pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given `plugins/meow-flow/templates/constitution.md`, when a fixture reads
   it, then it names none of the seven steps and quotes no rule of the method
   skill (REQ-2740). Closed by: a fixture under `plugins/meow-flow/tests/`
   naming REQ-2740, seen failing first.
2. Given the init skill, when the fixture reads it, then it tells the model to
   write `CLAUDE.md` from the template and the repository's own files and to
   copy nothing from the method into it (REQ-2740). Closed by: the same
   fixture.
3. Given `steps/design.md`, when the fixture reads it, then it asks, for each
   decision adding a constitution rule, whether the rule pulls against one
   already there, and says two that do become one rule with its exception
   stated (REQ-2738). Closed by: the same fixture naming REQ-2738.

## What to do

Change the constitution template, the init skill and
`plugins/meow-flow/skills/method/steps/design.md` in the unit's prompt form,
held to SPC-1030 and the unit's `budget.toml`.

## Depends on

- TSK-4760 (not blocking): both add a question to `steps/design.md`, and whichever lands second rebases its rule.

## Evidence

Not yet.

## Left alone

This repository's `CLAUDE.md`, which TSK-4730 cuts.
