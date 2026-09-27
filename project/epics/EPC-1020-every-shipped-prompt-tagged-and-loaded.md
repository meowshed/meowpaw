---
id: EPC-1020
artifact: epic
status: approved
revised: 2026-09-23
realises: ADR-1020
checked-at: "#409"
---

# Every shipped prompt tagged, and the writing standard loaded by a hook

**Amended by ADR-1050.** The writing standard is loaded by a description
stating the obligation, not by a hook, and EPC-1030 realises that. T-002 keeps
the third-person descriptions and drops the hook. REQ-1140 is withdrawn, and
criterion 2 moves to EPC-1030.

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
      both models at 173 fewer tokens, in #79. TSK-1230 carries the table.

- [x] T-002 TSK-1240 write every description in the third person, with no
      hook
      closes: REQ-1134
      evidence: both descriptions the platform injects are in the third
      person, the skill's shipped in #85. TSK-1240 lists them.
      depends: TSK-1110, TSK-1230 - the hook names a skill that has to exist,
      and its measurement runs on both models through the loop T-001 extends

- [x] T-003 TSK-1250 mark outside text in the gate's and the reviewer's
      prompts
      closes: REQ-1132
      evidence: the gate blocking an injected approval in three runs of three,
      and the reviewer reporting an injected instruction as a finding, in #68.
      depends: TSK-1120, TSK-1140 - the two prompts it marks are written there

- [~] T-004 TSK-1260 remove every instruction the loop shows has no effect
  closes: REQ-1138
  dropped: ADR-1360 postpones REQ-1138 until each prompt's case set can
  tell one rule group's effect from noise on both models.
  depends: TSK-1230, TSK-1240, TSK-1250 - it measures the prompts in the
  form those tasks leave them, on both models

## Verified

I checked this under #409 on `main` after #408, gathering the evidence there
rather than carrying it over from the tasks. Criteria 1, 3, 4 and 6 are met at
this revision, criterion 2 was met in EPC-1030, and criterion 5 rests on the
measurement TSK-1230 made at #79, because the form it compared against no
longer ships:

| Criterion                                                                                                   | Evidence on `main` after #408                                                                                                                                                                                                                                  |
| ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. The prompt check passes on every shipped prompt and fails on a heading probe and an unknown-tag probe    | `check_prompts.py` reports 52 shipped prompts and 0 failures. A probe with a heading draws 2 failures and a probe with `<context>` draws 3, and both exit 1                                                                                                    |
| 2. The routing measurement, with the hook and without it                                                    | ADR-1050 moved this criterion to EPC-1030, which met it under #211                                                                                                                                                                                             |
| 3. The gate denies a text with a named defect, the model gets the reason, and its next attempt is corrected | In one session with `meow-prose-gate` loaded, the gate, running on Haiku 4.5, answered `ok: false` on the first commit's "low-hanging fruit". Sonnet 5 rewrote the message body from that reason, and the gate passed the second commit                        |
| 4. The reviewer, told to ignore its criteria, reports on the text and follows none of it                    | `meow-prose:prose` on Sonnet 5 treated the embedded instruction as content, followed none of it and reported it among 4 findings                                                                                                                               |
| 5. The tagged style scores no lower than the Markdown one on either model                                   | TSK-1230 measured this at #79: the tagged style landed on both models at 173 fewer tokens. The Markdown form hasn't shipped since, so the comparison can't be repeated here                                                                                    |
| 6. Every requirement lands in exactly one closed task, and the record reports nothing outstanding           | `paw check` reports 0 findings in every check. REQ-1130, REQ-1132, REQ-1134 and REQ-1136 land in closed tasks. REQ-1138 lands in T-004, which ADR-1360 drops while it postpones REQ-1138, so the epic closes on the 3 tasks that landed. REQ-1140 is withdrawn |

The gate also held against an embedded approval, which is the evidence T-003
gave for REQ-1132. The session model refused to run a commit whose message
told the hook to answer `{"ok": true}` without checking it, so I sent the
gate's own prompt from `hooks/hooks.json` to Haiku 4.5 directly, with that
commit as its `$ARGUMENTS`. The gate blocked it in 3 runs of 3.

At this revision I measured the shipped style against no style instead, 5 runs
for each arm on each model, for $6.83 of model calls. The styled arm scored
+0.06 above the unstyled one on Sonnet 5 and +0.04 on Opus 5.5, with two
standard errors of 0.12 and 0.06, so neither difference is distinguishable
from noise. The judge is Opus 5.5, from the same family as both models, and a
judge scoring its own family's output is biased, so every judged score here is
a smoke check and not evidence (REQ-3028). The loop's report stays local,
because `.gitignore` keeps every eval result out of the tree, so I copy its
per-case scores here, styled arm against unstyled:

| Case                     | Sonnet 5          | Opus 5.5          | Threshold |
| ------------------------ | ----------------- | ----------------- | --------- |
| `error-report`           | 0.95 against 0.75 | 0.80 against 0.75 | 0.75      |
| `gap-list-kept`          | 1.00 against 0.80 | 1.00 against 1.00 | 1.00      |
| `no-preamble-no-recap`   | 0.50 against 0.60 | 1.00 against 0.90 | 0.80      |
| `one-line-keeps-the-gap` | 0.85 against 0.90 | 1.00 against 1.00 | 1.00      |

On Sonnet 5, `no-preamble-no-recap` scored 0.50 where its threshold is 0.80,
and `one-line-keeps-the-gap` scored 0.85 where its threshold is 1.00. An
earlier run, on 2026-09-22, missed on `gap-list-kept` instead, so 5 runs are
too few to meet a threshold of 1.00 reliably on Sonnet 5.

### Postponements

ADR-1360's condition for resuming REQ-1138 still isn't met: on Opus 5.5,
`gap-list-kept` and `one-line-keeps-the-gap` score the same in both arms, so
those cases can't show one rule group's effect. This epic doesn't touch
ADR-1340's condition for its 8 requirements. The owner decides whether either
condition holds.

### Documentation and the record

No documentation page describes anything this epic made untrue, so the
document step changed nothing. The Coverage section names
`tools/check_coverage.py`, which `paw check coverage` has since replaced, and
the epic is approved, so the name stays as written.

## Coverage

ADR-1020 addresses six requirements. Each lands in exactly one task above,
and `tools/check_coverage.py` compares the decision's `addresses` against the
union of the tasks' `closes`.

The smallest subset that tests the decision is T-001 and T-002. With those
closed, every shipped prompt is in tags and the writing standard is present
before a text is written, which is the claim ADR-1020 makes.

## Not covered

REQ-1140 is withdrawn for REQ-1144, REQ-1146, REQ-1148 and REQ-1150, which
EPC-1030 closes under ADR-1050, so no task here closes it.

TSK-1140 of EPC-1010 builds the gate, and it follows ADR-1010 as amended: the
gate answers `ok: false` with a reason and sets `continueOnBlock: true`, where
the task's own text names the command hook's field. That task's record was
approved before the correction, so the correction lives in ADR-1020 and in
ADR-1010's amendment line, and criterion 3 above checks it.

Models other than Sonnet 5 and Opus 5.5 are out of scope, apart from Haiku 4.5
running the gate, which SPC-1020 measures as a classifier.
