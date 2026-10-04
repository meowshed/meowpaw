---
id: TSK-1900
artifact: task
status: done
revised: 2026-09-26
epic: EPC-1280
closes: [REQ-3114, REQ-3116]
issue: 352
---

# The onboard command migrates an existing record and writes drafts

The onboard command migrates an existing record and writes drafts, as ADR-1280 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given the command, when the trace is read, then each requirement this task closes maps to a labelled rule that exists in it. Closed by: the trace table and a script finding each label.

## What to do

Add rules to `/meow-method:onboard`: migrate a record kept in the repository's own format to the matching artifact kind, and write each recovered requirement and decision as a draft. Make its last step name `meow-method onboarding remove` as what follows approval. Record the trace under Evidence.

## Depends on

Nothing. ADR-1280 is approved.

## Evidence

Each requirement this task closes is carried by a labelled rule in the onboard
command, and no rule names a requirement:

| Requirement | Carried by                       |
| ----------- | -------------------------------- |
| REQ-3114    | B12 in `skills/onboard/SKILL.md` |
| REQ-3116    | B11 in `skills/onboard/SKILL.md` |

Step 6 now names `meow-method onboarding remove` as what follows the report's
approval. A script found both traced labels. Whether the model follows the
rules is measured by evaluation, which is postponed.

## Left alone

Reading a forge's history, which ADR-1290 and ADR-1300 take.
