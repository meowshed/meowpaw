---
id: TSK-1270
artifact: task
status: approved
revised: 2026-09-23
epic: EPC-1030
closes: [REQ-1144, REQ-1146, REQ-1148, REQ-1150]
issue: 84
---

# Describe the writing skill by its obligation

One task, one branch, one pull request, one review.

## What to do

Replace the description in `plugins/meow-prose/skills/writing/SKILL.md` with
the one ADR-1050 states (REQ-1144, REQ-1146, REQ-1148), and bump the version
of `meow-prose` so an installed copy picks it up. Ship no hook.

Measure routing with the published plugin on Sonnet 5 and Opus 5.5, on the
writing requests and near misses RES-0272 lists, three runs each (REQ-1150).

## Depends on

Nothing. The skill exists, and the measurement runs by the method RES-0272
records.

## Evidence

The description, run by the method RES-0272 records on the 24 requests, three
runs each, in a fresh `claude -p` session with only this copy of `meow-prose`
installed:

| Model    | Writing | Near misses that change code | Chat answers | README typo |
| -------- | ------- | ---------------------------- | ------------ | ----------- |
| Sonnet 5 | 36/36   | 0/30                         | 0/9          | 0/3         |
| Opus 5.5 | 33/33   | 0/30                         | 5/9          | 3/3         |

Both models load the skill in every writing run, and neither loads it on work
that changes code, which meets ADR-1050's criteria 1 and 2. `meow-prose` ships
no hook. REQ-1144, REQ-1146, REQ-1148 and REQ-1150 are closed.

## Left alone

The skill's body, which TSK-1180 measures, and the other units' descriptions,
which TSK-1240 rewrites.
