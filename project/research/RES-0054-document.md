---
id: RES-0054
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:document`

## Summary

Of everything a project writes down, documentation drifts furthest from what
shipped, because it describes the proposal and nobody revisits it. This step
brings the project's user-facing documentation into agreement with what the
epic changed, names the kind of each document it writes, never mixes two kinds,
checks generated reference material without hand-writing it, and reports what
it deliberately left alone. It runs before verification, so verification covers
it and review sees it checked.

## Who has an equivalent

Nobody. Documentation sits outside every surveyed chain.

The nearest anything comes: vlie's `/research` and `/design` both end with
"Update `docs/index.md`" as a step, which maintains an index and leaves the
documentation itself untouched. spec-kit generates a `quickstart.md` during its
design phase, so that document describes the plan and the work happens
afterwards.

That absence is the finding. Every surveyed harness names documentation drift
as a problem somewhere in its README, and none has a step that addresses it.

## Method

We fetched and read the surveyed harnesses' own command templates on
2026-09-20, because the mechanisms live in the templates and the readmes only
describe them, alongside the internal repositories' commands read from their
working trees.

We fetched the platform's documentation on commands for the frontmatter fields
the surface depends on.

We ran nothing. Nobody implemented or tested a command here, so every statement
about behaviour is a design claim measured against what comparable commands do.

## Why documenting is a step

A step nobody is obliged to run is a step nobody runs. That argument carries
every other step in the chain, and the six internal repositories are the
evidence: all of them have documentation, none has a process point where
somebody updates it, and in all of them the documentation lags the code.

## Why it runs before verification

We considered documenting after the verdict and rejected it. Documentation
nobody checked is the artifact most likely to have drifted and least likely to
be caught, and putting it after the verdict makes the verdict a lie, because
something still happens afterwards.

Running it before verification sharpens the same argument, and running it merely
before review doesn't. Documentation is a change to the tree like any other, so
running it after verification would leave the last change before review as the
one nothing checked, and it would expire the evidence verification had just
reconciled.

The cost is real: a returned unit re-runs the step. That costs less than
documentation nobody ever reviews.

## What it touches

The project's **user-facing** documentation: tutorials, how-to guides,
reference, the README. It leaves the unit's own artifacts alone, because the
previous steps produced them and rewriting them here would edit the record of
what was decided.

Per [RES-0020-documentation.md](RES-0020-documentation.md), the language
generates reference material wherever it can, so the command's reference work
is usually checking that doc comments exist and are current, and it writes no
pages.

## Reporting what it left alone

The step reports both what it changed and what it deliberately didn't, and that
report is what keeps it honest.

"Nothing needed changing" is a common and correct outcome, because most tasks
change nothing a user reads. A reader can't tell silence from an omission, so
the command says which one it was. That's the same rule as the unresolved verb:
report the honest answer and never pass over it.

## Conclusions

1. Touch user-facing documentation, and leave the unit's artifacts to the steps
   that produced them.
2. Name the kind of each document it writes and never mix kinds.
3. Check generated reference material, and hand-write none of it.
4. Report what changed and what it deliberately left alone.
5. Run before verification, so verification covers it and review sees it
   checked.

## Sources

All read 2026-09-20.

- [Diátaxis](https://diataxis.fr/) - the four kinds and the rule against mixing
  them.
- [Specbound/sdd-harness](https://github.com/Specbound/sdd-harness) - the
  `doc-sync` agent, the post-commit trigger, and the `docs: auto-sync` commit
  subject that prevents re-firing. The only automatic documentation maintenance
  in the survey.
- `~/workspace/vlie/.claude/commands/research.md` and `design.md` - index
  maintenance as a numbered step of the command, which nothing leaves to
  memory.
- [github/spec-kit `plan.md`](https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/plan.md)
  - `quickstart.md` generated during design, so it documents the plan and the
    work happens afterwards.
