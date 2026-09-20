---
id: TSK-1040
artifact: task
status: draft
revised: 2026-09-21
unit: U-0001
epic: EPC-1000
closes: [REQ-0931]
issue:
---

# Check the style mechanically

One task, one branch, one pull request, one review.

## What to do

Write a check that reads every style `meow-core` ships and fails, naming the
file and the field, when either holds:

- `keep-coding-instructions` is false or absent. The platform's default is
  false, so a careless style silently deletes the engineering guidance, and the
  failure leaves no trace without this check.
- A rule ships with no condition under which it yields (REQ-0931). A rule with
  no stated exception is switched off entirely the first time it costs an
  answer.

Run the check in the repository's gate. The check is seen to fail first
(REQ-2072): write a style with `keep-coding-instructions: false`, watch it
fail, and only then point it at the shipped style.

A check that cannot fail is rewritten and never supplemented (REQ-2078).

## Depends on

TSK-1020, because the check has nothing to read before the style exists.

## Evidence

The check failing on a style with `keep-coding-instructions: false`, then
passing on the shipped one, both with the command, the output and the revision.

## Left alone

The check reads the style's front matter and its rule table. It does not judge
the prose, which is what the writing standard governs and what no program
settles.
