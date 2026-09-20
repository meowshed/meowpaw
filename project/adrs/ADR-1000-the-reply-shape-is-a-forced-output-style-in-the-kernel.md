---
id: ADR-1000
artifact: adr
status: draft
revised: 2026-09-21
unit: U-0001
addresses:
  [
    REQ-0930,
    REQ-0931,
    REQ-0932,
    REQ-0933,
    REQ-0934,
    REQ-0936,
    REQ-0938,
    REQ-0940,
    REQ-0942,
    REQ-0944,
    REQ-0946,
    REQ-0948,
    REQ-0950,
    REQ-0952,
    REQ-0954,
    REQ-0956,
  ]
supersedes: []
---

# 1000. The reply shape is a forced output style carried by the kernel

## Decision

The kernel is a plugin named `meow-core`, and it ships the reply shape as an
output style in its own `output-styles/` directory. The style sets
`keep-coding-instructions: true`, so it adds a shape and removes none of the
platform's engineering guidance. It sets `force-for-plugin: true`, so the shape
applies wherever `meow-core` is enabled and a person's own output-style setting
does not switch it off.

The style carries eight rules, and every one of them ships the condition under
which it yields:

| Rule                                                          | Yields when                                             |
| ------------------------------------------------------------- | ------------------------------------------------------- |
| Lead with the command, the path or the line (REQ-0934)        | The person asked for an explanation                     |
| Report a failure as cause, location and fix (REQ-0938)        | Never; a failure always carries all three               |
| Open a failure without dismay (REQ-0940)                      | Never                                                   |
| Open with no preamble (REQ-0944)                              | A destructive action needs confirming first             |
| Close with no recap and no offer of help (REQ-0946, REQ-0948) | A stop must name the command that resumes it (REQ-0942) |
| State progress as computed, never as recalled (REQ-0936)      | Nothing in the record has a state to compute            |
| Keep every verb, finding, question and real hedge (REQ-0950)  | Never; this rule is what the others yield to (REQ-0952) |
| Run the pre-send check (REQ-0933)                             | Never; it is the last act before sending                |

The pre-send check deletes an opening sentence announcing intent, a closing
sentence asking whether anything else is wanted, a sidebar, and a hedging
adverb carrying no information. It keeps a hedge that carries real uncertainty,
because deleting that one manufactures confidence. It then asks one question:
does a reader who reads the first line and the last line know what to do next
and what just happened?

An output style reaches a fork and never a subordinate agent, so `meow-core`
also ships the same rules as a prompt fragment, and every unit dispatching a
subordinate agent includes it (REQ-0954).

A change to any of this is measured before it lands: a stated case set, a
weighted rubric, several trials, and a judge grading blind on labels shuffled
per case (REQ-0956).

## Why

Everything this method does against an unearned answer acts on an artifact.
Evidence expires, a gate stops the run, and an unresolved verb is never a pass.
The sentence a person actually reads is guarded by none of them. A run can
gather correct evidence and then report it in a paragraph that opens with a
pleasantry and buries the one unresolved verb in the middle, and the person
skims it and approves (RES-0038).

The shape of a reply is therefore the last stage of every honest-failure rule
already written, and it is the only stage nothing guards. A shape that some
plugins follow guards nothing at all, because the report that hides the
unresolved verb is the report that gets approved. REQ-0930 states the rule as
unconditional and REQ-0932 puts it in the kernel, and `force-for-plugin` is the
only field the platform offers that holds a style without asking each person to
opt in.

We did not measure this, and somebody else did. A published suite of 14 cases
over 3 trials, judged blind, scored a shaped baseline at 4.473 against 4.045,
with correctness up 0.190 and blocking findings down from seven to three. Its
two largest gains were multi-step progress at +2.53 and error reports at +2.40,
which is most of what a nine-step chain with a gate after every step produces.
We carry that source's own weaknesses: three trials, single-case variance above
0.90, and a judge from the same model family as the candidate.

## Alternatives

| Option                                        | Better at                                                        | Why it lost                                                                                          |
| --------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| An output style with `force-for-plugin: true` | Holding for every reply of every unit, with no per-person opt-in | Chosen                                                                                               |
| An output style a person selects              | Leaving the person's own setting in charge                       | REQ-0930 admits no exemption, and a shape one can switch off is off in the report that most needs it |
| The rules written into `CLAUDE.md`            | Costing nothing to ship and reading in the repository            | It reaches one repository, drifts between copies, and is what the six harnesses here already do      |
| A rule in each unit that produces a report    | Letting a unit word its own reports                              | It leaves every future unit free to forget, which is the failure REQ-0930 names                      |
| Do nothing                                    | Costing nothing now                                              | The gap is measured and specific: no harness surveyed here shapes a reply, and reports leak          |

## What it costs

A plugin overrules a person's own preference. Somebody who set an output style
deliberately finds it replaced whenever `meow-core` is enabled, and their only
recourse is to disable the kernel, which takes the rest of the harness with it.
We accept that cost knowingly, because a rule holds unconditionally only if it
also holds when the person would rather it did not.

It also costs the platform's default engineering guidance if the style is
written carelessly, since `keep-coding-instructions` defaults to false. The
field is set to true here, and a check enforces it, because the failure is
silent.

## What would reverse it

Either of two conditions, each observable:

- A repository disables `meow-core` in order to escape the style, and says so.
  The style has then become a reason to drop the kernel, and a dropped kernel
  costs more than an unshaped reply.
- A measurement run to the standard REQ-0956 sets shows the shape scoring below
  the unshaped baseline on correctness. Concision losing is not a reversal,
  since REQ-0950 already subordinates it.

## Consequences

- A plugin directory exists for the first time: `plugins/meow-core/`, carrying
  a manifest, a version and an `output-styles/` directory.
- Every unit dispatching a subordinate agent carries the shape fragment in the
  prompt it sends, and a unit that forgets is a defect against REQ-0954.
- The harness gains its first evaluation: a case set, a rubric and a blind
  judge, which REQ-0956 requires before any later change to the shape.
- A static check reads the style's front matter and fails when
  `keep-coding-instructions` is anything other than true, or when a rule ships
  with no stated exception (REQ-0931).

## How we will know it was realised

We write these observations now, so that whoever verifies the epic reads them
and does not invent them:

1. A repository with `meow-core` installed and no other unit receives the
   shape, and `/output-style` shows it in force without the person selecting
   it.
2. The static check fails on a style whose `keep-coding-instructions` is false,
   and passes on the one shipped.
3. A subordinate agent dispatched by any shipped unit answers in the shape,
   which is checked against a case that dispatches one.
4. The evaluation runs, publishes a weighted delta against the unshaped
   baseline, and states its trial count and its judge.

## What this does not settle

- How a verb resolves, and what the harness's not-working states are called.
  REQ-2774 names six of them and is deliberately left to the decision that
  creates verb resolution.
- What `/meow:status` computes. REQ-0936 obliges a progress report to be
  computed from the artifacts, and what it computes over is not decided here.
- Whether `meow-core` carries anything else. This decision puts the reply shape
  in the kernel and makes no claim that the kernel is only that.
- The writing standard for artifacts, which governs what is written to a file
  and not what is said in a terminal.
