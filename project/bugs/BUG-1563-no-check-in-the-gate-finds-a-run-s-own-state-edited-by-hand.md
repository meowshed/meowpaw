---
id: BUG-1563
artifact: bug
status: done
severity: minor
violates: REQ-2712
enters: design
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# No check in the gate finds a run's own state edited by hand, so `meow-loop`'s `guard` rule is held by the hook alone

SPC-1240 holds each rule three times: a hook, a check in the gate and an
instruction. For `guard`, which stops a write into a run's own state or a status the run can't give, the gate holds nothing.

## Reproduction

Seen on the trunk after pull request 1046.

1. Read the tasks of `mise.toml` and the jobs of `.github/workflows/ci.yml`
   for a check that finds a tree or a history that breaks the rule `guard`
   holds.
2. Read the README of `meow-loop` under `## Hooks`.

## What the system does

A run's `run.toml` or `log.jsonl` edited outside a session is found by nothing before the run's program reads it. The unit's README names no check, and its sentence names this defect
instead.

## What it should do, and why

REQ-2712 says each hook that stops a call names the gate check that holds the
same rule and the skill that explains it, and that a rule with no gate check
is a finding against the unit until one exists. A rule only a hook holds is
safe only for as long as the hook runs.

## Triage

It enters at design, because which check holds the rule, and where it runs,
is a decision: it may be a `mise` task, a CI job or a verb of the unit.
Severity is minor, because the hook still stops the call in a session.

## Closed by

A check in `mise.toml` or the CI workflow that fails a tree or a history
breaking the rule, named in the unit's README sentence in place of this defect.
