---
id: TSK-2290
artifact: task
status: done
revised: 2026-09-27
epic: EPC-1470
closes: [REQ-0132, REQ-0147, REQ-0819, REQ-2828, REQ-2830]
issue: 521
projected: 4da0054d0a6f
---

# `meow-flow` ships `record-reviewer`, with a question set per kind and read-only tools

The agent reviews one record against the questions ADR-1490 lists for its
kind and the two every kind gets, reports findings without editing, and opens
with its label. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the agent's file, when `meow-author check` and `meow-author cost`
   run, then both exit 0, and its front matter declares `Read`, `Grep` and
   `Glob` as its only tools. Closed by: their output, naming REQ-0819.
2. Given the agent's body, when it is read, then it carries each question set
   ADR-1490 lists, the two every kind gets, the rule to ask nothing `paw check`
   settles and to report each finding as a judgement, and the label. Closed
   by: the trace, naming REQ-2828, REQ-2830, REQ-0132 and REQ-0147.
3. Given evaluation cases for a draft decision with a rule given no reason and
   no cost section, and for a clean requirement, when they run by hand through
   the loop, then the agent reports both findings in the first, reports the
   second clean, and opens each report with its label. Closed by: the loop's
   report, naming REQ-2828 and REQ-2830.

## What to do

Write `plugins/meow-flow/agents/record-reviewer.md` and its evaluation cases
under `plugins/meow-flow/evals/`, state the agent on the unit's page, and move
the unit to its next minor version.

## Depends on

Nothing. ADR-1490 is approved.

## Evidence

Closes REQ-0132, REQ-0147, REQ-0819, REQ-2828 and REQ-2830.
`meow-verbs evidence format lint test` exits 0:

```text
format: passed, record ed22fa4857b0, current at tree ad37c24af073
lint: passed, record e36728e3df52, current at tree ad37c24af073
test: passed, record d43c0b0d5776, current at tree ad37c24af073
```

`lint` runs `meow-author check`, 0 authoring failures, and `meow-author cost`,
with `meow-flow` at 487 of 500 characters. The trace:

1. The agent's front matter declares `tools: Read, Grep, Glob` and nothing
   else (REQ-0819).
2. R3 carries a question set for research, requirements, decisions,
   specifications, epics, tasks, defects, insights and the vision, and R4 the
   two every kind gets, reporting a rule with no reason as a finding
   (REQ-2828, REQ-2830). R1 asks nothing `paw check` settles, and R2 reports
   each finding as a judgement (REQ-0132, REQ-0147). R7 opens the report with
   the label.
3. `python3 tools/loop.py plugins/meow-flow --mode classifier`, run by hand
   with thresholds of 0.66 set in `evals/thresholds.toml` before the first
   run, judged by Opus 5.5, which is a smoke check (REQ-3028):

   | Model    | Defect case | Clean case |
   | -------- | ----------- | ---------- |
   | Sonnet 5 | 1.00 (n=5)  | 1.00 (n=5) |
   | Opus 5.5 | 1.00 (n=5)  | 1.00 (n=5) |

The first runs reached these scores only after three changes. The session
running the case had no tool to write the record to a path, so the cases now
hand the agent the record's text, and step 1 accepts it. The first "clean"
requirement named no observable condition, a fair finding, so the fixture now
states one. And the agent raised edges a check's author would settle as fixes,
passing the clean case 0.20 and then 0.40 on Sonnet 5, so R6 now counts such
an edge as a preference.

The defect case has a cost section that states no cost, where ADR-1490's
criterion says "no cost section": a missing section is what `paw check`
settles, which R1 keeps out of the review.

`paw check` read the cases' sample records as documents citing records that
don't exist, so the walk now skips `evals` beside `templates`, with
`Connections.test_an_evaluation_case_may_name_a_record_that_does_not_exist`,
seen failing first. `meow-flow` moves to 0.33.0.

## Left alone

The method skill and the review step, which TSK-2300 changes.
