---
id: BUG-1562
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

# No check in the gate finds a change to how the repository is governed, and the unit ships no skill that explains the rule, so `meow-github`'s `governance-guard` is held by the hook alone

SPC-1240 holds each rule three times: a hook, a check in the gate and an
instruction. For `governance-guard`, which stops a `gh` command that changes how the repository is governed, the gate holds nothing.

## Reproduction

Seen on the trunk after pull request 1046.

1. Read the tasks of `mise.toml` and the jobs of `.github/workflows/ci.yml`
   for a check that finds a tree or a history that breaks the rule `governance-guard`
   holds.
2. Read the README of `meow-github` under `## Hooks`.

## What the system does

A governance change made from a terminal outside a session is found by nothing in the gate, and no skill in `plugins/meow-github/` tells the model why the hook asks. The unit's README names no check, and its sentence names this defect
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
breaking the rule, and a skill in the unit that explains it, both named in the
unit's README sentence.

## Tasks

- [x] T-001 TSK-5400 fail a workflow that changes governance, and say why in a skill (done: pull request 1047)
