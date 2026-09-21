---
id: SPC-1000
artifact: spec
status: live
revised: 2026-09-21
checked-at: "#27"
states:
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
---

# The reply shape

## Scope

The reply shape covered here is the shape of every reply the harness makes to a
person: what the first line carries, how a report states where a run has got
to, how a failure is worded, and what a reply must never open or close with. It
also covers the kernel's obligation to carry that shape, and the fragment that
carries it into a subordinate agent.

Read the writing standard in `CLAUDE.md` for the English inside an artifact,
because the shape governs the terminal and the standard governs the file. Verb
resolution, the names of the harness's not-working states, and what a status
command computes are all settled elsewhere and left out here.

`meow-core` implements this, and EPC-1000 closed at #27 with one
criterion unmet: the style applies when a person selects it and not on its own,
which BUG-1040 records. REQ-0930 is unmet until that is resolved.

## Boundary

What is observable from outside the part:

| Surface                                | What it is                                                                       |
| -------------------------------------- | -------------------------------------------------------------------------------- |
| `plugins/meow-core/output-styles/*.md` | The style file the platform loads, with its YAML front matter                    |
| `keep-coding-instructions`             | Set to true, so the platform's engineering guidance survives                     |
| `force-for-plugin`                     | Set to true, and not honoured on Claude Code 2.1.278; see BUG-1040               |
| The shape fragment                     | A file in `meow-core` that any unit includes in a subordinate agent's prompt     |
| The style check                        | A check that reads the front matter and the rules, and fails with a named reason |

Everything behind those surfaces is prose loaded into a context window, and no
program reads it.

## Behaviour

The kernel carries the shape, so a repository installing any part of the
harness receives it (REQ-0932), and no plugin, skill or step is exempt
(REQ-0930).

Those two sentences state the obligation, and the harness does not yet meet
it. On Claude Code 2.1.278 the style applies only when a person selects it,
because `force-for-plugin` is not honoured, which BUG-1040 records with its
reproduction. The shape is therefore opt-in per session and REQ-0930 is unmet,
until the platform honours the field or a decision replaces the mechanism.

A reply leads with the action: the command, the path or the line, and prose
follows if it is needed at all (REQ-0934). A reply does not open by announcing
what it is about to do (REQ-0944), does not close by recapping what it did
(REQ-0946), and does not close by offering further help (REQ-0948).

A reply reporting progress states which step of how many, what is pending and
what is unresolved, and it computes that from the artifacts (REQ-0936). Where
the record holds nothing to compute from, the reply says so and states nothing
it cannot support.

A reply reporting a failure gives the cause, the location and the fix
(REQ-0938), and no expression of dismay precedes it (REQ-0940). Where a step
stops, the reply names the command that resumes it (REQ-0942).

Completeness outranks brevity (REQ-0950). No verb leaves a verification report,
no finding leaves a review, no question leaves a gap list, and no hedge
carrying real uncertainty is deleted. Where a rule of shape would delete part
of an answer, the answer wins and the shape yields (REQ-0952).

Every rule ships the condition under which it yields (REQ-0931), and the rules
and their conditions are in one table in ADR-1000.

Before sending, the harness runs the pre-send check (REQ-0933). The check
deletes an announcing opening, a closing offer of help, a sidebar, and a hedging
adverb carrying no information. It keeps a hedge that carries real uncertainty,
because deleting that one manufactures confidence. It then asks whether the
first line and the last line tell a reader what to do next and what just
happened.

A subordinate agent runs its own system prompt and the style does not reach it,
so the prompt a unit sends to one carries the shape itself (REQ-0954).

## Changing the shape

A change to any rule here is measured against the shape it replaces before it
lands: a stated case set, a rubric, several trials, and a judge grading blind
on labels shuffled per case (REQ-0956). The case set lives in
`plugins/meow-core/evals/`, and a measurement reports the number of runs it
used and the judge that graded it.

A result that contradicts the decision is reported as it stands, and the
measurement is not repeated until it agrees.

## Failure paths

| Condition                                                  | What happens                                                                                     |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `keep-coding-instructions` is false or absent              | The style check fails, naming the field and the file, and the gate stops                         |
| A rule is stated with no condition under which it yields   | The style check fails, naming the rule                                                           |
| A person has selected their own output style               | Nothing overrides it: the style is applied only when somebody selects it, which BUG-1040 records |
| A unit dispatches a subordinate agent without the fragment | The subordinate answers in the platform's default shape, which is a defect against REQ-0954      |
| A reply has nothing in the record to compute progress from | The reply states that, and states no step count it cannot support                                |
| The shape would require dropping a verb or a finding       | The shape yields and the item stays (REQ-0952)                                                   |
