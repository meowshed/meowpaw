---
id: TSK-NNNN
artifact: task
status: draft # draft, then approved; done is derived from the epic's mark
revised: YYYY-MM-DD
epic: EPC-NNNN
closes: [REQ-NNNN] # required: a task that closes nothing has no authority
issue: # the tracker's number, where the repository uses one
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# <What this task does>

What this task makes true, in a sentence or two, so a reader who stops here
knows whether it is theirs. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given <a starting state>, when <an action>, then <an observable outcome>.
   Closed by: <the evidence that will show it, such as a named test or a
   command's output>.

Each criterion is a state, an action and an outcome someone can observe,
never an adjective, and names the evidence that will close it. Where the work
predicts a measurable outcome, the criterion states the predicted number now,
before the work. The repository's definition of done applies as well and
isn't restated here.

## What to do

Enough that an implementer with none of the conversation can do it: the
constraints that bind the result, the interfaces it touches, and the evidence
that will close each requirement it cites. Not how to do it.

## Depends on

The tasks that must be done first, as `TSK-` identifiers, and why. `meow-method
ready implement` reads this section.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

What was deliberately not changed, documentation included, and why.
