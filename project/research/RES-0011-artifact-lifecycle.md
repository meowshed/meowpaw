---
id: RES-0011
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# What is permanent and what is living

## Summary

Documents divide by lifetime, and their kind decides nothing. A living document
states the present and gets rewritten; a record states what was true when it
was written, and nobody edits it once approved. The pattern is older than the
problem: it is the append-only store with projections built over it. The
consequences follow from it. Somebody withdraws a requirement and nobody
rewords it, the specification omits what is withdrawn and carries no
tombstones, and every statement traces to a requirement in force.

Research for the decision on what is permanent and what is living:
records that are written once and a specification that is rewritten. The
pattern is older than the problem, and the community that has argued about it
longest has arrived at the same split without completing it.

## Method

Two kinds of source were read on 2026-09-20. The published material on
event-sourced systems was fetched directly at the addresses listed below and
read for the store-and-projection pattern, and we took none of its
implementation advice. The internal repositories were read from their working
trees for how each already handles the distinction in practice.

Nothing was run, and no measurement was taken. The findings are comparisons
between what the sources say and what the internal repositories do.

One conclusion in this document corrects an earlier one and observes nothing
new: the original version concluded that the specification was the only living
document, which generalised from a single example. We recorded the correction
in place and left the conclusion standing, so the error stays visible.

## The pattern has a name

This is **event sourcing**, applied to documents.

An event store "persists all events in the exact order they occurred, and
unlike traditional databases, the event store is append-only and immutable",
providing "an audit trail that applications can use to monitor actions taken
against a data store". A **projection** transforms that log into a materialised
view - a read model - optimised for being queried, where the log records what
happened. The same log can produce several read models "without impacting the
write side".

Line the two up:

| Event sourcing                                                      | The harness                                                           |
| ------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Event store - append-only, immutable, ordered                       | Research, requirements, decision records, completed plans and reports |
| Projection / read model - derived, rewritten, optimised for reading | The specification                                                     |
| Command side                                                        | The chain's steps, which append                                       |
| Query side                                                          | Anyone asking what the system must do                                 |

The properties that carry over are the ones that matter. **The log is the truth
and the projection can be rebuilt.** Nothing is lost when the specification is
rewritten, because the statements it makes are traceable to requirements in
force. **The projection is optimised independently of the log**, which is why
the specification drops a withdrawn requirement entirely and carries no
tombstone. And **the log is the audit trail**, which is why execution records
are permanent: the plan as it ended is what actually happened.

The property that does _not_ carry over is automatic derivation. A read model
is computed; a specification is written, because prose is not mechanically
derivable from obligations. What replaces computation is the verification
direction [decision 0007] adds: every statement in the specification traces to
a requirement in force, and a requirement in force that the specification omits
is a finding. That is the rebuild check, and a reader performs it because
nothing runs.

## The ADR community has the same split, half-made

The architecture-decision-record practice has argued about exactly this, and its
current position is our position:

> ADRs are immutable, but the current state of decisions is not.

The older convention states it more strictly - "an accepted ADR's decision is
immutable", and "superseded and deprecated ADRs stay in the log; they are
immutable history, not deletions". Against that, some teams have moved the
other way: "a decision that changes is edited in place; a decision that no
longer exists has its file deleted."

Both positions are attempts to solve one problem with one artifact, and both
fail at the other half. The immutable log answers "why is it like this" and
cannot answer "what is true now" without reading every record and working out
which are still in force. The edited-in-place variant answers "what is true now"
and destroys the reasoning - which is the failure the convention existed to
prevent.

The status vocabularies that have grown up to paper over it are the evidence
that this costs something real: `proposed`, `accepted`, `superseded`,
`partially_superseded`, `deprecated`, `rejected`. Six statuses on the log
because there is no projection. And the practice that goes with them rests on
discipline alone: "revisit the corpus during architecture reviews, supersede
the decisions that no longer apply, and keep the live decision set roughly in
sync with what's actually running."

_Roughly in sync_ is what happens when the current state is a property somebody
maintains and no document anybody writes.

The harness's answer is to add the missing half. The log keeps its statuses;
the specification is the thing that is in sync, because writing it is a step
someone runs, where a discipline is something someone forgets.

## Double-entry is the same idea, and it is already in the family

`meowhub`'s ledger is double-entry. Postings are append-only, corrections
arrive as new postings and nobody edits an old one, and every view of the
household's finances is a SQL view over the postings. "The app computes no
totals of its own", and "a figure whose view is not in the catalogue does not
exist yet".

That is the same architecture in a different domain, decided independently, in a
repository by the same author. The journal is permanent; the balance is derived;
a mistake is corrected by a new entry, never by altering an old one.

This is the strongest available argument that the pattern is no affectation.
Two systems that share nothing else arrived at append-only plus projection,
because the alternative, editing the record, makes a mistake and a cover-up
indistinguishable.

## What each artifact's mode follows from

Not a taxonomy for its own sake. Each mode follows from what the artifact is
_for_.

Research is permanent because a finding has a date. What was true of a tool
in September is evidence about September. A later reading is a new artifact,
which is also why a changeable source carries the date it was read - a research document edited in
place has lost the thing that made it evidence.

Requirements are append-only because their history is the valuable part. A
withdrawn requirement, and the decision that withdrew it, is precisely what
stops the same mistake being made twice. Rewording in place destroys it.

Decisions are permanent because a decision is an event. It happened, at a
time, with alternatives that were live then and may not be now. Its reversal
condition is only meaningful against the circumstances it was made
in.

Plans freeze because execution is history. While the work runs the plan is
the working state - marks move, evidence accumulates, tasks are added and
dropped. When the decision is realised it stops being a
plan and becomes the account of what was done, in what order, closed by what
evidence. Tidying it afterwards would be rewriting the audit trail, and an audit
trail that gets tidied is not one.

Reports freeze for the same reason. A verify report says what was true at a
revision. Regenerating it later produces a different document about a different
tree; the corpus keeps both, and neither replaces the other.

The specification lives because it is the only artifact whose job is to be
current. Everything else answers a question about the past.

## The costs, stated

The record grows without bound. Every decision leaves a plan and reports,
permanently. This is the intended cost; the alternative is a tidy repository
that cannot say what happened. Retrieval answers the growth, and deletion never
does, which is what makes the index and the search tooling
([RES-0019-document-tooling.md](RES-0019-document-tooling.md)) load-bearing.

A fourth thing can drift. The specification can fall out of step with the
requirements, and only verification catches it. The event-sourcing analogy is
exact: a stale read model is the characteristic failure of the pattern, and the
answer there is the same - rebuild, and check that the rebuild matches.

The specification cannot explain itself in place. A reader asking why
follows a link. Accepted deliberately.

## Conclusions

1. Documents divide by lifetime, and their kind decides nothing. A living
   document states the present and is rewritten; a record states what was true
   when it was written. This document originally concluded that the
   specification was the only living document, which generalised from one
   example and is corrected in [RES-0035-vision.md](RES-0035-vision.md). 2. A
   record is never edited once approved. A later truth is a new record. 3. A
   requirement is withdrawn, never reworded, and the withdrawal names the
   decision. 4. The specification omits what is withdrawn and carries no
   tombstones. 5. Every statement in the specification traces to a requirement
   in force, and verification checks both directions. 6. An epic freezes when
   its authorising record is realised, and is then the account of what was
   done. 7. The growth is accepted and answered by retrieval, because deleting
   the record answers nothing.

## Sources

- [Event Sourcing pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing),
  Azure Architecture Center, read 2026-09-20 - the append-only immutable store,
  the audit trail property, and materialised views from stored events.
- [Guide to projections and read models in event-driven architecture](https://event-driven.io/en/projections_and_read_models_in_event_driven_architecture/),
  read 2026-09-20 - projections as views optimised independently of the write
  side, and several read models from one stream.
- [Projections and read models](https://eventsauce.io/docs/reacting-to-events/projections-and-read-models/),
  EventSauce, read 2026-09-20 - read models separating presentational state from
  the process being modelled.
- [ADR lifecycle triage: current / superseded / historical / retired](https://github.com/metel-lang/metel-core/issues/1158),
  read 2026-09-20 - "ADRs are immutable, but the current state of decisions is
  not", and the six-status vocabulary that grows in the absence of a projection.
- [Make ADRs living documents with no archive](https://github.com/jlaws/dotfiles/pull/102),
  read 2026-09-20 - the opposing position: edit in place, delete what no longer
  exists, and the immutable-log convention it replaces.
- [One decision-record convention: format, status vocabulary, index, living vs superseded](https://github.com/sebastian-software/project-infra/issues/37),
  read 2026-09-20 - the same tension stated as a convention problem.
- [Architecture Decision Records: the 2026 guide](https://www.catio.tech/blog/architecture-decision-record),
  read 2026-09-20 - "revisit the corpus during architecture reviews, supersede
  the decisions that no longer apply, and keep the live decision set roughly in
  sync with what's actually running".
- [Implementing a workflow for your architecture decision records](https://asiermarques.medium.com/implementing-a-workflow-for-your-architecture-decisions-records-ab5b55ee2a9d),
  read 2026-09-20 - status transitions in practice.
- `~/workspace/meowhub/docs/architecture/decisions/0011-double-entry-ledger-and-chart-of-accounts.md`
  and `0004-postgresql-as-system-of-record.md`, read 2026-09-20 - append-only
  postings with derived views, decided independently in the same family of
  repositories.
