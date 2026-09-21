---
id: EPC-NNNN
artifact: epic
status: draft # draft | approved | superseded — in-progress and done derive
revised: YYYY-MM-DD
realises: ADR-NNNN | BUG-NNNN # required: exactly one authorising record
checked-at: rN
---

<!-- Written to the writing standard in `CLAUDE.md`: lead with the answer, state the reason beside every rule, and show the failing case. No paragraph opens in bold, and a sentence that reads as a proverb is missing its reason. -->

# <What this realises>

Realises exactly one authorising record ([R-H-043a]), which is what gives it an
end: this epic is complete when that decision is realised or that defect is
closed.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass
([R-H-180]).

## Tasks

- [ ] T-001 [P] <what, with the path it touches>
      closes: R-AREA-nnn
      depends: T-000 — and why, since a convenience dependency is not one
      produces: SPC-NNNN — where the output is a document rather than code
      evidence: <command, result, revision> once done

## Coverage

Every requirement this epic is responsible for lands in exactly one task, or is
deferred here with a reason ([R-H-042a]).

## Not covered

What this deliberately leaves, and why.
