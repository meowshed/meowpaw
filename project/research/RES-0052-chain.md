---
id: RES-0052
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001, RES-0029
---

# `/meow:research`

## Summary

The first step of the chain takes a question and produces one document with
sources and conclusions. Two placements in the surveyed sequence carry weight,
and neither is a matter of style. Assumptions are challenged before
alternatives are explored, because an assumption every option shares turns
invisible once the options exist. The argument against the leading option lives
inside the command, because a separate adversarial step is one nobody runs.

The first step of the chain. It takes a question and produces one research
document with sources and conclusions, and stops for approval.

Its siblings have their own documents:
[RES-0151-requirements-command.md](RES-0151-requirements-command.md) and
[RES-0152-design-command.md](RES-0152-design-command.md). What all three share
is stated at the end of this one, because it was discovered here first.

## Who has an equivalent

| Harness        | Command           | What it does                                      |
| -------------- | ----------------- | ------------------------------------------------- |
| spec-kit       | `assess-research` | Assesses whether research is needed               |
| harness4claude | `graph-context`   | Gathers context from a knowledge graph            |
| vlie           | `/research`       | A Socratic sequence ending in a recorded document |
| cc-sdd         | -                 | None                                              |
| meowctl        | -                 | None                                              |

Naming across the survey is inconsistent enough that we mapped these by
function, and the names tell you nothing. spec-kit's `plan` is a _design_
command while its `tasks` is what everyone else calls planning, so a harness
borrowing its vocabulary borrows that confusion.

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

## The sequence, and why its order is the design

vlie's is the most developed, and it is Socratic: frame the question and the
non-goals; **challenge assumptions before exploring solutions**; gather
evidence from the repository, prior art and the web; compare at least three
alternatives; evaluate complexity, performance, maintainability and risk;
argue against the leading option; record; update the index.

Two placements in that list carry weight, and neither is a matter of style.

Challenge before explore is second on purpose. Once alternatives are on the
table, the assumption underneath them becomes invisible - every option shares
it, so nothing in the comparison surfaces it. Asked first, the assumption is
still a separate object.

Arguing against the leading option happens inside the command, because a
separate adversarial step is one nobody runs. A step nobody runs produces no
findings, and this is the step most likely to be skipped because it arrives
when the work feels done.

## What this command adds over the survey

The output is a document with sources, so a downstream claim points at where it
was recorded and never at a conversation.

The output ends in conclusions. A research document that stops at findings
leaves the requirements step to infer what follows, and two readers infer
differently. The conclusions are what requirements are built from, and they are
written without reference to any requirement, so the direction of the chain
stays one-way.

A fact carries the date it was read. Every source in this corpus has one,
because a toolchain's defaults change under the same command name and a reader
in a year needs to know what to re-check, and telling them to trust it helps
nobody.

## What it must refuse

A research document with no sources is an opinion with a filename. The command
refuses to record one.

A conclusion that no finding supports is the failure this step exists to
prevent, and it is the easiest one to commit, because the conclusions are
written last when the argument feels settled.

A figure taken from a secondary source is recorded as reported and unverified,
and never repeated as fact. This corpus already contains two cases where doing
that was the correct call and one where a widely circulated statistic turned
out not to be in the article it was attributed to.

## What all three upstream steps share

A refusal. Each refuses to run when its input is missing or unapproved, and
says what is missing. That refusal _is_ the chain; nothing else enforces the
order.

A stop. Produce the artifact, report, end the turn.

A citation rule. Research cites sources, requirements cite research, design
cites requirements. A claim with no upstream citation is the thing the chain
exists to prevent.

## Conclusions

1. Assumptions are challenged before alternatives are explored, because an
   assumption every option shares is invisible once the options exist. 2. At
   least three alternatives are compared, so the recommendation is a choice and
   not the first thing anyone found. 3. The leading option is argued against
   inside the command, because a separate adversarial step is one nobody runs. 4. Every research document ends in conclusions, written without reference to
   any requirement, because they are what the next step is built from. 5. Every
   research document carries sources with read dates, and one without sources
   is refused. 6. A figure from a secondary source is recorded as reported and
   unverified, and never repeated as fact. 7. The command refuses on a missing
   or unapproved input and stops after producing.

## Sources

All read 2026-09-20.

- `~/workspace/vlie/.claude/commands/research.md` - the Socratic sequence,
  challenge-before-explore, at least three alternatives, the devil's-advocate
  step, and recording with an index update.
- [github/spec-kit](https://github.com/github/spec-kit) - `assess-research` as
  a gate on whether research is needed, and the vocabulary confusion where
  `plan` is a design step and `tasks` is planning.
- [Lharden/harness4claude](https://github.com/Lharden/harness4claude) -
  `graph-context` as context gathering in place of research.
- [RES-0029-research-technique.md](RES-0029-research-technique.md) - the
  adversarial pass and what makes a comparison honest.
