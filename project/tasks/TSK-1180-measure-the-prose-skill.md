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

In progress. Routing is measured and meets its threshold: the description
ADR-1050 states loads the skill in 36 of 36 writing runs on Sonnet 5 and 33 of
33 on Opus 5.5, on eleven phrasings including a one-line commit message, and in
no run that only changes code. TSK-1270 carries the table.

Content is measured on six cases under `plugins/meow-prose/evals/write-*`, each
a writing task where the standard's defects appear without the skill, with a
threshold each in `thresholds.toml`. The free graders are regexes for bold
openers, counted openers, hype and judging words and American spellings; a
judge reads only what needs reading. `tools/loop.py`, five runs per arm, judged
by Opus 5.5, so every judged score is a smoke check (REQ-3028):

| Candidate | Model    | Change                                    | Delta | 2SE  | Tokens | Verdict             |
| --------- | -------- | ----------------------------------------- | ----- | ---- | ------ | ------------------- |
| baseline  | Sonnet 5 | the skill as TSK-1110 shipped it          | +0.11 | 0.09 | 4,544  | baseline            |
| C1        | Sonnet 5 | S2 asks for paragraphs, never bold labels | +0.15 | 0.06 | 4,590  | landed by the owner |
| baseline  | Opus 5.5 | the skill as TSK-1110 shipped it          | +0.29 | 0.08 | 4,544  | baseline            |
| C1        | Opus 5.5 | S2 asks for paragraphs, never bold labels | +0.31 | 0.05 | 4,590  | landed by the owner |

C1 scores higher at 46 more tokens, so the owner decided, and landed it. On
Sonnet 5 the baseline wrote pull request descriptions under bold labels such as
`**What changed**`, the pattern the standard forbids, in three runs of five,
and C1 took that case from 0.65 to 1.00. `write-commit-message` scores 1.00 in
both arms on both models and `write-code-comments` on Sonnet 5, so neither
discriminates yet. `write-explanation` on Sonnet 5 sits at 0.73 against its
threshold of 0.75.

Two faults in the instrument were found and fixed before these numbers: the
judge failed a text for opening with a Markdown title, and the eval's sandbox
refused the unit's reads of its own supporting files. `tools/loop.py` now
grants each unit `Read` on its own directory, and takes `--tag` so the
reviewer's classifier cases and these content cases run apart.

Eight more cases cover the rule groups the first six left out: steps with a
warning and a condition (A1, A2, B3), acronyms and times (H6, H7), idioms (H2),
a proposal's reader and headings (E2, F1), a code example (G2), a reply to a
reviewer (T2, S3), a bug report (S2) and plain verbs (D1, D4, D5). On all
fourteen, with the skill as #100 left it:

| Candidate | Model    | Change                                                     | Delta | 2SE  | Verdict  |
| --------- | -------- | ---------------------------------------------------------- | ----- | ---- | -------- |
| baseline  | Sonnet 5 | the skill on `main` after #100                             | +0.15 | 0.04 | baseline |
| C2 and C3 | Sonnet 5 | headings state what a section says; every acronym expanded | +0.16 | 0.05 | lost     |
| baseline  | Opus 5.5 | the skill on `main` after #100                             | +0.24 | 0.04 | baseline |
| C2 and C3 | Opus 5.5 | headings state what a section says; every acronym expanded | +0.25 | 0.05 | lost     |

C2 and C3 were first measured one at a time on the skill before #100. C2 raised
Opus 5.5's design proposal from 0.48 to 0.92 and C3 raised Sonnet 5's incident
summary from 0.50 to 1.00, and on those numbers I recommended both. Measured
together on the current skill, the overall deltas moved by 0.01, inside twice
their standard error, and the two case gains fell to 0.60 to 0.76 and 0.50 to
0.60, while other cases fell by as much: how-to steps on Opus 5.5 from 0.80 to
0.60, the pull request on Sonnet 5 from 1.00 to 0.80. At five runs one case
moves by 0.2 through noise, so the first gains were at least partly noise. The
owner dropped both, and SPC-1020 now reads a candidate from its overall delta.

The token column in these runs is unreliable: the same `SKILL.md` measured
3,281 tokens in one arm and 6,713 in another. A verdict of "costs no less" in
the loop's own table rests on that column, so none of the verdicts above does.

Still open: the patterns have no content cases of their own, and
`write-commit-message`, `write-onboarding-note` and `write-plain-verbs` score
the same with and without the skill on both models, so they cannot yet show a
change. The task closes when the patterns have cases and those three are
replaced by cases that discriminate.

## Left alone

The reviewer's and the gate's prompts, which TSK-1120 and TSK-1140 measure and
improve on their own labelled sets.
