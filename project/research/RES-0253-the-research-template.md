---
id: RES-0253
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0029, RES-0012
---

# The research template

## Summary

A hundred documents were written to a shape nobody wrote down, and repetition
is not evidence that it is right. The established form separates four things,
and this corpus merges two of them. What was done appears nowhere, so a reader
cannot tell a specification read in full from a summary skimmed off a search
result. Three sections are new - a summary, a method, and a traceability
requirement on conclusions - and the index should carry the summary, where the
scope note answers nothing.

Research for the shape of a research document: which sections it has, what each
one is for, and what a reader must be able to do with it that the current shape
does not allow.

One of nine template documents, one per artifact kind in the record.

It does not cover how research is conducted, which is
[RES-0029-research-technique.md](RES-0029-research-technique.md), nor the
command that produces one, which is [RES-0052-chain.md](RES-0052-chain.md).

## The question

This corpus has a hundred research documents written to a shape nobody wrote
down: a question, findings, conclusions, sources. Repetition produced that
shape and nobody designed it, and repetition is no evidence that it is right.

So the question is what the established form for reporting an investigation
contains, and what this corpus's shape is missing.

## Method

The established report structure was fetched and read on 2026-09-20 for its
four sections, the four questions they answer in order, and its stated reason
for separating them, which we quote in full.

We then read this corpus against it. We examined the documents in the research
directory for which carry provenance in prose and which do not, and read the
index to see what its rows summarise.

Nothing was measured. No reader was asked whether the current shape costs them
anything, so the claim that a missing method section is the largest structural
defect is an argument, and no finding about readers.

## Findings

### The established structure separates three things this corpus merges

The scientific report has a standard structure, IMRaD, and its value is
explicitly the separation, where the order carries nothing. The four sections
answer four questions in sequence: **why did you do it, what did you do, what
did you find, what does it mean.**

The property this corpus copies is stated directly in the guidance: the results
section reports findings **without interpretation**, and the discussion
explains what they mean. _"These distinctions enable readers to evaluate
methodology independently from findings and findings independently from
interpretations."_

Against that, this corpus's research documents have a question, a findings
section that mixes observation with interpretation, conclusions, and sources.
Two of the four separations are missing:

- **What was done is nowhere.** There is no methods section. A reader cannot
  tell whether a finding came from reading a specification, from running a
  command, from a vendor's marketing page or from a search-result summary,
  except where the author happened to say so in passing.
- **Observation and interpretation are in one section.** A findings heading in
  this corpus typically contains a fact, the author's reading of it, and the
  consequence for the harness, in three consecutive sentences.

The second is defensible for a design corpus and the first is not.

### The missing methods section is the corpus's largest structural defect

The method's own standard is that a claim without evidence is not a claim, and
that a figure from a secondary source is recorded as reported and never
repeated as fact. Both rules are about provenance, and both are enforced today
by the author remembering to write a sentence.

Where it was remembered, the corpus is strong. Some documents say a page did
not resolve, that two secondary sources disagree, or that a claim came from a
search index where no readable page could be reached. One records a command run
locally with its output. Where it was not remembered, a reader cannot
distinguish a specification read in full from a summary skimmed from a search
result.

A methods section makes that structural, so it survives an author who forgets.
It states what was read, what was run, what was searched and what could not be
obtained. The last is the most valuable, because an absent source is invisible
in every other section.

It also makes the document **re-checkable**, which is the property a dated
corpus needs most. A year from now the question is never _is this still true_
in general. It is _does this specific check still give this specific answer_,
and only a written-down check answers it.

### A conclusion that does not trace to a finding is the failure this shape exists to prevent

The discussion in the established structure is where interpretation lives, and
its discipline is that it interprets _the results reported above_ and
introduces none.

This corpus already requires conclusions, and requires them to be written
without reference to any requirement so the chain stays one-way. What it does
not require is that each conclusion be traceable to a finding.

That is a checkable property and it is not checked. A conclusion supported by
nothing in the document is the easiest defect to commit here. Conclusions are
written last, when the argument feels settled and the author is reasoning from
everything they now know, which is more than they wrote down.

### What the abstract does, and why this corpus's opening paragraph is not one

The structured abstract is _"a summary of the methods, results, and
implications"_ - it tells a reader whether to read the document.

This corpus's documents open with a paragraph describing scope and a _does not
cover_ pointer. That is a scope note and no summary: it says what the document
is about, and never what it found.

The index compounds this. The synthesis document lists every research document
with its opening paragraph as the summary, so the corpus's own index tells a
reader what each document is about and never what it concluded. For a hundred
documents that is the difference between an index that answers questions and
one that routes.

### The dating rules this corpus invented are absent from the standard form

Two conventions here have no equivalent in the scientific form and are better
than it for this purpose:

Every source carries the date it was read. A specification's defaults change
under the same command name, and a reader in a year needs to know what to
re-check, where being told to trust it helps nobody.

A fact that is time-sensitive carries its own date inline, and the sources
alone are not enough.

Both come from the subject matter: this corpus is mostly about tools that move.
The scientific form assumes a literature that does not.

### Where the corpus's current shape is better than the standard one

Two things, and they should survive the rewrite.

Conclusions are numbered and imperative. A research document here ends in a
list of statements that requirements can be built from, each standing alone.
That is a downstream interface, and a discussion section of flowing prose would
lose it.

A pointer to what the document does not cover. In a corpus of a hundred
linked documents, the boundary statement prevents the same ground being covered
twice and tells a reader where to go instead. No single-paper form needs this;
a corpus does.

### The sections it carries

| Section      | What it holds                                                | Mandatory |
| ------------ | ------------------------------------------------------------ | --------- |
| Front matter | Identifier, kind, status, revision date, what it elaborates  | Yes       |
| Title        | What was investigated                                        | Yes       |
| Summary      | What was found, in three or four sentences                   | Yes       |
| Scope        | What this covers, and what it does not, with pointers        | Yes       |
| The question | Why the investigation was done, and what turns on it         | Yes       |
| Method       | What was read, run, searched, and what could not be obtained | Yes       |
| Findings     | What was observed, each with its evidence                    | Yes       |
| Conclusions  | Numbered, standing alone, each traceable to a finding        | Yes       |
| Sources      | Every source, with the date it was read and what was taken   | Yes       |

Three of those are new to this corpus: the summary, the method, and the
traceability requirement on conclusions.

The order matters for one of them. The summary comes before the scope because
it is what decides whether the document is read, and a reader who has to pass
a boundary statement first has already paid for the document.

### What the template must refuse

A finding with no evidence. A statement of what the author believes is not
an observation.

A conclusion that no finding supports. This is the one to make checkable
first, because it is the most common and the most consequential.

A source with no read date.

A methods section that says what was concluded. The separation is the whole
value, and the commonest way to lose it is to summarise findings inside the
method.

A document with no conclusions, which is already enforced by a check.

## Conclusions

1. A research document separates why, what was done, what was found and what it
   means, because the separation is what lets a reader evaluate the method
   independently of the findings and the findings independently of the
   interpretation. 2. A method section is mandatory and states what was read,
   what was run, what was searched, and what could not be obtained. 3. What
   could not be obtained is recorded, since an absent source is invisible in
   every other section. 4. A method section makes a document re-checkable,
   which is what a corpus about tools that move needs most. 5. Each conclusion
   traces to a finding in the same document, and one that traces to nothing is
   a defect. 6. Conclusions remain numbered, imperative and standing alone,
   because they are the interface the requirements step builds on. 7. A summary
   precedes the scope note, stating what was found, where the scope note says
   what the document is about, because it is what decides whether the document
   is read. 8. The index carries the summary, so the corpus's index answers
   questions where an opening paragraph would only route. 9. The scope note
   stays, with pointers to the documents covering adjacent ground, because a
   corpus needs boundaries that a single paper does not. 10. Every source
   carries the date it was read, and a time-sensitive fact carries its date
   inline as well. 11. A finding carries its evidence, and a statement of
   belief is not an observation. 12. Interpretation is not written into the
   method section, since that is the separation the structure exists for.

## Sources

All read 2026-09-20.

- [Writing an IMRaD report](https://writingcenter.gmu.edu/writing-resources/imrad/writing-an-imrad-report)
  and [IMRaD format explained](https://blog.amwa.org/imrad-format-explained) -
  the four sections and the four questions they answer in order; that the
  results section reports findings without interpretation while the discussion
  explains what they mean; the stated benefit that the separations let readers
  evaluate methodology independently from findings and findings independently
  from interpretations; the methods section written in enough detail for
  replication; and the abstract as a summary of methods, results and
  implications.
- [RES-0029-research-technique.md](RES-0029-research-technique.md) - the
  adversarial pass, the rule against manufacturing findings, and what makes a
  comparison honest.
- [RES-0052-chain.md](RES-0052-chain.md) - the command that produces a research
  document, the requirement that conclusions be written without reference to
  any requirement, and the rule that a figure from a secondary source is
  recorded as reported.
- [RES-0012-catalogues.md](RES-0012-catalogues.md) - templates and indexes as
  artifacts, and what an index owes.
- This corpus, read 2026-09-20: one hundred and five research documents in
  `project/research/`, examined for which carry provenance in prose and which
  do not, and `project/research/RES-0001-synthesis.md`, whose index rows are
  generated from each document's opening paragraph.
