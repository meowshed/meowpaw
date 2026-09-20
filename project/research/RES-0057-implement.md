---
id: RES-0057
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:implement`

## Summary

One task is built against its requirements, on a branch, ending in a pull
request and never a merge. The task and every requirement it cites are read
verbatim rather than summarised, work that nothing covers is refused, and the
task is marked in the commit that completes it with its evidence. A sequential
failure halts and a parallel one is reported, and the gate's actual output is
what gets reported rather than a claim about it.

Builds one task against its requirements, on a branch, ending in a pull request
and never a merge.

## Who has an equivalent

Everyone. This is the most-implemented command in the survey and the one with
the widest variation.

| Harness     | Shape                                                                                                                             |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------- |
| spec-kit    | Phase-ordered execution of `tasks.md` with a checklist gate before starting; marks each task `[X]`; halts on non-parallel failure |
| cc-sdd      | Autonomous per-task TDD (red -> green), per-task independent review, auto-debug in clean context after two rejections             |
| superpowers | A fresh implementer subagent per task with a written brief; task review after each; a fix loop capped at five rounds              |
| vlie        | `/work` selects its own issue, branches, implements, self-reviews, opens a PR, makes checks green, waits                          |
| meowctl     | Reads the issue and every cited requirement, refuses if uncovered, builds to the requirements and nothing more                    |

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

## The refusal that matters

meowctl's second step: "Refuse to start if the spec does not cover the work. If
the issue asks for behaviour that no requirement describes, stop and say so.
Implementing uncovered behaviour is the failure the whole method exists to
prevent."

This is the rule most likely to be quietly skipped, because the work looks
obvious and the requirement looks like a formality. It is also where the method
either holds or stops being real.

## Scope discipline

"Build to the requirements and nothing more. Behaviour the spec does not ask for
does not go in, however obvious it seems; open an issue instead."

The model's default is to improve things it passes. That default has to be
countered explicitly, because the improvement is usually correct in isolation
and unreviewable in context.

## Marking progress

spec-kit marks `[X]` in `tasks.md` as each task completes. Ours goes further: the mark lands **in the commit that completes the task**
and carries the evidence and the requirement identifiers.

The difference matters on a squashed branch - the intermediate marks exist
during the work and collapse with everything else, so "was this ever ticked
prematurely" is a branch-review question ([RES-0014-commits.md](RES-0014-commits.md)).

## Failure handling

spec-kit halts on a non-parallel task failure and reports parallel failures
without blocking the others. That is the right split: a sequential dependency
failing invalidates what follows, a parallel one does not.

cc-sdd's auto-debug **in a clean context** after two rejections is the better
answer to the other failure - an implementer and a reviewer arguing in one
context converge on nothing.

## What it must never do

- **Merge.** Every harness that says anything says this.
- **Proceed past a contradiction.** When implementation contradicts an approved
  requirement, stop and amend.
- **Claim a gate it did not run**, or cite evidence from before its last edit.

## Conclusions

1. Read the task and every requirement it cites, verbatim.
2. Refuse if the work is uncovered.
3. Build to the requirements and nothing more.
4. Mark the task in the commit that completes it, with evidence.
5. Halt on a sequential failure; report a parallel one.
6. Run the gate and report what it actually said.
7. Stop at a pull request.

## Sources

All read 2026-09-20.

- [github/spec-kit `implement.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/implement.md)
  - the checklist gate, phase ordering, `[X]` marking, and halting on a
    non-parallel failure while reporting parallel ones.
- [obra/superpowers `subagent-driven-development`](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md)
  - a fresh implementer per task with a written brief.
- [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) - per-task TDD, per-task
  review, and auto-debug in a clean context after two rejections.
- `~/workspace/vlie/.claude/commands/work.md` - issue selection, branch, self-
  review, pull request, and waiting for approval to merge.
- `~/workspace/meowctl/.claude/commands/implement.md` - reading every cited
  requirement verbatim, refusing uncovered work, building to the requirements
  and nothing more, and stopping on a contradiction.
