---
id: TSK-2010
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1330
closes: [REQ-0325]
issue: 395
projected: a98413e55d12
---

# A decision postpones requirements, and each verification revisits them

A decision postpones requirements, and each verification revisits them, as
ADR-1330 decides. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given an approved decision postponing a requirement no task closes, when `show` and `status` run, then the requirement reads as postponed by that decision and is counted. Closed by: a fixture.
2. Given a task closing that requirement, when `show` runs, then it no longer reads as postponed. Closed by: a fixture.
3. Given a decision that only postpones, when `check` and `status` run, then it passes with no epic and shows as postponing; and given a decision with neither field, then `check rules` reports it. Closed by: fixtures.
4. Given the verify step, when the trace is read, then REQ-0325 maps to a labelled rule in it. Closed by: the trace and a script finding the label.

## What to do

Add `postpones` to the layout's relations, replace the decision's required `addresses` with the rule `addresses-or-postpones`, derive the postponed state in `show` and `status`, show a postponing decision's position, skip what it postpones in `check coverage`, and add the verify step's rule.

## Depends on

Nothing. ADR-1330 is approved.

## Evidence

`postpones` joins the layout's relations, and a decision's required
`addresses` becomes the rule `addresses-or-postpones`. Four fixtures, each
failing against a stub that returns nothing:

- A second requirement postponed by an approved decision that addresses
  nothing reads `postponed by` that decision in `show`; `status` shows the
  decision as "postponing: 1 requirement, revisited at each verification" and
  counts "1 postponed"; `check rules` and `check coverage` pass with no epic
  and no specification for it.
- Once a task closes that requirement, `show` reads it as in a task not yet
  done, and no longer as postponed.
- A decision with empty `addresses` and empty `postpones` fails `check rules`
  at its line, as does the clean record's decision with its `addresses`
  emptied; that fixture used to test the required value, which the rule
  replaces.

The verify step gains V13, listing every postponement with its condition at
each verification and asking whether it now holds. This repository's record
passes every check with the new layout.

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 123 tests in 9.860s
OK
```

## Left alone

Judging whether a postponement's condition holds, which ADR-1330 leaves to a
person.
