---
id: RES-0068
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Verifying a task

## Summary

Verifying a task asks whether the finished work did what it said, which is two
completion tests and never one. The evidence closes the requirements the task
cited, and the task's own criteria hold. Evidence is measured against the
requirements cited, and never against what the work happened to produce, and
evidence collected before a later change is stale, which is worse than old.

Research for the second of three activities the method had been calling by one
name. This one asks whether a finished task did what it said it would. It does
not ask whether the corpus is consistent, which is
[RES-0067-checking-the-record.md](RES-0067-checking-the-record.md), nor whether
the decision behind the work was realised, which is
[RES-0069-verifying-an-epic.md](RES-0069-verifying-an-epic.md).

It covers what the discipline already separates at this level, why two
different completion tests are needed, where one leaves a gap, and what the
evidence has to satisfy.

## The question

A task cites the requirements it closes and claims to have closed them. The
claim is made by whatever did the work, which in this method is usually an
agent, and it is made at the moment the work feels finished.

The question is what has to be true before that claim is accepted, and the
answer has to be checkable by something other than the party making it.

## Method

The published material on completion criteria and evidence was fetched and
read on 2026-09-20, and the surveyed harnesses were read for what each accepts
as proof that a task is finished.

Nothing was run. No task was verified as an experiment, so the two completion
tests are a design claim tested against what comparable harnesses do.

## Findings

### The discipline separates two completion tests, and both must pass

Agile practice distinguishes **acceptance criteria** from a **definition of
done**, and the distinction is exactly the one this method needs.

Acceptance criteria are specific to one item: what that particular piece of
work must do. A definition of done is universal: the conditions any piece of
work must meet before it counts as finished, regardless of what it does.

The relationship is stated plainly in the sources: a story can pass its
acceptance criteria and still not be done, because the code has not been
reviewed, tested, merged or documented. Both lists have to be satisfied, and
neither substitutes for the other.

The ownership differs too. Acceptance criteria come from whoever wanted the
work; the definition of done is a standing policy of the team. That is why a
task cannot negotiate its own definition of done downward.

### Mapped onto this method, the two lists already exist

The requirements a task cites are its acceptance criteria. They are
specific to it, they say what it must make true, and they came from somewhere
other than the implementer.

The definition of done is everything else the method demands of a finished
task: evidence that cites a command and its revision, a status moved in the
same change, the requirement identifiers recorded, checks passing, one squashed
commit on a branch with a pull request.

Naming them this way settles a question that had been open: what verifying a
task is _for_. It is the moment both lists are checked, by something other than
the party that wrote the code.

### The claim is the thing being checked

This is what makes task verification different from running tests. The tests
were already run - the verbs run during implementation, and a task may not be
reported complete while one relevant to the change fails or is unresolved.

What verification adds is the comparison: **does the evidence that exists close
the requirements that were cited?** A task can have a green test suite and
close nothing, because the tests it ran prove other requirements, or prove
nothing about any.

That comparison is why the evidence has to name the requirement. Without the
identifier there is no way to ask the question, only a way to observe that
something passed.

### Evidence at the wrong revision is the failure to design against

Evidence expires on every modification of the tree, and implementation modifies
the tree after it runs the verbs. So by the time a task claims completion, the
evidence it points at was almost certainly collected at an earlier revision
than the one being claimed for.

Accepting it is the harness's characteristic failure in its purest form: a
claim proved at one revision, presented as a claim about another, with nothing
in the report distinguishing the two. The only honest options are to collect
the evidence again or to report the claim as unproven.

### A check that cannot fail closes nothing

The third thing to establish is whether the check named by the evidence could
have failed. A tautological assertion satisfies every structural rule here -
the evidence exists, it names the requirement, it ran at the right revision -
and proves nothing.

This is a judgement in most ecosystems, where no check settles it, and the
harness carries it as one. Where mutation testing is available it is a
measurement, and elsewhere it is a question asked per check.

### What a task's verification may change

One status, on one task. The work is not touched, the requirements are not
touched, and no artifact is written. A step that both detects and repairs
divergence repairs it in the cheap direction, which is always to make the
discrepancy disappear.

## Conclusions

1. A task carries two completion tests, and both are checked here. The
   requirements it cites are its acceptance criteria; everything else the
   method demands of a finished task is its definition of done. 2. A task
   states its acceptance criteria, and inherits no unwritten condition, because
   what this task must make true differs from what any other must, and an
   unstated condition is not checked. This document originally called that
   statement the task's own definition of done, which conflated two
   obligations; the correction is in
   [RES-0257-the-task-template.md](RES-0257-the-task-template.md), where the
   definition of done is the repository's and is referenced, never restated. 3.
   A task may add to the repository's definition of done and may not weaken it.
   An item-specific extra condition is a real thing; removing a condition the
   repository declared is not. 4. Verification asks whether the evidence closes
   the requirements cited, which is a different question from whether the tests
   pass. 5. Evidence that names no requirement closes nothing, and a task
   citing it is reported as unproven, and never as failed. 6. Evidence
   collected before the current revision is collected again, or the claim is
   reported as unproven. Accepting it is presenting a proof about one state of
   the tree as a proof about another. 7. A check that could not have failed
   closes nothing, and the task is reported as unproven for that requirement. 8. The task claiming to be done triggers it, and no schedule and no progress
   on the epic does. 9. The outcome is a status on that task and nothing else.
   No artifact, no repair, no edit to the requirements it failed to meet. 10. A
   failure here is a statement about the task, never about the corpus. A
   requirement that turns out to be wrong is a separate finding, routed through
   amendment.

## Sources

All read 2026-09-20.

- [Acceptance criteria versus definition of done](https://www.theserverside.com/tip/Acceptance-criteria-vs-definition-of-done-Whats-the-difference)
  - acceptance criteria as feature-specific requirements unique to one item
    against a definition of done as universal completion standards; the ownership
    split between whoever wanted the work and the team; and that work with
    acceptance criteria met and the definition of done unmet remains incomplete.
- [Definition of done versus acceptance criteria](https://nulab.com/learn/software-development/definition-of-done-vs-acceptance-criteria/)
  and [What is the definition of done](https://www.atlassian.com/agile/project-management/definition-of-done)
  - that the definition of done applies to every item while acceptance criteria
    apply to one, that the first covers process and quality and the second covers
    function, and that both must be satisfied for an increment to be complete.
- [IEEE 1012-2016, verification and validation](https://blog.ansi.org/ansi/ieee-1012-2016-verification-validation-vv/)
  - verification as conformance of an activity's output to its input, which is
    what comparing evidence against cited requirements is.
