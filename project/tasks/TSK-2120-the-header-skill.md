---
id: TSK-2120
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1380
closes: [REQ-1008, REQ-1016, REQ-1018, REQ-1020, REQ-3066, REQ-3068]
issue: 445
projected: f36b18fac81b
---

# `meow-licence:header` adds the declared header to a file Claude Code creates

The unit gains a skill that loads before Claude Code creates a file in a
repository declaring licensing, adds the declared header in the form the
file's format permits, never rewrites a header, and declares nothing where
the repository declares nothing. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given `skills/header/SKILL.md`, when it is read, then a labelled rule
   carries each requirement this task closes, and no rule names a
   requirement, a language or a tool. Closed by: a table in the evidence
   tracing each requirement to its rule.
2. Given the step files and skills, when `mise run prompts` runs, then it
   passes, and `mise run budget` holds the unit to its ceiling. Closed by:
   their output.
3. Given a fresh session in a scratch repository declaring a header in its
   profile, when Claude Code is asked to create a new file, then the file
   carries the header and `meow-licence check` passes on it. Closed by: the
   session's result, on Sonnet 5.

## What to do

Write the skill with a description stating the obligation, as ADR-1050
decides, and rules for each requirement: read the declaration from
`REUSE.toml` or the profile, add it to a new file a bulk annotation doesn't
cover, in the file's own comment form or a `.license` file beside it, copy the
form the repository's files carry, never touch an existing header, and report
an undeclared repository without writing. Set the unit's budget to the
description's size with slack.

## Depends on

TSK-2110, because the skill ships in the unit it creates.

## Evidence

Not yet.

## Left alone

A hook applying headers, which the platform offers no event for on file
creation outside a tool call.
