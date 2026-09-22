---
id: TSK-1180
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes: [REQ-3032]
issue: 55
---

# Measure `meow-prose`: routing first, then what it says, then improve it

One task, one branch, one pull request, one review.

## What to do

Build `plugins/meow-prose/evals/` and measure routing before content
(REQ-3032). A skill nobody loads has no effect to measure, and the fix for poor
routing is the description, so the first question is whether the skill fires
on natural phrasing: "write the commit message", "draft the pull request
body", "add a comment here", with no mention of a standard.

Then measure what the skill says, in two arms, with and without it, on texts
where the standard's defects appear without it: a bold fragment standing in for
a heading, a counted opener, a proverb with its reason missing, an American
spelling.

Draw the content cases from the criteria table TSK-1110 publishes, so every
rule and pattern the skill states is measured and not a sample of them. Seed
each case from the examples in the appendix of ADR-1010: the failing example
gives the writing task, and the corrected one shows the grader what passes.
The standard's own self-review counts become graders that cost nothing:
sentences over 35 words, "rather than" and "instead of" per 500 words,
paragraphs opening in bold per section, and its list of words to search for. A
pattern here grades a measurement and enforces nothing, so REQ-3186 does not
reach it.

Follow the conventions TSK-1170 settles: the cheapest grader first, a
threshold per case, and regression read from the delta.

Then improve the skill and its description with the runner TSK-1170 builds, with the skill as
TSK-1110 shipped it as the baseline. Each candidate changes one thing: a rule
cut, a rule reworded, an example removed, the description rephrased. A
candidate lands when the delta holds or rises and the token cost falls, and a
better score at a higher cost is published with both numbers for the owner to
decide. A change to the description reruns the routing cases as well as the
content cases, because the description is what routes.

## Depends on

TSK-1110, because it measures the skill, and TSK-1170, because it grades with
the conventions the repaired case set settles.

## Evidence

Not yet. The task closes on the routing rate per phrasing with its threshold,
then the content delta per case, both with the run count and the judge named.
A routing rate below threshold is reported with the change to the description
that raised it, or as unmet. The loop's table follows, one row per candidate
with its delta, its token cost and whether it landed, including the ones that
lost.

## Left alone

The reviewer's and the gate's prompts, which TSK-1120 and TSK-1140 measure and
improve on their own labelled sets.
