---
id: EPC-1190
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1190
checked-at:
---

# The design obligations carried by the steps

Realises exactly one authorising record, ADR-1190. The epic is complete when
the design step and the six others carry every obligation ADR-1190 places on
them, traced from the tasks that close them.

## Acceptance criteria

Taken from ADR-1190, from its list of how I will know it was realised, before
the tasks below were written:

1. Every requirement ADR-1190 addresses maps, in the task that closes it, to a
   labelled rule in the step file named, or, for REQ-2130, to a search showing
   no step names a practice command.
2. The prompt check and `meow-method check` pass.
3. Evaluation measures that a design follows the rules.
4. Every requirement ADR-1190 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1650 the design step carries the obligations on what it designs
      closes: REQ-1230, REQ-1231, REQ-1232, REQ-1233, REQ-1234, REQ-1235, REQ-1236, REQ-1237, REQ-1238, REQ-1239, REQ-1240, REQ-1242, REQ-1244, REQ-1246, REQ-1248, REQ-1250, REQ-1252, REQ-1254, REQ-1256, REQ-1258, REQ-2130, REQ-2138, REQ-2140, REQ-2760, REQ-2762, REQ-2764, REQ-2766, REQ-2768, REQ-2770, REQ-2772, REQ-2776, REQ-2778, REQ-2780, REQ-2782, REQ-2794, REQ-2796
      evidence: 36 requirements traced, in #262.

- [ ] T-002 TSK-1660 the other steps carry their share of the design obligations
      closes: REQ-2131, REQ-2132, REQ-2133, REQ-2134, REQ-2137, REQ-2139, REQ-2256, REQ-2258, REQ-2260, REQ-2262, REQ-2264, REQ-2266, REQ-2268

## Coverage

ADR-1190 addresses 49 requirements. Each lands in exactly one task above,
and `meow-method check coverage` compares the decision's `addresses` against
the union of the tasks' `closes`. The two tasks can run in parallel.

## Not covered

Criterion 3, measuring behaviour, waits for evaluation, which the owner
postponed, and the epic closes with it named as unmet, as REQ-3170 allows.
