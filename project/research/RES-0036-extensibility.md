---
id: RES-0036
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Project-specific artifact kinds, and the relations between them

## Summary

A project may declare artifact kinds of its own, and three facts are enough
to declare one: a prefix, a mode and a template, plus a path and optionally a
check. A declared kind inherits every general obligation and may not have
looser rules. Relations are authored upward and derived downward, which is what
every bidirectional-link system has done since the wiki, and every declared
relation must resolve.

Research for two additions: that a project may declare artifact kinds of its
own, and that relations between artifacts are declared upward and derived
downward. It covers what a declared kind must carry, what a corpus with many
kinds needs that one with nine does not, and the prior art for derived
backlinks. It does not cover the nine default kinds.

## Method

The internal repositories were read from their working trees on 2026-09-20
for the kinds they have already invented, which is the evidence that projects
do this whether or not a mechanism exists.

The published material on bidirectional linking was fetched for the
authored-upward pattern.

Nothing was run, and no project-declared kind was implemented and tested, so
the three-facts claim is a design claim rather than a result.

## The worked example is in the family

`hephaestus` is a game, and its documentation tree is nothing like the nine
default kinds:

```text
docs/world/bible/      the author's bible — physics, the frame everything sits in
docs/world/lore/       the world
docs/design/           battle, economy, crew, council, galaxy, campaign, ship, voyage…
docs/specs/            including a design system
docs/references/       games it learns from
docs/presentation/
```

Narrative documents, produced by tasks, cited by other documents, and utterly
unlike a requirement. If the harness cannot hold them, it does not work for that
repository - which is the test the method sets.

Running its tree through the declaration mechanism, nothing resists:

```yaml
artifacts:
  bible: { prefix: BIB, mode: living, path: docs/world/bible/ }
  lore: { prefix: LOR, mode: living, path: docs/world/lore/ }
  design: { prefix: GDD, mode: living, path: docs/design/ }
  reference: { prefix: REFG, mode: record, path: docs/references/ }
```

Three facts per kind - prefix, mode, template - because those are what every
obligation needs to apply to it. The prefix makes identifiers
resolve, the mode decides whether it freezes, the template decides what it must
contain.

## What `hephaestus` has that the default kinds do not

Two mechanisms, and both generalise.

### An explicit authority order between documents

From its `canon-check` skill:

> `docs/world/bible/01-physics-framework.md` is the author's bible; when a doc
> conflicts with it, the bible wins and the other doc is the one to fix.

That is a **conflict rule between artifacts of different kinds**, and the
harness already has the same idea in one place - the design outranks a component
specification, and the constitution outranks any artifact. What `hephaestus`
shows is that the rule is general and belongs to the declaration rather than to
prose in one skill.

The general advice agrees and states it as the remedy for conflicting context:
"state the hierarchy explicitly, with a priority order... If they conflict with
items 1-3, ignore the archive and **report the conflict in one sentence**."

That last clause is the part this method takes. A conflict is not resolved
silently by precedence; precedence decides which to follow _and_ the conflict
is reported, because an unreported conflict means one of the two documents is
quietly wrong and nobody is told.

So a declared kind may state what it outranks, and a conflict across that order
is a finding rather than a silent resolution.

### A cross-document consistency audit

`canon-check` is a repeatable audit across the whole tree: entity names, fixed
counts, roster consistency, section boundaries, template compliance.

Its "one lesson" is a warning about scope, and it generalises past games:

> **Grep the whole tree before calling any term "undefined."** ... A reviewer
> scoped to one subtree will mislabel a cross-tree entity as undefined.

That is the same failure as a text search presented as a language server's
answer ([RES-0021-editing.md](RES-0021-editing.md)): a confident negative produced by looking in
the wrong place. In a corpus with project-specific kinds the risk is higher,
because the kinds live in different directories and the reviewer's instinct is
to stay in one.

For the harness this means a declared kind can bring a **check** as well as a
template - a project-specific consistency audit is exactly the kind of thing the
gate's `lint` verb should run, and `hephaestus` already runs its spelling and
format checks that way.

## Relations: authored upward, derived downward

The corpus needs to answer both "where did this come from" and "what came of
it". The second must not be written by hand.

The prior art is unanimous and it is the note-taking tools. Obsidian and
Roam made bidirectional links their central feature, and in both the back
direction is _computed_: a note declares its outgoing links, and the backlinks
pane shows incoming references - "the backlinks system automatically tracks and
displays both incoming references and potential unlinked mentions". Nobody
writes a backlink. Obsidian additionally maintains link integrity across file
moves, which is the same reason the harness's relations use identifiers rather
than paths.

The requirements-management family reaches the same place from the other end:
OpenFastTrace has artifacts declare what they _need_ and what they _cover_, and
computes the gaps ([RES-0019-document-tooling.md](RES-0019-document-tooling.md)). One direction
authored, the other derived.

The argument for it here is stronger than convenience. **The author of a
document cannot know what will cite it.** A `prompted:` list on a defect would
have to be updated by every artifact that later cites it - which is a write to a
permanent record performed by something that is not that record's
author. Derivation avoids both problems at once.

What derivation needs in exchange is that every declared relation resolves. An unresolvable identifier is the one failure mode this model has,
and it is a check.

## What a corpus with many kinds needs

Three things that a nine-kind corpus gets away with and a twenty-kind one does
not:

An index that is generated. With four kinds a person can maintain a list.
With twenty across five directories they cannot, and the index becomes the first
thing to be wrong.

Retrieval rather than browsing. `hephaestus`'s own lesson - search the whole
tree before concluding anything is absent - is a statement about scale. The
answer is the same as for the growing record: an index and search
([RES-0019-document-tooling.md](RES-0019-document-tooling.md)).

A stated authority order. With nine kinds the order is obvious and can live in
prose. With twenty it has to be declared, because the question "which of these
two wins" now has enough pairs that somebody will ask it.

## What extensibility must not become

An exit from the method. The risk is that the first artifact someone does
not want to hold to the obligations becomes a new kind with looser rules. So a
declared kind inherits everything: an identifier that resolves,
front matter, relations, and immutability where it is a record.

Extensibility adds artifacts to the method. It is not a way to hold one outside
it.

## Conclusions

1. Three facts declare a kind: prefix, mode, template - plus a path and,
   optionally, a check.
2. A declared kind inherits every general obligation. No looser rules.
3. A kind may state what it outranks, and a conflict across that order is
   reported rather than silently resolved.
4. Relations are authored upward and derived downward, as every
   bidirectional-link system since the wiki has done.
5. Every declared relation must resolve, and that is the check the model
   depends on.
6. Many kinds require a generated index and real retrieval, not browsing.

## Sources

All read 2026-09-20.

- `~/workspace/hephaestus/docs/` and
  `~/workspace/hephaestus/.claude/skills/canon-check/SKILL.md` - the tree of
  narrative and design documents, the bible's stated precedence, and the
  cross-tree audit with its scope warning.
- [Backlinks](https://help.obsidian.md/Plugins/Backlinks) and
  [Internal links and backlinks](https://deepwiki.com/obsidianmd/obsidian-help/4.2-internal-links-and-backlinks),
  Obsidian - outgoing links authored, incoming references computed, linked and
  unlinked mentions, and link integrity maintained across file operations.
- [Obsidian](<https://en.wikipedia.org/wiki/Obsidian_(software)>) - bidirectional
  links as the central feature, indexed by a metadata cache.
- [Single source of truth](https://en.wikipedia.org/wiki/Single_source_of_truth)
  and [Building a single source of truth](https://www.atlassian.com/work-management/knowledge-sharing/documentation/building-a-single-source-of-truth-ssot-for-your-team)
  - auditing for duplicate and conflicting information as the first step.
- [How to get better, more reliable results](https://www.elser.ai/blog/gpt-6-astra-prompt-guide)
  - stating a document hierarchy explicitly as a priority order, and reporting a
    conflict in one sentence rather than resolving it silently.
- [How to create worldbuilding bibles that ensure series consistency](https://rivereditor.com/guides/how-to-create-worldbuilding-bibles-2026)
  - continuity checking against an established canon as a standing practice.
- [OpenFastTrace](https://github.com/itsallcode/openfasttrace) - the needs and
  covers model, with gaps computed rather than recorded.
