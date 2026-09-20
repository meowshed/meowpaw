---
id: RES-0012
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Catalogues, indexes and templates

## Summary

Three internal repositories organise their specifications differently, and each
solved a real problem the others did not. The layout divides by artifact kind,
and no directory belongs to a unit of work, because a per-unit directory puts a
living document inside a folder owned by whatever work happened to produce it.
Each tree carries an index that is readable without the harness, and a number
becomes permanent at its first reference, which allocation alone does not do.

Research for the artifact layout in `meow-flow`. Three of the internal
repositories organise their specifications differently, each solved a problem
the others did not, and the differences teach something, so none of them is
arbitrary.

## Method

The internal repositories were read from their working trees on 2026-09-20: the
index files, the templates, and the directory layouts themselves, which are the
evidence here, and no prose about them is.

The conclusion that a repository might have both arrangements was reached and
then reversed within this document, and the reversal is stated in the
conclusion, so editing the finding above it hides nothing.

No external source was consulted and nothing was run, which is a real limit:
the arrangements compared here are three, all from one author's projects.

## Three layouts

|           | `meowctl` / `meowg1k`                                      | `meowhub`                                    |
| --------- | ---------------------------------------------------------- | -------------------------------------------- |
| Unit      | One file per **component**                                 | One directory per **feature**                |
| Path      | `docs/spec/<area>.md`                                      | `specs/NNNN-slug/{spec,plan,tasks,notes}.md` |
| Lifetime  | Permanent; the component exists as long as the system does | Finite; a slice is delivered and done        |
| Numbering | Requirement identifiers only                               | The directory is numbered too                |
| Index     | `docs/spec/README.md`, area table                          | `project/README.md`, a status table          |

They are not competing, and this is the finding. A component specification
describes something that exists continuously; a feature directory describes a
piece of work that starts and finishes. `meowctl` has both - its work items are
GitHub issues and no directories - and `meowhub` has both, with component
behaviour distributed across the slices that created it.

This settles a question the harness's own layout raised: **a requirement may
live somewhere other than the unit-of-work directory.** A repository keeps
permanent component specifications _and_ per-unit directories, and the profile
declares both paths.

## What `meowhub` does best

### The index is a status table

`project/README.md` lists every slice with its number, name and status, so the
overview is a file that any reader opens, where a command would run.
`/spec-status` exists too, but the file is what a human reads and what survives
without the harness installed.

### A reference makes a number permanent

> A spec's number is permanent once anything references it. While a spec is
> still `draft` and unreferenced, renumbering is allowed - that is how slices
> get inserted in front of unwritten ones.

This is more precise than the usual "numbers are permanent" and it solves a real
problem: sequences need insertions early and stability later, and the moment
that separates the two is the first citation. Worth adopting verbatim, and it
generalises to requirement identifiers during a draft.

### The template asks questions

`_templates/spec.md` is the best-designed document in the internal survey, and
the reason is that most of its sections are _questions with a stated failure
mode_:

- **Problem** - "Name the person and the moment, and give the reason the pain
  exists. Describe no solution here, only the pain."
- **Why** - "Name a metric or an observable sign somebody could check without
  asking you."
- **Out of scope** - and _why_, which is the half everyone omits.
- **Acceptance criteria** - "phrased so that an implementer can write the test
  straight from the sentence", as `Given / When / Then` checkboxes.
- **Ergonomic cost** - four questions, with "None is a valid answer, and you
  earn it by saying why nobody does more work."
- **Non-functional** - "If nothing here matters for this feature, leave the
  section empty; an invented limit is one nobody will check."

The last two generalise: **a section that permits an empty answer and makes you
earn it.** A template whose sections must all be filled produces invented
content, and invented content is worse than a blank, because somebody cites it.

### Open questions classified by what they block

Five values, each with a precise meaning:

| Value     | Meaning                                                                                                         |
| --------- | --------------------------------------------------------------------------------------------------------------- |
| `design`  | The behaviour cannot be settled without it. **Blocks the plan.**                                                |
| `build`   | Needed during implementation - a credential, a file, a verified assumption - blocking a task and never the plan |
| `deploy`  | Only needed to go live: a provider, a domain, a purchase.                                                       |
| `data`    | A real-world fact needed to _use_ the system, not to build it.                                                  |
| `nothing` | A preference with a sensible default, recorded so it is a choice rather than an accident.                       |

The instruction attached is the point: "Classify each question by what it
blocks, not by how important it feels."

`nothing` is the category most templates lack and the most useful. It converts a
silent default into a recorded choice, at the cost of one line.

The vocabulary is slightly project-shaped - `data` means "the household's real
balances" - but four of the five generalise directly, and `data` generalises to
"a real-world input needed to operate, not to build".

## What `meowctl` does best

### An index of every documentation file, with a maintenance obligation

`docs/README.md` opens with: "Every documentation file in the repository is
listed here. Update this index whenever a file is added, moved, or deleted." The
constitution's `<maintenance>` section repeats the obligation from the other
side.

This keeps the record current in the same way the contradiction report does,
and it is cheap. A script finds a file that exists and is not in the index, and
it finds an index entry with no file.

### Specifications listed in dependency order, with a citation rule

> The files are listed bottom-up, in dependency order: each one may cite the
> requirements above it in this table, and none cites a requirement below it
> except where the higher layer constrains the lower on purpose.

The layering rule is expressed _as the ordering of the index_. Citation
direction equals dependency direction, and a violation is visible by reading two
identifiers. That is a considerable amount of architecture enforcement for one
sentence in a table's preamble.

### A trade-off register with reversal conditions

`docs/design/0.2.0-requirement-tradeoffs.md`: "Every one of the 284
requirements, with the alternative that was available, why it lost, and what
would reverse it."

This is the strongest artifact idea found anywhere in the survey, internal or
public, and nothing in the harness currently has it. Three properties:

- It records the alternative **at the moment of deciding**, when it is still
  known. Six months later nobody remembers what else was considered. - It
  records **why it lost**, which is what a future reader needs to judge whether
  the reasoning still holds. - It records **what would reverse it**, as a
  condition that somebody can test. That turns a decision into something
  falsifiable: when the condition occurs, the decision is revisited, and when
  it does not, the argument is over.

The cost is real: 284 entries is a large document, and the temptation is to
write "no alternative was available" for most of them. But the discipline is
what produces requirements somebody actually chose, where the alternative is a
set that accumulated.

The companion document records decisions **with what each costs**, which is the
same honesty applied one level up.

### The execution plan carries a coverage check

"The 284 requirements decomposed into 34 issues with dependencies, sizes, and a
coverage check." That coverage check is what stops a decomposition from quietly
dropping requirements: every requirement lands in exactly one issue, or is
explicitly deferred with a reason. The harness's plan has this obligation
through decomposition and the "not covered" section, but does not name it as a
check.

### The spec template's Scope paragraph is a routing device

> **Scope.** What this component owns, and what it explicitly does not. Two or
> three paragraphs. A reader who stops here knows whether their question belongs
> in this file.

That last sentence is the three-tier disclosure idea applied to a document: the
first section exists so the rest need not be read. Every artifact in the harness
should have one.

### Withdrawn requirements are collected at the end

The template ends with a `## Withdrawn requirements` section holding the
tombstones, so none of them interrupts the reading order. Both work; collecting
them keeps the live document readable while preserving resolution for old
citations.

## What `meowg1k` does best

### A compact provenance header

```text
Status: approved 2026-09-19
Elaborates: docs/design/0.3.0-architecture.md sections 4, 9
```

Two lines that answer "is this agreed?" and "what decides the things this
elaborates?". The harness's front matter carries the status; **`Elaborates` is
missing, and this harness adds it**, because it is what makes the authority
chain navigable in the direction people actually read.

### Requirement numbers allocated in blocks per topic

`R-INDEX-001`-`005` for walking, `R-INDEX-010`+ for chunking, and so on. Gaps
of ten between groups, so a new requirement joins its neighbours and never
lands at the end of the file, far from the statements it belongs with.

This costs nothing and preserves the "never renumber" rule, because the gap is
allocated up front and nobody reclaims it later. The harness's own requirements
document has already drifted from this and has two blocks - 180s and 200s -
appended out of order for exactly the reason the convention exists.

## Conclusions

1. One layout, by artifact kind. The survey found two arrangements - component
   specifications and per-unit directories - and concluded a repository might
   have both. That was wrong for the same reason a per-unit directory is: it
   puts a living document inside a folder owned by the work that happened to
   produce it. The layout divides by kind, and the unit an artifact belongs to
   is declared in its front matter. 2. An index file per artifact tree, showing
   status, kept current, readable without the harness. 3. An index of every
   documentation file, with add/move/delete obligations on both sides. 4. A
   dependency-ordered index with a citation-direction rule, for the
   specification. The ordering there carries the layering rule and a violation
   is visible by reading two identifiers. It does not generalise to an index
   over a record, where the reader arrives holding an identifier and the order
   is by identifier, which is recorded in
   [RES-0259-the-index-template.md](RES-0259-the-index-template.md). 5. Number
   permanence triggered by first reference. 6. Requirement numbers allocated in
   blocks of ten per topic. 7. A provenance header: status, date, and what it
   elaborates. 8. A Scope section whose job is to let a reader stop. 9.
   Sections that permit an empty answer and make you earn it. 10. Open
   questions classified by what they block, with `nothing` as a value. 11. A
   trade-off register: the alternative, why it lost, what would reverse it. 12.
   A coverage check named as a check, which a section heading only implies. 13.
   Withdrawn requirements collected at the end.

## Sources

All read 2026-09-20.

- `~/workspace/meowhub/project/README.md` - the status-table index, and the rule
  that a number becomes permanent at first reference.
- `~/workspace/meowhub/specs/_templates/spec.md` - the section-as-question
  template, the ergonomic-cost four questions with "None is a valid answer", the
  non-functional section that may be left empty, and the five-value
  open-question classification.
- `~/workspace/meowctl/docs/README.md` - the index of every documentation file
  with its maintenance obligation, and the dependency-ordered specification
  table with its citation-direction rule.
- `~/workspace/meowctl/docs/spec/README.md` - the area table, the spec
  template with its Scope-to-let-a-reader-stop paragraph, and the withdrawn-
  requirements section at the end.
- `~/workspace/meowctl/docs/design/` - the four design documents, including
  `0.2.0-requirement-tradeoffs.md` (every requirement with its alternative, why
  it lost and what would reverse it), `0.2.0-decisions.md` (decisions with what
  each costs) and `0.2.0-execution-plan.md` (the decomposition with a coverage
  check).
- `~/workspace/meowg1k/docs/spec/README.md` and `docs/spec/index.md` - the
  two-line provenance header (`Status:`, `Elaborates:`) and per-topic numbering
  in blocks of ten.
