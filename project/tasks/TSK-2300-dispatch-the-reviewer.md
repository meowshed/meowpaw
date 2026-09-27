---
id: TSK-2300
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1470
closes: [REQ-0149, REQ-0151, REQ-0157, REQ-0822, REQ-0823, REQ-2202]
issue: 522
projected: 208d11ab0a07
---

# The method skill dispatches the reviewer before each gate, and the review step dispatches a review of the session's own work

The method skill dispatches `record-reviewer` with the record's path alone,
repairs for at most two rounds, writes what stays open into the record, and
labels its gate report; the review step dispatches a review of work the
session produced. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the method skill and the review step, when they are read, then they
   carry the dispatch with the path alone, the two rounds, the Open review
   findings section, the label, the refusal to review the session's own
   record, and the self-assessed report. Closed by: the trace, naming each
   requirement.
2. Given evaluation cases for a session writing a draft decision, when they
   run by hand through the loop, then the session dispatches the agent naming
   only the path, and writes a finding left open after the second round into
   the record. Closed by: the loop's report, naming REQ-0149, REQ-0151,
   REQ-0822 and REQ-0823.
3. Given the changed skill, when `meow-author check` and `meow-author cost`
   run, then both exit 0. Closed by: their output.

## What to do

Change `plugins/meow-flow/skills/method/SKILL.md` and
`plugins/meow-flow/skills/method/steps/review.md`, add the evaluation cases,
and move the unit to its next patch version.

## Depends on

TSK-2290, whose agent the skill dispatches.

## Evidence

Closes REQ-0149, REQ-0151, REQ-0157, REQ-0822, REQ-0823 and REQ-2202.
`meow-verbs evidence format lint test` exits 0:

```text
format: passed, record 8ac9ba51d627, current at tree 8e40496c9117
lint: passed, record 16e4b8d4dbc2, current at tree 8e40496c9117
test: passed, record 3fd16f36189f, current at tree 8e40496c9117
```

`lint` runs `meow-author check`, 0 authoring failures, and `meow-author cost`,
with `meow-flow` at 487 of 500 characters. The trace:

1. The method skill: step 7 dispatches `meow-flow:record-reviewer` on each
   record written, and M19 gives it the path alone (REQ-0149, REQ-0151); M20
   bounds repair at two rounds (REQ-0822); M21 writes what stays open, and
   what the author rejects, under `## Open review findings` and names the
   section in the gate report (REQ-0823); step 8 and M22 say the record was
   reviewed by an agent and is unreviewed by a person, review nothing where no
   agent can be dispatched, and report a review of the session's own work as
   self-assessed (REQ-0157, REQ-2202).
2. The review step: W13 dispatches a review of the session's own work to an
   agent with read-only tools or reports it as self-assessed, and W14 names
   the verdict as an agent's (REQ-0149, REQ-0157).
3. `python3 tools/loop.py plugins/meow-flow --mode classifier --cases <case>
--allow-tool Write --allow-tool Edit`, run by hand with thresholds of 0.66
   set before the first run, judged by Opus 5.5, which is a smoke check
   (REQ-3028):

   | Case                     | Sonnet 5   | Opus 5.5   |
   | ------------------------ | ---------- | ---------- |
   | `review-before-the-gate` | 1.00 (n=5) | 1.00 (n=5) |
   | `open-findings-kept`     | 1.00 (n=5) | 1.00 (n=5) |

   `review-before-the-gate` checks the dispatch with `tool_used` graders on
   the `Agent` call, the second allowing at most 100 characters around the
   path, and the report's label with a judge. `open-findings-kept` forbids
   changing the Decision section, so the reviewer's finding on the 30-minute
   expiry can't be fixed, and judges the record left behind.

Three things had to change before these numbers meant anything. The runner
grants a gated tool only through its `--allow-tools` flag, never through a
case's front matter, so `tools/loop.py` gains `--allow-tool`. `paw` can't run
in the runner's scratch directory, so the cases say so, where sessions had
spent their turns trying. And a judge reading the trace saw a truncated copy
that sometimes lacked the dispatch, failing runs whose prompt was the path
alone, seen in three kept traces; the `tool_used` grader replaced it.

Not measured: a record reported as unreviewed where no agent can be
dispatched, because the runner can't remove the `Agent` tool from a session.
M22 carries it, traced above.

## Left alone

The agent, which TSK-2290 ships.
