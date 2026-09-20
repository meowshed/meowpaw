---
id: RES-0259
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0012, RES-0067
---

# The index template

## Summary

The index is the only document in the record whose content could be computed,
and the finding is that it should be. This corpus has already been through the
failure: its research index was forty documents behind with six changed titles,
and nothing noticed because it was prose that happened to be true. What
generation cannot supply is the choice of what each row says, and the current
choice is wrong. The rows carry scope notes, so a hundred of them answer what
each document is about and never what it found.

Research for the shape of an index: the living document that says what is in a
directory and lets a reader find the one artifact they need.

One of nine template documents, one per artifact kind in the record. It is the
last of them, and the only one whose content is derivable from the others.

It does not cover the checks that keep an index honest, which are
[RES-0067-checking-the-record.md](RES-0067-checking-the-record.md).

## The question

A corpus of a hundred research documents, seven hundred requirements and fifty
decisions is not readable. The index is what makes it usable, and it is the
only document in the record whose content could be computed.

So the template question is what a generated index should contain, and what a
human-written one adds that generation cannot.

## Method

This corpus was the evidence. The index was read before and after being
regenerated, and the discrepancy - forty missing documents and six titles
changed under it - was measured rather than estimated, by comparing the listing
with the directory.

The rules for what an index owes come from research already in this corpus, and
from no new external source. The generation rule comes from the record-checking
research, which names index disagreement as a defect checked in both
directions.

No external source was consulted for this document.

## Findings

### An index that can be generated should be generated

Everything a directory listing supplies is derivable: the identifier, the
title, the status, the revision date. A hand-maintained copy of it is wrong the
first time somebody adds a file without updating the table.

This corpus has already been through the failure. The research index was forty
documents behind and carried six titles that had changed under it, and nothing
noticed, because the index was prose that happened to be true.

The correction is structural, and no diligence supplies it: **the index is
generated from the tree, and a check fails where the two disagree in either
direction**. A file present and unlisted is undiscoverable, and a listing with
no file is a promise the repository does not keep.

### What generation cannot supply, and this corpus gets wrong today

A generated row can carry the title. It cannot decide what to say _about_ the
document, and the choice this corpus made is the wrong one.

Today each row carries the document's opening paragraph, which is a scope note:
it says what the document is about. So the index of a hundred research
documents answers _what is this about_ a hundred times and never _what did it
find_.

For a reader looking for an answer, a hundred scope notes is a routing table
with no information in it. The row should carry **what the document
concluded**, which is what a reader is choosing between.

That makes the index a genuine reason for the summary field the research
template introduces: the summary is written once, in the document, and the
index generates from it.

### An index has a reader, and the order is the design

The rows can be ordered by identifier, by date, by status or by topic, and the
choice decides what the index is for.

By identifier is right for a record that is cited: a reader arriving with an
identifier finds it immediately, and allocation order carries the history of
what was investigated when.

By topic is right where the corpus is large enough that a reader arrives with a
subject rather than an identifier - which is the state this corpus has reached.
A hundred documents in identifier order is a list; the same hundred grouped by
what they are about is a map.

Both are cheap to generate, so the template allows both views and requires the
grouped one where the directory exceeds a few dozen entries.

### The inverted pyramid applies to the prose above the table

An index has a paragraph or two before the listing, and the rule for it is the
readme's. What this directory holds, how the identifiers work, and where to go
next, in that order and with no throat-clearing.

The failure to avoid is an index that explains the method. That belongs in the
documentation, is read once by a person, and in an index displaces the one
thing the reader came for.

### Status belongs in the index; derived state does not

A row carries the stored status, because it is a fact about the document that a
reader choosing between rows wants.

It carries no derived state: whether a requirement is satisfied, whether a
decision is realised. Those are computed from elsewhere, and an index carrying
them has made a second copy that goes stale silently. The same rule the epic
template applies to per-task status applies here.

### The index is live, and it is the one document where staleness is invisible

Every other living document is read in full by someone who would notice it
contradicting the tree. An index is scanned, one row at a time, by a reader
looking for something else - which is exactly the reading that does not notice
a missing row.

So the index is the document that most needs a mechanical check and least
benefits from careful authorship, which is the argument for generating it
stated from the reader's side rather than the maintainer's.

### The sections it carries

| Section        | Holds                                                        | Mandatory                               |
| -------------- | ------------------------------------------------------------ | --------------------------------------- |
| Front matter   | Kind `index`, status `live`, revision date                   | Yes                                     |
| Title          | What this directory holds                                    | Yes                                     |
| What is here   | One paragraph: the kind, the identifier scheme, the lifetime | Yes                                     |
| How to read it | Where a newcomer should start, in one line                   | Where the directory is large            |
| The listing    | Generated: identifier, title, summary, status                | Yes                                     |
| Grouped view   | Generated: the same rows by topic                            | Where the directory exceeds a few dozen |

## Conclusions

1. The index is generated from the tree, because a hand-maintained copy of
   derivable facts is wrong the first time a file is added.
2. A check fails when the index and the tree disagree in either direction,
   since an unlisted file is undiscoverable and a listed absence is a broken
   promise.
3. A row carries what the document concluded, not what it is about, because
   a reader is choosing between answers rather than between subjects.
4. The row's summary comes from the document's own summary field, written
   once and generated from.
5. Rows are ordered by identifier, so a reader arriving with a citation
   finds it immediately.
6. A grouped view by topic is generated as well where the directory exceeds
   a few dozen entries, because a reader with a subject needs a map rather than
   a list.
7. The prose above the listing says what is here, how identifiers work and
   where to start, and explains no method.
8. A row carries the stored status and never a derived one, so no second
   copy goes stale.
9. The index is the document staleness hides in best, being scanned rather
   than read, which is the reader's argument for generating it.

## Sources

All read 2026-09-20.

- [RES-0012-catalogues.md](RES-0012-catalogues.md) - catalogues, indexes and
  templates as artifacts, and what each owes its reader.
- [RES-0067-checking-the-record.md](RES-0067-checking-the-record.md) - index
  disagreement as a named corpus defect, checked in both directions.
- [RES-0020-documentation.md](RES-0020-documentation.md) - the inverted pyramid
  and the rule against promotional or explanatory furniture ahead of the
  answer.
- [RES-0253-the-research-template.md](RES-0253-the-research-template.md) - the
  summary field the index generates from, and the finding that this corpus's
  index currently carries scope notes instead.
- This corpus, read 2026-09-20: `project/research/RES-0001-synthesis.md`, whose
  index table was forty documents behind with six changed titles before being
  regenerated, and `project/README.md`.
