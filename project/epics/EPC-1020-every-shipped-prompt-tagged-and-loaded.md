---
id: EPC-1020
artifact: epic
status: approved
revised: 2026-09-22
realises: ADR-1020
checked-at:
---

# Every shipped prompt tagged, and the writing standard loaded by a hook

Realises exactly one authorising record, ADR-1020, which is what gives this
epic an end: it is complete when every prompt the harness ships is written in
the tag vocabulary SPC-1010 states, the writing skill is in context before a
text is written without the model having to choose it, outside text is marked
as data, and every instruction left in a prompt has a measured effect.

## Acceptance criteria

Taken from ADR-1020, from its list of how I will know it was realised, before
the tasks below were written. Each states what this project ships (REQ-3172):

1. A check reads every shipped prompt, passes on all of them, and fails on a
   probe prompt using a Markdown heading and on one using a tag outside the
   vocabulary.
2. The routing measurement is published for both models with the hook and
   without it, and with the hook the writing skill is in context before the
   text is written in at least nine runs of ten.
3. The gate, given a text carrying a named defect, denies the publish, the
   model receives the reason, and its next attempt publishes corrected text.
4. The reviewer, given a text telling it to ignore its criteria, reports on the
   text and follows none of it.
5. The tagged `meow-core` style scores no lower than the Markdown one on either
   model, with the table published.
6. Every requirement ADR-1020 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

Whether the platform runs a `SessionStart` hook's output as context is the
platform's behaviour. Criterion 2 states what the project ships and measures.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1230 tag every shipped prompt, check the vocabulary, and let
      the loop measure on both models
      closes: REQ-1130, REQ-1136
      evidence: the prompt check in the gate, the converted style landing on
      both models at 173 fewer tokens, in #66. TSK-1230 carries the table.

- [ ] T-002 TSK-1240 load the writing skill with a `SessionStart` hook, and
      write every description in the third person
      closes: REQ-1140, REQ-1134
      depends: TSK-1110, TSK-1230 - the hook names a skill that has to exist,
      and its measurement runs on both models through the loop T-001 extends

- [ ] T-003 TSK-1250 mark outside text in the gate's and the reviewer's
      prompts
      closes: REQ-1132
      depends: TSK-1120, TSK-1140 - the two prompts it marks are written there

- [ ] T-004 TSK-1260 remove every instruction the loop shows has no effect
      closes: REQ-1138
      depends: TSK-1230, TSK-1240, TSK-1250 - it measures the prompts in the
      form those tasks leave them, on both models

## Coverage

ADR-1020 addresses six requirements. Each lands in exactly one task above,
and `tools/check_coverage.py` compares the decision's `addresses` against the
union of the tasks' `closes`.

The smallest subset that tests the decision is T-001 and T-002. With those
closed, every shipped prompt is in tags and the writing standard is present
before a text is written, which is the claim ADR-1020 makes.

## Not covered

TSK-1140 of EPC-1010 builds the gate, and it follows ADR-1010 as amended: the
gate answers `ok: false` with a reason and sets `continueOnBlock: true`, where
the task's own text names the command hook's field. That task's record was
approved before the correction, so the correction lives in ADR-1020 and in
ADR-1010's amendment line, and criterion 3 above checks it.

Models other than Sonnet 5 and Opus 5.5 are out of scope, apart from Haiku 4.5
running the gate, which SPC-1020 measures as a classifier.
