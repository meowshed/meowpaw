---
id: RES-0158
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0011, RES-0060
---

# `/meow:decide`

## Summary

The command that writes a numbered decision record. Beyond the published
template it carries the alternatives and why each lost, what the decision
costs, and what would reverse it - the last arrived at independently by two
internal projects, which is the strongest evidence in the survey for any single
field. The record is immutable: it describes the decision and never the history
of the document.

Writes a numbered decision record. One of five practice commands; its siblings
are listed in [RES-0060-practice.md](RES-0060-practice.md).

## Who has an equivalent

`meowhub`'s `adr-new` is the working precedent. The published templates are
Nygard's - title, status, context, decision, consequences - and MADR, which
adds explicit options and decision drivers.

## Method

The surveyed harnesses' own command templates and the internal repositories'
commands were read on 2026-09-20 for what a comparable command does, and the
platform's command documentation was fetched for the frontmatter fields the
surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against comparable
commands, and none of it is an observation.

## What this record carries beyond the templates

The Nygard shape is the floor. On top of it:

- **The alternatives, and why each lost.** A decision without them is
  indistinguishable from a decision nobody thought about.
- **What it costs.** Every decision buys something with something, and a record
  that lists only benefits is advocacy.
- **What would reverse it.** vlie and meowctl arrived at this independently,
  which is the strongest evidence in the survey that it belongs.

The reversal condition is what lets **evidence** revisit a decision, where
otherwise only argument can. Without it, revisiting a decision means
relitigating it, and the person who wants to change it has to beat the original
argument, where a fact should settle it.

## Immutability, and the rule that enforces it

`meowhub`'s rule is exact and is quoted as written:

> An ADR describes the decision, never the history of the document.

So a decision record is not edited to reflect what happened afterwards. It is
superseded by another record, and the supersession is a relation between two
records, and no edit to one.

That is the same property the rest of the corpus has: a record freezes when it
is finished, and only the specification and the other living documents change.

A decision may be withdrawn before it is approved, rejected, or superseded
after. Those are three different states and mean different things to a reader:
withdrawn means the author stopped proposing it, rejected means somebody
declined it, superseded means it was true and then something replaced it.

## Status is stored; realisation is observed

A decision's status - draft, approved, withdrawn, rejected, superseded - is
stored in the document, because it is a fact about what people decided.

Whether the decision has been _realised_ in the tree is not stored. It is
derived, by asking whether the work authorised by it is done, and storing it
would create a second copy of the truth that goes stale silently.

That distinction is easy to lose here specifically, because "implemented" feels
like a status and reads naturally in a list.

## What it must refuse

To write a decision with no requirement behind it, which is a preference.

To edit an approved record, including to correct what later turned out to be
wrong. The correction is a new record.

To record a decision nobody made. A command that infers a decision from the
code has written a reconstruction, which is the same failure onboarding has to
avoid.

## Conclusions

1. The record carries the alternatives and why each lost, or it is
   indistinguishable from a decision nobody thought about. 2. It states what
   the decision costs, since a record listing only benefits is advocacy. 3. It
   states what would reverse it, which is what lets evidence revisit the
   decision, where otherwise only argument can. 4. A record describes the
   decision and never the history of the document. 5. An approved record is not
   edited; it is superseded by another, and the supersession is a relation
   between two records, and no edit. 6. Withdrawn, rejected and superseded are
   three distinct states and mean different things to a reader. 7. Status is
   stored and realisation is derived, so there is one copy of whether the work
   is done. 8. A decision cites the requirements it addresses, and one with
   none is refused. 9. A decision nobody made is not recorded, because
   inferring one from the code produces a reconstruction.

## Sources

All read 2026-09-20.

- [Architectural Decision Records](https://adr.github.io/) and
  [MADR](https://adr.github.io/madr/) - the Nygard template of title, status,
  context, decision and consequences, and what MADR adds in explicit options
  and decision drivers. - `~/workspace/meowhub/.claude/commands/adr-new.md` - a
  decision record command in practice, and the rule that a record describes the
  decision, and never the history of the document. -
  `~/workspace/vlie/.claude/commands/design.md` and
  `~/workspace/meowctl/.claude/commands/` - the reversal condition, arrived at
  independently in two repositories. -
  [RES-0011-artifact-lifecycle.md](RES-0011-artifact-lifecycle.md) - the
  permanent-against-living distinction and the stored-against-observed status
  vocabulary.
