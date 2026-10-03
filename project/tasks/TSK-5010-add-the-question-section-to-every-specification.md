---
id: TSK-5010
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2545
closes: [REQ-2250]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Add the question section to every specification in this repository

Every specification under `project/specs/` carries the template's question
section, each question answered from what the specification already states or
marked `unanswered`, so the specification is this repository's one
architecture description, as SPC-1090 states. One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given every file under `project/specs/`, when a test reads them, then each carries the question section with all seven questions, each answered or marked `unanswered` (REQ-2250). Closed by: a test under `tools/` naming REQ-2250, seen failing first.
2. Given the changed specifications, when `paw check` runs, then it reports nothing new. Closed by: `paw check`'s output.

## What to do

Answer each question only from what the specification already states or what
the tree shows, and mark the rest `unanswered`, because an answer invented to
fill the section hides the gap the question exists to show. Write each answer
to the writing standard. No specification gains a second architecture
document beside it.

## Depends on

- TSK-5000 (blocking): the section's wording is the template's.

## Evidence

Not yet.

## Left alone

Answering an `unanswered` question with new behaviour, which needs a decision
of its own.
