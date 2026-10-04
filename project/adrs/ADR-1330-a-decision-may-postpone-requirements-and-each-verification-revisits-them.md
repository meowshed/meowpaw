---
id: ADR-1330
artifact: adr
status: done
revised: 2026-09-26
addresses: [REQ-0325]
supersedes: []
---

# 1330. A decision may postpone requirements, and each verification revisits them

## Decision

A decision may carry `postpones:`, the requirements it decides not to realise
now, beside or in place of `addresses:`, and says under What would reverse it
when they should be taken up. The program treats a postponement as a state it
derives, never a status it stores:

- A requirement an approved decision postpones, and no task closes, is
  derived as postponed. `show` names the decision, and `status` counts the
  postponed requirements beside the other four states.
- A decision that only postpones needs no epic and no specification for what
  it postpones: `status` shows it as postponing, with its count, and `check
coverage` asks nothing of it.
- A decision carries `addresses:` or `postpones:`, at least one, where it
  used to be required to carry `addresses:`.
- The verify step lists every postponement and its condition whenever an epic
  is verified, and asks whether the condition now holds.

After this decision a person can postpone requirements with one reviewed
record and see them counted as postponed, not as forgotten. What still doesn't
work: nothing judges whether a condition holds, which stays a person's call at
each verification.

## Why

RES-0069 found that a requirement deferred with a reason is recorded as
deferred and then never looked at again, because no task waits on it, and that
verifying an epic is the only point at which anything looks at it again. A
requirement is approved and frozen, so its status can't carry the deferral;
the decision to defer is a choice, and a choice is a decision record.

The strongest objection: a `postponed` status on the requirement would be
simpler to read. It would be a stored observed state, which REQ-0586 forbids,
and it would need rewording an approved record, which the method forbids;
derived from a decision, it goes away the moment a task closes the
requirement.

## Alternatives

| Option                                         | Better at                         | Why it lost                                                |
| ---------------------------------------------- | --------------------------------- | ---------------------------------------------------------- |
| A decision's `postpones`, derived as a state   | Reviewed, reversible, never stale | Chosen                                                     |
| A `postponed` status on the requirement        | Visible in the file               | Rewords an approved record and stores a derived state      |
| A list of postponed requirements in the README | Nothing to build                  | Checked by nothing, and goes stale when a task closes one  |
| Do nothing                                     | Costs nothing                     | A postponed requirement reads as one nobody has considered |

## What it costs

A relation, a rule replacing a required value, a derived state in `show` and
`status`, a position in `status`, and a rule in the verify step.

## What would reverse it

- Postponements pile up unrevisited across verifications, and they move into
  a review of their own.

## Consequences

- `postpones:` is a relation a decision may carry.
- `status` counts postponed requirements and shows a postponing decision.
- The verify step revisits every postponement.

## How I will know it was realised

1. Fixtures show a requirement an approved decision postpones derived as
   postponed by `show` and counted by `status`, and no longer postponed once a
   task closes it.
2. A fixture shows a decision that only postpones passing `check`, with no
   epic and no specification, and one with neither `addresses` nor
   `postpones` reported.
3. The verify step carries a rule revisiting postponements, traced in the
   task.
4. Every requirement ADR-1330 addresses lands in exactly one closed task.

## What this does not settle

- Judging whether a postponement's condition holds.
