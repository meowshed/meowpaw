---
id: ADR-1250
artifact: adr
status: draft
revised: 2026-09-26
addresses:
  [
    REQ-1554,
    REQ-1560,
    REQ-1561,
    REQ-1562,
    REQ-1563,
    REQ-1564,
    REQ-3098,
    REQ-3180,
  ]
supersedes: []
---

# 1250. `/meow-method:init` writes a profile and a constitution from what the repository holds

## Decision

`meow-method` gains `/meow-method:init`, a command only a person invokes, which
brings a repository with no profile into the harness by reading it:

- It writes `.meowpaw/profile.toml` from a template the unit ships,
  `meow-method template profile`, and a `CLAUDE.md` from the constitution
  template where the repository has none. It writes nothing else: no unit of
  work, no verb run, nothing installed, and no file the repository already
  keeps.
- It reports which verbs resolve before anything else, through
  `meow-verbs status` where that unit is installed, and says which don't.
- It records the layout and templates the repository already has, and reports
  a convention the repository follows inconsistently as the variants with how
  often each appears, choosing none.
- Run again, it shows what it would change in an existing profile and changes
  nothing until the person agrees.

`check coverage` and `status` report coverage over an empty record as zero, not
as complete, and the evidence is recorded that no unit writes into the
repository to run its own capabilities.

After this decision a person can bring a repository into the harness with one
command and a review of two files. What still doesn't work: recovering the
vision, the specification and the constitution's rules from the documents a
repository already has is onboarding, which the next decision takes.

## Why

RES-0058 found initialisation to be reading before asking, asking only what
reading can't answer, reporting what is inconsistent and picking nothing,
writing only the two files the harness owns, recording the layout it finds, and
reporting loudly which verbs don't resolve, because that is the first thing a
person hits. RES-0154 found that nothing required and nothing missing look the
same to a check, so an empty record must read as zero. A repository that
installed a unit agreed to that install and to nothing else, so a unit keeps
its own state inside itself, as REQ-3180 states.

The strongest objection: a program could write the profile, and a program is
repeatable where a model isn't. It could for the parts it can compute, and
`meow-verbs status` is that program for the verbs; the rest is reading a
repository's conventions, which no language-free program can do, and the
harness names no language.

## Alternatives

| Option                                   | Better at                               | Why it lost                                                      |
| ---------------------------------------- | --------------------------------------- | ---------------------------------------------------------------- |
| A command driving a step, and a template | Reads any repository, names no language | Chosen                                                           |
| A program that detects the toolchain     | Repeatable                              | Detection is language knowledge, which belongs in packs          |
| A new unit carrying init                 | Init without the method                 | A unit for one command; `meow-method` works without a record     |
| Do nothing                               | Costs nothing                           | Every adopter writes the profile by hand from the specifications |

## What it costs

A command skill, a profile template, the rules of the step, and a change to
how `coverage` and `status` report an empty record.

## What would reverse it

- Packs that detect a toolchain arrive, and the verbs' part of init moves to
  them.

## Consequences

- `/meow-method:init` and `meow-method template profile` exist.
- `check coverage` and `status` say an empty record's coverage is zero.

## How I will know it was realised

1. `meow-method template profile` prints a template that names no language,
   build tool or package manager, and `/meow-method:init` carries
   `disable-model-invocation`.
2. Each rule ADR-1250 places in the command maps to its requirement in the
   task that closes it.
3. A fixture shows `check coverage` and `status` on an empty record reporting
   zero requirements and coverage as zero.
4. Every requirement ADR-1250 addresses lands in exactly one closed task.

## What this does not settle

- Onboarding: recovering the vision, the specification and the constitution
  from a repository's existing documents.
