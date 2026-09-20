---
id: RES-0029
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Research, brainstorming and adversarial review

## Summary

Elicitation is an iterative practice and no interview, and the strongest moves
are about order. Read the repository before asking, and challenge assumptions
before exploring alternatives. Run the red-team pass before implementation,
because afterwards it costs a rewrite. A fixed question set is the fallback
that keeps an out-of-ideas model moving, and a premortem paragraph closes the
design step.

Research for `meow-research`: `/meow:brainstorm`, `/meow:options`,
`/meow:grill`, `/meow:decide`, and the `research` step itself. What elicitation
practice knows, what the agentic harnesses added, and the specific failure a
model brings to all of it.

## Method

The published elicitation material was fetched and read on 2026-09-20 for
the technique catalogue and for the framing of elicitation as iterative.

The internal repositories and the surveyed harnesses were read for the phases
they already name, which is where brainstorming-as-a-phase and the red-team
pass came from.

Nothing was run, and no session was measured. The claim that challenging
assumptions before exploring alternatives changes the outcome is an argument
from the ordering, and no result of ours.

## The failure this exists to prevent

A model asked for a solution produces one. It asks nothing about the
constraint, whether the problem is the stated problem, or what was already
tried. The answer it produces is fluent enough that nobody notices the
questions were skipped.

Everything below is a mechanism for putting a question between the request and
the answer.

## Elicitation, from the discipline that has done it longest

Requirements elicitation is a named practice with named techniques: interviews,
document analysis, interface analysis, observation, prototyping. Two of them
transfer to an agent working in a repository.

Document analysis. The repository already contains the answer to a
surprising share of elicitation questions: the decision records, the existing
requirements, the code's actual boundaries. Asking a human what the system does
before reading what it does is the amateur move, and it is what a model does by
default because reading is expensive and asking is cheap.

Socratic questioning, described in the practice literature as an ancient
technique for uncovering what a stakeholder has not said. The useful families
of question, in the order they pay:

| Question                                                   | Surfaces                                                       |
| ---------------------------------------------------------- | -------------------------------------------------------------- |
| "What makes you say that?"                                 | The evidence behind a stated requirement - often there is none |
| "What would happen if we did nothing?"                     | Whether the problem is worth solving at all                    |
| "What are we assuming is true?"                            | The premise that is about to be wrong                          |
| "Who is hurt by this?"                                     | The constituency nobody in the room represents                 |
| "What would have to be true for the opposite to be right?" | The alternative that was dismissed without examination         |

The **W6H pattern** - who, what, when, where, why, which, how - is the ordered
checklist version, and it serves as a fallback for a model that has run out of
its own questions.

## What the agentic harnesses added

`superpowers` makes brainstorming a _named phase that runs before any code_:
refine the rough idea by asking, explore alternatives, and present the design
in sections for validation, because a finished block gets approved whole. The
sectioning matters - a design presented whole gets approved whole, and a design
presented in sections gets argued with.

`harness4claude` contributes `grill-me`: attack a draft specification from
several angles to surface the edge cases nobody wrote down, _before_
implementation. This is a red-team pass applied to a document, and it is the
highest-value technique here. Finding a missing edge case in a specification
costs a paragraph, and finding it in code costs a rewrite.

It also runs several review dimensions in parallel and then **tries to refute
its own findings** - the same adversarial discipline pointed at itself.

`spec-kit` has an assessment path ending in an explicit verdict: go, needs
clarification, or kill. Naming "kill" as an available outcome transfers
directly; a research step with no negative outcome is a research step that
always recommends proceeding.

## The premortem

The harness survey has none, and this method adds it, because it is the
cheapest known technique for surfacing what a plan assumes: _assume this has
failed; write the story of why._ It works where "what are the risks?" does not.
It removes the social and cognitive cost of predicting failure, because the
failure is already stipulated and only the explanation is being supplied.

For the harness it fits naturally at the end of `/meow:design`, before the gate:
one paragraph on how this design is most likely to be wrong. That paragraph is
also what `/meow:review` should read first when the work comes back.

## Options, and the honest recommendation

`/meow:options` has a specific failure to avoid: the **straw-man survey**, in
which three alternatives are presented, two of them plainly weak, and the
recommendation is the one the model wanted at the start. It looks like
diligence and is worse than a bare recommendation, because it manufactures
consent.

The rules that prevent it:

- Each option is stated in the terms its **advocate** would use, and never its
  critic's. - Each names what it is genuinely better at. An option that is
  better at nothing is no option at all, and it is deleted. - The
  recommendation is explicit, with the condition under which it flips. - "Do
  nothing" is an option and is evaluated, where mentioning it settles nothing.

## When research earns its turn

A research step that always runs produces ceremonial documents for work nobody
had a question about. The routing classes already answer this: L0 has no
research, L1 has research only where the reproduction or the constraint is
unclear, L2 has it.

The other trigger is specific: **research is required when a claim would
otherwise be asserted from memory.** The internal-harness survey found this
repeatedly: a specification written from memory of a format, a parity claim
written from memory of a binary. The rule follows: if the design is about to
say "X does Y", either the research says where that was checked, or it is
checked now.

## Conclusions

1. Read the repository before asking. Document analysis first; questions are
   for what the repository cannot answer. 2. Brainstorming is a named phase and
   presents in sections, because a finished design gets approved whole. 3. A
   fixed question set as the fallback - the Socratic families and W6H - so an
   out-of-ideas model still has somewhere to go. 4. `grill` is a red-team pass
   on the draft before implementation, aimed at edge cases and unwritten
   failure paths. 5. A premortem paragraph closes the design step. 6. Options
   are stated by their advocates, include "do nothing", and end in an explicit
   recommendation with its flip condition. 7. "Kill" is an available verdict. 8. A claim from memory is not a claim - research it or drop it.

## Sources

- [How to conduct effective
  elicitation](https://www.adaptiveus.com/blog/tasks/how-to-conduct-effective-elicitation/)
  and [Top requirement elicitation
  techniques](https://www.theknowledgeacademy.com/blog/requirement-elicitation-techniques/),
  read 2026-09-20 - the technique catalogue, and elicitation as an iterative
  practice that no interview replaces. - [Socratic questioning as a
  requirements elicitation
  tool](https://masteringbusinessanalysis.com/mba180-socratic-questioning/),
  read 2026-09-20. - [Ordering interrogative questions for effective
  requirements engineering: the W6H pattern](https://arxiv.org/pdf/1508.01954),
  read 2026-09-20 - the ordered fallback question set. -
  [obra/superpowers](https://github.com/obra/superpowers), read 2026-09-20 -
  `brainstorming` as a named phase, and presenting a design in sections. -
  [Lharden/harness4claude](https://github.com/Lharden/harness4claude), read
  2026-09-20 - `grill-me`, and `discuss` with its Locked / Deferred /
  Discretion tiers. - [github/spec-kit](https://github.com/github/spec-kit),
  read 2026-09-20 - the assessment path ending in go / needs-clarification /
  kill. - `~/workspace/vlie/.claude/commands/research.md`, read 2026-09-20 -
  challenge assumptions before exploring, at least three alternatives, the
  devil's-advocate step, and revisit conditions.
