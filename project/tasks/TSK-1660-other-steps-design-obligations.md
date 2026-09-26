---
id: TSK-1660
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1190
closes:
  [
    REQ-2131,
    REQ-2132,
    REQ-2133,
    REQ-2134,
    REQ-2137,
    REQ-2139,
    REQ-2256,
    REQ-2258,
    REQ-2260,
    REQ-2262,
    REQ-2264,
    REQ-2266,
    REQ-2268,
  ]
issue:
---

# The other steps carry their share of the design obligations

The other steps carry their share of the design obligations, as ADR-1190 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given the six step files, when the trace is read, then each requirement this task closes maps to a labelled rule that exists in the file named. Closed by: the trace table and a script finding each label.

## What to do

Append the rules ADR-1190 places on the research, requirements, spec, verify, implement and review steps to each file's rules block, labelled after the existing ones. Record the trace under Evidence.

## Depends on

Nothing. ADR-1190 is approved.

## Evidence

Not yet.

## Left alone

Measuring whether the model follows the rules, which waits for evaluation.
