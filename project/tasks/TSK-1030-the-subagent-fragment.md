---
id: TSK-1030
artifact: task
status: draft
revised: 2026-09-21
unit: U-0001
epic: EPC-1000
closes: [REQ-0954]
issue:
---

# Carry the shape into a subordinate agent

One task, one branch, one pull request, one review.

## What to do

An output style reaches a fork and never a subordinate agent, which runs its
own system prompt. Ship the same rules as a fragment inside `meow-core`, and
have every unit that dispatches a subordinate agent include it in the prompt it
sends.

The constraints that bind it:

- A subordinate agent's prompt MUST carry the reply shape itself (REQ-0954).
- A unit MUST address its supporting files through the platform's own directory
  variable rather than by a fixed path (REQ-2688).
- Material MUST name its supporting files and say when each is worth reading
  (REQ-1124).

The fragment states the rules once. Where it would restate the style's wording
at length, it cites the style and keeps the obligations.

## Depends on

TSK-1020, because the fragment restates the rules the style carries and cannot
precede them.

## Evidence

A subordinate agent dispatched by a shipped unit, and its reply in the shape:
leading with the action, with no closing offer of help. Recorded with the
command and the revision.

## Left alone

No unit dispatches a subordinate agent yet, so this task ships the fragment and
the obligation on any unit that later does. The kernel's documentation page
states that obligation, and it is not left implicit.
