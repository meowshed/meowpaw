---
id: BUG-1360
artifact: bug
status: approved
severity: major
violates: REQ-0332
enters: research
found: 2026-09-29
revised: 2026-09-30
issue: 716
---

# A session under the route skill calls a tool before it reports the route

A session that loads `meow-flow:route` often calls Bash, or edits, before it
writes the route report, and Opus 5.5 often writes no report at all. So the
person doesn't see the route before work starts, which REQ-0332 asks for.

## Reproduction

Claude Code 2.1.283, `meow-flow` 0.40.0 from the branch that closes issue 649,
on 2026-09-29. Run the 13 route cases by hand:

```bash
claude plugin eval plugins/meow-flow --case 'route-*' -j 4 --scaffold \
  --ablation none --model claude-opus-5-5 --judge-model claude-opus-5-5 \
  --allow-tools Edit Write Bash --trust-plugin --keep-temp
```

Then run it again with `--model sonnet`, and read each run's grader
`no-write-before-route` and its kept trace.

## What the system does

The shared grader passed 30 of 36 runs on Sonnet 5 and 27 of 36 on Opus 5.5,
leaving out `route-a-question`. On Opus 5.5, five cases scored below their
threshold of 0.66: `route-reduced-unauthorised` 0.00, `route-list-one` 0.17,
`route-overridden` 0.20, `route-reported-ambiguous` 0.33 and `route-given`
0.58. In their traces the session goes from the router's reply, or from the
skill's load, straight to Bash, `paw ready` or the method skill, and no text
block holds the route. On Sonnet 5 the failing runs call Bash to read, such as
`find` for an epic after `route reduced`, before the report.

## What it should do, and why

Every run writes the route, its size, shape, reason, ambiguity and override
words, as text before any Write, Edit, NotebookEdit or Bash call, because a
person overrides from that report and a route they never see is one they can't
override (REQ-0332). The skill's R1 and step 4 say so. Nothing else holds
them, and ADR-2100 names that gap: no hook refuses a write before the route
is reported.

## Triage

It enters at research, because the cause is unknown: whether a wording holds
Opus 5.5 to a text report before its next tool call, or whether only a hook
can, is unmeasured, and ADR-2100 rejects the hook until one reads the
conversation as it stands (RES-0203). Two rewordings in TSK-3510, a step
saying to call no tool until the report is written and a failing example of a
route never shown, left Opus 5.5 below threshold on the same five cases.
Major, because the route is the one place a person sees how much method a
change gets before it starts.

## Closed by

Not closed. It closes with each route case at or above its threshold on Sonnet 5 and Opus 5.5 in a run
by hand, with `no-write-before-route` passing in every run of every case but
`route-a-question`.
