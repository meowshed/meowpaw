---
id: REQ-NNNN
artifact: requirement
status: draft # draft | approved | withdrawn | superseded
revised: YYYY-MM-DD
elaborates: RSH-NNNN
prompted-by: BUG-NNNN # where a defect revealed the gap
---

<!-- Written to the writing standard in `CLAUDE.md`: lead with the answer, state the reason beside every rule, and show the failing case. No paragraph opens in bold, and a sentence that reads as a proverb is missing its reason. -->

# Requirements

What must be true. This document is **append-only**: a requirement is never
reworded, only withdrawn and replaced ([R-H-302]).

## How to read it

Identifiers are allocated once and never reused, in blocks of ten per topic so a
later statement joins its neighbours ([R-H-253]). Each carries a status and,
once implemented, the checks that cover it.

## <Topic>

**[R-AREA-001]** `proposed` · The system MUST …

> verify: static | behavioural | eval
> covers: path/to/check

## Withdrawn

**[R-AREA-00n]** _Withdrawn by [ADR-NNNN] — superseded by [R-AREA-0nn]._

Kept here permanently so that every citation resolves forever ([R-H-308]).
