---
id: BUG-1561
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

# No check in the gate finds a commit whose message or signature fails the convention, so `meow-git`'s `push-guard` rule is held by the hook alone

SPC-1240 holds each rule three times: a hook, a check in the gate and an
instruction. For `push-guard`, which stops a push of a commit whose message or signature fails the declared convention, the gate holds nothing.

## Reproduction

Seen at revision `224c9462`.

1. Read the tasks of `mise.toml` and the jobs of `.github/workflows/ci.yml`
   for a check that finds a tree or a history that breaks the rule `push-guard`
   holds.
2. Read the README of `meow-git` under `## Hooks`.

## What the system does

The CI workflow's one commit check finds a credited tool and no other part of the convention, so a commit that meets the hook's rule only because the hook ran isn't found when it didn't. The unit's README names no check, and its sentence names this defect
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
