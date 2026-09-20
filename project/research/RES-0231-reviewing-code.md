---
id: RES-0231
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0030, RES-0201
---

# The `code-review` skill

## Summary

The standard is improvement, and never perfection. That counts for more with a
model reviewer than a human one, because a model asked to review will always
find something, so the counterweight is a rule to say plainly when the change
is clean. Conformance and quality are two verdicts, in that order, and the
subject is the diff against a recorded base. The reviewer is given the
structure as well, because a structural regression is invisible in a diff by
construction.

Research for one of three review skills: reviewing a change to code. Its
siblings are
[RES-0232-reviewing-project-artifacts.md](RES-0232-reviewing-project-artifacts.md)
and
[RES-0233-reviewing-documentation.md](RES-0233-reviewing-documentation.md).

The shared severity model, the order of checks and the adversarial pass are in
[RES-0030-review.md](RES-0030-review.md); this covers what is specific to code.

## Method

The published review standard was fetched and read on 2026-09-20 and is quoted
in full, including its comment convention for marking a preference.

The rest comes from research already in this corpus. The review research gave
the severity model and the adversarial pass. The verification research gave the
measured self-preference bias, and the architecture research what a diff cannot
show.

Nothing was reviewed as an experiment, and no review was scored.

## The standard, restated because it is the whole thing

> In general, reviewers should favor approving a CL once it is in a state where
> it definitely improves the overall code health of the system being worked on,
> even if the CL isn't perfect.

And: _"there is no such thing as 'perfect' code - there is only better code."_

That matters more for a model reviewer than for a person, because a model asked
to review will always find something. An instruction to report findings with no
counterweight produces findings, and a review that manufactures them to look
thorough teaches everyone to skim reviews.

The countermeasure is a sentence, and it belongs in the body, where a rationale
would bury it: **say plainly when the change is clean.**

## What is specific to reviewing code

### Conformance and quality are two verdicts

A change can be a faithful implementation of the wrong thing. One verdict
cannot say so, so the review returns two: does this do what the requirement
said, and is it well made.

The order matters as well as the separation. Conformance first, because a
quality finding about code that should not exist is wasted, and the author will
act on the quality finding before noticing the conformance one.

### The subject is the diff against a recorded base

Not the working tree. A review of the working tree reviews whatever is
currently there, including uncommitted experiments, and cannot be repeated.

Where the base has moved - which a stacked series guarantees - the base is read
back before the diff is taken, or the review is of a diff nobody proposed.

### Structure is invisible in a diff by construction

Nothing in the changed lines says an import crossed a boundary, because the
boundary is not in the file.

So a review meant to catch structural regression is **given** the structure:
which parts the change touches, which dependencies it adds, and which of those
the architecture permits. The first two are computable, which is what makes
this practical, where an aspiration changes nothing.

### The reviewer did not do the work

The self-preference finding is measured, and capability fixes none of it.
Seventeen of twenty models show statistically significant bias when evaluating
their own output, the effect is strongest on open-ended tasks, and code review
is exactly that kind of task.

So the reviewer is a separate agent that did not write the change, and where
that cannot be arranged the result is reported as self-assessed, and never as a
review.

### The adversarial pass is what makes a model's findings usable

Each finding is attacked before it is reported: the characteristic model
failure is a confident finding that does not survive five minutes of checking.

A finding that survives is reported with its evidence. One that does not is
dropped silently - reporting it as _considered and rejected_ fills the report
with noise about the reviewer and nothing about the change.

### The fix loop is bounded

Five rounds, with the later rounds escalated and residual findings adjudicated,
and never retried. An unbounded loop between a reviewer and an implementer that
are both models converges on agreement, and never on correctness.

### What the language pack supplies

The idioms a reviewer of that language needs come from the pack, and never from
this skill, which names no language. The ownership question in Rust, the error
boundary in Go, decorative typing in Python, the strictness flags in
TypeScript.

That division is what keeps this skill loadable in every repository.

## What it must refuse

To manufacture findings, and to withhold a clean verdict.

To review the working tree.

To report a preference as a finding. The published convention is to mark it:
_"prefix it with something like 'Nit: ' to let the author know that it's just a
point of polish that they could choose to ignore"_. An unmarked preference is
the most common way a review loses its reader.

To review its own work without saying so.

To hold a change for lacking polish, because the standard is improvement rather
than perfection.

## Conclusions

1. A change is approved once it definitely improves the codebase, even where it
   is not perfect, because there is only better code. 2. A clean change is
   stated plainly as clean, which is the counterweight to a reviewer that will
   otherwise always find something. 3. Conformance and quality are two
   verdicts, in that order, since a quality finding about code that should not
   exist is wasted. 4. The subject is the diff against a recorded base, never
   the working tree, and the base is read back when it has moved. 5. The
   reviewer is given the parts touched and the dependencies added, because a
   structural regression is invisible in a diff by construction. 6. The
   reviewer did not write the change, and where that cannot be arranged the
   result is reported as self-assessed. 7. Every finding is attacked before it
   is reported, and one that does not survive is dropped without narration. 8.
   A preference is marked as a preference, or the review loses its reader. 9.
   The fix loop is bounded and residual findings are adjudicated, because an
   unbounded loop between two models converges on agreement and never on
   correctness. 10. Language idioms come from the language pack, so this skill
   names no language and loads everywhere.

## Sources

All read 2026-09-20.

- [The standard of code review](https://google.github.io/eng-practices/review/reviewer/standard.html)
  - approving once a change definitely improves overall code health even where
    it is not perfect; that there is no perfect code, only better code; and
    prefixing a point of polish so the author knows it may be ignored.
- [RES-0030-review.md](RES-0030-review.md) - the severity model, the order of
  checks, the two-verdict split from `superpowers`, the diff against a recorded
  base, the bounded fix loop, and the adversarial pass from `harness4claude`.
- [RES-0070-who-verifies.md](RES-0070-who-verifies.md) - the measured
  self-preference bias, that capability does not correct it, and that
  open-ended tasks trigger it most.
- [RES-0072-architecture-discipline.md](RES-0072-architecture-discipline.md) -
  that a structural regression is invisible in a diff and that the parts
  touched and dependencies added are computable.
- `~/workspace/meowctl/.claude/skills/` - the instruction to say plainly when
  the pull request is clean and not to manufacture findings.
