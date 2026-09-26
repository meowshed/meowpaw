---
id: ADR-1300
artifact: adr
status: approved
revised: 2026-09-26
addresses: [REQ-3110, REQ-3112, REQ-3128]
supersedes: []
---

# 1300. Onboarding reads what the documents and the forge history state, and recovers it as drafts

## Decision

`/meow-method:onboard` reads the repository's forge history through
`meow-github history` where that pack is installed, alongside its documents,
its existing harness and its code, and recovers two more things, each as a
draft citing where it was stated:

- a requirement for each obligation a document, an issue or a pull request
  states, citing the file, the issue or the comment by its address;
- a decision for each choice a document, an issue or a pull request records
  with the alternative it rejected, citing the discussion, where a pull
  request closed without merging is a rejected alternative.

Code alone yields neither. Where `meow-github` isn't installed, onboarding
reports the history as unread in the report's gaps and names the pack that
would read it, and recovers from the documents alone.

After this decision onboarding converts a repository from its documents, its
code and its forge history: its vision, specifications and constitution, its
stated requirements and decisions as drafts, and every document placed, with
the placed ones removed once the report is approved. What still doesn't work:
whether a model recovers statements faithfully is measured by evaluation,
which is postponed, and a forge other than GitHub needs a pack of its own.

## Why

RES-0277 found that issues and pull requests state obligations and decisions
that code doesn't, that each has an address a draft can cite, that a pull
request closed without merging records a rejected alternative, and that the
person approving a draft affirms it. RES-0037 found that nothing recovered
from code alone is a requirement, and RES-0277 that forge knowledge lives in a
pack, with onboarding reporting the history as unread without one.

The strongest objection: a draft requirement recovered from an issue may
state what one person wanted and the project never agreed to. It may, which
is why it stays a draft: the approval gate is where the project agrees, and a
draft nobody approves never enters the record in force.

## Alternatives

| Option                                             | Better at                       | Why it lost                                                            |
| -------------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------- |
| Recover stated obligations and decisions as drafts | A full record, each draft cited | Chosen                                                                 |
| Recover only the specification                     | Nothing to approve              | The record starts empty although the history states what it would hold |
| Recover requirements from the code as well         | More drafts                     | Code states no obligation, which REQ-1544 forbids inventing            |
| Do nothing                                         | Costs nothing                   | The history stays unread and the person rewrites it by hand            |

## What it costs

Three rules and a step in the onboard command.

## What would reverse it

- Evaluation shows recovered drafts are mostly rejected at approval, and
  recovery narrows to decisions alone.

## Consequences

- `/meow-method:onboard` reads the forge history through `meow-github` and
  recovers stated requirements and decisions as drafts.

## How I will know it was realised

1. Each rule ADR-1300 places in the onboard command maps to its requirement
   in the task that closes it.
2. The onboard command runs `meow-github history` only as a bare command, and
   `check_standalone.py` passes.
3. Every requirement ADR-1300 addresses lands in exactly one closed task.

## What this does not settle

- Measuring whether a model recovers statements faithfully.
- A forge other than GitHub.
