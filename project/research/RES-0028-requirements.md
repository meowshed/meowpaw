---
id: RES-0028
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Writing requirements

## Summary

Four notations compete, and none of them is an alternative to the others. The
standard supplies the quality properties, and keyword prose suits a constraint
that always holds. The structured syntax suits triggered and conditional
behaviour, including a pattern for unwanted behaviour that most requirement
sets omit. Of the standard's properties, three are the ones actually
enforceable - singular, implementation-free and verifiable - and each
requirement names its own verification method rather than relying on a
preamble.

Research for the `requirements` step and the identifier and traceability rules
in `meow-flow`. Four notations compete, they are not interchangeable, and the
standards body has already said what makes a requirement good.

## Method

We fetched and read the published material on 2026-09-20. The structured syntax
came from its author's site and the encyclopedia summary. The requirements
standard came through the descriptions of it that are publicly readable,
because the standard itself was behind a paywall.

The limitation: the quality properties used throughout this corpus are taken
from secondary descriptions of a paid standard. They are consistent across the
descriptions read, and none was checked against the normative text.

The internal repositories were read for how requirements are written there
today. Nothing was run.

## What makes a requirement good

ISO/IEC/IEEE 29148 lists the properties, and this corpus takes them verbatim,
because they are the accumulated answer to decades of unusable specifications.
A requirement should be **necessary, implementation-free, unambiguous,
consistent, complete, singular, feasible, traceable, verifiable, affordable and
bounded.**

Three of those do most of the work:

- **Singular** - one obligation per statement. Two obligations are two
  requirements, because they get checked separately and one may be withdrawn
  without the other.
- **Implementation-free** - it constrains what is observable, not how it is
  built.
- **Verifiable** - there exists a process that can prove the system satisfies
  it. "The platform must be secure and fast" traces to no evidence and is
  therefore not a requirement; subjective language such as "user-friendly" is
  the canonical example of what fails this.

INCOSE's practical rules add: one idea per requirement, a unique identifier,
rationale, and a named verification method.

The harness already requires the first three of those. **Naming the
verification method is the one it adds**, and it costs nothing. The
requirements document already says which of static, behavioural or eval
applies, and putting that on the requirement instead of in the preamble makes
it checkable per statement.

## The four notations

| Notation       | Shape                                                          | Best at                                                              | Fails at                                                                   |
| -------------- | -------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| RFC 2119 prose | "The system MUST ..."                                          | Constraining a boundary precisely; obligations of a protocol or tool | Conditional behaviour, where the prose has to carry the trigger informally |
| EARS           | `WHILE <state>, WHEN <trigger>, the <system> SHALL <response>` | Triggered and conditional behaviour; unwanted behaviour              | Ubiquitous properties, where the template adds ceremony                    |
| User story     | "As a X, I want Y, so that Z"                                  | Capturing _why_, and who wants it                                    | Precision - it does not say what the system must do                        |
| Gherkin        | `Given / When / Then`                                          | Being executed as a test                                             | Being read as a specification; it is a test script                         |

The summary that survives contact with practice: **EARS for "the system does Y
under condition X", user stories for "what does someone want", Gherkin for "how
is this tested".** They complement each other, and none replaces another, so a
document that picks one for everything is fighting its notation somewhere.

### EARS in detail

Published at IEEE RE09, EARS constrains prose with a small set of patterns:

- **Ubiquitous** - always active. "The system shall ..."
- **Event-driven** - "WHEN <trigger>, the system shall ..."
- **State-driven** - "WHILE <state>, the system shall ..."
- **Unwanted behaviour** - "IF <condition>, THEN the system shall ..."
- **Optional feature** - "WHERE <feature is included>, the system shall ..."
- **Complex** - combinations of the above.

The **unwanted behaviour** pattern is the one this method adopts outright,
because it is the failure-path requirement given a shape. "IF an invalid credit
card number is entered, THEN the website SHALL display 'please re-enter credit
card details'" is exactly the kind of statement that otherwise gets left out.
The research on the internal harnesses found failure paths to be where defects
accumulated.

`cc-sdd` adopted EARS for its `requirements.md`, which is the closest thing to
a precedent among the surveyed harnesses.

### Why the harness uses RFC 2119 prose, with EARS where it fits

The harness's own requirements constrain a _tool_, not a reactive system, and
most of them are ubiquitous - "the harness MUST NOT report the check as
passed". Forcing those into `WHEN … SHALL` adds a trigger that does not exist.

But a repository specifying a reactive system should use EARS, and the skill
should say so rather than imposing prose everywhere. The rule that generalises:
the notation follows the shape of the obligation, and a document may mix
patterns as long as each statement is singular and verifiable.

What does not vary: the identifier, the status, the singularity, and the named
verification method.

## Traceability

ISO 29148 formalises the matrix: every requirement traced **backward** to the
need or regulation that created it, and **forward** to design elements, test
cases and verification activities.

The harness has both directions already and arrives at them more cheaply than
a matrix does:

- Backward - a requirement rests on a claim recorded in the research.
- Forward - a check names the identifier, and `/meow:verify` reads
  both sets and reports the differences.

The important difference from a traditional matrix: the harness keeps no
matrix. A separate traceability document is a third artifact that drifts from
the other two. The identifiers in the requirements and the identifiers cited by
checks are the two sets, and their difference is computed on demand. That is
the same reasoning as the contradiction report: derived state is not stored.

## Identifiers and tombstones

`meowctl`'s scheme is `R-<AREA>-<n>`: allocated once, never reused, never
renumbered on reorganisation, with a withdrawn requirement leaving a tombstone
naming its replacement. Every property in that sentence transfers except the
form of the identifier itself.

The property that earns this is not tidiness. A pull request from six months
ago, a test comment, a commit message and a review finding all cite an
identifier, and every one of them resolves forever. Renumbering breaks all of
them silently, which is why "numbers carry no ordering" is stated explicitly.
The temptation to tidy is constant, and the damage is invisible at the moment
somebody does it.

## Decision records are not requirements

ADRs answer a different question and belong in a different place. The two
templates that matter:

- **Nygard** (2011) - title, status, context, decision, consequences. Most
  teams saying "we use ADRs" mean a variant of this.
- **MADR** - adds explicit decision drivers, considered options with pros and
  cons, and a decision outcome. Full and minimal variants, annotated or bare.

The practical guidance: Nygard by default for small teams, because it is small
enough to actually get written; MADR above roughly fifteen engineers, where the
consultation record starts to matter. Keep them in source control - described
as the operational choice that pays back most.

And the warning, because it names the actual failure mode: "Nobody decided when
an ADR is required, who reviews it, or where it lives in the daily workflow.
Without those answers, ADRs become a thing you might write if you remember,
which translates in practice to _you don't write them_."

The harness answers this with structure. `/meow:decide` writes a decision
record, it lives at a path the profile declares, and it is numbered and
immutable once made. The requirements step records unknowns as open questions,
classified by what they block. That turns "if you remember" into a step with an
output.

## Conclusions

1. The 29148 properties as the checklist, with singular, implementation-free
   and verifiable as the ones actually enforced.
2. Name the verification method on each requirement, not only in the
   preamble.
3. Notation follows the obligation's shape: RFC 2119 prose for ubiquitous
   constraints, EARS for triggered and conditional behaviour, and EARS's
   unwanted-behaviour pattern for failure paths.
4. User stories capture why and never substitute for a requirement.
5. No traceability matrix - the two identifier sets and their difference.
6. Identifiers allocated once, never reused, never renumbered, tombstoned on
   withdrawal.
7. Decision records are Nygard-shaped by default, numbered, immutable, in
   the repository, and written by a step rather than by remembering.

## Sources

- [Easy Approach to Requirements Syntax](https://alistairmavin.com/ears/), the
  author's own site, and the [Wikipedia summary](https://en.wikipedia.org/wiki/Easy_Approach_to_Requirements_Syntax),
  read 2026-09-20 - the patterns, the `WHILE / WHEN / SHALL` shape, and the
  IEEE RE09 origin.
- [EARS and the segue to behaviour-driven development](https://conductofcode.io/post/easy-approach-to-requirements-syntax-and-the-segue-to-behavior-driven-development/),
  read 2026-09-20 - where EARS, user stories and Gherkin each fit.
- [ISO 29148 explained](https://www.modernrequirements.com/blogs/iso-29148-explained/)
  and [IEEE 29148-2018](https://www.cwnp.com/req-eng/), read 2026-09-20 - the
  eleven properties, and verifiability as the existence of a process that can
  prove satisfaction.
- [Requirements traceability matrix](https://www.jamasoftware.com/requirements-management-guide/requirements-traceability/traceability-matrix/),
  read 2026-09-20 - tracing backward to the need and forward to design and
  verification.
- [Architectural Decision Records](https://adr.github.io/) and
  [MADR](https://adr.github.io/madr/), read 2026-09-20 - the Nygard template
  and what MADR adds.
- [Master architecture decision records: best practices](https://aws.amazon.com/blogs/architecture/master-architecture-decision-records-adrs-best-practices-for-effective-decision-making/),
  AWS Architecture Blog, and
  [ADR templates and operational patterns](https://hidekazu-konishi.com/entry/architecture_decision_records_templates_and_operations.html),
  read 2026-09-20 - Nygard by default below roughly fifteen engineers, source
  control as the operational choice that pays back most, and the warning that ADRs
  without a decided trigger become "a thing you might write if you remember".
- `~/workspace/meowctl/.claude/skills/spec-driven/SKILL.md` and
  `~/workspace/meowg1k/docs/spec/`, read 2026-09-20 - the identifier scheme,
  tombstones, and per-topic numbering in blocks.
