---
id: BUG-NNNN
artifact: bug
status: draft # draft | approved | withdrawn — triaged and closed derive
severity: minor | major | critical
violates: R-AREA-nnn # omit where no requirement covers it yet
found: YYYY-MM-DD
revised: YYYY-MM-DD
---

# <What is wrong, as a statement>

## Reproduction

The smallest sequence that produces it, reliably. **A defect with no
reproduction is a report** ([R-H-058]) and cannot be triaged, because the
triage question cannot be answered about behaviour nobody has observed twice.

## What the system does

Observed, precisely. Not inferred.

## What it should do, and why

The requirement it violates, cited. Where none exists, say so — that is a
requirement defect and routes to the requirements step.

## Triage

Does a requirement in force cover this? The answer decides where in the chain
this enters ([R-H-057]): implementation, research, requirements, or amendment.

## Closed by

The reproduction, now passing, and where it lives as a regression check
([R-H-059]). Where this is closed as not-a-defect, the reasoning instead — so
the same report is not triaged from scratch next time ([R-H-059a]).
