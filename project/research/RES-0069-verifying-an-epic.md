---
id: RES-0069
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Verifying an epic

## Summary

Verifying an epic asks whether the decision behind the work was realised. Every
way a decomposition can be wrong survives task verification untouched: a
missing task, a task that built something adjacent, evidence that closed a
requirement the decision never meant. So the epic is measured against the
authorising record, and never against its own task list.

Research for the third of three activities the method had been calling by one
name. This one asks whether the decision behind the work was realised. It does
not ask whether the corpus is consistent, which is
[RES-0067-checking-the-record.md](RES-0067-checking-the-record.md), nor whether
a task did what it said, which is
[RES-0068-verifying-a-task.md](RES-0068-verifying-a-task.md).

It covers why a complete task list is not a realised decision, what the
discipline calls the gap, and what an epic's own completion test has to
contain.

## The question

An epic exists to realise one authorising record: a decision or a defect. Its
tasks were cut from the requirements that record addresses, and each task was
verified against what it claimed.

The question is whether anything is left. It is not obviously a question at all

- if every task passed, what could be missing - and the answer is the reason
  this activity is separate.

## Method

We fetched and read the published material on acceptance at the level above a
single item on 2026-09-20. We also read the surveyed harnesses for whether any
of them verifies above the task, and none does.

Nothing was run. The enumeration of ways a decomposition can be wrong was
derived by working through the model, and we observed no failures, which is its
limitation.

## The gap this exists to find

A decomposition is a judgement made once, before the work, about how a set of
requirements divides into tasks. Every way it can be wrong survives task
verification untouched.

A requirement the decomposition missed is closed by no task, so no task
fails. **A requirement deferred with a reason** is recorded as deferred, and
the deferral is never revisited because no task is waiting on it. **A
requirement two tasks each believed the other covered** is cited by neither.
A task added after approval to cover something the decomposition missed
proves that the decomposition was wrong and says nothing about what else it
missed.

In every case the task list is complete and the decision is not realised. That
is the gap, and only a check against the authorising record itself finds it.

## Findings

### This is the level where verification meets validation

Boehm's split puts the two questions at different levels. Verification asks
whether the output conforms to the input; validation asks whether the right
thing was built.

Task verification is purely the first: the evidence against the requirements
cited. Epic verification is the first applied to a different input: the
authorising record's full requirement set, where a task verification reads one
task's citations. It is also the first point at which the second question can
be asked, because it is the first point with a whole thing to ask about.

The method stops short of validation deliberately. Whether the decision was
right is answered by its reversal condition, on evidence, later; whether the
decision was realised is answerable now.

### Benefits realisation names the failure at the level above

Outside software, the practice of checking whether a completed initiative
delivered what justified it is called benefits realisation. Its central
discipline is to compare actual outcomes against the ones planned, and its
stated failure mode is **tracking activity where the outcomes are what
matter**.

That failure is exactly the one an epic verified by its task list commits. A
complete task list is activity. A realised decision is the outcome, and the two
are measured differently.

The practice is not adopted wholesale here: benefits realisation measures
business value after release, which is validation and is out of scope. What
transfers is the comparison discipline - planned against actual, at the level
of the thing that was authorised - and the warning about counting activity.

### The definition of done divides by level too

The agile split between a universal definition of done and item-specific
acceptance criteria appears again here, one level up. A feature-level or
epic-level definition of done is a standing set of conditions, distinct from
any story's. The sources describe teams using an epic tier explicitly for large
initiatives, where the story-level checks are not enough.

For this method the epic's acceptance criteria are the requirements its
authorising record addresses. Its definition of done is what the method demands
of a finished epic: every requirement closed or explicitly deferred with a
reason, every task accounted for, and no artifact in a state the record check
would report.

### An epic is not verified by re-running its tasks

The task verifications are inputs. Re-running them answers a question already
answered and costs the same again, and worse, it invites the epic's check to
become a longer task check, where it should ask a different question.

The question the epic adds is about the requirements no task claimed. That
question cannot be asked of a task, because a task can only be asked about what
it cited.

### The outcome is a status and, where the gap is real, a report

Where a requirement the record addresses is closed by nothing, the honest
outcome is a reported gap, and never a silently added task. Deciding whether to
extend the epic or amend the decision is a judgement. The requirement may be
unnecessary, which makes the decision wrong, or the decomposition missed it,
which makes the epic incomplete. Those are different repairs and the harness
cannot choose between them.

## Conclusions

1. An epic is not verified by its tasks being done. A complete task list that
   leaves a requirement of its authorising record unclosed is an incomplete
   epic, and nothing at the task level can see it. 2. Its subject is the
   authorising record's requirement set, and never the union of what the tasks
   cited. The difference between those two sets is the whole point of the
   activity. 3. Its trigger is the tasks being done, which is the earliest
   moment the question can be answered and the last moment it is cheap to act
   on. 4. An epic carries its own acceptance criteria, distinct from a task's:
   every requirement of its authorising record closed or deferred with a
   reason, every task accounted for, and nothing outstanding that the record
   check would report. This document originally called those the epic's
   definition of done, which conflated two obligations; the correction is in
   [RES-0256-the-epic-template.md](RES-0256-the-epic-template.md). 5. An epic
   states those criteria, and inherits no unwritten condition, and may add to
   the repository's definition of done without removing from it. 6. The task
   verifications are inputs and are not repeated. The epic's question is about
   what no task claimed, which no task can be asked. 7. A requirement closed by
   nothing is a reported gap, never a task added silently, because extending
   the epic and amending the decision are different repairs and choosing
   between them is a judgement. 8. A deferral is revisited here. It is the only
   point at which a requirement deferred with a reason is looked at again by
   anything. 9. Counting activity is the failure to design against. The
   practice one level up calls this out by name, and a task list is activity. 10. This is where verification stops and validation would start. Whether the
   decision was realised is answerable now; whether it was right is answered by
   its reversal condition, on evidence, later.

## Sources

All read 2026-09-20.

- [Benefits realisation
  management](https://en.wikipedia.org/wiki/Benefits_realisation_management)
  and [Benefits realization management, a
  guide](https://www.epicflow.com/blog/benefits-realization-management/) -
  comparing actual outcomes against planned ones when an initiative finishes,
  outcomes as changes stakeholders identified as important, and the stated
  failure of tracking activity where the outcomes are what matter. - [Agile
  epics, a guide](https://monday.com/blog/rnd/agile-epics/) - the epic tier
  used above stories for large initiatives, and measurement that keeps an epic
  on track by its goals, and never by its activity. - [Acceptance criteria
  versus definition of
  done](https://www.theserverside.com/tip/Acceptance-criteria-vs-definition-of-done-Whats-the-difference)
  - the universal definition of done against item-specific acceptance criteria,
    applied here one level above the story. - [IEEE 1012-2016, verification and
    validation](https://blog.ansi.org/ansi/ieee-1012-2016-verification-validation-vv/)
  - the split between conformance to the input and satisfaction of the need,
    which is where this activity ends and validation would begin.
