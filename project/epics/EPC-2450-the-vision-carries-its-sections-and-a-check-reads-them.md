---
id: EPC-2450
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2580
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The vision carries the sections a vision must have, and `paw check` reads them

Realises exactly one authorising record, ADR-2580. The epic is complete when
`paw check` reports a vision missing a section, carrying a date, restating a
requirement or running past 2,000 words, the design step asks the two
questions SPC-1230 states, and this repository's `project/vision.md` passes
the check.

## Acceptance criteria

Taken from ADR-2580's list of how it will be known realised:

1. `paw check` reports a fixture vision with no non-goals section (REQ-0620).
2. It reports a fixture vision with a date in it (REQ-2856).
3. It reports a fixture vision over 2,000 words (REQ-0611).
4. Every requirement ADR-2580 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-4740 rewrite `project/vision.md` to the template's sections, with quality goals in order and live risks
      closes: REQ-2850, REQ-2852, REQ-2854

- [ ] T-002 TSK-4750 report a vision's missing section, date, restated requirement and length from `paw check`, in the `record` feature of `crates/meow/`
      closes: REQ-0611, REQ-0614, REQ-0616, REQ-0618, REQ-0620, REQ-2856, REQ-2857
      depends: TSK-4740 (blocking) - the check fails today's vision, so the rewrite lands first or the gate goes red

- [ ] T-003 [P] TSK-4760 ask in the design step whether a decision's vision claims are falsifiable and which of a contradicting pair is stale, in `steps/design.md`
      closes: REQ-0624, REQ-2852

## Coverage

Each of the eleven requirements ADR-2580 addresses lands in a task. REQ-2852
lands in two, because the rewrite applies it to today's vision and the design
step applies it to every later change. TSK-4740 and TSK-4750 are the smallest
set that tests the decision, because a check that passes on a vision rewritten
to it is the claim. TSK-4740 and TSK-4760 run in parallel.

## Not covered

What this repository's quality goals are, which ADR-2580 leaves to the
rewrite, so TSK-4740 proposes them in its pull request for the owner to read.
