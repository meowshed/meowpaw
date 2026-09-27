---
id: TSK-2330
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1500
closes: [REQ-0140, REQ-0142]
issue:
---

# `meow-verbs` runs a verb over part of the work through its declared form

A verb's profile value may be a table with `command` and `subset`;
`run <verb>... -- <targets>` runs the subset form, reports a verb with none as
`no subset form`, and records the targets, which `evidence` keeps out of the
whole verb's result. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the fixtures ADR-1520's first criterion lists, when `run`, `status`
   and `evidence` run, then each behaves as that criterion says. Closed by:
   fixtures naming REQ-0140 and REQ-0142, seen failing first.
2. Given a later subset record, when `evidence test` runs, then it reports the
   whole run's record and prints the subset one as `subset only`. Closed by: a
   fixture naming REQ-0142.
3. Given the `verify` skill, when it is read, then it runs a part through
   `run <verb> -- <targets>`, reports `no subset form`, asks the person before
   a whole run, and never runs a tool around the program; `meow-author check`
   passes. Closed by: the trace and its output.

## What to do

Change the native tool's `verbs` feature and `plugins/meow-verbs/skills/verify/SKILL.md`,
state the form on `meow-verbs`' page, and move the unit to its next minor
version.

## Depends on

Nothing. ADR-1520 is approved.

## Evidence

Not yet.

## Left alone

A language pack's subset form.
