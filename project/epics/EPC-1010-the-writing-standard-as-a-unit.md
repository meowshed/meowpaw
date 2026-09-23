---
id: EPC-1010
artifact: epic
status: approved
revised: 2026-09-22
realises: ADR-1010
checked-at:
---

# The writing standard, shipped as a unit that reviews itself

Realises exactly one authorising record, ADR-1010, which is what gives this
epic an end: it is complete when the standard ships as `meow-prose`, a
separately installed gate blocks a publish on narrow defects, no pattern over
prose is left enforcing it, and a change to any prompt the harness ships is
measured on a case set that can see the change and improved through a loop
that publishes every candidate.

## Acceptance criteria

Taken from ADR-1010, from its list of how we will know it was realised, before
the tasks below were written. Each states what this project ships, because
REQ-3172 forbids a criterion that asks the platform to behave:

1. `meow-prose` ships a skill whose description routes on writing work, and a
   routing case set measures it firing on natural phrasing, with the run count
   and the threshold published.
2. The reviewer, given a text carrying a bold fragment where a heading belongs,
   a counted opener and an over-long sentence, names all three with their
   lines.
3. The reviewer, given a text the standard is happy with, names nothing.
4. The reviewer has read the unit's own skill, its own prompt and the
   documentation page, and each finding is fixed or disputed on the record.
5. The rewritten `meow-core` style is measured against the one it replaces, on
   a case set where the baseline does not already score 1.00, with the run
   count and the judge stated.
6. The gate blocks a publish carrying a named defect, passes a clean one, and
   denies a publish that hides its text behind a path, with its block rate on
   each kind published.
7. The reviewer, given a source file, names a comment that restates the code.
8. Every skill and prompt the harness ships goes through one loop and lands
   with its baseline, every candidate tried, and each candidate's delta and
   token cost published, including the ones that lost. Those are the
   `meow-prose` skill and its description, the reviewer, the gate, the
   `meow-core` style and the fragment a subordinate agent carries.
9. Every rule, pattern and self-review check in the standard as it stands,
   the first text in the appendix of ADR-1010, lands in the rewritten skill or
   is dropped with its reason, and each one a reader can see in a text has a
   case in the reviewer's labelled set.
10. Every requirement ADR-1010 addresses lands in exactly one closed task, and
    the checks over the record report nothing outstanding.

Whether a session loads the skill depends on the platform routing on its
description, which this project does not control. The routing measurement in
criterion 1 is what we can ship, and a routing rate below its threshold is a
defect in the description, which is the thing we change.

No judge from another model family is available to this project, so every
judged result in criteria 5 and 8 is reported as a smoke check (REQ-3028). The
judge is Opus 5.5, stronger than the Sonnet 5 it grades, which meets the rest
of that requirement. Where a criterion can rest on a grader that costs nothing,
it does (REQ-3024), because that grader's verdict is evidence and a smoke check
is not. A judge from another family becomes available only through a later
change, which would re-run the judged cases and publish both verdicts.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1110 `plugins/meow-prose/`: the manifest, the marketplace
      entry, the skill carrying the standard rewritten smaller, and the
      documentation page
      closes: REQ-0990, REQ-0991, REQ-0992, REQ-0993, REQ-0994, REQ-0995,
      REQ-0996, REQ-0997, REQ-0998, REQ-3188, REQ-1062, REQ-1064, REQ-1066
      evidence: the unit in #70, the split in #74 and #86, and the skill loading
      in every writing run on both models in #85. TSK-1110 carries the counts.

- [>] T-002 TSK-1120 `plugins/meow-prose/agents/prose.md`: the reviewer that
  reads line by line and reports, including comments in code
  closes: REQ-3184, REQ-0999, REQ-1012, REQ-1013, REQ-1014, REQ-1024,
  REQ-1026
  depends: TSK-1110, TSK-1170 - the reviewer reads against the standard
  the skill states, and its prompt is improved with the runner TSK-1170
  builds

- [x] T-003 [P] TSK-1130 a repository's replacement standard in
      `.meowpaw/prose/`
      closes: REQ-1000, REQ-1002
      evidence: a session and the reviewer following a replacement that
      contradicts T6 in a scratch repository, in #50. TSK-1130 carries both.
      depends: TSK-1120 - replacing the standard replaces what the reviewer
      reads, so both the skill and the reviewer must exist to be replaced

- [x] T-004 [P] TSK-1140 `plugins/meow-prose-gate/`: the `PreToolUse` prompt
      hook that blocks a publish
      closes: REQ-3182
      evidence: five candidates on twelve cases, the one that landed blocking
      every covered defect and no clean text, in #93. TSK-1140 has the table.
      depends: TSK-1110, TSK-1170 - the gate's criteria are drawn from the
      rewritten standard, and they are improved with the runner TSK-1170
      builds

- [x] T-005 TSK-1150 retire `tools/check_prose.py` and name the unit in
      `CLAUDE.md`
      closes: REQ-3186, REQ-1671
      evidence: the check deleted, `CLAUDE.md` naming the unit, and
      `meow-prose` enabled at user scope, in #52. TSK-1150 carries the output.
      depends: TSK-1120 - removing the pattern check before the reviewer ships
      would leave this repository with nothing holding the standard

- [x] T-006 [P] TSK-1160 a stated size budget for every shipped unit, and the
      check that measures it
      closes: REQ-1050, REQ-1056, REQ-1057, REQ-1058, REQ-1060
      evidence: every unit within its stated budget, the check failing a probe
      over one, in #96 and #93. TSK-1160 carries the output.
      depends: TSK-1120, TSK-1140 - a budget covers what a unit loads, and the
      three units have to exist before anything can be measured against one

- [x] T-007 [P] TSK-1170 replace the `meow-core` case set with one that
      discriminates, and build the loop every prompt is improved with
      closes: REQ-3024, REQ-3030, REQ-3036
      evidence: `tools/loop.py` on Sonnet 5 judged by Opus 5.5, five runs per
      arm: four cases that each separate the arms, the baseline at +0.04, and
      a deliberately worse candidate losing at -0.31. TSK-1170 carries the
      tables, in #60.

- [ ] T-008 TSK-1180 measure `meow-prose`: routing first, then what it says,
      then improve the skill through the loop
      closes: REQ-3032
      depends: TSK-1110, TSK-1170 - it measures the skill, and it grades with
      the conventions the repaired case set settles

- [ ] T-009 TSK-1190 rewrite the `meow-core` style and fragment against the
      standard, each improved through the loop against what it replaces
      closes: REQ-0956
      depends: TSK-1110, TSK-1170 - the rewrite follows the standard, and a
      case set scoring 1.00 in both arms cannot see whether it helped

- [ ] T-010 TSK-1200 the reviewer reads the unit's own material
      closes: REQ-1115, REQ-1674, REQ-1676
      depends: TSK-1120 - the reviewer is what reads it, and the skill and the
      documentation page it reads land in TSK-1110

- [x] T-011 [P] TSK-1210 run the suite locally, at release and on a new model
      closes: REQ-3038
      evidence: `mise run eval` on Sonnet 5 and again on Haiku 4.5, each with
      its table, in #61. `all` runs no model.
      depends: TSK-1170 - a runner for a suite that cannot discriminate spends
      a model call on every run and reports nothing

## Coverage

ADR-1010 addresses forty requirements. Thirty-nine land in exactly one task
above and one is deferred below, and `tools/check_coverage.py` compares the decision's `addresses` against the
union of the tasks' `closes`, failing on a requirement in neither or in two.

The smallest subset that tests the decision is T-001 and T-002. With those two
closed, a repository installs `meow-prose`, loads the standard before it
writes, and gets a line-by-line review of what it wrote, which is the claim
ADR-1010 makes. T-004 adds the gate, T-005 removes the mechanism the decision
replaces, and T-006 to T-011 make the cost and the effect measurable.

T-007 comes first. It has no dependency, and every prompt in this epic is
improved with the loop it builds, so the loop exists once and is not rebuilt in
each task that uses it. The thing measurable before the epic finishes is T-009's
delta against the current `meow-core` style, on the case set T-007 repairs.

## Not covered

`.claude/skills/commits/`, the repository's own skill for commit messages. It
retires into `meow-scm` once that unit is specified, and it goes through the
loop there, because a prompt improved here would be replaced before it
shipped.

REQ-3034 asks for the suite to run on a schedule and at release. The owner
decided that no CI job makes a model call, and a schedule needs a runner nobody
is watching, so T-011 builds a local task run at release and on a new model,
and the scheduled half waits for a decision about where a scheduled run would
live. T-011 does not close REQ-3034, because closing it would claim the
schedule exists.

Licence headers, which REQ-1008 and REQ-1016 to REQ-1022 govern. ADR-1010
leaves them out, because they ask whether a header of a declared form is
present, which `reuse` settles.

How the reply shape reaches a session. BUG-1040 is open and routes to design,
and T-009 changes what the style says without changing how it arrives, so its
measurement selects the style explicitly in both arms.

SPC-1020 states REQ-3022, REQ-3026 and REQ-3028, which no decision addresses.
TSK-1050 already applied all three, and T-007 and T-009 keep applying them, but
this epic closes none of them, because a task closes only what its authorising
record addresses.

The budget numbers themselves. ADR-1010 leaves them to the first measurement,
so T-006 sets each one from what it measured and records how.
