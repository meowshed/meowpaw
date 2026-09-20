---
id: RES-0070
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Who verifies, and what each can see

## Summary

The method contained a contradiction: one requirement said everything that
verifies anything goes through the five verbs, while several others required
judgements no verb can make. Four verifiers exist rather than one - a verb, an
agent's judgement, a person's judgement and a measured evaluation - and each
sees what the others cannot. The measured findings are that seventeen of
twenty models show significant self-preference, that capability does not
correct it, and that position bias is large and judge-dependent.

Research for a contradiction in the method. One requirement says everything
that verifies anything goes through the five verbs; several others require
judgements that no verb can make, and six requirements declare themselves
verified by a recorded evaluation.

It covers what each kind of verifier can and cannot see, what is measured about
agents as judges, and what the check vocabulary is missing. It does not cover
what the three verification activities are, which is
[RES-0067-checking-the-record.md](RES-0067-checking-the-record.md),
[RES-0068-verifying-a-task.md](RES-0068-verifying-a-task.md) and
[RES-0069-verifying-an-epic.md](RES-0069-verifying-an-epic.md).

## The question

The five verbs are mechanical. They run a command and report an exit status,
and what they cover is whatever a program can settle.

The method also demands things no program settles. Whether a check would have
failed had the requirement been violated. Whether a document mixes two kinds.
Whether a rule states its reason, and whether the work is well made. And it
demands one thing that is neither: a measurement against a case set with a
rubric and a judge.

So: how many kinds of verifier are there, what can each see that the others
cannot, and what does the harness have to say about the ones that are not
programs.

## Method

Two studies were fetched and read on 2026-09-20 for the measured figures on
self-preference and position bias, including their sample sizes and the
direction of each effect.

The inspection figures that circulate widely were pursued and not obtained: the
primary study was not readable and the lecture material carrying them could not
be reached. They are recorded in the document as reported and unverified rather
than repeated as fact, and the mechanism they illustrate is attested
separately.

The corpus's own declaration counts - how many requirements declare each
verification method - were computed from the requirement files rather than
estimated.

## Findings

### The method already contains three, and one requirement forbids two of them

Stated plainly, so the contradiction is visible:

| Requirement                                                                                                           | Says                           |
| --------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| Everything that verifies anything goes through the five verbs                                                         | mechanical only                |
| A requirement is checkable by a static check, a behavioural fixture or a recorded evaluation                          | three kinds                    |
| The half of the writing standard that requires judgement must be a review criterion and must not be made into a check | judgement is not a check       |
| Verification judges whether each check would actually fail                                                            | a judgement                    |
| Review assesses conformance and quality as two separate judgements                                                    | judgements                     |
| Where the harness reviewed its own work it reports the change as unreviewed by a human                                | a human is a distinct verifier |

The first forbids the rest. It was written about the mechanical part and
generalised past its evidence.

The vocabulary is short by one. Every requirement declares which of three
checks verifies it, and across the corpus that is 309 static, 288 behavioural
and 6 evaluation. **None declares itself verified by judgement**, although the
standard requires that some are.

### Inspection finds classes of defect that no test can

The oldest measured result here is Fagan's. The figures circulate widely. 38
defects per thousand lines found by inspection against 8 by unit test, and 82%
of the total defects found for the released product. A detection rate of 60% to
80% for a properly run inspection against 40% to 60% for an engineer working
alone, and a session limit of about 100 lines before the rate falls.

Those numbers are recorded here as reported. The primary source was not
readable, and by this method's own rule a figure taken from a secondary source
is marked unverified rather than repeated as fact.

What is not in doubt, and does not depend on the numbers, is the mechanism: an
inspection can find a defect for which dynamic testing is not applicable at
all. A missing explanatory comment, an omission from a specification that is
invisible at runtime, an inconsistency that never produces a wrong answer.
Nobody can write a test for the absence of something nobody specified, and a
reader notices it in a sentence.

The session limit matters as much as the rate. Effectiveness falls with the
size of what is in front of the reader, which is the same finding that drives
small pull requests and small tasks, arriving from a different direction.

### An agent judging its own work is measurably biased, and capability does not fix it

Self-preference bias is a directional deviation in which a model systematically
favours or disfavours its own output when evaluating. It is measured by
comparing how often a model picks its own response among pairs of equal
quality against its baseline preference when judging third parties.

Across twenty mainstream models the effect ranges from -0.229 to +0.307, and
seventeen of the twenty show a statistically significant bias. Eight favour
themselves, nine disfavour themselves, three are neutral.

Two findings make this harder to design around than it first appears.
Capability does not correct it: advanced ability is uncorrelated with low
bias and sometimes negatively correlated, and models with stronger reasoning
sometimes show _more_ self-preference. And **open-ended tasks trigger stronger
bias than structured ones**, which is exactly the shape of a code review.

The paper names the worst case precisely: a judge combining strong
discriminability with pronounced bias, where capability masks evaluative
unfairness.

### Position bias is large, judge-dependent, and not noise

A study across 15 judges, 2 benchmarks, 22 tasks, roughly 40 solution-producing
models and more than 150,000 evaluation instances measured the tendency to
favour a solution by where it sits in the prompt.

Position bias is not due to chance and varies significantly across judges and
tasks. The quality gap between the solutions strongly affects it; the length
of the prompt components affects it only weakly. The choice of judge model has
the largest influence of the factors examined.

The practical consequence is narrow and useful: a comparison whose order is
fixed is a comparison whose result is partly the order. Shuffling per case, and
concealing which side is which, is not rigour for its own sake.

### An evaluation is a third thing, and it has a shape

The one worked example this project has read in detail is a measured change to
reply shape, and it is built the way the literature prescribes. A fixed case
set, a rubric with weighted dimensions, several trials per case, a judge that
grades blind on labels shuffled per case, and a published delta with its
caveats.

Its own stated weaknesses are the ones to carry: three trials left single-case
variance above 0.9, and a judge from the same model family as the candidate is
a weaker judge than a cross-family one.

An evaluation is therefore not a check that passes or fails. It produces a
distribution and a comparison, and using one as a gate means deciding what
delta counts before running it.

### What each verifier can see

| Verifier             | Sees                                                                                        | Cannot see                                                             |
| -------------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| A verb               | What a program can settle: syntax, types, a failing assertion, a broken link                | Whether the assertion could have failed; whether anything is missing   |
| An agent's judgement | Omissions, mixed kinds, unstated reasons, inconsistency - at speed, across the whole corpus | Its own bias, which is measurable and which capability does not remove |
| A person's judgement | The same, plus whether the work should exist                                                | More than about a hundred lines at a sitting before the rate falls     |
| An evaluation        | Whether a change moved a measured outcome                                                   | Anything about one instance; it is a distribution                      |

## Conclusions

1. Four verifiers exist, and not one. A verb, an agent's judgement, a person's
   judgement and a measured evaluation, and each sees what the others cannot. 2. Only the mechanical part goes through the verbs. The rule that everything
   goes through them was written about the mechanical part and generalised past
   its evidence; it is narrowed rather than kept. 3. The check vocabulary gains
   a fourth value. A requirement verified by judgement declares that, so the
   corpus can report how much of itself rests on judgement rather than leaving
   it uncounted. 4. A judgement is declared, never disguised as a check. A
   check that encodes a judgement fires on the wrong thing and is disabled,
   which loses both the check and the judgement. 5. An agent MUST NOT judge its
   own work. Seventeen of twenty models show significant self-preference, the
   effect is strongest on open-ended tasks, and capability does not correct it. 6. A judge is not told which side it produced, and where that cannot be
   arranged the result is reported as self-assessed rather than as a judgement. 7. Order is controlled in any comparison. Position bias is large,
   judge-dependent and not noise, so the order is shuffled per case and the
   judge does not see a fixed one. 8. A cross-family judge is stronger than a
   same-family judge, and where the same family is used that is recorded as a
   limitation of the measurement. 9. An agent's judgement does not substitute
   for a person's. It is faster and it covers more, and it cannot answer
   whether the work should exist. 10. A person's judgement has a rate limit.
   Effectiveness falls with the size of what is reviewed, which is why the work
   arrives in small pieces and not only because small pieces merge sooner. 11.
   An evaluation is a measurement rather than a pass. Using one as a gate means
   stating the delta that counts before running it, and recording the variance
   and the judge's family alongside the result. 12. Inspection is not redundant
   with testing. It finds defects for which no test can be written, starting
   with everything that is missing.

## Sources

All read 2026-09-20.

- [Quantifying and mitigating self-preference bias of LLM judges](https://arxiv.org/html/2604.22891v4)
  - the definition as a directional evaluative deviation; measurement by
    comparing selection of one's own output among equal-quality pairs against a
    third-party baseline; a range of -0.229 to +0.307 across twenty models with
    seventeen statistically significant; that capability is uncorrelated or
    negatively correlated with low bias; that open-ended tasks trigger stronger
    bias; and the judge combining discriminability with pronounced bias.
- [Judging the judges: a systematic study of position bias in LLM-as-a-judge](https://arxiv.org/abs/2406.07791)
  - 15 judges, 2 benchmarks, 22 tasks, roughly 40 solution-producing models and
    more than 150,000 instances; that position bias is not due to chance and
    varies across judges and tasks; that the quality gap strongly affects it and
    prompt length weakly; and that the judge model is the largest factor.
- Fagan inspection figures - 38 defects per thousand lines by inspection
  against 8 by unit test, 82% of total defects, 60% to 80% detection against
  40% to 60% for an individual, and a session limit near 100 lines - are
  **recorded as reported and treated as unverified**. The lecture material
  carrying them was not readable, and the primary study was not obtained. The
  mechanism they illustrate, that inspection finds defects for which dynamic
  testing is not applicable, is separately attested in the same material.
- [RES-0038-reporting.md](RES-0038-reporting.md) - the worked evaluation this
  project read in full: a case set, a weighted rubric, several trials, a judge
  grading blind on labels shuffled per case, a published delta, and its own
  stated weaknesses of low trial count and same-family judging.
