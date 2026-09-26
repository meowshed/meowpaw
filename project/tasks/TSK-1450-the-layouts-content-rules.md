---
id: TSK-1450
artifact: task
status: draft
revised: 2026-09-26
epic: EPC-1110
closes:
  [
    REQ-0216,
    REQ-0219,
    REQ-0234,
    REQ-0247,
    REQ-0266,
    REQ-0309,
    REQ-0512,
    REQ-0514,
    REQ-0538,
    REQ-0540,
    REQ-0546,
    REQ-0556,
    REQ-0560,
    REQ-0562,
    REQ-0587,
    REQ-0588,
    REQ-0589,
    REQ-0592,
    REQ-0593,
    REQ-2668,
    REQ-2864,
    REQ-2866,
    REQ-2878,
    REQ-2884,
    REQ-2886,
    REQ-2898,
    REQ-2912,
    REQ-2914,
    REQ-2923,
    REQ-2924,
    REQ-3102,
  ]
issue:
---

# The layout's content rules and their scope

One task, one branch, one pull request, one review.

## What to do

Extend `lib/layout.toml` and the checker with the per-kind keys SPC-1070 states: `sections` for every record, `draft_sections` for drafts, `first_section`, `required_values` for fields that must be non-empty, and `forbidden_fields`. Exempt a kind's own index file from its sections. Write a fixture for each key, each showing a draft held to a drafts-only rule and an approved record not held to it, each seen failing first against a program that returns nothing. Add fixtures for the existing rules ADR-1140 records as held: one file per artifact, the numbered kinds, the status vocabulary and the unstored observed statuses.

## Depends on

Nothing. ADR-1140 and SPC-1070 are approved.

## Evidence

Not yet.

## Left alone

The named rules, which TSK-1460 adds.
