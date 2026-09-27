---
id: TSK-2230
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1440
closes:
  [
    REQ-1052,
    REQ-1054,
    REQ-1068,
    REQ-1070,
    REQ-1076,
    REQ-1078,
    REQ-2696,
    REQ-2698,
    REQ-2700,
    REQ-2702,
    REQ-2704,
  ]
issue: 494
projected: fc8ab449b446
---

# `meow-author:write` carries the rules on when material loads

The `write` skill gains a group of labelled rules carrying each requirement
this task closes. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the skill, when it is read, then a labelled rule carries each
   requirement this task closes, and no rule names a requirement, a language
   or a tool. Closed by: a table in the evidence.
2. Given the unit, when `meow-author check` runs, then it passes. Closed by:
   its output.

## What to do

Add a rules group on loading to `meow-author:write`, each rule with its
reason, and a step pointing at `meow-author cost` where the material adds to
what loads on every turn, and at `/skill-doctor` before a unit is cut or kept.

## Depends on

Nothing. It changes only the skill.

## Evidence

`meow-author:write` gains a step pointing at `meow-author cost` and
`/skill-doctor`, and a rules group, "when material loads", of eleven labelled
rules, each with its reason and none naming a requirement, a language or a
tool:

| Requirement | Carried by |
| ----------- | ---------- |
| REQ-1052    | C1         |
| REQ-1054    | C2         |
| REQ-1068    | C3         |
| REQ-1070    | C4         |
| REQ-1076    | C5         |
| REQ-1078    | C6         |
| REQ-2696    | C7         |
| REQ-2698    | C8         |
| REQ-2700    | C9         |
| REQ-2702    | C10        |
| REQ-2704    | C11        |

The skill's description is unchanged, so its measured routing stands.

```text
$ plugins/meow-author/bin/meow-author check plugins/meow-author
1 files, 0 authoring failures
$ plugins/meow-verbs/bin/meow-verbs run format lint test
summary: format passed, lint passed, test passed
```

## Left alone

The cost report, which TSK-2220 adds.
