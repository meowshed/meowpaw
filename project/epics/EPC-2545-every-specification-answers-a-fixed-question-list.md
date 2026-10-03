---
id: EPC-2545
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2630
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Every specification answers a fixed list of questions, and each concern a decision names is framed

Realises exactly one authorising record, ADR-2630. The epic is complete when
the `spec` template carries the seven questions, the design step names a
decision's concerns, `paw check` reports a concern no specification frames,
and every specification in this repository carries the question section, as
SPC-1090 states under "The questions a specification answers".

## Acceptance criteria

Taken from ADR-2630's list of how it will be known realised:

1. Every specification carries the question section, with each question answered or marked `unanswered` (REQ-2252).
2. `paw check` reports a fixture decision naming a concern no specification cites (REQ-2254).
3. Every requirement ADR-2630 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 TSK-5000 add the seven questions to the `spec` template and the `concerns:` field to the design and spec steps, in `plugins/meow-flow/`
      closes: REQ-2252

- [ ] T-002 [P] TSK-5005 report a decision's concern that no specification section frames, in the `record` feature of `crates/meow/`
      closes: REQ-2254
      depends: TSK-5000 (blocking) - the check reads the `concerns:` field TSK-5000 adds to the layout

- [ ] T-003 [P] TSK-5010 add the question section to every specification under `project/specs/`
      closes: REQ-2250
      depends: TSK-5000 (blocking) - the section's wording is the template's

## Coverage

Each of the three requirements ADR-2630 addresses lands in exactly one task.
TSK-5000 and TSK-5010 are the smallest set that tests the decision, because
every specification answering the same questions, with the gaps marked, is
the claim. TSK-5005 and TSK-5010 run in parallel once TSK-5000 lands.

## Not covered

Whether an answer is right, which ADR-2630 leaves to review, and how a
diagram in a view is drawn, which ADR-2620 decides and EPC-2540 realises.
