---
id: TSK-1190
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes: [REQ-0956]
issue: 56
---

# Rewrite the reply shape to the standard, and measure it

One task, one branch, one pull request, one review.

## What to do

Rewrite `plugins/meow-core/output-styles/meow.md` and
`plugins/meow-core/fragments/reply-shape.md` against the standard `meow-prose`
states. Keep every rule and its condition, since `tools/check_style.py` fails
on a rule with none.

Measure the rewrite against the style it replaces (REQ-0956), with the runner
TSK-1170 builds. The style and the fragment each go through the loop
separately, because the fragment reaches a subordinate agent the style never
reaches, and its cases are replies from an agent dispatched with it:

- The current style, or the current fragment, is the baseline.
- Each candidate changes one thing, so its delta can be attributed.
- Every candidate runs on the same cases, with the same run count and the same
  judge.
- A candidate lands when the delta holds or rises and the token cost falls. A
  better score at a higher cost is published with both numbers, and the owner
  decides.
- Every candidate's delta is published, including the ones that lost. If none
  lands, the baseline stays, and that is reported as the result.

Select the style explicitly in both arms, because BUG-1040 means it does not
apply on its own.

## Depends on

TSK-1110, because the rewrite follows the standard, and TSK-1170, because a
case set scoring 1.00 in both arms cannot see whether a rewrite helped.

## Evidence

The style stays as it is: no candidate landed, which the task counts as its
result. `plugins/meow-core/fragments/reply-shape.md` no longer exists, because
ADR-1040 has the style carry its own rules to a subordinate agent through R10,
so there was no fragment to put through the loop.

The reviewer as #100 left it read `output-styles/meow.md` and found nothing at
fix level and eight findings at improve level, mostly one rule repeating
another. Each group of findings became one candidate. Merging R3 into R2 was
left out, because it renumbers rules that other records cite by number.
`tools/loop.py` on `meow-core`'s four cases, five runs per arm, the style
selected in the arm that has it, judged by Opus 5.5, so every judged score is
a smoke check (REQ-3028):

| Candidate | Change                                                         | Sonnet 5 delta (2SE) | Opus 5.5 delta (2SE) | Verdict |
| --------- | -------------------------------------------------------------- | -------------------- | -------------------- | ------- |
| baseline  | the style as #79 landed it                                     | +0.15 (0.08)         | +0.02 (0.03)         | stays   |
| S1        | R8 and R9 stop repeating what R1, R4, R5 and R7 already say    | +0.07 (0.12)         | +0.01 (0.09)         | lost    |
| S2        | R7 and R8 split under 35 words, with contractions where spoken | +0.07 (0.10)         | +0.06 (0.06)         | lost    |
| S3        | R10 puts its condition first and defines a fork; R9's reason   | +0.08 (0.08)         | +0.04 (0.03)         | lost    |

No candidate moved its overall delta beyond twice its standard error, which
SPC-1020 asks of a candidate before it lands. On Opus 5.5 three of the four
cases score 1.00 in both arms, so the set cannot see a change to the style on
that model; a set that discriminates there is work for TSK-1260. The token
column in this run is noise, from -797 to 1,315 for files within 180
characters of each other, so no verdict rests on it; `tools/check_budget.py`
counts the style at 3,945 characters.

`mise run style` passes on the style as it stands. REQ-0956 is closed.

## Left alone

How the style reaches a session, which BUG-1040 routes to design.
