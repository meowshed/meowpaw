---
id: RES-0155
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0059, RES-0024
---

# `/meow:cancel`

## Summary

Only one surveyed harness can stop an autonomous run, and everything else
relies on interrupting the session - which is not the same thing, because it
stops at an arbitrary point. The command's value is the state it leaves rather
than the stopping, which makes cancellation a design constraint on the loop: an
iteration that does not end in a recorded, consistent state makes stopping
expensive.

Stops an autonomous run. Its sibling is
[RES-0059-loop.md](RES-0059-loop.md), which starts one.

## Who has an equivalent

The official `ralph-wiggum` plugin ships `/cancel-ralph` beside `/ralph-loop`,
which is the only precedent in the survey. Every other harness that runs a loop
relies on the user interrupting the session.

That is the finding. An interrupt is not a cancel: it stops the process at an
arbitrary point, and what the run had done up to then is whatever it happened
to have written.

## Method

The surveyed harnesses' own command templates and the internal repositories'
commands were read on 2026-09-20 for what a comparable command does, and the
platform's command documentation was fetched for the frontmatter fields the
surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against comparable
commands, and none of it is an observation.

## The obligation is what it leaves behind

Stopping is the easy half. What the command buys is the state afterwards:

- **A tree that is inspectable.** No half-applied edit, no file the run was
  part-way through rewriting. - **A plan whose marks reflect what actually
  landed**, where the run's own plan says what it intended to do next. - **A
  run log saying what each iteration changed**, so the question _how far did it
  get_ has an answer somebody can read.

A run that cannot be stopped cleanly is a run nobody will start. That is the
whole argument for the command, and it explains why cancellation constrains the
design of the loop, where a feature bolted on afterwards would not: the loop
has to reach a consistent point often enough that stopping is cheap.

## Which means the loop's iteration boundary is the cancellation point

If an iteration is _make many changes and then record them_, a cancel in the
middle leaves the tree ahead of the record. If an iteration is _make one
bounded change and record it_, cancellation is free at every boundary.

So the cancel command's requirement propagates backwards into the loop's
design: an iteration ends in a recorded, consistent state, and the frequency of
those boundaries is what determines how much work a cancel can lose.

## What it must refuse

To revert work. Cancelling stops the run and leaves what it did; a cancel that rolls back
destroys the evidence of what the run did and makes a failed run
uninvestigable.

To leave the stop condition ambiguous. The log says the run was cancelled, by
whom and when, distinctly from a run that finished or one that exhausted its
budget - three different outcomes that a later reader must be able to tell
apart.

To be model-invocable. A run that can cancel itself can cancel itself for the
wrong reason, and the user's ability to stop it is the thing being protected.

## Conclusions

1. The command's value is the state it leaves, and never the stopping: an
   inspectable tree, a plan whose marks match what landed, and a log of what
   each iteration changed. 2. A run that cannot be stopped cleanly is a run
   nobody will start, which makes cancellation a constraint on the loop's
   design, and no feature. 3. An iteration ends in a recorded, consistent
   state, because that boundary is where cancellation is free. 4. Cancelling
   does not revert, since rolling back destroys the evidence of what the run
   did. 5. Cancelled, finished and out-of-budget are three distinct outcomes
   and the log says which, with who cancelled and when. 6. The command is
   user-invocable only, because the ability to stop the run is what it
   protects.

## Sources

All read 2026-09-20.

- [anthropics/claude-code `plugins/ralph-wiggum`](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md)
  - `/cancel-ralph` beside `/ralph-loop`, the only cancellation command in the
    survey.
- [RES-0024-loop.md](RES-0024-loop.md) - long autonomous runs, the budget and
  the stop condition.
- [Slash commands](https://code.claude.com/docs/en/slash-commands) -
  `disable-model-invocation` as the control that makes a command user-only.
