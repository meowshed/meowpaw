---
id: RES-0072
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# The architecture discipline

## Summary

Decisions and requirements carry no structure, so an agent implementing a task
makes every structural choice locally and the shape erodes one reasonable
choice at a time. The standards supply the vocabulary - a viewpoint frames a
concern, and every identified concern must be framed by at least one - and the
evolutionary-architecture literature supplies the split between what a program
can check and what needs judgement. A structural regression is invisible in a
diff by construction, so review is given the structure and not only the change.

Research for a capability the harness carries into three steps: design, where
the shape is chosen; implementation, where it is kept or lost; and review,
where the loss is caught or not.

It covers what an architecture description is made of, which architectural
properties can be checked by a program and which cannot, and what an agent
needs in front of it to keep a structure it did not choose. It does not cover
the obligations a design document carries, which is
[RES-0017-design-lenses.md](RES-0017-design-lenses.md), nor how the
specification divides, which is
[RES-0071-specification-granularity.md](RES-0071-specification-granularity.md).

## The question

The method records decisions and requirements, and neither carries structure. A
decision says what was chosen and why; a requirement says what must be true.
Neither says what the system is made of, how its parts depend on each other, or
which of those dependencies are allowed.

Without that, an agent implementing a task sees a file tree and a requirement,
and every structural choice it makes is made locally. The structure erodes one
reasonable local choice at a time, and the review that would catch it is
reading a diff, which shows no structure.

## Method

The architecture standard, the twelve-section template and the fitness-function
material were fetched and read on 2026-09-20, including the recent extension of
fitness functions to judgement-heavy governance performed by an agent.

Nothing was run, and no architecture description was written and tested here.
The claim that a structural regression is invisible in a diff follows from what
a diff contains, and no experiment tested it.

## Findings

### An architecture description is organised by concern, and every concern is framed

ISO/IEC/IEEE 42010 gives the vocabulary. A **viewpoint** specifies how to
construct one view: it names the stakeholders, their concerns, and the
techniques used. A **view** is the system seen through one viewpoint. The
binding rule is that **every identified concern is framed by at least one
viewpoint**.

That last clause is the checkable part. A concern nobody framed is a concern
nobody described, and the description is incomplete in a way that can be
detected by listing concerns and listing views.

`arc42` turns the same idea into a fixed set of questions: context and scope,
solution strategy, building blocks, runtime, deployment, crosscutting concepts,
decisions, quality requirements, risks, glossary. The building block view is
the most extensive and is hierarchically refined. Crosscutting concepts get
their own section, and nothing scatters them.

For a harness the useful property of a fixed question set is that an unanswered
question is visible. A design with no runtime view has not been shown to work;
a design with no deployment view has not been shown to ship.

### Abstraction levels have names, and mixing them is the common failure

The C4 model names four: system, container, component, code. Each is a
hierarchical abstraction with a diagram at that level, and the model is
deliberately **notation independent and tooling independent**.

The value here is not the diagrams. It is that the levels are named, so a
description can say which level it is at, and a reader can tell when two levels
have been mixed in one picture. A design that jumps from system to code in one
paragraph is the same defect as a document that mixes a tutorial with a
reference, and it is detectable the same way: by naming the level first.

### Some architectural properties are checkable, and treating them as review is waste

Evolutionary architecture's central idea is the **fitness function**: an
objective assessment of an architectural characteristic that must be preserved.
Its stated purpose is to make architectural governance **continuous and
automated rather than episodic and manual**, turning intent into feedback,
where periodic reviews and tribal memory carry nothing.

The taxonomy transfers whole:

| Axis    | Values                                                                     |
| ------- | -------------------------------------------------------------------------- |
| Trigger | Triggered by an event, or continual                                        |
| Result  | Static, a fixed pass or fail; or dynamic, against a shifting definition    |
| Scope   | Atomic, one property; or holistic, emergent behaviour no atomic check sees |

The holistic case is the one that bears on this method directly: a system can
pass every atomic check and fail under combined conditions. That is the same
shape as an epic whose tasks all pass while the decision goes unrealised.

Recent work extends this to judgement-heavy governance - boundary fidelity,
decision drift, semantic contract checks - performed by an agent alongside the
fixed gates. That maps onto the four verifiers already established: some
architectural properties are verbs, some are an agent's judgement, and the
split is the same one.

### What erodes a structure is a sequence of locally reasonable choices

The failure to design against is not a bad decision. It is a hundred small ones
made by whoever was closest to the code, each defensible, none aware of the
shape.

Three things make the shape present at the moment of the choice, and all three
are cheap:

- **The parts are named**, so a file belongs to something. - **The allowed
  dependencies are stated**, so an import is either permitted or is a finding
  that nobody argues about. - **The level is named**, so a change can be said
  to be at the component level, and the argument never drops to the code level.

Without the second, every dependency question is a debate. With it, most are a
check.

### Review needs the structure in front of it

A review reads a difference against a recorded base. A structural regression is
invisible in a diff by construction: nothing in the changed lines says the
import crossed a boundary, because the boundary is not in the file.

So a review that is meant to catch structure has to be given the structure. In
practice that means the reviewer is told which parts the change touches, which
dependencies it adds, and which of those the architecture permits - and the
first two are computable.

## Conclusions

1. The harness carries an architecture description organised by concern, and
   the file layout organises nothing. Its parts are the ones the project
   declared for the specification, so the project has one structure and never
   two. 2. A fixed set of questions is answered, and an unanswered one is
   visible. Context, building blocks, runtime, deployment, crosscutting
   concerns: a design that omits one has not been shown to work at that level. 3. Every concern the design identifies is framed by at least one view, and a
   concern nothing frames is reported and never assumed covered. 4. The
   abstraction level is named before the description is written, and a
   description does not mix levels, for the same reason a document does not mix
   kinds. 5. Allowed dependencies between parts are stated, and nothing is left
   implied. An import that crosses a boundary the architecture forbids is a
   finding nobody argues about, which is what makes it checkable. 6. An
   architectural property that can be checked is checked, and review spends no
   attention on it. Governance is continuous and automated where it can be; a
   property left to periodic review is a property that erodes between reviews. 7. A property that cannot be checked is a declared judgement, made by an
   agent where it can be and by a person where it cannot, under the same rules
   as any other judgement. 8. Holistic properties are separate from atomic
   ones. A system can pass every individual check and fail under combined
   conditions, so a passing set of atomic checks is not an architectural pass. 9. Implementation is told the structure as well as the task. The parts it
   touches and the dependencies it may use are inputs to the work, and it
   infers nothing from the file tree. 10. Review is given the parts touched and
   the dependencies added, because a structural regression is invisible in a
   diff by construction. 11. The description is notation independent. What is
   fixed is the levels and the questions; how they are drawn is decided
   separately.

## Sources

All read 2026-09-20.

- [ISO/IEC/IEEE 42010 architecture description](https://quality.arc42.org/standards/iso-42010)
  and [its conceptual model](http://www.iso-architecture.org/42010/cm/) -
  viewpoints as specifications for constructing a view, naming stakeholders,
  concerns and techniques; and the rule that every identified concern is framed
  by at least one viewpoint.
- [arc42 overview](https://arc42.org/overview) - the fixed set of twelve
  sections, the building block view as the most extensive and hierarchically
  refined, and crosscutting concepts as a section of its own.
- [The C4 model](https://c4model.com/) - the four hierarchical abstractions of
  system, container, component and code, and the model's deliberate
  independence from notation and tooling.
- [Agentic fitness functions, extending evolutionary architecture](https://www.infoq.com/articles/agentic-fitness-functions-evolutionary-architecture/)
  and [Fitness functions, safeguarding architecture with automated checks](https://www.continuous-architecture.org/practices/fitness-functions/)
  - the fitness function as an objective assessment of a characteristic that
    must be preserved; governance as continuous and automated rather than
    episodic and manual; the trigger, result and scope axes; the holistic case
    where a system passes every atomic check and fails in combination; and the
    extension to judgement-heavy governance performed by an agent.
