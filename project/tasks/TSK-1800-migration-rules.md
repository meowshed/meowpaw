---
id: TSK-1800
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1240
closes: [REQ-3008, REQ-3009, REQ-3012, REQ-3014, REQ-3016, REQ-3018, REQ-3019]
issue:
---

# The method says how a change to the record's shape migrates it

The method says how a change to the record's shape migrates it, as ADR-1240 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given the skill, when the trace is read, then each requirement this task closes maps to a labelled rule that exists in it. Closed by: the trace table and a script finding each label.

## What to do

Add rules to the `method` skill: expand, migrate and contract, naming the release that removes the old form; a new obligation migrated or grandfathered as a draft rule; structured data edited as structured data and links as links; smaller where no parser exists; split into separately reviewed parts, the mechanical apart from the editorial; and `count` run before and after. Record the trace under Evidence.

## Depends on

Nothing. ADR-1240 is approved.

## Evidence

Not yet.

## Left alone

A command that runs a migration, which ADR-1240 leaves.
