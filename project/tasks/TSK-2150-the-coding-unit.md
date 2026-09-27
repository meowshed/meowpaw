---
id: TSK-2150
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1400
closes:
  [
    REQ-0090,
    REQ-0092,
    REQ-0094,
    REQ-0096,
    REQ-0098,
    REQ-1010,
    REQ-1015,
    REQ-2010,
    REQ-2012,
    REQ-2014,
    REQ-2016,
    REQ-2018,
    REQ-2070,
    REQ-2072,
    REQ-2074,
    REQ-2076,
    REQ-2078,
  ]
issue:
---

# `meow-code` ships the skill that holds how code is changed and checked

A new unit, `meow-code`, ships `meow-code:change`, whose rules carry each
obligation ADR-1420 lists, loaded before Claude Code changes code. One task,
one branch, one pull request, one review.

## Acceptance criteria

1. Given the skill, when it is read, then a labelled rule carries each
   requirement this task closes, and no rule names a requirement, a language,
   a tool or a file extension. Closed by: a table in the evidence tracing each
   requirement to its rule, and a search of the file.
2. Given the unit, when `mise run prompts` and `mise run budget` run, then
   both pass. Closed by: their output.
3. Given a scratch repository and a session on Sonnet 5 with only the unit
   installed, when Claude Code is asked to change a function, then it loads
   the skill before its first edit. Closed by: the session's transcript.

## What to do

Create `plugins/meow-code/` with a manifest, a page, a budget and a
`requires.toml`, and the skill with a description stating the obligation, as
ADR-1050 decides. Write the two groups of rules ADR-1420 lists, each with its
reason in the same sentence. Add the unit to the catalogue.

## Depends on

Nothing. ADR-1420 is approved.

## Evidence

Not yet.

## Left alone

Evaluation cases for the unit, which a later measurement adds.
