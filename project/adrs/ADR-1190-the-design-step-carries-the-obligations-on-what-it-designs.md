---
id: ADR-1190
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-1230,
    REQ-1231,
    REQ-1232,
    REQ-1233,
    REQ-1234,
    REQ-1235,
    REQ-1236,
    REQ-1237,
    REQ-1238,
    REQ-1239,
    REQ-1240,
    REQ-1242,
    REQ-1244,
    REQ-1246,
    REQ-1248,
    REQ-1250,
    REQ-1252,
    REQ-1254,
    REQ-1256,
    REQ-1258,
    REQ-2130,
    REQ-2131,
    REQ-2132,
    REQ-2133,
    REQ-2134,
    REQ-2137,
    REQ-2138,
    REQ-2139,
    REQ-2140,
    REQ-2256,
    REQ-2258,
    REQ-2260,
    REQ-2262,
    REQ-2264,
    REQ-2266,
    REQ-2268,
    REQ-2760,
    REQ-2762,
    REQ-2764,
    REQ-2766,
    REQ-2768,
    REQ-2770,
    REQ-2772,
    REQ-2776,
    REQ-2778,
    REQ-2780,
    REQ-2782,
    REQ-2794,
    REQ-2796,
  ]
supersedes: []
---

# 1190. The design step carries the obligations on what it designs, and the other steps their share

## Decision

The obligations the requirements place on what a design has to say go into
the design step's file, as labelled rules after the ones ADR-1160 placed:
the ergonomic cost, increments that each leave a working whole, accumulations
with a ceiling and a drain, interruption budgets and notifications that fire
once, failure states with a next step and one audience, baselines and budgets
with their reasons and slack, security boundaries, surfaces that answer a
question, the person the work bottlenecks on, and recommendations with their
reversal condition. The obligations that fall on other steps join theirs:
comparisons in research, elicitation in requirements, abstraction levels and
permitted dependencies in the specification, architectural properties in
verification, the parts a task touches in implementation and review.

Practice commands stay optional: no step names one, which REQ-2130 asks and
this decision records.

As ADR-1160 decided, the rules name no requirement and the tasks carry the
trace. After this decision a design written through the method is asked the
questions these requirements ask. What still doesn't work: whether the model
answers them is behaviour, measured by evaluation, which is postponed; the
architecture description the repository's declared parts would organise, and
recorded insights, wait for decisions of their own.

## Why

The requirements drawn from RES-0017, RES-0152 and RES-0215 on design, and
from RES-0071 and RES-0252 on the specification, are judgements a model makes
while it designs, which no program settles; ADR-1160 established that such an
obligation lives in the file the model reads for its step. `CLAUDE.md`'s
principle of growing the system in working increments is REQ-1231 to REQ-1239
applied to this repository, and the design step now asks it of every
repository.

The strongest objection: the design step's file grows long. It does, and it is
read only when a design is written; evaluation, when it runs, removes a rule
that doesn't change the result.

## Alternatives

| Option                                                | Better at                   | Why it lost                                                           |
| ----------------------------------------------------- | --------------------------- | --------------------------------------------------------------------- |
| Each obligation in the file of the step that meets it | Read where the work happens | Chosen                                                                |
| A design checklist skill of its own                   | Loaded on demand by name    | A second skill for one step, and a description on every turn          |
| The obligations as sections of the decision template  | Visible in every decision   | Most apply only to some designs, and an empty section invites padding |
| Do nothing                                            | Costs nothing               | A design written through the method is asked none of these questions  |

## What it costs

A longer design step, six other step files a rule or two longer, and two tasks
of writing. Behaviour isn't measured.

## What would reverse it

- Evaluation shows a rule doesn't change what the model writes, and it is
  removed.
- The design step grows past what a model follows in one read, and it splits.

## Consequences

- The seven step files gain their rules, and SPC-1090 lists the requirements
  each holds.

## How I will know it was realised

1. Every requirement ADR-1190 addresses maps, in the task that closes it, to a
   labelled rule in the step file named, or, for REQ-2130, to a search showing
   no step names a practice command.
2. The prompt check and `meow-method check` pass.
3. Evaluation measures that a design follows the rules.
4. Every requirement ADR-1190 addresses lands in exactly one closed task.

## What this does not settle

- The architecture description by declared parts.
- Recording insights.
- Measuring the rules.
