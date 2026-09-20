---
id: RES-0211
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0017, RES-0201
---

# The `operational-ergonomics` skill

## Summary

What a design asks of the people who live with it, how often, and what happens
when they stop. The claim behind the lens is that the real failure mode is
abandonment, and no bug causes it: a system can work exactly as specified,
violate no requirement, and produce nothing. Every accumulating thing needs a
drain and a ceiling, because a backlog eventually approved unread is worse than
none - the state now claims a review that did not happen.

Research for one design lens: what a design asks of the people who live with
it, how often, and what happens when they stop doing it.

Its siblings are the other four lenses, listed in
[RES-0017-design-lenses.md](RES-0017-design-lenses.md).

## The question

Functional requirements say what the system does. Nothing in them asks who ends
up doing more work, what queue the design creates, what it interrupts, or what
state it reaches after a month of neglect.

That is the lens, and the claim behind it is that **the real failure mode is
not a bug but abandonment.**

## Method

The donor standard was read in full from its working tree on 2026-09-20 and
is quoted directly, because its value is in specific sentences.

We fetched and read the published alerting philosophy for independent
confirmation, because the donor material is one project's. The rules about
actionable alerts and about pages requiring intelligence are quoted from it in
full.

Nothing was measured, and no system was observed being abandoned. The central
claim is an argument supported by two sources, and no result of ours.

## Findings

### Abandonment is a design outcome

A ledger three weeks stale is worth less than no ledger, because nobody trusts
a number they cannot date. The same shape appears everywhere: a monitoring
dashboard nobody reads, a test suite everyone skips, an approval queue everyone
rubber-stamps.

In each case the system is working as specified and producing nothing, and no
functional requirement is violated. That is why this is a design question,
which operations settle nothing about.

### There is a bottleneck person, and the design either accounts for them or fails

Every system has one: the person who approves, corrects, downloads or receives
the alerts. Three consequences generalise from the donor material:

- **Nothing may require them in real time.**
- **Every funnel has a drain that does not depend on willpower.**
- **The system survives two weeks of their absence** with no data loss and no
  unrecoverable queue.

The two-week test is the useful form, because it is answerable at design time
and it is a question nobody asks otherwise.

### No unbounded queues, and the reason is the most transferable sentence in the survey

Anything that accumulates and then needs a person needs two mechanisms: an
automatic drain wherever draining is safe, and a ceiling that raises an alert
once when exceeded.

The reason, quoted from the donor standard:

> a queue nobody drains is a failure of the process and not a state of the data

and, without both mechanisms, it becomes

> a permanent guilty backlog whose contents are eventually rubber-stamped
> unread, which makes the state meaningless

That describes a continuous-integration dashboard with forty known-failing
tests as exactly as it describes an approval queue. The rubber-stamping is the
part that makes it worse than having nothing: the state now _claims_ to have
been reviewed.

### Interruption has a budget, and the published alerting guidance agrees

One channel is good for attention, and overspending it is fatal: people mute a
channel that interrupts them too often, and a muted channel is worse than no
channel.

The rules that follow line up with Google's alerting philosophy. Alert only
where a person can act, once per condition, never repeated without new
information, and "still broken" is no new information. That philosophy states
that _"Every page should be actionable"_ and that _"Every page response should
require intelligence. If a page merely merits a robotic response, it shouldn't
be a page."_

Two of the five questions that source asks before creating an alert rule are
the ones this lens asks of any interruption a design introduces. _Can I take
action in response to this?_ And _will I ever be able to ignore this, knowing
it is benign?_

An alert that will be ignored is not a safety mechanism. It is a cost.

### Confirmations echo what was inferred

If the person supplied a value, repeating it back is noise. What they might
want to catch is what the system _chose_.

Generalised: **a confirmation shows the system's decisions, and never the
user's input.** It is the cheapest rule in the lens and the most commonly
violated, because echoing the input is easier to build and looks like
diligence.

### For this harness specifically

The lens applies to the harness's own design before it applies to anything it
reviews. A pending gate is a queue; a report is an interruption; a
verification that is skipped because it is slow is a drain that depends on
willpower.

The status command leading with the pending gate is this lens applied: the one
item requiring a person goes first, because burying it is how a gate is missed.

## Conclusions

1. A design states its ergonomic cost: who does more work, what queue it
   creates, what it interrupts, and what state it reaches after a month of
   neglect. 2. Abandonment is the failure mode to design against, because a
   system that works as specified and is not used violates no requirement and
   produces nothing. 3. The bottleneck person is identified, and nothing
   requires them in real time. 4. The system survives two weeks of their
   absence without data loss or an unrecoverable queue, which is a question
   answerable at design time. 5. Every accumulating thing has a drain and a
   ceiling, because a queue nobody drains is a failure of the process, and no
   state of the data. 6. A backlog that is eventually approved unread is worse
   than no backlog, since the state now claims a review that did not happen. 7.
   Interruption has a budget, and an alert fires once per condition; "still
   broken" is not new information. 8. An alert that cannot be acted on is not
   created, and one that will be ignored is a cost that safeguards nothing. 9.
   A confirmation echoes what the system inferred, and never what the user
   supplied. 10. The lens applies to the harness's own design first, since a
   gate is a queue and a report is an interruption.

## Sources

All read 2026-09-20.

- `~/workspace/meowhub/docs/standards/ergonomics.md` - the system as something
  people live with for years; the bottleneck person and the three consequences;
  the drain-and-ceiling rule with the two quoted sentences; the interruption
  budget and the alert rules; and the confirmation rule.
- [Monitoring distributed systems](https://sre.google/sre-book/monitoring-distributed-systems/)
  - that every page should be actionable and every page response should require
    intelligence; that a page meriting a robotic response should not be a page;
    the preference for symptoms over causes; the four golden signals of latency,
    traffic, errors and saturation; and the questions of whether an alert can be
    acted on and whether it could ever be safely ignored.
- [RES-0017-design-lenses.md](RES-0017-design-lenses.md) - the five lenses and
  what survived the strip from their donor project.
