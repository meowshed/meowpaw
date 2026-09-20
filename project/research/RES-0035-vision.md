---
id: RES-0035
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# The vision, and how many living documents there are

## Summary

A project needs a document saying what it is and where it is going, kept
current. Three such documents exist where this project expected one: the
vision, the constitution and the specification. All three are projections over
records and none carries its own history. The specification is project-level
and epics update it, and nobody writes one per epic, and a decision that
contradicts the vision means one of the two is stale.

Research for a central document describing what a project is and where it is
going, kept current. It covers what such a document contains, what makes it stay
alive, and what its existence does to the claim that the specification is the
only living artifact. It does not cover the specification's own contents.

## Method

The published material on vision and briefing documents was fetched and read
on 2026-09-20, including the working-backwards process, for what such a
document is expected to contain.

The internal repositories were read for which of the three documents each
already keeps, which is how we counted three and assumed nothing.

Nothing was run. The claim that a vision which cannot be read in one sitting is
not a north star is a judgement stated as one.

## The claim it breaks

The earlier decision
said the specification is the only living document and everything else is a
record. A vision is unarguably living - it changes as the project's
understanding of itself changes - and it is unarguably not a specification.

So the claim was too narrow. The correct generalisation is not "one living
document" but **living documents sit at altitudes where the present matters more
than the history**, and there are three of them.

## The three altitudes

| Document          | Answers                                             | Changes when                             |
| ----------------- | --------------------------------------------------- | ---------------------------------------- |
| **Vision**        | What is this, for whom, why, and where is it going? | The understanding of the problem changes |
| **Constitution**  | How do we work here, and what is non-negotiable?    | A principle is added or retired          |
| **Specification** | What must the system do, now?                       | A decision changes what is required      |

All three are projections over the records. The vision is a projection over
everything learned about the problem; the constitution over decisions about
method; the specification over requirements in force. None of them carries its
own history, and all three are rewritten freely, because the history is in the
research, the decisions and the requirements.

Two of the three already existed in the design - the constitution is in the
profile, the specification is a step. The vision is the missing one.

## The precedent: Amazon's PR/FAQ

The strongest external case for a living vision is the press-release-and-FAQ
narrative Amazon has used since 2004 for Kindle, Prime, AWS and Alexa.

Its properties transfer:

- **Written from the future.** A one-page press release dated at launch,
  announcing the product as though it exists. This forces a statement of what
  someone will actually get, in their words, where a list of intentions says
  nothing. - **It is the starting point for everything else** - "the key
  document in the product discovery process... the starting point for all other
  product documents and mockups". - **It is a north star for shared
  understanding**, which is the job a vision does that no other artifact does:
  it is what people agree on before they can usefully disagree about anything
  smaller. - **It stays living after approval**: "once approved by the
  leadership team, [it] will almost certainly still be edited and changed". The
  approval is not the end of the document. - **Internal and external FAQs are
  separate** - what a customer would ask, and what a stakeholder would ask
  about feasibility, cost, risk and metrics.

The six-page limit does not transfer literally; what it encodes is that a
vision that cannot be read in one sitting is not a north star, because nobody
re-reads it.

## The internal example

`meowhub`'s `docs/product/vision.md` is a working instance and its shape is
better than most templates:

- **What it is** - two paragraphs, including what its predecessor was and _why
  it was replaced_: "nexus costs too much to own - it spends the admins'
  evenings on infrastructure, and those evenings should go into scenarios
  instead."
- **Problem** - the pain, named at the moment it happens: "the expense happens
  at the till, phone in one hand and bag in the other, so there's no time for
  six fields."
- **Who it is for** - a table of audiences with what each wants and _why they
  would open it at all_, which is the question most audience sections skip.
- Then the deliberate asymmetry the product is built on, stated as a choice
  with a reason.

Two things it does generalise. It names **what it will not trade away** - "this
household wants both halves and won't trade either one away" - which constrains
what the project may trade away, where an aspiration constrains nothing, and it
is what settles a later argument. And it is **written about a real situation**,
so every claim in it is falsifiable by the people it describes.

`meowctl`'s repository-level statement is the same idea at a smaller scale, and
`vlie`'s README carries a comparison table against the alternatives it means to
replace, which is a vision statement in the form of a claim someone could
disprove.

## What makes a vision rot, and what stops it

The failure is not that a vision becomes wrong. It is that it becomes
unfalsifiable - a page of ambitions nobody could disagree with, which
therefore settles no argument and gets read once.

Three properties keep it alive, and all three are observable:

1. It names who it is for and what they would otherwise do. An audience with
   no alternative is not an audience.
2. It names what it will not do. A vision with no non-goals cannot be cited
   against a proposal, and a vision that never rejects anything is decoration.
3. It is revised when a decision contradicts it. This is the mechanism: a
   decision record that conflicts with the vision means one of the two is stale,
   and the conflict is visible because both are written down.

The third is what makes it a step somebody runs, where a habit is forgotten.
`/meow:decide` can ask whether the decision sits inside the vision, and that
question is cheap because the vision is short.

## Where it lives, and what this does to the specification

The vision is **project-level**, and no unit of work owns a copy. And once that
is said, the specification's level has to be settled too, because it has the
same property: "what the system must do now" is a statement about the system,
not about one unit.

This corrects a loose end in the previous design. A unit of work produces
research, requirements, decisions, an epic and reports - all records, all
per-unit. What it _does_ to the specification is **update it**, in place, at
project level. `meowctl`'s `docs/spec/<component>.md` is exactly this: one
living specification tree for the whole system, elaborated by many units over
time.

So the layout divides by artifact kind, and each document declares its
lifetime, which no path implies. One artifact is one file, named for its
identifier - a directory per unit of work would put a living specification
inside a per-unit folder, which is the arrangement this section argues against:

```text
CLAUDE.md                     living    the constitution
project/vision.md             living    what this is, where it is going
project/specs/SPC-NNNN-*.md   living    what the system must do now
project/research/RES-NNNN-*.md          what was read
project/requirements/R-*.md             one obligation per file
project/adrs/ADR-NNNN-*.md              why it is like this
project/epics/EPC-NNNN-*.md             one authorising record, decomposed
project/tasks/TSK-NNNN-*.md             one task, one branch, one pull request
project/bugs/BUG-NNNN-*.md              where it is not
```

Each record names its unit of work in its front matter and never in its path,
so you find a record by what it says and never by the week somebody wrote it.

## Conclusions

1. Three documents live, and not one: the vision, the constitution and the
   specification. All are projections; none carries its own history. 2. The
   specification is project-level, and epics update it where nobody writes one
   per epic. 3. The vision names its audiences, their alternatives, and its
   non-goals. 4. A vision that cannot be read in one sitting is not a north
   star. 5. A decision that contradicts the vision means one of them is stale,
   and the decision step asks. 6. Approval does not freeze it. A living
   document is edited after approval; that is what living means.

## Sources

All read 2026-09-20.

- [The Amazon Working Backwards PR/FAQ process](https://workingbackwards.com/concepts/working-backwards-pr-faq-process/)
  and [Working Backwards: how to write an Amazon PR/FAQ](https://docs.superhuman.com/@colin-bryar/working-backwards-how-write-an-amazon-pr-faq)
  - the six-page narrative, the press release written from a future date, the
    internal and external FAQ split, and the north-star framing.
- [Working Backwards: the Amazon PR/FAQ for product innovation](https://medium.com/@smwii/working-backwards-the-amazon-pr-faq-for-product-innovation-f7cafeaff574)
  - that the document remains living and edited after leadership approval.
- [An insider look at Amazon's culture and processes](https://www.aboutamazon.com/news/workplace/an-insider-look-at-amazons-culture-and-processes)
  - Working Backwards as the process behind Kindle, Prime, AWS and Alexa.
- `~/workspace/meowhub/docs/product/vision.md` - the internal worked example:
  what it is, the problem at the moment it happens, the audience table with
  alternatives, and the stated refusal to trade either half away.
- `~/workspace/meowctl/docs/spec/README.md` - a project-level specification tree
  elaborated by many changes over time, which is the arrangement this document
  argues the specification should have.
