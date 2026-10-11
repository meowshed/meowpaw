---
id: TSK-5630
artifact: task
status: approved
revised: 2026-10-11
realises: ADR-2990
closes: []
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Bind the surfaced requirements to their decisions

The task is the addresses ADR-2990 wrote: each requirement RES-0354 and
BUG-1680 surfaced names the decision whose behaviour holds it, and the
record's relations pass on this repository (REQ-3900). One task, one branch,
one pull request, one review.

## Acceptance criteria

1. Given this repository, when `paw check relations` runs, then it reports no
   requirement in force with no provider (REQ-3900).
2. Given ADR-2990, when the record check runs, then the decision names an
   approved task that realises it (REQ-3902).

## What to do

The addresses in ADR-2990's front matter are the change; the behaviours they
name are held by the checks their owning decisions already carry, and this
task writes none of them again.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The behaviours themselves, which their owning decisions' tasks hold.
