---
id: TSK-1240
artifact: task
status: approved
revised: 2026-09-23
epic: EPC-1020
closes: [REQ-1134]
issue: 67
---

# Load the writing skill with a hook, and describe every unit in the third person

**Amended by ADR-1050.** No hook, and REQ-1140 is withdrawn. The writing
skill's description and its routing measurement move to TSK-1270. This task
rewrites every other shipped unit's description in the third person
(REQ-1134), and its evidence is those descriptions.

One task, one branch, one pull request, one review.

## What to do

Add `plugins/meow-prose/hooks/hooks.json` with a `SessionStart` command hook,
and the program it runs, which prints one line of `additionalContext` naming
the writing skill and the work it governs (REQ-1140). The line stays under 300
characters, the program reads nothing and writes nothing, and it runs on every
platform the harness supports.

Rewrite every shipped unit's description in the third person, stating what the
unit does and when to use it, with the words a request contains first
(REQ-1134, REQ-3050).

Measure how often the writing skill is in context before a text is written,
on the routing requests TSK-1180 defines, on both models, with the hook and
without it.

## Depends on

TSK-1110, because the hook names a skill that has to exist, and TSK-1230,
because the measurement runs on both models through the loop that task
extends.

## Evidence

Not yet. The task closes on the routing table for both models with and without
the hook, the hook's line and its character count, and every description
rewritten.

## Left alone

The skill's body, which TSK-1110 writes and TSK-1180 measures.
