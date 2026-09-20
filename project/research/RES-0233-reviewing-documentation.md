---
id: RES-0233
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0020, RES-0030
---

# The `documentation-review` skill

## Summary

Documentation has a reader who is not on the team, cannot ask a question and
will stop reading, so it can be accurate, complete, well written and useless.
The first review question is which kind of document this is, because the
commonest defect is a document that is two of them. The most valuable action is
mechanical: follow the quick start on a clean machine, which is what finds the
unstated prerequisite.

Research for one of three review skills: reviewing the documentation a project
publishes for its users. Its siblings are
[RES-0231-reviewing-code.md](RES-0231-reviewing-code.md) and
[RES-0232-reviewing-project-artifacts.md](RES-0232-reviewing-project-artifacts.md).

## The question

Documentation has a reader who is not on the team, cannot ask a question, and
will stop reading. That makes its failure modes different from both code and
the project's own record: a document can be accurate, complete, well written
and useless.

## Method

This document draws on research already in this corpus: the documentation
research for the four kinds and the generated-reference rule, the review
research for the shared discipline, the Markdown research for what the
structural and prose checks already cover, and the diagram research for what a
picture may not be the only source of.

No external source was consulted for this skill specifically.

No documentation was reviewed as an experiment, and no quick start was followed
to test the claim that following one finds the unstated prerequisite.

## Findings

### The first question is which kind of document this is

Tutorial, how-to, reference or explanation. The kinds serve different readers
in different states, and the most common documentation defect is a document
that is two of them.

A reference with narrative in it cannot be scanned. A tutorial with caveats in
it cannot be followed. Neither problem is visible sentence by sentence, which
is why the kind is the first review question, and no stylistic observation.

### Reference is generated, and a hand-written reference is a finding

Reference material derived from declarations stays true when the code changes;
a hand-written one is wrong at the first change nobody propagated.

So a hand-maintained reference is reported as a structural problem, and never
as an accuracy one, because fixing the entries does not fix the mechanism.

### A quick start is tested by following it

The most valuable review action for a readme or a getting-started page is to
run it on a clean machine, exactly as written.

Almost every such document has an unstated prerequisite - an installed tool, an
environment variable, a directory that must exist - which is invisible to
whoever wrote it and fatal to the reader.

That makes this the one review in the method with a mechanical action attached,
and where the action is impossible the review says the quick start was read and
never run.

### The readme is an inverted pyramid and carries no promotional furniture

What it is, who it is for, how to start, where to go next - in that order. A
badge row and a feature list before the first sentence delay the only question
the reader arrived with.

### Accuracy questions a reviewer can actually answer

- **Does the example run?** An example that does not is worse than none,
  because the reader assumes their environment is wrong. - **Is the version
  stated?** A document about a tool that has changed is wrong without any of
  its sentences being false. - **Are the links relative and do they survive a
  move?** - **Does the diagram assert something the prose does not say?** A
  diagram is never the only place a fact lives, because a reader may receive
  the source and never the picture.

### The parts that are checkable are not reviewed

Structure, spelling and link resolution are checked by a verb. A review that
spends its findings on a missing full stop has spent them on what a check
covers, and the finding a reader needed is not in the report.

The prose linter covers a further slice - consistency against a declared style

- and stops where judgement starts. The review starts where it stops.

## Conclusions

1. The kind is identified first, and a document that is two kinds is a finding
   regardless of the quality of each part. 2. A hand-written reference is
   reported as a structural problem, since fixing entries does not fix the
   mechanism that made them wrong. 3. A quick start is followed on a clean
   machine, and where that is impossible the review says it was read and never
   run. 4. An unstated prerequisite is the most likely defect and is what
   following the instructions finds. 5. A readme is an inverted pyramid with no
   promotional furniture before the first answer. 6. An example that does not
   run is worse than no example, because the reader blames their environment. 7. The version the document describes is stated, or the document is wrong
   without any sentence being false. 8. A diagram is never the only place a
   fact lives, since a reader may get the source and never the picture. 9. What
   a check covers is not reviewed, so findings are spent on what only a reader
   can see. 10. A clean document is stated plainly as clean.

## Sources

All read 2026-09-20.

- [RES-0020-documentation.md](RES-0020-documentation.md) - the four kinds and
  the rule against mixing them, reference generated and never hand-written, and
  the readme as an inverted pyramid. - [RES-0030-review.md](RES-0030-review.md)
  - the severity model and the adversarial pass both reviews share. -
    [RES-0111-markdown.md](RES-0111-markdown.md) - what the structural linter,
    the prose linter, the spell check and the link check cover, and therefore
    what a review must not spend findings on. -
    [RES-0073-diagrams.md](RES-0073-diagrams.md) - that everything a diagram
    asserts is stated in prose beside it.
