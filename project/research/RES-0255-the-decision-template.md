---
id: RES-0255
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0158, RES-0253
---

# The decision template

## Summary

Fifty decisions are written to a shape this project invented, and the published
templates carry one field it has no equivalent for: how compliance with the
decision will be confirmed. That gap is larger here than in the projects the
template came from, because epic verification currently reconstructs the answer
later from a document written by someone who was never asked. Three of this
corpus's own sections have no published equivalent and each earns its place. A
second criterion is missing from both templates and from this corpus. A
decision has to be realisable as a complete story, which is what separates one
somebody can build and show from a quarter of something.

Research for the shape of a decision record: which sections it has, what the
published templates carry that this corpus does not, and which of its own
sections this corpus invented and should keep.

One of nine template documents, one per artifact kind in the record.

It does not cover the command that writes one, which is
[RES-0158-decide-command.md](RES-0158-decide-command.md), nor the design step,
which is [RES-0152-design-command.md](RES-0152-design-command.md).

## The question

Fifty decisions in this corpus are written to a shape this project invented:
decision, why, alternatives, what it costs, what would reverse it,
consequences, what it does not decide, premortem.

The two published templates are older and have been used across far more
projects. The question is what they carry that this shape does not, and whether
the difference is an improvement or an omission.

## Method

We fetched and read the fuller published template on 2026-09-20 for its
complete field list, the optional fields included, and we quote its definition
of the confirmation field in full. We read the minimal form for the base.

This corpus's fifty decisions were read against both, section by section, which
is how the missing field and the three invented ones were identified.

The argument that the approver field is about to become load-bearing comes from
the unattended-mode research rather than from either template.

The completeness criterion was added after the rest and grounded separately, in
the published material on end-to-end slices. Its primary source does not
resolve: the page under the originator's own name returns not-found, checked
the same day. So the definitions here come from secondary accounts that quote
it consistently, and this document cites them as secondary.

## Findings

### The published templates, and the field this corpus is missing

The minimal form is title, status, context, decision, consequences. The fuller
one adds, with most fields optional:

| Field                         | What it holds                                          |
| ----------------------------- | ------------------------------------------------------ |
| `title`, `status`, `date`     | Identity and state                                     |
| `decision-makers`             | The people involved in deciding                        |
| `consulted`                   | Subject-matter experts, two-way                        |
| `informed`                    | Stakeholders, one-way                                  |
| Context and problem statement | The situation                                          |
| Decision drivers              | The forces and concerns                                |
| Considered options            | The alternatives                                       |
| Decision outcome              | The chosen option, justified                           |
| Consequences                  | Positive and negative                                  |
| **Confirmation**              | **How compliance with the decision will be confirmed** |
| Pros and cons of the options  | Per option                                             |
| More information              | Evidence and resources                                 |

Most of this corpus's sections map onto these. One published field has no
equivalent here, and it is the interesting one.

Confirmation asks _"how the implementation of/compliance with the ADR
can/will be confirmed. Is the chosen design and its implementation in line with
the decision?"_, with design or code review and architectural tests given as
examples. The template calls it optional and notes that it appears in many real
decision records.

This corpus has nothing that answers it. It has _what would reverse it_, which
is about the decision becoming wrong, and _consequences_, which is about what
changes. Neither asks how anyone will know the decision was actually carried
out.

### That gap is larger here than in the projects the template came from

This method already has the machinery the field needs and does not connect it.

Verifying an epic asks whether the decision behind the work was realised, and
the corpus's own finding is that every way a decomposition can be wrong
survives task verification untouched. That verification needs a statement of
what realising the decision would look like - and today it derives one, at
verification time, from a decision written earlier by someone who was not asked
the question.

Writing it at decision time is strictly better. The author knows what they
meant; the verifier a month later is reconstructing it. It also makes a
decision falsifiable in the same way requirements are: a decision whose author
cannot say how anyone would confirm it was implemented has probably not decided
anything checkable.

So **confirmation is adopted**, phrased as _how we will know this was
realised_, and it becomes the input to epic verification rather than something
verification invents.

### A decision has to be realisable as a complete story

The method already requires each decision to leave the system working, and one
decision to be realised by one epic. Neither says what makes a decision the
right size, and without that the requirement is a hope.

The published name for the shape is a thin end-to-end slice. The descriptions
agree on three properties. It is a _"tiny implementation of the system that
performs a small end-to-end function"_. It _"need not use the final
architecture, but it should link together the main architectural components"_.
And it arrives as _"a skinny vertical slice that goes through the layers"_,
where building a layer at a time would not.

That gives a test applicable to a draft:

Can you state, from the decision alone, what the system does after it that it
did not do before?

A decision that cannot answer is a fragment. Three shapes fail it, and all
three are common:

- **The horizontal decision.** _Adopt a logging library._ Nothing observable
  changes; the value arrives only when something uses it.
- **The dependent fragment.** A decision whose realisation is useless until
  three neighbours are realised too. Each of the four is reasonable on its own,
  which is why all four get approved and none can be demonstrated.
- **The oversized decision.** One that cannot be realised as a reviewable
  series, which is the defect the epic and task sizes already guard against,
  appearing one level up.

The remedy differs per shape. A horizontal decision merges into the first
decision that uses it. A dependent fragment merges with its neighbours into one
complete decision. An oversized one splits along a different axis - by
capability rather than by component - so each part is thin and whole rather
than thick and partial.

### The completeness criterion is what makes the confirmation field answerable

The two are connected, and noticing that is what puts them in the template
together.

A decision that is a complete story can say how anyone will know it was
realised, because there is an observable difference to point at. A fragment
cannot: the honest answer to _how will we know_ is _when the other three land_,
which is an admission that this is not one decision.

So the confirmation field doubles as the test. A draft whose confirmation
cannot be written without referring to decisions that do not exist yet needs
merging or re-splitting before it is approved.

That also explains a failure this project has already had. A decision was
written that left the system working only in the sense that nothing broke -
nothing worked differently either - and it took writing the epic to notice.
Applying the test at the decision step moves that discovery one step earlier,
where it costs a paragraph.

### Who decided is not recorded, and this corpus needs it more than most

The published template carries deciders, consulted and informed. This corpus
carries none of them.

For most projects that is a mild omission. Here it is about to become a real
one, because the project is designing a mode in which the harness approves its
own gates. A record that does not say who approved cannot later distinguish a
decision a person made from one the harness made, which is exactly the
distinction a morning review depends on.

The minimal version is enough: **a decision records who approved it**, and
where that was the harness, it says so. Consulted and informed are ceremony for
a project this size and are not adopted.

### What this corpus invented and should keep

Three sections have no equivalent in either published template and each earns
its place.

What it costs. The published templates have consequences, which in practice
collects benefits. A section that names the price separately resists the drift
towards advocacy, because a decision record listing only benefits is a
proposal.

What would reverse it. Two internal projects arrived at this independently,
which is the strongest evidence in the survey for any single field. It turns a
decision into something evidence can revisit rather than something only
argument can, and it is the difference between a decision that can expire and
one that has to be relitigated.

What this does not decide. The boundary statement. In a corpus where decisions
are layered so each leaves the system working, the commonest review question is
whether an earlier decision already settled a later one. This section answers
it in advance.

The premortem is a fourth, and it is the weakest of them: it is a prediction,
it is rarely revisited, and its value is concentrated in the moment of writing.
It is kept, because the act of writing it is where the value is, and marked
optional.

### Status is stored and realisation is derived

The published vocabulary is proposed, rejected, accepted, deprecated,
superseded. This corpus uses draft, approved, withdrawn, rejected, superseded,
which is the same set with the addition of a state for a proposal its own
author retracted.

The rule that matters more than the vocabulary: **whether a decision has been
realised is not a status.** It is derived from whether the work authorised by
it is done. Storing it creates a second copy of the truth that goes stale
silently, and "implemented" reads naturally enough in a list that this is easy
to get wrong.

### Immutability, and what supersession means

A record describes the decision, never the history of the document. An approved
record is not edited to reflect what happened afterwards; it is superseded, and
the supersession is a relation between two records rather than an edit to one.

The template rule that follows is small and is routinely broken: **a correction
to an approved decision is a new decision**, including when the correction is
obviously right.

### The sections it carries

| Section                          | Holds                                                                                              | Mandatory |
| -------------------------------- | -------------------------------------------------------------------------------------------------- | --------- |
| Front matter                     | Identifier, kind, status, revision date, requirements addressed, research elaborated, who approved | Yes       |
| Title                            | The decision as a statement, not a topic                                                           | Yes       |
| Decision                         | What was chosen, in the imperative                                                                 | Yes       |
| Why                              | The forces, and the reasoning                                                                      | Yes       |
| Alternatives                     | Each option, what it is better at, why it lost                                                     | Yes       |
| What it costs                    | The price, separately from the consequences                                                        | Yes       |
| How we will know it was realised | The confirmation, and the input to epic verification                                               | Yes       |
| What works after this            | The observable difference, in one sentence                                                         | Yes       |
| What would reverse it            | The condition that makes it wrong                                                                  | Yes       |
| Consequences                     | What works after this, and what does not yet                                                       | Yes       |
| What this does not decide        | The boundary                                                                                       | Yes       |
| Premortem                        | How it could fail, and the guard                                                                   | Optional  |

## Conclusions

1. A decision is realisable as a complete story, and states in one sentence
   what the system does after it that it did not do before.
2. A draft that cannot answer that is merged or re-split: a horizontal
   decision joins the first decision that uses it, a dependent fragment joins
   its neighbours, and an oversized one splits by capability rather than by
   component.
3. One decision is realised by one epic, which the completeness criterion
   makes possible rather than merely hoped for.
4. A decision records how anyone will know it was realised, which the
   published template calls confirmation and this corpus had no equivalent for.
5. That statement is written at decision time and is the input to epic
   verification, rather than reconstructed later by whoever is verifying.
6. A decision whose author cannot say how it would be confirmed has probably
   not decided anything checkable.
7. A decision records who approved it, and says so where that was the
   harness rather than a person.
8. Consulted and informed are not adopted, being ceremony at this scale.
9. The cost is stated separately from the consequences, because a record
   that lists only benefits is a proposal.
10. The reversal condition is kept, being the field two internal projects
    arrived at independently and what lets evidence revisit a decision.
11. The boundary statement is kept, because layered decisions make _was this
    already settled_ the commonest review question.
12. The premortem is optional, since its value is in the writing rather than
    in the reading.
13. Whether a decision has been realised is derived, never stored.
14. An approved record is superseded rather than edited, including when the
    correction is obviously right.
15. The title states the decision rather than the topic, so a list of
    decisions reads as a list of positions.

## Sources

All read 2026-09-20.

- [MADR](https://adr.github.io/madr/) - the full field list including title,
  status, date, decision-makers, consulted and informed; context and problem
  statement, decision drivers, considered options, decision outcome,
  consequences, confirmation, pros and cons of the options, and more
  information; the definition of confirmation as how implementation of or
  compliance with the decision will be confirmed, with review and architectural
  tests as examples; and its statement that the field is optional but common
  in practice.
- [Architectural Decision Records](https://adr.github.io/) - the minimal
  Nygard form of title, status, context, decision and consequences, and the
  status vocabulary.
- [RES-0158-decide-command.md](RES-0158-decide-command.md) - the immutability
  rule that a record describes the decision and never the history of the
  document, and the distinction between withdrawn, rejected and superseded.
- [RES-0069-verifying-an-epic.md](RES-0069-verifying-an-epic.md) - that
  verifying an epic asks whether the authorising decision was realised, and
  that every way a decomposition can be wrong survives task verification.
- [RES-0074-unattended-mode.md](RES-0074-unattended-mode.md) - the requirement
  that every approval be attributable, which is what makes the approver field
  load-bearing.
- [Walking skeletons and tracer bullets](https://tinnedfruit.com/list/20180815)
  and [Kickstart your next project with a walking skeleton](https://codeclimate.com/legacy/kickstart-your-next-project-with-a-walking-skeleton)
  - the thin end-to-end slice as a tiny implementation performing a small
    end-to-end function, linking the main components without requiring the final
    architecture, and delivered as a vertical slice rather than a layer at a
    time. **Recorded as secondary**: the page under the originator's own name did
    not resolve when checked on 2026-09-20, so these accounts are cited in its
    place and agree with each other.
- This corpus, read 2026-09-20: the fifty decisions in `project/adrs/`, whose
  sections were compared against both published templates.
