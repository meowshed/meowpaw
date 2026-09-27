---
id: TSK-2320
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1490
closes: [REQ-1664]
issue: 535
projected: 2938ffea9b6a
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

Closes REQ-1664. `meow-verbs evidence format lint test` exits 0:

```text
format: passed, record 79fc1c75e4e9, current at tree 3190db84228c
lint: passed, record a06a0df28889, current at tree 3190db84228c
test: passed, record 4604deb7850e, current at tree 3190db84228c
```

Each criterion's check:

1. `VerificationKind.test_a_kind_outside_the_four_is_reported_on_drafts_and_approved_records`,
   seen failing on the program before the rule.
2. `VerificationKind.test_each_of_the_four_passes`, which passed before the
   rule as well, since it holds that the rule adds no false finding.
3. The `test` verb runs `paw check` on the project record, which reports 0
   findings, withdrawn requirements included.

`meow-flow` moves to 0.33.1.

## Left alone

REQ-1662, which ADR-1510 leaves open.
