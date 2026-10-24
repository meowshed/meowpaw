---
id: TSK-5630
artifact: task
status: done
revised: 2026-10-11
realises: ADR-2990
closes: []
issue: 1114
projected: e62cd679b787
tracked: b0cb76ce8a23
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

Criterion 1 closes with `paw check relations` reporting 0 findings on this
repository, the provider rule included. Criterion 2 closes with the record
check's shape rules passing over ADR-2990, which names this task as its
plan.

The five stages passed at tree `4364d882ff98`, each bound by `meow-checks run` and
confirmed by `meow-checks evidence`, exit 0: format `fcdc5ab700f0`, check
`c6bd6909315a`, lint `19fafec9381e`, test `fb6e4836449c`, build `a982d16b0043`.

## Left alone

The behaviours themselves, which their owning decisions' tasks hold.
