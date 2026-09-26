---
id: TSK-1580
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1160
closes:
  [
    REQ-0303,
    REQ-0534,
    REQ-0535,
    REQ-0536,
    REQ-0537,
    REQ-2900,
    REQ-2902,
    REQ-2910,
    REQ-2916,
    REQ-2917,
    REQ-2918,
    REQ-2919,
    REQ-2920,
    REQ-2922,
    REQ-2926,
  ]
issue:
---

# The task and defect templates carry their obligations

One task, one branch, one pull request, one review.

## What to do

Give the `task` template an `## Acceptance criteria` section whose criteria are each a starting state, an action and an observable outcome with the evidence that will close it, and add it to the task kind's `draft_sections` in `lib/layout.toml`. Give the `bug` template the environment and versions, the revision observed at, sanitised evidence, the violated requirement or a statement that none exists, the reason for the severity, and a fix that is a task of its own. Give every template an opening that lets a reader stop, sections that permit an empty answer that is earned, and the relation naming what it elaborates. Map each requirement to the template line that carries it under Evidence.

## Depends on

Nothing. ADR-1160 and SPC-1090 are approved.

## Evidence

Not yet.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
