---
id: TSK-NNNN
artifact: task
status: draft # draft, then approved; done is derived from the authorising record's mark
revised: YYYY-MM-DD
epic: EPC-NNNN # or bug: BUG-NNNN, where a defect carries this task itself; name one
closes: [REQ-NNNN] # the requirements it closes; a defect's task restores one and may close none
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

One task to a line, each saying whether it blocks and why, or `Nothing.`
where the task depends on none. `paw ready cover` and `paw ready implement`
wait only on a blocking line. A dependency that exists only for convenience
is declared as not blocking, never left out.

- TSK-NNNN (blocking): what this task needs from it before it can start.
- TSK-NNNN (not blocking): what the two share, which either task can write.

## Cover

Not yet. The cover step replaces this line with four, `Checks`,
`Failing run`, `Landed in` and `Judgement`, and `paw ready implement` refuses
the task until they are filled.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

What was deliberately not changed, documentation included, and why.
