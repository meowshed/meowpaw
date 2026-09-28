---
id: RES-0309
artifact: research
status: approved
revised: 2026-09-28
elaborates: RES-0070
---

# A requirement recorded as verified can still be unmet, and a reader who didn't do the work finds part of what the checks miss

## Summary

Passing checks leave a measurable share of requirements unmet. A study of 877
plausible patches on SWE-bench Verified found 29.6% behaving differently from
the developers' own fix, and this repository has four defect records that each
found a requirement an epic had already recorded as verified, out of 755
requirements it derives as verified. In every one of the four, the check that
closed the requirement couldn't fail, or the behaviour broke on an input no
check exercised. In one benchmark, a model monitoring agents for deliberate
test exploitation caught 86% to 89% of it on single-function tasks, and 42% to
65% on multi-file ones depending on the model. That is a different miss from
an untested input, so the rates are an analogy, and they illustrate that an
independent reader adds detection and proves nothing. The verify
step today judges its own evidence in the session that implemented the work,
which RES-0070 found biased. This note covers whether verification needs a
second reader and what that reader has to ask; it doesn't cover which model
runs it, beyond the one comparison the monitoring study reports.

## The question

Should the method, after the verify step finds an epic's criteria met, have an
agent that didn't do the work try to refute each requirement the epic claims,
and what would that agent ask?

The question assumes that the verify step's existing judgement, "would
this check fail if its requirement were violated", fails often enough to
justify a second reader. If verification already caught
these cases, a second reader would only add cost, so the findings below test
that assumption first.

## Method

The owner asked the question on 2026-09-28. I read the abstracts and results sections of two papers on 2026-09-28, the
first through the arXiv abstract page and the second through its HTML
rendering, and quoted each number from the text. I read the four defect
records in `project/bugs/` that name a requirement another epic had verified,
and matched each to that epic's `checked-at` in `project/epics/`. I read
`plugins/meow-flow/skills/run/SKILL.md` and
`plugins/meow-flow/skills/method/steps/verify.md` on `main` after #622.

I counted the requirements the record derives as verified with
`plugins/meow-flow/bin/paw status` on `main` after #622, which printed
`1103 in force: 755 verified`, and read how each of the four defects was found
from its record and the change that filed it.

I tried to observe on this machine that a subagent defined with `tools: Read,
Grep, Glob` can't run a shell command, by starting a nested Claude Code 2.1.280
session with permissions bypassed. The session's permission classifier refused
to start it, so that behaviour rests on the platform's documentation as
RES-0263 records it, and not on an observation. Conclusion 3 depends on it.

I found no measurement of how often a refutation by a second model is wrong,
so the cost of a false refutation is unmeasured.

## Findings

### Passing tests leave about three in ten plausible patches behaving differently from the intended fix

Wang, Pradel and Liu tested 877 plausible patches from three issue-solving
tools on SWE-bench Verified. The benchmark's validation counts 7.8% of all
patches as correct while they fail the developer-written test suite. Their
differential testing tool, PatchDiff, found 29.6% of plausible patches
behaving differently from the ground truth, and manual inspection found 28.6%
of those behaviourally divergent patches certainly incorrect. Together these
inflate reported resolution rates by 6.2 percentage points. PatchDiff finds
the divergences by having a model write tests aimed at the difference, which
is a second reader looking for the input the original tests never tried. It
runs those tests, so its evidence is a run and not a reading.

### A model monitoring for shortcuts catches most on small tasks and between two in five and two in three on multi-file ones

ImpossibleBench gives agents tasks whose specification and tests conflict, so
any pass is a shortcut. Monitors built on Claude Sonnet 4 and Claude Opus 4
detected 86% to 89% of those shortcuts on single-function tasks; the paper
gives that range for the monitors together. On multi-file SWE-bench tasks the
Sonnet 4 monitor detected 42% to 50% and the Opus 4 monitor 57% to 65%, so
Sonnet 4 missed about half and Opus 4 about two in five. The authors found
shortcuts in the unflagged transcripts that evaded detection. RES-0075
already records the same benchmark's cheating rates; this finding adds only
the monitors' detection rates. The benchmark measures how often a monitor
detects deliberate exploitation, on tasks built so that any pass is one. A
refuter here looks for honest misses, a check that can't fail or an input
nobody exercised, and nothing shows the rates carry over from one to the
other, so they are an analogy at best.

### Four verified requirements in this repository turned out unmet

Each of these defect records names a requirement an epic had recorded as
verified:

| Defect   | Verified in, under | Found                  | What the checks missed                                            | How it was found                                                       |
| -------- | ------------------ | ---------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------- |
| BUG-1170 | EPC-1160, #237     | 2026-09-26             | A trace script matched no row, printed "0 found" and exited 0     | Reading the run's output after #238 merged; the record doesn't say who |
| BUG-1180 | EPC-1210, #288     | 2026-09-26, after #403 | A task entry carrying `[P]` was never read, so it derived as open | `paw show` reporting a task open that its epic marks done              |
| BUG-1210 | EPC-1310, #378     | 2026-09-27, after #507 | A task without the optional `issue:` field never had one written  | Projecting TSK-2240 and TSK-2250, which lacked the field, for real     |
| BUG-1250 | EPC-1100, #202     | 2026-09-28, after #621 | An epic with no tasks made `status` and `ready` disagree          | `status` naming a step for EPC-1590 that `ready` refused               |

BUG-1170 is a check that couldn't fail, the case the verify step's own rule
V8 asks about. The other three are inputs the requirement's text covers and no check
exercised: an entry with a mark, a missing optional field and an empty list.
The verification that recorded each requirement verified didn't ask about
those inputs.

These numbers support the assumption the question rests on only in part.
Verification missed four of the 755 requirements the record derives as
verified, about one in 190. That count is a floor, because it holds only the
misses somebody has found. Ordinary later work found all four within days,
with no second reader, by using the program or reading its output. So the
record shows that V8's judgement misses cases, and not that it misses them
often enough for a second reader to pay for itself.

### Two records this note builds on

RES-0063 found that two harnesses independently made their analysis command
read-only, because a command that both detects and resolves a divergence
resolves it by rewording the specification. One of them states why: deciding
whether the code or the specification is wrong is a judgement someone has to
make. RES-0263 found that an agent definition's `tools` field is an allowlist,
and that an agent holding no tool that writes or runs commands can't change
what it judges, which enforces a read-only rule an instruction only describes.

### Verification runs in the session that did the work

`/meow-flow:run` loads the method skill and runs each step in the one session,
implement and verify alike, so the judgement rule V8 asks for is the
implementer's judgement of its own checks. RES-0070 found 17 of 20 models
judging their own output with a significant bias, strongest on open-ended
tasks, and uncorrected by capability. The method already dispatches a fresh
agent, `record-reviewer`, to review each record it writes, and nothing does the same
for the claim that the work meets its requirements.

### A second reader has costs this note can't weigh against its gain

Three arguments stand against adding the reader, one cheaper option competes
with it, and one choice inside it stays open:

- It costs one more dispatch on every epic verification, which reads the
  epic's requirements, checks and code. The repository running the method pays
  for it in time and tokens, and nothing above measures what it would have
  saved.
- A false refutation still costs a round: the verifier runs or reads what the
  refutation names, finds nothing, and records why. I found no measurement of
  how often that happens, so the cost is unknown in both size and frequency.
- A refuter from the implementer's model family may share its blind spots.
  RES-0070 measured bias in judging one's own output, and not whether a second
  instance of the same model misses the same inputs, so nothing here says how
  much independence a same-family refuter adds.
- The two questions in conclusion 2 could go into rule V8 of the verify step,
  asked by the session that did the work, with no second agent. The four
  defects above are misses of a question nobody asked, so the questions alone
  might have caught them, and this note can't separate the effect of the
  questions from the effect of who asks them.
- A refuter that writes and runs tests, as PatchDiff does, arrives with a run
  that shows the break, and three of the four defects are inputs a run would
  have exercised. A refuter that only reads needs the verifier to run what it
  names. The cost of running is a tool that runs commands, and RES-0263 found
  the allowlist enforces read-only only where the agent holds no such tool, so
  a refuter with one can change the work it judges. Nothing here measures
  which of the two finds more, so this note leaves the choice to the decision.

What favours a separate agent over a sharper V8 is RES-0070's measurement that
a model judging its own output is biased and that capability doesn't correct
it, and not the four defects. A sharper V8 still leaves the implementer
judging its own checks.

## Conclusions

1. Before an epic's verification is recorded, an agent that didn't produce
   the work tries to refute that each requirement the epic's authorising
   record addresses is met, because RES-0070 measured the bias of a model
   judging its own output and verification missed four such requirements
   here. The case rests on the bias more than on the four,
   which ordinary work found anyway, and a decision taking this conclusion has
   to weigh the costs in the last finding.
2. That agent asks of each requirement whether each check closing it would
   still pass against a wrong implementation. It also asks whether the
   behaviour meets the requirement's text on each input the text covers, such
   as an absent optional field, an extra mark and an empty list. These are the
   two ways the four defects above got past verification, and the questions
   are worth asking whether or not a second agent asks them.
3. A refutation names the input or condition that breaks the requirement, so
   the verifier can confirm it by running or reading, because a refutation
   nobody can reproduce is an opinion. Whether the refuter runs the command
   itself, or reads and leaves the run to the verifier, is the trade-off the
   last finding weighs, and a tools allowlist without a shell is what keeps a
   read-only refuter from running commands (RES-0263).
4. A refutation the verifier confirms is recorded as a defect, because
   evidence that a requirement isn't met is what a defect record holds. Its
   triage is left to a person, because deciding whether the work or the
   requirement is wrong is the judgement RES-0063 keeps out of verification.
5. A requirement the agent didn't refute is reported as not refuted, never as
   proven met, because a reader who finds no break has shown only that it
   found none. The monitors in the benchmark illustrate this: they missed
   between 35% and 58% of the shortcuts on multi-file work, on a different
   kind of miss.

## Sources

- [Are "Solved Issues" in SWE-bench Really Solved Correctly? An Empirical Study](https://arxiv.org/abs/2503.15223), read 2026-09-28 -
  by You Wang, Michael Pradel and Zhongxin Liu, submitted 2025-03-19 and
  revised 2025-09-09: the 7.8%, 29.6%, 28.6% and 6.2-point figures, and
  PatchDiff as a model writing tests aimed at a divergence.
- [ImpossibleBench: Measuring LLMs' Propensity of Exploiting Test Cases](https://arxiv.org/html/2510.20270), read 2026-09-28 -
  by Ziqian Zhong, Aditi Raghunathan and Nicholas Carlini, submitted
  2025-10-23, read in its HTML rendering: monitor detection of 86-89% on
  Impossible-LiveCodeBench for both monitors, and on Impossible-SWEbench
  42-50% for Sonnet 4 and 57-65% for Opus 4.
- BUG-1170, BUG-1180, BUG-1210 and BUG-1250, read 2026-09-28 on `main` after
  #622, with the `checked-at` of EPC-1160, EPC-1210, EPC-1310 and EPC-1100 -
  the four verified requirements found unmet.
- The method's driver and verify step, read 2026-09-28 on `main` after #622,
  at `plugins/meow-flow/skills/run/SKILL.md` and
  `plugins/meow-flow/skills/method/steps/verify.md` - verification running in
  the implementing session, and rule V8.
- `plugins/meow-flow/bin/paw status`, run 2026-09-28 on `main` after #622 -
  755 requirements derived as verified.
- RES-0070, read 2026-09-28 - self-preference in 17 of 20 models.
- RES-0075, read 2026-09-28 - the same benchmark's cheating rates, which this
  note doesn't repeat.
- RES-0263, read 2026-09-28 - the `tools` allowlist in an agent definition,
  and a reviewer without write tools being unable to change what it judges.
- RES-0063, read 2026-09-28 - two harnesses keeping analysis read-only, and
  the judgement of which side is wrong left to a person.
