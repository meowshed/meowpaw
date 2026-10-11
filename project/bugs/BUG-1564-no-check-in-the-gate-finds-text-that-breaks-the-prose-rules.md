---
id: BUG-1564
artifact: bug
status: approved
severity: minor
violates: REQ-2712
enters: design
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# No check in the gate finds text that breaks the prose rules the gate holds, so `meow-prose-gate`'s `check` rule is held by the hook and by review alone

SPC-1240 holds each rule three times: a hook, a check in the gate and an
instruction. For `check`, which stops a publish whose text breaks a rule the gate holds, the gate holds nothing.

## Reproduction

Seen at revision `224c9462`.

1. Read the tasks of `mise.toml` and the jobs of `.github/workflows/ci.yml`
   for a check that finds a tree or a history that breaks the rule `check`
   holds.
2. Read the README of `meow-prose-gate` under `## Hooks`.

## What the system does

A document or a record merged with a banned phrase fails no stage of `mise run all`, and only the review the method asks for reads it. The unit's README names no check, and its sentence names this defect
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
