---
id: RES-0038
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# How the harness reports to the person

## Summary

Every mechanism this method has against an unearned answer acts on artifacts,
and none of them reaches the reply the person actually reads. So the shape of a
report is a mechanism, and no preference, it belongs in the kernel because a
rule some plugins follow shapes nothing, and the platform's output style is
what enforces it. The worked evaluation read here is also the corpus's one
example of a measured change, with its own weaknesses stated.

Research for the shape of every reply the harness makes to a human: what the
first line carries, how a multi-step run states where it is, and how a failure
is worded. It covers the mechanism the platform provides, the measured effect of
shaping output this way, and the rules that survive contact with an agent
harness.

It does not cover the English inside an artifact, which is
[RES-0027-prose.md](RES-0027-prose.md), nor what a status command computes, which
is [RES-0062-status.md](RES-0062-status.md). The distinction is the point: the
writing standard governs what is written to a file, and nothing yet governs what
is said in the terminal.

## The question

The harness's own failure is an unearned answer delivered with the confidence of
an earned one ([RES-0001-synthesis.md](RES-0001-synthesis.md)). Every mechanism
against it so far acts on artifacts: evidence expires, a gate is a stop, an
unresolved verb is never a pass.

None of it reaches the sentence the person actually reads. A run can gather
correct evidence and record it honestly, and then report it in a paragraph that
opens with "Great question, let me look at that" and closes with "let me know
if you need anything else". At that point the person skims, misses the one
unresolved verb, and approves. The gate held and the report leaked.

So: is the shape of a reply a matter of taste, or is it load-bearing, and if it
is load-bearing, where does it live?

## Method

We fetched and read the published material on 2026-09-20, including one
project's ten rules for reply shape and the evaluation that measured them. That
evaluation used a case set, a weighted rubric, several trials, a judge grading
blind on labels shuffled per case, and a published delta.

That evaluation is the only measurement in this corpus that anyone else
performed, and we carry its stated weaknesses, smoothing over none: low trial
count and a judge from the same family as the candidate.

No evaluation was run here. Nothing in this document is measured by this
project.

## Findings

### None of the six internal harnesses shapes a reply

Searched for reply-shaping rules across all six `CLAUDE.md` files. Two matches,
neither relevant: `vlie` uses "closing" about a ticket, and `meowary` asks that
root-level guidance be kept concise, which is a rule about the harness's own
files, and says nothing about its output. No `output-styles/` directory exists
in any of the six.

All six govern what is written to disk. Not one governs what is said. That is
the gap this document exists for, and every public harness surveyed has it
except one. `kiro` ships a `caveman-activate.js` terse-mode ruleset, which
targets context cost where this rule targets the person reading
([RES-0003-external-harnesses.md](RES-0003-external-harnesses.md)).

### The platform provides a first-class mechanism, and a trap inside it

Claude Code has **output styles**: a Markdown file with front matter that
replaces the instructions sent with every request. They live at
`~/.claude/output-styles`, `.claude/output-styles`, or the managed settings
directory, **and a plugin can ship them in an `output-styles/` directory**.

Four properties decide the design:

1. `keep-coding-instructions` defaults to **false**, and a custom style
   therefore _removes_ the built-in software engineering instructions: how to
   scope changes, write comments and verify work. A style written to fix the
   wording of a report would silently delete the platform's verification
   guidance. For this harness the field is `true` or the style is a defect. 2.
   `force-for-plugin: true` applies a plugin's style whenever the plugin is
   enabled, overriding the person's own `outputStyle` setting. A base principle
   is what that field is for, and it is also a plugin overruling a human
   preference, which needs a decision somebody takes, where a default would
   decide it by accident. 3. The platform re-states a non-default style during
   the conversation. Style drift over a long session is the obvious failure,
   and the platform already solves it for any style that is not Default. 4. A
   style does not reach a subagent, which runs its own system prompt. Only a
   fork inherits it. Everything dispatched through `meow-review` and
   `meow-loop` ([RES-0016-delegation.md](RES-0016-delegation.md)) reports in
   the default shape unless its own prompt says otherwise.

The built-in **Concise** style already leads with the result and skips preamble,
and keeps the full content of error reports, security warnings and confirmations
of destructive actions. The exception list is the interesting part: the platform
reached the same conclusion that brevity must not be allowed to eat a failure.

### Shaping the reply measurably improves correctness as well as length

`i-have-adhd` is the largest published instance of this idea: 49,000 stars, ten
rules, shipped for seven agent harnesses, adapted from _The Adult ADHD Tool Kit_
by Ramsay and Rostain. Its value here is that **it was measured**, which is rare
for anything to do with tone.

Its eval suite runs 14 cases over 3 trials on Claude Opus 4.8, scoring
correctness, autonomy, actionability, safety and concision from 1 to 5, with a
judge that grades blind on shuffled condition labels. Against the unshaped
baseline:

| Dimension     | Weight | Delta                            |
| ------------- | ------ | -------------------------------- |
| Correctness   | 35%    | +0.190                           |
| Autonomy      | 25%    | +0.405                           |
| Actionability | 20%    | +0.714                           |
| Safety        | 10%    | +0.024                           |
| Concision     | 10%    | +1.143                           |
| **Weighted**  |        | **+0.427** (4.473 against 4.045) |

Ten wins, two ties, two losses. **Blocking findings fell from seven to three.**

Two results matter more than the headline. First, correctness rose. The
assumption under test was that constraining the shape of a reply costs
accuracy, and on this evidence it does not. Second, **the gains concentrate
exactly where this harness lives**: `multi-step-progress` at +2.53 and
`error-report` at +2.40 were the two largest, and cases with an explicit output
contract were unchanged. A method built from a nine-step chain with a gate
after each step is almost entirely multi-step progress and error reports.

The suite then **failed its own release gate** over a rule permitting no
blocking findings, and published that. A source that reports its own gate
failing has earned more weight than one that does not.

The caveats are its own: three trials, single-case variance above 0.90, and a
judge from the same model family as the candidate.

### Which rules survive an agent harness, and which are for a chat window

The ten rules were written for an assistant answering a person. Read against a
harness that executes, four transfer unchanged, three transfer with their
meaning changed, and three fight something this repository already decided.

Transfer unchanged:

- _Lead with the next action._ The command, the path and the line go first. -
  _Matter-of-fact failure._ No "uh oh". Cause, location, fix. This is the
  wording of the faithful-reporting rule, which already calls a report omitting
  a failure or a skip a defect, and no rounding. - _No preamble, no recap, no
  closers._ Announcing what you are about to do, then doing it, then restating
  it, spends three turns of a person's attention on one fact. - _Suppress
  tangents._ Finish the first thing, offer the second as a question.

Transfer with the meaning changed:

- _Restate state every turn._ In a chat window this compensates for a reader's
  working memory. Here it is the same obligation as `/meow:status`, and the
  correct form is "step 4 of 9, task 3 of 7 verified, one verb unresolved" -
  computed from the artifacts, and remembered never
  ([RES-0062-status.md](RES-0062-status.md)). The platform's own advice agrees:
  where a plan tool exists, the checklist does the restating and the prose does
  not repeat it. - _End with one concrete next action._ At a gate this is not a
  courtesy. A gate that stops without naming the command that resumes it is a
  gate people route around, and a routed-around method reports process it did
  not perform ([vision.md](../vision.md)). - _Specific time estimates._ For an
  agent the estimate belongs to whoever executes the step. The rule's own
  escape clause says so.

Fight something already decided:

- _Cap lists to five items._ Presentation only, and the rule says so twice. A
  verification report lists every verb, a review lists every finding
  worst-first ([RES-0061-review.md](RES-0061-review.md)), and a gap list is a
  deliverable ([RES-0037-onboarding.md](RES-0037-onboarding.md)). Truncating
  any of those is the unearned answer again. - _Number multi-step tasks, using
  the fewest steps that still work._ The second half is a method claim, and
  this method already answers it: routing decides how much process work gets,
  and trivial work skips the chain
  ([RES-0053-discover.md](RES-0053-discover.md)). A shape rule must not get a
  vote on scope. - _Ask before acting._ Its own sixth exception concedes this:
  inside a harness, do the work, because asking "want me to" spends a turn.
  Worth naming, because it is the rule most likely to be copied across and
  quietly reintroduce a question at every step, which is the failure a gate
  exists to make rare and deliberate.

### The escape clauses are the load-bearing part

Six stated exceptions: an explicit request to explain, a destructive action
ahead, a debug spiral, real ambiguity, a rule that would delete the answer, and a
rule that fights the harness. The last two generalise to one sentence: **the
constraint wins, the shape stays.**

A shape rule with no escape clause is worse than none, because the first time
it costs an answer somebody switches the whole rule off. That is the argument
the prose gate already makes about a check that trips on the wrong thing
([RES-0027-prose.md](RES-0027-prose.md)).

The pre-send check is the other reusable piece, and it runs mechanically.
Delete an opening sentence that announces intent, a closing sentence that asks
"anything else", a "by the way" sidebar, a hedging adverb carrying no
information, and an idiom. Then one test - **if the reader reads only the first
line and the last line, do they know what to do next and what just happened?**

Note the fourth item's own limit: keep a hedge that carries real uncertainty,
because deleting it manufactures confidence. That is this harness's failure
mode stated from the other direction, and it is why a brevity rule needs
supervision here, where praise would only entrench it.

## Conclusions

1. The shape of a report is a mechanism, and no preference. It is the last
   stage of every honest-failure rule already written, and the only one
   currently unguarded. 2. It belongs in the kernel, because it applies to
   every reply of every plugin, and a rule that some plugins follow shapes
   nothing. 3. An output style is the mechanism, shipped from `meow-core`, with
   `keep-coding-instructions: true`. Whether it also sets `force-for-plugin`
   trades a base principle against a person's own setting, and somebody decides
   that, where a default would decide it by accident. 4. Subagent prompts must
   carry the shape themselves, since a style does not reach them. 5. The
   transferable rules are the four unchanged ones plus state restatement and
   the next action at a gate, and `/meow:status` computes the state
   restatement, recalling none of it. 6. Completeness outranks brevity, stated
   explicitly, so that no item of a verification report, a review or a gap list
   is ever dropped for shape. 7. The escape clauses ship with the rules, and
   the shortest statement of them is that the constraint wins and the shape
   stays. 8. This harness adopts the pre-send check verbatim, including its own
   limit on deleting hedges. 9. This is measurable. A suite of cases, a rubric,
   a blind judge on shuffled labels, and a published delta is a better model
   for evaluating a harness change than an opinion, and the harness has nothing
   like it yet.

## Sources

All read 2026-09-20.

- [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) - the ten rules,
  the six exceptions and the pre-send check, read from
  `skills/i-have-adhd/SKILL.md`; 49,000 stars and 245 commits; credited as
  adapted from _The Adult ADHD Tool Kit_ by Ramsay and Rostain.
- [i-have-adhd evals](https://github.com/ayghri/i-have-adhd/tree/main/evals) -
  the rubric, the case set and `RESULTS.md`: 14 cases, 3 trials, Claude Opus 4.8,
  weighted 4.473 against 4.045, per-dimension deltas, 10 wins against 2 losses,
  blocking findings 7 to 3, the `multi-step-progress` and `error-report`
  concentration, and the failed release gate.
- [Claude Code output styles](https://code.claude.com/docs/en/output-styles) -
  the file locations, the front matter fields including
  `keep-coding-instructions` and `force-for-plugin`, the plugin
  `output-styles/` directory, the mid-conversation restatement of a non-default
  style, the fact that a style does not apply to a subagent, and the built-in
  Concise style with its exception list.
- `~/workspace/{meowctl,meowg1k,vlie,hephaestus,meowhub,meowary}/CLAUDE.md` -
  searched for reply-shaping rules; none found, and no `output-styles/`
  directory in any of the six.
