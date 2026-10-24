---
id: TSK-4740
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2450
closes: [REQ-2850, REQ-2852, REQ-2854]
issue: 958
projected: b4fe12e389cf
tracked: f22dd4c53730
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Rewrite `project/vision.md` to the template's sections

`project/vision.md` carries the sections SPC-1230 requires, its quality goals
in priority order with ties broken and the risks live now, no dated plan, no
restated requirement and no claim that no requirement makes falsifiable. One
task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given the rewritten vision, when a reader looks for its headings, then it
   carries Who it is for, Quality goals, What it will not do and Risks, and
   Who it is for names what each audience does today instead (REQ-2850,
   REQ-2854). Closed by: a fixture under `plugins/meow-flow/tests/` that reads
   `project/vision.md`'s headings, seen failing first.
2. Given its Quality goals section, when a reader reads it, then the goals are
   numbered in priority order and each pair that could tie says which wins
   (REQ-2850). Closed by: judgement in the pull request's review.
3. Given each claim the vision makes, when a reviewer reads it, then it cites
   no requirement as an obligation and either a requirement in force makes it
   falsifiable or it is gone, and the pull request lists each claim removed
   (REQ-2852). Closed by: judgement in the pull request's review.
4. Given the rewritten vision, when `wc -w` counts its body, then it holds at
   most 2,000 words and no date. Closed by: the command's output in the pull
   request.

## What to do

Rewrite the vision from `paw template vision`, keeping what is true of the
project today. Turn "What it will not trade away" into the ordered quality
goals, and "Where it is going" into a direction with no roadmap and no dates.
Propose the order of the quality goals in the pull request, because ADR-2580
leaves the goals to this rewrite and the owner reads them there.

## Depends on

Nothing.

## Evidence

Criterion 1 is closed by the `Vision` class in
`plugins/meow-flow/tests/test_constitution_vision.py`, which reads the four
headings, seen failing first (REQ-2850, REQ-2854). Criterion 4: the same class
counts 1609 words and finds no date or requirement identifier in the body.

Criteria 2 and 3 rest on judgement, because the order of the goals and
whether a requirement makes a claim falsifiable are read. The pull request
body lists the six goals in order, the claims removed and the reasoning.

Every stage passed in pull request #PR.

## Left alone

The check, which TSK-4750 adds once this rewrite has landed.
