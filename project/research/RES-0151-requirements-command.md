---
id: RES-0151
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0028, RES-0052
---

# `/meow:requirements`

## Summary

The step that turns approved research into requirements, and the approval that
matters most because everything downstream cites these identifiers. The finding
that transfers whole is bounded clarification: at most a few questions,
everything else defaulted with the default recorded, and the self-validation
loop capped - because the failure mode of a tireless asker is an interrogation
and an uncapped loop converges by exhaustion.

The second step of the chain. It takes approved research and produces
requirements, and stops for approval - the approval that matters most, because
everything downstream cites these identifiers.

Its siblings are [RES-0052-chain.md](RES-0052-chain.md) and
[RES-0152-design-command.md](RES-0152-design-command.md).

## Who has an equivalent

| Harness        | Command             |
| -------------- | ------------------- |
| spec-kit       | `specify`           |
| cc-sdd         | `spec-requirements` |
| harness4claude | `write-spec`        |
| meowctl        | `/spec`             |
| vlie           | -                   |

## Method

The surveyed harnesses' own command templates and the internal repositories'
commands were read on 2026-09-20 for what a comparable command does, and the
platform's command documentation was fetched for the frontmatter fields the
surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against comparable
commands, and none of it is an observation.

## The finding that transfers whole: clarification is bounded

spec-kit's `specify` is the only one in the survey that **bounds its
clarification**. At most three `[NEEDS CLARIFICATION]` markers, with
instructions to make informed guesses using industry defaults for everything
else, and a validation loop capped at three iterations against a generated
checklist of ten criteria.

The bound exists because the failure mode of a tireless asker is an
interrogation. An agent that can ask will ask, and an agent that asks about
everything it is uncertain about produces a session the person abandons.

It pairs with open-question classification: a question that blocks nothing is
recorded with a default chosen, and nobody is asked. So the three markers are
reserved for questions where proceeding under either answer would produce
different work.

The validation cap is the other half. Three iterations against a checklist, and
then the artifact is what it is. Without a cap, a self-validating loop either
converges by exhaustion or runs until the budget does.

## What a requirement has to be, which is settled elsewhere

The ten criteria spec-kit generates - no implementation details, testable
requirements, measurable success criteria - are a weaker version of the
properties already adopted from ISO/IEC/IEEE 29148 and recorded in
[RES-0028-requirements.md](RES-0028-requirements.md). This command applies
those; it does not redefine them.

The two that bite hardest in practice, because they are the ones a generated
requirement fails:

One obligation per requirement. A requirement with two `MUST` clauses
cannot be cited by one check, and cannot be withdrawn in half.

It stands alone. A requirement that says _that command_ or _such a record_
depends on its neighbour, which breaks as soon as either moves. Sixteen
requirements in this corpus were written that way and had to be rewritten.

## Identifiers are allocated here, and that is why approval matters

An identifier is permanent once cited. So the approval at this step is not
approving prose; it is approving a set of names that the design, the
specification, every epic and every task will refer to for the life of the
project.

Two consequences for the command.

It does not renumber. An identifier allocated in an earlier run keeps its
number even if the requirement is rewritten, and a withdrawn requirement leaves
a gap that nothing reuses.

It allocates from a block with gaps, so a requirement added later to an
existing topic sits beside its topic, and never at the end of the corpus.

Both were learned by getting them wrong: this corpus has allocated the same
identifier twice, in two separate blocks, and the check that would have caught
the first one printed the duplicate without failing.

## What it must refuse

A requirement with no citation upstream. Every requirement cites the research
whose conclusions it comes from, and the relation may be many-to-many: one
requirement can elaborate several research documents, and one research
conclusion can produce several requirements.

A requirement that states a mechanism and no obligation, because a mechanism is
a decision and belongs in the design step.

A prohibition written as a negated requirement. _No X MUST Y_ reads under RFC
2119 as negating a requirement, and it prohibits no behaviour; the form is _X
MUST NOT Y_. Twelve requirements here were written the first way and had to be
corrected.

## Conclusions

1. Clarification is bounded to a small number of questions, and everything else
   is defaulted with the default recorded as a choice. 2. A question that
   blocks nothing is not asked, it is answered and recorded. 3. Self-validation
   is capped, so the loop terminates by design, and never by exhaustion. 4.
   Each requirement carries exactly one obligation, so one check can cite it
   and it can be withdrawn whole. 5. Each requirement stands alone, naming its
   own subject, and referring to no neighbour. 6. Every requirement cites the
   research it comes from, and the relation is many-to-many in both directions. 7. Identifiers are permanent, allocated from blocks with gaps, never reused
   and never renumbered. 8. A duplicate identifier fails the check, and no
   report softens it, which this corpus learned by allocating one twice. 9. A
   prohibition is written as `MUST NOT`, never as a negated requirement. 10. A
   statement of mechanism is refused and referred to the design step. 11. The
   command refuses on missing or unapproved research and stops after producing.

## Sources

All read 2026-09-20.

- [github/spec-kit `specify.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/specify.md)
  - the at-most-three `[NEEDS CLARIFICATION]` budget, informed guesses with
    industry defaults, the ten-criteria checklist and the three-iteration
    validation cap.
- [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) - requirements written in
  EARS form as a structured alternative.
- `~/workspace/meowctl/.claude/commands/spec.md` - the stopping point stated as
  "do not implement, do not create a branch, do not open an issue".
- [RES-0028-requirements.md](RES-0028-requirements.md) - the 29148 properties
  this command applies, including one obligation per requirement and
  standing alone.
