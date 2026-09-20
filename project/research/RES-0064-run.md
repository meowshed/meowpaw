---
id: RES-0064
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:run`

## Summary

One command drives the whole chain from a research question to a reviewed
change, stopping at every gate exactly as the individual step would. It
classifies first and reports the class, advances step by step writing each
artifact, reports where it stopped and what the next invocation will do,
resumes from state, because it remembers nothing of its own run, and is
idempotent when run again without an approval.

Drives the whole chain - research to review - stopping at every gate and
resuming after each approval.

## Method

We fetched and read the surveyed harnesses' own command templates on
2026-09-20, because the mechanisms live in the templates and the readmes only
describe them, alongside the internal repositories' commands read from their
working trees.

The platform's documentation on commands was fetched for the frontmatter
fields the surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against what comparable
commands do.

## The problem it solves

Nine steps is nine invocations, and eight of the nine are "do the obvious next
thing". A method that costs nine deliberate acts to move one unit of work
through it is a method people shortcut, and the shortcut people take is
skipping steps, which is not the typing.

## Who has an equivalent

| Harness               | Command                      | Shape                                           |
| --------------------- | ---------------------------- | ----------------------------------------------- |
| Specbound/sdd-harness | `/kiro:spec-quick "Feature"` | "All phases in one shot"                        |
| gotalab/cc-sdd        | `/kiro-impl`                 | Autonomous across tasks, within one phase       |
| github/spec-kit       | `/speckit-converge`          | Implement and converge repeat until convergence |
| obra/superpowers      | The subagent chain           | Drives tasks, not phases                        |

Only Specbound drives the _phases_, and its name is the tell: "quick" positions
it as the fast path, and something else as the normal one. Every other harness
leaves the phase transitions to the person.

## The design question, and it is the whole document

A command that runs the chain must not abolish the gates. If it does, it is
not an accelerator - it is a second method with the approvals removed, and it
will be the one everybody uses.

So the rule is exact: _driving the chain changes how many times a
person types a command; it must not change how many times a person decides._

In practice the command advances until it reaches a stop, and then stops:

```text
/meow:run "the thing"
  → discover: L2, and here is why
  → research      → RES-0007 written
  → requirements  → 6 written, in one block of identifiers
  ⏸ approval required on 6 requirements
     next: /meow:run continues at design
```

The person reads, approves or corrects, and runs it again. Three gates on the
full path - requirements, design, epic - mean three stops, so three decisions
and three commands cover what would otherwise take nine.

## Resumability is the hard part

A second invocation continues and never restarts, which is possible only
because state already exists: the pending gate is recorded with the artifact
and its content hash, and the artifacts on disk say how far the work has got.

So the command does not track its own progress. It reads the same state
everything else reads, decides which step is next, and runs it. That matters
because a progress counter of its own would be a second source of truth about
where the work stands, and the first thing to disagree with the directory
listing.

Three cases it must handle:

- **Approved and unchanged** - continue at the next step. - **Approved but the
  artifact changed since** - the approval is invalidated; stop and say so. -
  **Not approved** - stop where it is, again, with the same message. Running it
  twice without approving is idempotent, and it never loops.

## Where it ends

At review's verdict. A verdict of "finished" ends the run; anything else names
the step to return to, and the next invocation resumes _there_ - which is what
makes the cycle a cycle.

The implementation step is where this command meets `meow-loop`: `/meow:run`
drives phases, `/meow:loop` drives tasks within the implementation phase, and
neither crosses a gate ([RES-0024-loop.md](RES-0024-loop.md)).

## What it must not become

A no-questions mode. The temptation is a flag that suppresses the stops for
"trivial" work. That is what routing is for ([RES-0053-discover.md](RES-0053-discover.md)): L0
skips the chain entirely and L1 runs a shorter one. A flag that skips gates on
the full path is the second method described above.

A progress tracker. It reads state; it does not own any.

Silent about its route. It reports the classification before it starts, because a command that begins by deciding how much method to apply
must say what it decided.

## Conclusions

1. Classify first, and report the class and the reason. 2. Advance step by
   step, writing each artifact. 3. Stop at every gate, exactly as the
   individual step would. 4. Report the step reached, why it stopped, and what
   the next invocation does. 5. Resume from state, remembering nothing of the
   run itself. 6. Be idempotent when run again without an approval. 7. End at
   the review verdict, and resume at the step the verdict names.

## Sources

All read 2026-09-20.

- [Specbound/sdd-harness](https://github.com/Specbound/sdd-harness) -
  `/kiro:spec-quick` running all phases in one shot, and the phase gates it
  otherwise enforces. - [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) -
  `/kiro-impl` as autonomous execution bounded to one phase, with approval
  between phases. - [github/spec-kit](https://github.com/github/spec-kit) -
  `/speckit-converge` as a repeat-until-done loop inside implementation. -
  [obra/superpowers](https://github.com/obra/superpowers) - the subagent chain,
  which drives tasks and never phases.
