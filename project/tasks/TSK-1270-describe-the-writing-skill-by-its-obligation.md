---
id: TSK-1270
artifact: task
status: approved
revised: 2026-09-23
epic: EPC-1030
closes: [REQ-1144, REQ-1146, REQ-1148, REQ-1150]
issue:
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

Not yet. The task closes on the routing table for both models: loads on the
writing requests, loads on the near misses, and loads on the answers in chat.

## Left alone

The skill's body, which TSK-1180 measures, and the other units' descriptions,
which TSK-1240 rewrites.
