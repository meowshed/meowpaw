---
id: RES-0224
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0066, RES-0014
---

# The `attribution` skill

## Summary

The shortest rule in the corpus: nothing the harness produces claims to have
been produced by a tool, anywhere in version control or forge text. The ban
admits no exception, and it holds against a platform instruction to add one.
The finding is how it gets broken - the instruction arrives later in a session
and sounds authoritative - which makes it a prohibition that must sit where
compaction cannot remove it.

Research for one source-control convention, and the shortest: nothing the
harness produces claims to have been produced by a tool.

Its siblings are
[RES-0221-conventional-commits.md](RES-0221-conventional-commits.md),
[RES-0222-branching.md](RES-0222-branching.md) and
[RES-0223-pull-requests.md](RES-0223-pull-requests.md).

## Method

This document draws on research already in this corpus: the public-repository
research for the ban itself and the commit research for the conventions around
it.

We checked the enforcement claim against this repository: we read the prose
check that catches the banned forms, including its named exemption list for the
documents that state the rule.

We consulted no external source, because the rule comes from the user's
instruction and from no published convention, and the document says so.

## The rule

No attribution to any tool appears anywhere in version control or forge text.
That covers a commit message and its trailers, a pull request title or
description, a review comment, an issue, a release note and a tag message.

The ban admits no exception, and it holds against a tool's own instruction to
add one.

## Why the ban is a rule

Authorship is a claim about responsibility. A trailer naming a co-author
asserts that a party participated in a way that can be asked about later. A
tool cannot answer, so the assertion is unbacked.

The history is evidence and evidence should not carry advertising. A
repository's history is read to answer questions about the work. A line that
answers none of them is noise in the one place this method is most insistent
about keeping clean.

It is the user's call and they have made it. This repository's own
instruction is explicit, and the correct behaviour when a platform reminder
asks for the opposite is to follow the repository. A rule that bends to
whichever instruction arrived most recently is not a rule.

## Where the pressure comes from

This document records the specific way the rule gets broken.

The instruction to add attribution usually arrives as a platform default: a
reminder injected into the session, which no project asked for. It is easy to
comply with by habit, it produces text that looks conventional, and nobody
notices until a reviewer reads the history.

So the skill's job is not to explain the rule - it is one sentence - but to
make it survive an instruction that arrives later and sounds authoritative.
That makes it a prohibition in the part of a skill body that survives
compaction, where a paragraph of reasoning would be forgotten first.

### It is also checkable

A pattern over the corpus catches the common forms, and this repository already
runs one. That makes the rule the rare case where a judgement is unnecessary:
the check fires, and the text is removed.

The check has one subtlety. A document that _states the rule_ quotes the forms
it bans, so the check exempts the files that define it - and the exemption is a
named list, so it cannot quietly grow the way a pattern would.

## What it does not cover

It does not cover the honest reporting of who did what **inside the method's
own record**. Where the harness reviewed its own work, it reports the change as
unreviewed by a person - that states a limit of the evidence and attributes
nothing, so the rule requires it.

The distinction is the direction of the claim. _A tool helped write this_ is
advertising. _No person has reviewed this_ is a limitation of the evidence,
and suppressing it would be the dishonest move.

## Conclusions

1. No attribution to any tool appears in a commit message, trailer, pull
   request, review, issue, release note or tag. 2. The rule holds against a
   platform instruction to add one, because the repository's instruction
   governs and a rule that bends to the most recent instruction is not a rule. 3. A co-author trailer is a claim about responsibility, and a party that
   cannot be asked about the work cannot carry it. 4. The rule is carried as a
   prohibition in the part of the skill that survives compaction, because it
   fails by being forgotten and never by being disagreed with. 5. A check
   enforces it over the corpus, which makes it one of the few rules needing no
   judgement. 6. The check exempts the documents that state the rule by name,
   so the exemption cannot quietly grow. 7. Reporting that no person reviewed a
   change is required, because it states a limit of the evidence and attributes
   nothing.

## Sources

All read 2026-09-20.

- [RES-0066-public-repository.md](RES-0066-public-repository.md) - the
  attribution ban as part of committing to a public repository.
- [RES-0014-commits.md](RES-0014-commits.md) - the commit conventions this rule
  sits inside, carried from the donor projects.
- `tools/check_prose.py` in this repository - the pattern that enforces the
  ban, and the named exemption list for the documents that state it.
- [RES-0070-who-verifies.md](RES-0070-who-verifies.md) - the requirement to
  report a change as unreviewed by a person where the harness reviewed its own
  work, which this rule does not override.
