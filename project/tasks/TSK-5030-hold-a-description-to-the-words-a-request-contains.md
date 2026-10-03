---
id: TSK-5030
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2550
closes: [REQ-3050]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold a unit's description to the words a request contains

`meow-author check` fails a description whose first sentence carries none of
the verbs its unit's `when_to_use` names, as SPC-1030 states under "The
check". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture skill whose `when_to_use` names `commit` and whose description's first sentence carries no verb from it, when `meow-author check` runs, then it fails naming the file and the field (REQ-3050). Closed by: a test under `plugins/meow-author/tests/` naming REQ-3050, seen failing first.
2. Given every unit under `plugins/`, when `meow-author check` runs, then it passes. Closed by: the `lint` verb's `prompts` task.

## What to do

Add the rule to the `author` feature of `crates/meow/`, beside the
description rule ADR-1050 decided. Where a shipped description fails it,
rewrite the description in the same change, measured as SPC-1030 states
under "Descriptions and loading", because a description change is measured
before it ships.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

A skill with no `when_to_use`, which the rule doesn't read, so it passes as
it does today.
