---
id: TSK-1510
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1150
closes: [REQ-0692, REQ-0698, REQ-0700, REQ-0702]
issue: 215
---

# The epic's rules for a done, an added and a dropped task

One task, one branch, one pull request, one review.

## What to do

Add the named rules `done-has-evidence`, `added-says-why` and `dropped-says-why` to the `rules` check and list them under the epic kind's `rules` in `lib/layout.toml`, as SPC-1070 states them. A task marked `[x]` whose `## Evidence` section holds nothing past a leading "Not yet." paragraph fails, as does a `[+]` entry with no `added:` line and a `[~]` entry with no `dropped:` line. Write a fixture for each, seen failing first.

## Depends on

Nothing. ADR-1150 and SPC-1100 are approved.

## Evidence

Not yet.

## Left alone

Whether work that landed belongs to a task still unmarked.
