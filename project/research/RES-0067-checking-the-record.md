---
id: RES-0067
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Checking the record

## Summary

Checking whether the documents agree with each other is neither verification
nor validation. Giving it its own name changes when it runs and what it
reports: its subject is the corpus and never any unit of work, every change
triggers it, and it reports without changing anything. The tracing tools
converge on the same defect set, and two of their defects - a coverage link
pointing at an older version, and an orphan - are not checked here.

Research for the first of three activities the method had been calling by one
name. This one asks whether the documents agree with each other and with the
tree. It does not ask whether any piece of work is finished, which is
[RES-0068-verifying-a-task.md](RES-0068-verifying-a-task.md) and
[RES-0069-verifying-an-epic.md](RES-0069-verifying-an-epic.md).

It covers what the discipline calls this, what a corpus of linked documents can
be wrong about, what the tools that do it already detect, and when it should
run.

## The question

The method produces six kinds of accumulating record, three living documents
and a web of relations between them. Every one of those relations can be wrong,
and most of the ways they can be wrong are invisible to a reader of any single
document.

The harness had one word for three activities. This document exists because
naming them apart changes when each runs, what each may touch, and what each
reports, and because two of the three were being triggered by the third.

## Method

We fetched and read the published material on verification and validation on
2026-09-20 for the distinction. We read the two open tracing tools'
documentation for their defect vocabularies, which is where outdated, predated
and deep-against-shallow coverage came from.

The tools were not installed or run against this corpus. The list of which
defects this repository already checks was compiled by reading its own checks,
and we ran neither tool.

## Findings

### The discipline already has the word, and it is not verification

Boehm's formulation, carried into IEEE 1012 and the testing standards ever
since, splits two questions. **Verification** asks whether the product was
built right: whether the output of an activity conforms to what went into it.
Validation asks whether the right product was built: whether it meets the
need.

By that division this activity is neither, and that is the useful finding. It
asks whether the _specification itself_ is internally consistent, before
anything has been built from it. IEEE 1012 places this among the verification
tasks performed on a requirements phase output, and it checks a document set,
where verification checks a system.

Calling it verification and calling a finished task's check verification means
one word covers a property of the corpus and a claim about work. The two are
triggered differently, scoped differently, and reported to different people.

### The tools that do this converge on the same defect set

`OpenFastTrace` traces a specification corpus and names its defects precisely.
An item is **covered** when every required coverage link exists and is valid,
and **undercovered** when one or more are missing. It can also be overcovered,
carrying more coverage links than required. Its defects divide in two.
**Direct** is a gap or error on the item itself: missing, outdated, predated or
unwanted coverage. **Transitive** is a gap caused by an undercovered provider
further up the chain.

The distinction between **shallow** and **deep** coverage is the one this
method takes. Full coverage means an item's own required links are present.
Deep coverage means full coverage of the item _and every transitive provider
down to a terminating item_. An item can be shallowly covered and deeply
broken, and only the deep check finds it.

`Doorstop` runs integrity checks over the document tree as its default action,
validating item traceability across the whole tree, and never per document.
Both tools make the same architectural choice: the check covers the corpus and
never one document, and it is the tool's primary verb, which no reporting
option replaces.

### Outdated and predated are the pair nobody implements

`OpenFastTrace`'s defect list contains two that most home-grown checks omit.
Outdated coverage points at an older version of what it covers; **predated**
coverage points at a version that does not exist yet. Both compare
fingerprints, where an existence check compares nothing, and both are invisible
to a link checker.

They matter here because this method already has the ingredient: an artifact
carries the date it was last revised, and evidence carries the tree revision it
was collected at. A link that resolves to an artifact revised after the citation
was written is a suspect link, and nothing currently looks for it.

### The check covers the corpus, so a change triggers it

Every property here is a property of the whole set: an identifier resolves or
it does not, an index matches the tree or it does not, a requirement has a
check or it does not. None of them is about a unit of work, and none of them
becomes true or false because a task finished.

That decides the trigger. A corpus property is checked when the corpus changes,
which is every change, which is what a verification verb is for. Running it as
a step in the chain would mean the corpus is knowably inconsistent between
steps and nobody is told.

It also decides the blame. A failure here belongs to the change that broke it,
and never to whatever unit of work happened to be in flight. Reporting it as a
failure of that unit is how a real corpus defect gets closed as "not my task".

### What can be wrong, enumerated

Drawn from the two tools and from what this corpus has actually contained:

| Defect                  | What it means                                                               |
| ----------------------- | --------------------------------------------------------------------------- |
| Broken link             | A relative link resolves to nothing                                         |
| Unresolvable identifier | A citation names an artifact that does not exist                            |
| Duplicate identifier    | Two artifacts claim the same one                                            |
| Undercovered item       | A requirement no check names                                                |
| Unwanted coverage       | A check naming a requirement that does not exist                            |
| Orphan                  | An artifact nothing cites and that cites nothing                            |
| Suspect link            | The cited artifact was revised after the citation                           |
| Index disagreement      | An entry with no file, or a file with no entry                              |
| Status disagreement     | A stored status the tree contradicts                                        |
| Vocabulary violation    | A status outside its kind's declared set                                    |
| Missing metadata        | An artifact with no kind, status or revision date                           |
| Shape violation         | A research document with no conclusions, a requirement with two obligations |

Eight of these are already checked in this repository. **Orphan and suspect
link are not**, and the transitive form of undercoverage is not.

## Conclusions

1. This activity is not verification and is not validation. It asks whether the
   documents agree with each other, before anything is built from them, and it
   needs its own name so that the other two can keep theirs. 2. Its subject is
   the corpus, never a unit of work. No finding here belongs to a task, and
   reporting one as a task's failure is how corpus defects get closed as
   somebody else's problem. 3. Its trigger is a change to the corpus, which is
   every change, which means it runs as a verification verb, and never as a
   step in the chain. 4. It reports and changes nothing. It has no status to
   move, because no status describes the corpus. 5. Coverage is checked deep as
   well as shallow. An item whose own links resolve can sit on a provider whose
   do not, and only the transitive check finds it. 6. Coverage is checked in
   both directions. An uncovered requirement and a check naming a requirement
   that does not exist are different defects and neither finds the other. 7. A
   link to an artifact revised after the citation is suspect, and this corpus
   has the dates to detect it and does not look. 8. An artifact nothing cites
   and that cites nothing is reportable. It is either work nobody connected or
   a document that should not exist. 9. The shape of an artifact is part of its
   consistency, and no separate concern: a research document with no
   conclusions and a requirement with two obligations are both corpus defects. 10. A false positive here is a defect in the check. A corpus check runs on
   every change, so one that fires wrongly is disabled within a week and then
   finds nothing at all.

## Sources

All read 2026-09-20.

- [IEEE 1012-2016, verification and
  validation](https://blog.ansi.org/ansi/ieee-1012-2016-verification-validation-vv/)
  and [Software verification and
  validation](https://en.wikipedia.org/wiki/Software_verification_and_validation)
  - Boehm's split between building the product right and building the right
    product, and the placement of checks on a requirements-phase output among the
    verification tasks. - [OpenFastTrace
    terminology](https://openfasttrace.itsallcode.org/terminology.html) -
    covered, undercovered and overcovered; the split between direct defects
    (missing, outdated, predated or unwanted coverage) and transitive defects
    caused by an undercovered provider; and full coverage against deep coverage
    through every transitive provider to a terminating item. -
    [OpenFastTrace](https://github.com/itsallcode/openfasttrace) - a tracing
    suite whose primary output is a report over the whole corpus, tracing itself
    as its own example. - [Doorstop](https://doorstop.readthedocs.io/en/latest/)
  - integrity checks over the document tree as the tool's default action,
    validating item traceability across the tree and never per document.
