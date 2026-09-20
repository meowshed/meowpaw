---
id: RES-0212
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0017, RES-0033
---

# The `failure-vocabulary` skill

## Summary

Naming every state in which the system is not working, giving each a next
step and exactly one audience. The failure this prevents is not an unhandled
case but a system whose parts describe the same condition in incompatible
words, so nobody can tell whether two reports are one problem. Applied to this
harness it is immediately concrete: five distinct not-working states look alike
in a report, and collapsing any two of them loses the action.

Research for one design lens: naming every state in which the system is not
working, giving each one a next step and exactly one audience.

Its siblings are the other four lenses, listed in
[RES-0017-design-lenses.md](RES-0017-design-lenses.md).

## The question

The donor standard exists because eleven specifications each enumerated their
own edge cases - which was right - and between them invented a dozen ways to be
broken without ever agreeing on the names.

That is the failure this lens prevents: not an unhandled case, but a system
whose parts describe the same condition in incompatible words, so that nobody
can tell whether two reports are one problem.

## Method

The donor standard was read in full from its working tree on 2026-09-20 and
is quoted directly, including its stated reason for existing and its phrasing
rule.

The five harness states enumerated at the end were collected from this
project's own tool research, and from none of the donor material, which is why
that finding is specific to this corpus.

No external source was consulted for this lens, which is its limitation: the
three rules are one project's, and we argue their generality, having found it
nowhere else.

## Findings

### Three rules, all universal

1. Nothing fails silently. A state that is reachable and not on the list is
   a defect, regardless of whether anything crashed.
2. Every failure names its next step. _Something went wrong_ is not a
   state; it is the absence of one.
3. Every failure has exactly one owner. A user is never shown
   infrastructure; an operator is never left guessing which component broke.

The third is the one that makes the other two tractable. Once each state has a
single audience, who reads it decides what it must contain, and what the system
knows decides nothing.

### The form is a table per audience

The name, when it happens, what that audience gets, and where the state lives.

The discipline of naming - _stale action_, _queue ceiling_, _drift detected_,
_integrity mismatch_ - is what stops parts of the system inventing parallel
vocabularies. Once a name exists, the next specification uses it and coins no
synonym.

The names are worth more than the table. A shared name makes two reports
comparable; a table makes one report complete.

### A deliberate collapse is documented as deliberate

Where the system cannot distinguish two conditions, that is written down as a
deliberate indistinguishability, so nobody reads it as a gap.

The donor material does this for a schema violation against an unparsed
capture. Saying so is what stops a future reader treating the collapse as a
bug and 'fixing' it into two states the system has no way to tell apart.

### The fault is the system's

The phrasing rule: a failure message describes what the system could not do,
never what the user did wrong. This is not politeness. A message that blames
the user ends the investigation, and the investigation is the point.

### This lens and the unresolved verb are the same rule

The harness already requires an unresolved verb to be reported, and guessed at
never. That is rule one applied to a specific case.

What this lens adds is that the requirement becomes a design obligation rather
than a behaviour of one component: every part names its states, and the
vocabulary is shared, so _unresolved_, _unavailable_, _untrusted_ and _stale_
mean one thing each across the whole system.

That matters here concretely. This project's tool research produced at least
five distinct not-working states that look alike in a report: a verb that
cannot resolve, a verb whose tool is absent, a configuration that was not
trusted, a task skipped as fresh, and a check that could not reach the network.
Collapsing any two of them loses the action.

## Conclusions

1. Every failure state is named, and a reachable state that is not on the list
   is a defect. 2. Every failure names its next step, since a message with none
   marks the absence of a state, and no state at all. 3. Every failure has
   exactly one audience, which decides what it must contain. 4. The vocabulary
   is shared across the whole system, so two reports of one condition are
   comparable. 5. A deliberate collapse of two states says that it is
   deliberate, or a later reader fixes it into a distinction the system cannot
   make. 6. A message describes what the system could not do, never what the
   user did wrong, because blame ends the investigation. 7. The harness's own
   not-working states are distinct and named: unresolved, tool absent,
   untrusted, skipped as fresh, and unreachable - each with a different action.

## Sources

All read 2026-09-20.

- `~/workspace/meowhub/docs/standards/failure-vocabulary.md` - the reason the
  standard exists; the three rules; the table per audience with name, trigger,
  what that audience gets and where the state lives; the named states; the
  documented deliberate indistinguishability; and the phrasing rule that the
  fault is the system's.
- [RES-0033-defects.md](RES-0033-defects.md) - what a defect is in this method
  and how one is recorded.
- [RES-0017-design-lenses.md](RES-0017-design-lenses.md) - the five lenses and
  what survived the strip from their donor project.
