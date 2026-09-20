---
id: RES-0213
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0017, RES-0201
---

# The `budgets` skill

## Summary

Non-functional baselines kept in one place, each carrying the reason for its
number, with a specification refining them and restating none of them. The
donor standard supplies the refinement mechanism and the rule that exceeding a
budget is a finding and never a description of how the system works. The
reliability literature adds what it lacks: perfection is the wrong target, and
a budget with slack is a decision-making instrument where an absolute is only a
pass or a fail.

Research for one design lens: latency, cost and size baselines kept in one
place per repository, each carrying the reason for its number.

Its siblings are the other four lenses, listed in
[RES-0017-design-lenses.md](RES-0017-design-lenses.md).

## The question

The donor standard exists because eleven specifications carried their own
non-functional requirements and none could say whether a number was consistent
with the others.

That is the failure: not an absent budget, but several, each defensible alone
and incoherent together.

## Method

The donor standard was read in full from its working tree on 2026-09-20 and
quoted directly, including the form of a justification attached to a number.

The published reliability material was fetched and read for the error-budget
mechanism and for the statement that a perfect target is not a target, which is
quoted in full.

Nothing was measured. No budget of this project's was set or tested, so the
application to the harness's own numbers is a proposal.

## Findings

### Refinement, and never restatement

A specification refines a shared baseline and reinvents none of it. Stricter is
allowed if stated; looser needs a reason.

That single rule does the work. It makes the baseline the default answer, makes
a deviation a visible decision, and makes the question _is this number
consistent with the others_ answerable by reading one file.

### Budgets cover the paths where a person is waiting

A machine waiting costs nothing. So a latency budget applies where someone is
in front of it, and not to a background job whose duration nobody experiences.

This prevents the common waste of optimising something to a target no user
perceives - which is the same instinct the reliability literature warns about
from the other direction.

### Exceeding a budget is a finding, never how the system works

Without this rule, every budget decays into a description of current behaviour:
the number is adjusted to what was measured, and the budget becomes a label.

Stated as a rule, an exceeded budget is a finding with a decision attached -
fix it, or change the number and say why.

### A budget carries its reason, or it is negotiated away

The donor material's example is the form to copy, and the number in it belongs
to that service: _"3 s, and 5 s at the 95th - someone is at a till with a bag
in one hand."_

A budget with a reason attached survives an argument, because the argument has
to address the reason. A budget without one is a preference, and preferences
lose to schedules.

### The reliability literature adds the part the donor standard lacks

Two ideas transfer directly and neither is in the donor material.

A target of perfection is the wrong target. The published statement is blunt:
_"100% is probably never the right reliability target: not only is it
impossible to achieve, it's typically more reliability than a service's users
want or notice."_ It describes increasing reliability past that point as _worse
for a service and its users rather than better_, because it constrains feature
work and costs disproportionately.

The gap between the target and the measurement is itself a budget, and it
can be spent. An error budget is the difference between the objective and the
observed behaviour over a period; while it remains, changes ship, and when it
is exhausted, the work turns to reliability.

The transferable part is not the arithmetic. It is that **a budget with slack
is a decision-making instrument**, where a budget stated as an absolute is only
a pass or a fail. The first tells a team what to do this week; the second tells
them whether they are in trouble.

### What this means for the harness's own budgets

The harness has budgets of its own, and this lens applies to them first. A
skill body's size, the token cost of a description loaded on every turn, the
time a gate may take, and the number of forge requests an epic may spend.

Each of those shares one property: the number counts for less than whether a
deviation is a finding. At least one of them, the forge quota, is a hard
external limit nobody here chose, which the baseline distinguishes: **a budget
the project chose and a limit somebody else imposed behave differently when
exceeded.**

## Conclusions

1. Non-functional baselines live in one place per repository, and a
   specification refines them and restates none of them. 2. Stricter than the
   baseline is allowed when stated; looser needs a reason. 3. A budget carries
   the reason for its number, or it is a preference and loses to a schedule. 4.
   Budgets cover paths where a person is waiting, because a machine waiting
   costs nothing. 5. Exceeding a budget is a finding with a decision attached,
   never adopted as how the system works. 6. A target of perfection is not a
   target, since it is unachievable and usually more than anyone notices. 7. A
   budget with slack is a decision-making instrument, where an absolute is only
   a pass or a fail. 8. A chosen budget and an imposed limit are distinguished,
   because they behave differently when exceeded. 9. The lens applies to the
   harness's own numbers first: skill body size, the permanent cost of a
   description, gate duration, and forge quota.

## Sources

All read 2026-09-20.

- `~/workspace/meowhub/docs/standards/budgets.md` - the reason the standard
  exists; refinement of a shared baseline with stricter allowed if stated and
  looser needing a reason; budgets covering paths where a person waits; an
  exceeded budget as a finding and never a description; and the form of a
  justification attached to a number. - [Embracing
  risk](https://sre.google/sre-book/embracing-risk/) - that 100% is probably
  never the right reliability target, being both unachievable and more than
  users want or notice; that increasing reliability past that point makes
  things worse; and the error budget as the difference between an objective and
  the measurement, spent on change while it remains. -
  [RES-0017-design-lenses.md](RES-0017-design-lenses.md) - the five lenses and
  what survived the strip from their donor project.
