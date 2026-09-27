---
id: TSK-2320
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1490
closes: [REQ-1664]
issue:
---

# `paw check rules` holds each requirement's `verification` to the four kinds

The rule `verification-kind` reports a requirement whose `verification` isn't
`static`, `behavioural`, `evaluation` or `judgement`, on every requirement.
One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a draft and an approved requirement whose `verification` is `statc`,
   when `paw check rules` runs, then it reports each, naming the four kinds.
   Closed by: a fixture naming REQ-1664, seen failing first.
2. Given a requirement with each of the four kinds, when it runs, then it
   passes. Closed by: a fixture naming REQ-1664.
3. Given the project record, when `paw check` runs, then it exits 0. Closed
   by: its output.

## What to do

Add the rule to the native tool's `record` feature, list it in
`plugins/meow-flow/lib/layout.toml` for requirements, name it on the unit's
page, and move `meow-flow` to its next patch version.

## Depends on

Nothing. ADR-1510 is approved.

## Evidence

Not yet.

## Left alone

REQ-1662, which ADR-1510 leaves open.
