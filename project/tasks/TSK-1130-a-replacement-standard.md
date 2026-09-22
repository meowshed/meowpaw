---
id: TSK-1130
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes: [REQ-1000, REQ-1002]
issue: 50
---

# Let a repository replace the standard

One task, one branch, one pull request, one review.

## What to do

A repository replaces the writing standard by declaring its own in
`.meowpaw/prose/` (REQ-1000). When the declaration exists, the skill loads the
replacement and not the shipped standard, and the reviewer reads against the
replacement.

The replacement is total (REQ-1002). The skill never merges the two, because
two standards disagreeing about voice produce text that follows neither, and
an author has no way to tell which one applies.

The unit writes nothing into the repository to make this work (REQ-3180). The
repository writes `.meowpaw/prose/` itself, and the unit only reads it.

Document the declaration on the unit's documentation page: where the file goes,
what it replaces, and that nothing of the shipped standard survives it.

## Depends on

TSK-1120, because replacing the standard replaces what the reviewer reads, so
the skill and the reviewer must both exist before either can be replaced.

## Evidence

Not yet. The task closes on a scratch repository declaring a replacement that
contradicts one shipped rule, where a session follows the replacement's rule
and the reviewer, given a text that breaks only the shipped rule, names
nothing.

## Left alone

`meow-prose-gate`, which carries its own criteria and reads no replacement.
Whether the gate should honour one is a question for a later decision, because
ADR-1010 does not settle it.
