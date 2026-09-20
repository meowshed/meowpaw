---
id: RES-0017
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Design review lenses

## Summary

One internal project wrote five standards that read as project-specific and
are not: strip the ledger and the household from them and each becomes a
question any design should answer. They cover the ergonomic cost of a design,
the vocabulary of its failures, shared budgets, the threat model, and what a
surface is for. The strongest of them is that the real failure mode is
abandonment rather than a bug, and that a queue nobody drains is a failure of
the process rather than a state of the data.

Research for `meow-design`. `meowhub` wrote five standards that read as
project-specific and are not: strip the ledger, the household and the bot, and
each one is a question any design should be made to answer. This records what
each says, what survives the strip, and what does not.

These are the strongest donor material found in the internal survey, because
they are the only documents anywhere in the six repositories that constrain a
_design_ rather than a process or a language.

## Method

We read one internal repository from its working tree on 2026-09-20: five
standards documents, in full. The line counts are recorded in the sources
table, so a reader can tell how much of each survived the strip.

The material is quoted directly rather than paraphrased, because the value is
in specific sentences and a paraphrase would have lost them.

Nothing external was consulted, which is this document's main limitation: the
five lenses are one project's, and the claim that they generalise rests on
reading them rather than on finding them elsewhere. That gap is closed in the
per-lens documents, which do consult published sources.

## 1. Operational ergonomics

`meowhub`'s `ergonomics.md` is about "the system as something three people live
with for years: what it asks of them, how often, and what happens when they stop
doing it."

Its central claim generalises completely: **the real failure mode is not a bug
but abandonment.** A ledger three weeks stale is worth less than no ledger,
because nobody trusts a number they cannot date. The same is true of a monitoring
dashboard nobody reads, a test suite everyone skips, a queue everyone
rubber-stamps.

Four rules survive the strip intact.

Every one of these systems bottlenecks on one person, and the design either
accounts for them or fails. In `meowhub` it is the owner, who approves
model-derived records, makes every financial correction, downloads the
statements and receives every alert. The three consequences generalise. Nothing
requires them in real time. Every funnel has a drain that depends on no
willpower. And the system survives two weeks of their absence with no data loss
and no unrecoverable queue.

No unbounded queues. Anything that accumulates and then needs a person needs
two mechanisms. An automatic drain wherever draining is safe, and a ceiling
that raises an alert once when exceeded, "because a queue nobody drains is a
failure of the process and not a state of the data". Without both, it becomes
"a permanent guilty backlog whose contents are eventually rubber-stamped
unread, which makes the state meaningless".

That sentence is the most transferable in the entire internal survey. It
describes a CI dashboard with forty known-failing tests as exactly as it
describes a confirmation queue.

Interruption has a budget. One channel is good for attention and
overspending it is fatal, because people mute a channel that interrupts them too
often, and a muted channel is worse than no channel. Alerts only when a person
can act, once per condition, never repeated without new information - "still
broken" is not new information.

Confirmations echo what was inferred, not what was said. If the person
supplied the amount and the merchant, repeating those back is noise; what they
might want to catch is what the system _chose_. Generalised: a confirmation
shows the system's decisions, not the user's input.

## 2. The failure vocabulary

`meowhub`'s `failure-vocabulary.md` exists because "eleven specs each enumerate
their own edge cases, which is right, but between them they invented a dozen ways
to be broken without ever agreeing on the names."

Three rules, and all three are universal:

1. Nothing fails silently. A state not on the list is a defect.
2. Every failure names its next step. "Something went wrong" is not a state.
3. Every failure has one owner. A user is never shown infrastructure; an
   operator is never left guessing which component broke.

The form is a table per audience: the name, when it happens, what that audience
gets, and where the state lives. The discipline of naming each state - "stale
action", "queue ceiling", "drift detected", "integrity mismatch" - is what makes
the specs stop inventing parallel vocabularies.

Two details carry over:

- A failure the system cannot distinguish from another is documented as
  _deliberately_ indistinguishable. `meowhub` does this for a schema violation
  against an unparsed capture, and saying so is what stops a future reader
  treating the collapse as a bug.
- The phrasing rule: the fault is always the system's and never the user's.

This pairs directly with the unresolved-verb rule and honest absence. A harness that
requires unresolved verbs to be reported is already committed to the first of
these three rules; the vocabulary makes it a design obligation rather than a
kernel behaviour.

## 3. Shared budgets

`meowhub`'s `budgets.md` collects latency, cost and size baselines in one place
"because eleven specs carry their own non-functional requirements, and none of
them could say whether a number was consistent with the others."

The mechanism, which is the universal part: **a specification refines a shared
baseline instead of reinventing it - stricter is allowed if stated, looser needs
a reason.**

Two more rules survive:

- Budgets cover the paths where **a person is waiting**, because a machine
  waiting costs nothing. This prevents the common waste of optimising a
  background job to a latency target nobody experiences.
- **Exceeding a budget is recorded as a finding, not adopted as how the system
  works.** Without this, every budget decays into a description of current
  behaviour.

The numbers themselves do not transplant, and their justifications transfer as
a _form_: "3 s, and 5 s at the 95th - someone is at a till with a bag in one
hand". A budget with a reason attached survives an argument; a budget without
one is negotiated away.

## 4. The threat model

`meowhub`'s `threat-model.md` opens with the reason it exists: "Tests written
without a threat model are mechanical, because they assert whatever the policy
happens to say."

That is the transferable insight, and it is sharper than most security guidance:
without a statement of what is being protected and from whom, a security test
verifies the implementation against itself.

The structure generalises: **what is protected** (asset, why it matters, worst
case), and **who you defend against, ordered by likelihood of causing damage**.

And the finding that most threat models get wrong: the most probable adversary
is **accident by a legitimate insider** - a stray tap, a bulk approval read too
quickly, a deletion meant for something else. `meowhub` lists it first and
designs most of the system around it. A threat model that opens with external
attackers is usually inventorying imaginary adversaries, which it warns produces
"a document nobody reads".

The scale rule is explicitly stated and this lens keeps it: a three-person
household is not an enterprise, and the model is kept short on purpose.

## 5. Interface design

`meowhub`'s `ui-design-process.md` is the most product-specific of the five standards, and
two of its rules are nonetheless general.

A screen answers one question that somebody actually asked - in the words
they used, not a topic and not an entity. "If you can't name a proposed screen
as a question, it isn't designed yet. If it answers four questions, it is four
screens."

This applies to anything with a surface: a CLI subcommand, an API endpoint, a
report, a dashboard panel, a bot reply. The failure it prevents is the
entity-shaped interface - a screen called "Transactions" that answers nothing in
particular.

Name the data before the layout. Where the view the interface reads does not
exist, the work starts with the data and never with the component. And where
the system computes nothing of its own, a number no view produces is
unavailable at any price. Generalised: establish what can be known before
designing how it is shown, because the alternative is an interface promising an
answer the system cannot support.

The rest - the design system, the chart heuristic, the specific ten steps - is
product work and belongs to a domain pack if anywhere.

## What does not transplant

`agent-persona.md` is the butler's voice and is entirely `meowhub`'s. What
generalises is one line from its surrounding rules: **the product's voice is a
documented standard, and it applies to the product and never to the
repository** - specs, decision records and commits stay plain. The prose skill
states that distinction, and the persona itself is no harness material.

The forty-six decision records, the data model and the eleven specs are the
project. They are useful as _examples_ of the form and as nothing else.

## Conclusions

1. A design states its ergonomic cost: who does more work, what queue it
   creates, what it interrupts, and what happens if nobody touches it for a
   month.
2. Every accumulating thing has a drain and a ceiling.
3. Interruption has a budget, and an alert fires once per condition.
4. Failure states are named, owned, and each names its next step. Nothing
   fails silently, and a deliberate collapse of two states says it is
   deliberate.
5. Non-functional baselines live in one place; a design refines them, and
   exceeding one is a finding.
6. A budget carries the reason for its number.
7. What is protected, and who from, ordered by likelihood - with accident by
   an insider considered first.
8. Every surface answers one question somebody asked, and the data is named
   before the shape.

## Sources

`~/workspace/meowhub`, read 2026-09-20. Five standards, each quoted directly:

| File                                   | Lines | Taken                                                                                                                                                               |
| -------------------------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/standards/ergonomics.md`         | 161   | Abandonment as the real failure mode; the bottleneck person; queues needing a drain and a ceiling; the interruption budget; confirmations echoing what was inferred |
| `docs/standards/failure-vocabulary.md` | 78    | Nothing fails silently; every failure names its next step; every failure has one owner; deliberate indistinguishability stated as deliberate                        |
| `docs/standards/budgets.md`            | 89    | One place for baselines; refine rather than reinvent; budgets cover paths where a person waits; exceeding one is a finding; each number carries its reason          |
| `docs/standards/threat-model.md`       | 111   | Tests without a threat model are mechanical; assets with worst cases; adversaries ordered by likelihood; accident by an insider first; keep it short on purpose     |
| `docs/standards/ui-design-process.md`  | 192   | A surface answers one question somebody asked; name the data before the layout                                                                                      |

Also `~/workspace/meowhub/CLAUDE.md` and `specs/_templates/spec.md`, read the
same day, for the ergonomic-cost section and how the standards are invoked from
the specification template.

`docs/standards/agent-persona.md` was read and deliberately not taken; only the
rule that a product's voice is a documented standard, applying to the product
and never to the repository, generalises.
