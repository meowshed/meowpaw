---
id: RES-0223
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0065, RES-0022
---

# The `pull-requests` skill

## Summary

A proposal is the only artifact in the method written for somebody who was
not there. Size is the variable that decides whether review happens at all -
beyond a point the review becomes an approval and nothing distinguishes the
two. The description states what changed in the requirement's terms, why, and
the evidence as a reference to a run at a named revision rather than an
assertion that checks pass.

Research for one source-control convention: what a proposal contains, how large
it may be, and what a series of dependent proposals owes its reviewer.

Its siblings are
[RES-0221-conventional-commits.md](RES-0221-conventional-commits.md),
[RES-0222-branching.md](RES-0222-branching.md) and
[RES-0224-attribution.md](RES-0224-attribution.md).

## The question

A pull request is the only artifact in the method that exists to be read by
somebody who was not there. Everything else - the requirement, the decision,
the task - is written for the record; this one is written for a person who has
to decide.

## Method

This document draws on research already in this corpus rather than on new
external sources: the stacked-proposal research for the ordering and staleness
rules, the verification research for the inspection finding about size, and the
forge and tracker research for the three-valued status and the linking words.

The inspection figures behind the size rule are recorded there as reported and
unverified, and that limitation carries into this document unchanged.

Nothing was run.

## Findings

### Size is the variable that decides whether review happens

The inspection literature's finding is that effectiveness falls with the size
of what is in front of the reader, with a session limit well below what a
normal change contains. Those figures are recorded in this corpus as reported
and unverified, and the mechanism is not in doubt.

So the rule is not _keep pull requests small because it is tidy_. It is that
beyond a size, the review stops being a review and becomes an approval, and
nothing in the process distinguishes the two.

### A description states the change, the reason and the evidence

The three parts, and what each is for:

- **What changed**, in the terms of the requirement rather than the file tree.
  A reviewer who has to derive the intent from the diff is doing the author's
  work.
- **Why**, which the diff cannot carry.
- **The evidence**: which checks ran, at which revision, and what they
  reported. Not a claim that the tests pass - a reference to the run.

The evidence part is what distinguishes this from a general convention. A
proposal whose evidence is _tests pass_ is asking the reviewer to trust an
assertion, and the method's whole position is that a claim without evidence is
not a claim.

### A stacked series has obligations a single proposal does not

Where a change is too large for one reviewable proposal, it becomes a series,
and the series carries rules:

They are ordered by dependency, and each states its base. A proposal whose
base is another proposal is not reviewable against the trunk, and saying so
prevents a reviewer reading the wrong diff.

The base is read back after any change to it. A rebase of the lower
proposal moves the upper one's base, and an upper proposal whose base moved has
a diff nobody has seen.

A check against a previous base is not evidence. This is the sharpest rule
in the stack, because the check is green, the label says passing, and it ran
against a tree that no longer exists. The evidence names the revision, which is
what makes the staleness detectable.

Only the bottom merges first. Merging out of order produces a diff in the
remaining proposals that includes changes nobody proposed.

### A pull request links to the work item, and the link is checked

Where a tracker is in use, the proposal carries the identifier, and the pack
verifies the link exists rather than assuming the convention was followed.

The linking word matters where an integration acts on it: a closing word
finishes the work item on merge, and a member of a stacked series that uses one
closes an item the series has only partly addressed.

### The review's state is three-valued

A proposal's checks are pending, passing or failing. Pending is neither
neighbour, and a harness that reads a rollup while a workflow is queued and
reports either is reporting something false.

### What it must refuse

To open a proposal larger than one reviewable change, which becomes a series.

To claim a check passed without naming the revision it ran against.

To merge out of order in a series.

To carry any attribution, which is
[RES-0224-attribution.md](RES-0224-attribution.md).

## Conclusions

1. A proposal contains one reviewable change, because beyond a size the
   review becomes an approval and nothing distinguishes the two.
2. The description states what changed in the requirement's terms, why, and
   the evidence, rather than leaving the reviewer to derive intent from the
   diff.
3. Evidence is a reference to a run at a named revision, never an assertion
   that checks pass.
4. A series is ordered by dependency and each proposal states its base.
5. A base is read back after it changes, since a rebase below moves the
   diff above.
6. A check against a previous base is not evidence, which is detectable
   only because the evidence names the revision.
7. Only the bottom of a series merges first, or the remaining proposals
   contain changes nobody proposed.
8. The link to the work item is verified rather than assumed, and the
   linking word is chosen so that a partial change does not close the item.
9. Check status is three-valued, and pending is reported as pending.
10. No proposal carries attribution.

## Sources

All read 2026-09-20.

- [RES-0065-stacked-pull-requests.md](RES-0065-stacked-pull-requests.md) - the
  dependency ordering, reading the base back, and that a check against a
  previous base is not evidence.
- [RES-0070-who-verifies.md](RES-0070-who-verifies.md) - the inspection
  finding that review effectiveness falls with the size of what is reviewed,
  recorded there as reported and unverified.
- [RES-0133-github-and-gh.md](RES-0133-github-and-gh.md) - the three-valued
  check status and reading a rollup while a workflow is queued.
- [RES-0134-linear.md](RES-0134-linear.md) - the closing and referencing magic
  words and what each does to a linked work item on merge.
