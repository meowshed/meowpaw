---
id: BUG-1565
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

# No check in the gate finds a run whose turn ended with work left, so `meow-loop`'s `stop` rule is held by the hook alone

SPC-1240 holds each rule three times: a hook, a check in the gate and an
instruction. For `stop`, which blocks the end of a turn while a run has work
left, the gate holds nothing.

## Reproduction

Seen on the trunk after pull request 1046.

1. Read the tasks of `mise.toml` and the jobs of `.github/workflows/ci.yml`
   for a check that finds a run ended with work left.
2. Read the README of `meow-loop` under `## Hooks`.

## What the system does

A run whose turn ended while requirements stayed open is found by nothing in
the gate. The unit's README names no check for `stop`.

## What it should do, and why

REQ-2712 says each hook that stops a call, or the turn, names the gate check
that holds the same rule and the skill that explains it, and that a rule with
no gate check is a finding against the unit until one exists.

## Triage

It enters at design, because which check holds the rule, and where it runs, is
a decision. Severity is minor, because the hook still blocks the end of a turn
in a session.

## Closed by

A check in `mise.toml` or the CI workflow that fails a tree or a history
breaking the rule, named in the unit's README sentence.
