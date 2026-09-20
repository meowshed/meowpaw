---
id: RES-0232
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0030, RES-0067
---

# The `artifact-review` skill

## Summary

Reviewing the record is not reviewing code with different nouns: the defects
are mostly omissions, and an omission is invisible in a diff because nothing
was written. So the review runs against a fixed question set per artifact kind
rather than against the text, which is the same mechanism the architecture
standards use. The mechanical corpus checks are not repeated as judgements, and
a finding must change what somebody does.

Research for one of three review skills: reviewing the project's own record -
research, requirements, decisions, specifications, epics and tasks. Its
siblings are [RES-0231-reviewing-code.md](RES-0231-reviewing-code.md) and
[RES-0233-reviewing-documentation.md](RES-0233-reviewing-documentation.md).

## The question

Reviewing a document is not reviewing code with different nouns. The defects
are different, most of them are omissions, and the mechanical checks that exist
cover a smaller fraction of what matters.

## Method

This document draws on research already in this corpus: the record-checking
research for which defects are mechanical and therefore out of scope here, the
review research for the order and the adversarial pass, the architecture
research for the fixed-question-set mechanism, and the per-kind standards for
what conformance means.

No external source was consulted for this skill, which is a gap: the per-kind
question lists are derived from this project's own standards rather than
compared with anyone else's practice.

Nothing was reviewed as an experiment.

## Findings

### The corpus checks already cover one half, and the skill covers the other

Checking the record - identifiers resolving, links working, coverage in both
directions, front matter present, index agreeing with the tree - runs as a
verb on every change. That is mechanical and is not this skill's job.

What is left is everything a program cannot settle, and it is most of the
value: whether a requirement is testable, whether a decision states a real
alternative, whether a conclusion follows from its findings, whether a document
mixes two kinds.

Stating the division explicitly is what stops the skill re-implementing checks
as judgements, which is the failure that makes a review slow and redundant.

### Most defects here are omissions, which changes how the review is done

A missing requirement, an unaddressed consequence, an alternative nobody
considered, a failure state nobody named. None of them appears in a diff,
because nothing was written.

So the review is against a **fixed set of questions** rather than against the
text. That is the same mechanism the architecture standards use - an unanswered
question is visible where a missing paragraph is not - and it is why a
checklist here is not bureaucracy.

The questions differ per artifact kind:

| Artifact      | What is most often missing                                                                                  |
| ------------- | ----------------------------------------------------------------------------------------------------------- |
| Research      | Conclusions that follow from the findings; sources with read dates; the argument against the leading option |
| Requirement   | Testability; a single obligation; standing alone; a citation upstream                                       |
| Decision      | The alternatives and why each lost; the cost; what would reverse it                                         |
| Specification | A statement for a requirement in force; removal of what is no longer true                                   |
| Epic          | Acceptance criteria that the authorising decision would recognise                                           |
| Task          | A definition of done; the evidence that would close it                                                      |

### Conformance before correctness, the same order as code

Does this artifact meet the standard for its kind, before is what it says
right. A correctness objection to a document that is the wrong kind is wasted.

### Two things a reader can check that a check cannot

Whether the document mixes kinds. A tutorial with reference material in it
is two documents, and the reader of either is served badly.

Whether a rule states its reason. A rule with no reason cannot be applied
to a case its author did not foresee, which is most cases.

### The adversarial pass applies here too, and harder

A model reviewing a document it did not write will find phrasing to object to
indefinitely. The finding has to be attacked before it is reported, and the
test is specific: **would this change what somebody does?**

A finding that improves the prose and changes nothing about the work is a
preference, and belongs marked as one or not at all.

### The date is a reviewable property

This corpus's artifacts carry the date they were revised and the date each
source was read. A citation pointing at an artifact revised after the citation
was written is a suspect link, and nothing currently looks for it.

That makes staleness a review question until it becomes a check: is this
document's account of a tool still the tool's behaviour.

## Conclusions

1. The mechanical checks are not repeated as judgements, since checking the
   record runs as a verb on every change.
2. The review is against a fixed set of questions per artifact kind,
   because most defects here are omissions and an omission is invisible in a
   diff.
3. Conformance to the kind's standard comes before correctness, for the
   same reason it does in code.
4. A document that mixes two kinds is a finding, whatever the quality of
   each part.
5. A rule that does not state its reason is a finding, because it cannot be
   applied to an unforeseen case.
6. A finding must change what somebody does, or it is a preference and is
   marked or dropped.
7. Every finding is attacked before it is reported, and one that does not
   survive is dropped without narration.
8. A citation to an artifact revised after the citation is treated as
   suspect, which is a review question until a check can make it.
9. A clean artifact is stated plainly as clean.

## Sources

All read 2026-09-20.

- [RES-0067-checking-the-record.md](RES-0067-checking-the-record.md) - the
  mechanical corpus checks, the defect list, and the suspect link that nothing
  currently detects.
- [RES-0030-review.md](RES-0030-review.md) - the severity model, conformance
  before correctness, and the adversarial pass.
- [RES-0072-architecture-discipline.md](RES-0072-architecture-discipline.md) -
  the fixed question set as the mechanism that makes an unanswered question
  visible.
- [RES-0028-requirements.md](RES-0028-requirements.md),
  [RES-0011-artifact-lifecycle.md](RES-0011-artifact-lifecycle.md) and
  [RES-0069-verifying-an-epic.md](RES-0069-verifying-an-epic.md) - the
  per-kind standards the conformance verdict is against.
