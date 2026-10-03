---
id: ADR-2440
artifact: adr
status: approved
revised: 2026-10-03
addresses: []
postpones: [REQ-2840, REQ-2842, REQ-2844, REQ-2846, REQ-2848]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2440. Answering a symbol question through a language server is postponed

## Decision

I postpone REQ-2840 to REQ-2848, which govern how the harness answers a symbol
question through a language server. No unit the harness ships talks to a
language server, and the platform's own code intelligence answers symbol
questions in a session without the harness. Each requirement keeps its
wording and reads as postponed in `paw status`.

Once this is accepted, the five requirements stop reading as open work, and
the loop doesn't pick them. What still doesn't work: the harness itself can't
say which request produced a symbol answer, or prepare a rename.

## Why

RES-0241 read an `lsp` skill and found that answers from a server, from a
search because no server runs and from a search because the server lacks the
feature look the same unless the harness names each. That matters only to a
unit that asks a server, and the harness has none. ADR-1330 lets a decision
postpone requirements with a condition.

## Alternatives

| Option                      | Better at                            | Why it lost                                               |
| --------------------------- | ------------------------------------ | --------------------------------------------------------- |
| Do nothing                  | No record                            | Five requirements read as open work nobody owns           |
| Ship a language-server unit | Symbol answers with their provenance | It duplicates what the platform already does in a session |
| Withdraw the requirements   | A smaller record                     | The findings hold for the first unit that asks a server   |

## What it costs

A person who wants a symbol answer's provenance relies on the platform's code
intelligence, which doesn't name the request behind each answer.

## What would reverse it

- A unit of the harness needs to ask a language server directly, or the
  owner asks for one.

## Consequences

`paw status` lists the five requirements under Postponed with the condition
above.

## How I will know it was realised

1. `paw status` lists REQ-2840, REQ-2842, REQ-2844, REQ-2846 and REQ-2848 as
   postponed by ADR-2440.

## What this does not settle

- Which language servers a pack would talk to.
