---
id: TSK-4720
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2440
closes: [REQ-2742]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Forbid a shipped rule that leans on being read last

`meow-author:write` tells an author that no rule a unit ships depends on being
read last, with the reason, and every shipped prompt meets it, as SPC-1030
states under "What a rule says". One task, one branch, one pull request, one
review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given `plugins/meow-author/skills/write/SKILL.md`, when a fixture reads
   it, then it carries a rule that no shipped rule depends on being read last,
   with the reason that several instruction files load in an order the unit
   doesn't control (REQ-2742). Closed by: a fixture under
   `plugins/meow-author/tests/` naming REQ-2742, seen failing first.
2. Given every prompt under `plugins/`, when a reviewer searches them for a
   rule that claims to override what was read before it, such as "this
   overrides any earlier instruction", then each hit is rewritten to hold
   wherever it loads. Closed by: judgement in the pull request's review,
   because no pattern tells a rule that leans on its place from one that
   doesn't.

## What to do

Add the rule to the skill, held to SPC-1030 and the unit's `budget.toml`, and
list each prompt the search found in the pull request with what changed.

## Depends on

Nothing.

## Evidence

Not yet.

Criterion 2 rests on judgement, for the reason it gives.

## Left alone

`CLAUDE.md`, which is the repository's own and not a shipped rule, and which
TSK-4730 cuts.
