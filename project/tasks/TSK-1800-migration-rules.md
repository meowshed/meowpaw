---
id: TSK-1800
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1240
closes: [REQ-3008, REQ-3009, REQ-3012, REQ-3014, REQ-3016, REQ-3018, REQ-3019]
issue: 311
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

Each requirement this task closes is carried by a labelled rule in the
`method` skill, and no rule names a requirement:

| Requirement | Carried by        |
| ----------- | ----------------- |
| REQ-3008    | M14 in `SKILL.md` |
| REQ-3009    | M14 in `SKILL.md` |
| REQ-3012    | M15 in `SKILL.md` |
| REQ-3014    | M16 in `SKILL.md` |
| REQ-3016    | M16 in `SKILL.md` |
| REQ-3018    | M17 in `SKILL.md` |
| REQ-3019    | M17 in `SKILL.md` |

M18 names `meow-method count`, which TSK-1790 added, for the count REQ-3020
asks of a migration's evidence. The draft rules that ADR-1140 introduced are
the grandfathering M15 names. A script found all 7 traced labels in
`SKILL.md`. Whether the model follows the rules is measured by evaluation,
which is postponed.

## Left alone

A command that runs a migration, which ADR-1240 leaves.
