---
id: EPC-2100
artifact: epic
status: done
revised: 2026-09-28
realises: ADR-2200
---

# A skeptic tries to refute each requirement an epic claims, and verification records each refutation it confirms as a draft defect

Realises exactly one authorising record, ADR-2200. The epic is complete when
`meow-flow` ships the read-only `skeptic` agent, the verify step dispatches it
before writing `## Verified` and writes a draft defect for each refutation it
confirms, and review judges each refutation the verifier rejected.

## Acceptance criteria

Taken from ADR-2200, from its list of how I will know it was realised, before
the tasks below were written:

1. `meow-author check` passes on `agents/skeptic.md`, whose tools are `Read`,
   `Grep` and `Glob` alone, and a static fixture in `plugins/meow-flow/tests`
   finds in its body the input rule, both questions, the three states, the
   rule that it attacks each refutation before reporting it, the rule that a
   faulty check is rewritten and not supplemented, and the label.
2. A static fixture finds, in `steps/verify.md`, the dispatch named before the
   step that writes `## Verified`, the draft defect with empty triage, the
   `Refutation` paragraph and its `not attempted` form, and REQ-3520 in V2;
   and in `steps/review.md`, the rule on rejected refutations.
3. An evaluation case gives the agent an epic whose closing check is a
   tautology and grades that it reports that requirement `refuted`, naming
   the check's lines. A second gives it a sound epic and grades that it
   reports no refutation. A third gives the verify step a confirmed
   refutation and grades that it writes a draft defect whose `violates` names
   the requirement, whose reproduction names the refutation's input and its
   revision, with a `severity`, `## Triage` empty and no `enters`. All three
   run by hand on Sonnet 5 and Opus 5.5, with Opus 5.5 judging, at thresholds
   set in `thresholds.toml` before the first run.
4. `paw check` accepts a draft defect with `violates` and `severity` set, a
   reproduction, an empty `## Triage` and no `enters`, shown by a fixture.
5. Every requirement ADR-2200 addresses, REQ-0314, REQ-2070, REQ-2078,
   REQ-3520, REQ-3522 and REQ-3524, lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [~] T-001 TSK-3700 add `plugins/meow-flow/agents/skeptic.md`, its static
  fixture, its two evaluation cases, its README entry and the budget of
  600 characters
  closes: REQ-0314, REQ-2070, REQ-2078
  dropped: ADR-2300 supersedes ADR-2200, so no step dispatches the skeptic

- [~] T-002 TSK-3710 make `steps/verify.md` dispatch the skeptic and write a
  draft defect for each refutation it confirms, make `steps/review.md`
  judge each rejected refutation, and add the defect fixture and the
  third evaluation case
  closes: REQ-3520, REQ-3522, REQ-3524
  depends: TSK-3700, because the verify step dispatches
  `meow-flow:skeptic`, and a dispatch of an agent the unit doesn't ship
  fails in every session that runs it
  dropped: ADR-2300 removes the verify step it would change

Both tasks raise `meow-flow`'s minor version and its README's `describes`, so
TSK-3710 takes the next minor version above the one TSK-3700 lands with.

Both tasks are dropped: ADR-2300 supersedes ADR-2200, so no step is left to
dispatch the skeptic.

## Coverage

ADR-2200 addresses six requirements, and each lands in one task. REQ-0314,
REQ-2070 and REQ-2078 land in TSK-3700, because the agent's body carries all
three: it attacks each refutation before reporting it, it reports a weak or
tautological check as a defect in the check, and it names the fix to such a
check as a rewrite. REQ-3520, REQ-3522 and REQ-3524 land in TSK-3710, because
the verify step's prompt is what writes only the three permitted things,
records the skeptic's outcome for each requirement, and writes the draft
defect.

The smallest set that tests the decision is both tasks: the agent alone
reports refutations that nothing records, and the verify step alone
dispatches an agent that doesn't exist. Criterion 4 can be measured before
either task lands: as `crates/meow/src/record.rs` reads, `paw check` asks for
`enters` only on a defect whose `## Triage` is written, so it is expected to
pass already, and TSK-3710 changes the program only if its fixture fails.

## Not covered

- Which model the agent runs on, a skeptic for a single task or for work no
  epic covers, and confirming a refutation that needs the code changed, which
  ADR-2200 names as not settled.
- A program that checks each `## Verified` section for its `Refutation`
  paragraph. ADR-2200 makes the paragraph an obligation on the step, and the
  epics verified before it keep their sections as written.
- The user-facing pages beyond `meow-flow`'s README: `docs/` and `llms.txt`.
  The document step updates them once both tasks are done, from ADR-2200's
  consequences.
- The reversal conditions ADR-2200 gives, which the next ten epic
  verifications measure after this epic closes.
