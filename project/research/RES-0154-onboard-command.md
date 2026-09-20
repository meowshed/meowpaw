---
id: RES-0154
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0037, RES-0058
---

# `/meow:onboard`

## Summary

Almost every surveyed harness assumes a new project, which is the finding:
the overwhelmingly common case is a repository that already exists, and it is
the case the survey handles worst. The honest answer is that the record starts
nearly empty and says so, because a requirement generated from code is a
reconstruction wearing a record's clothes. What can be derived are facts about
the repository, and the first output is a gap report.

The command for a repository that already exists. It adopts a codebase with
history, conventions and decisions nobody wrote down, and produces the record
the rest of the method needs without pretending the work started today.

Its sibling is [RES-0058-init.md](RES-0058-init.md), which is for a repository
that does not exist yet.

## Who has an equivalent

`agent-os` is the closest: it derives standards from the codebase and asks the
user to declare nothing. Most of the surveyed harnesses assume a new project
and have no onboarding step at all, which is the finding - the overwhelmingly
common case is an existing repository, and it is the case the survey handles
worst.

## Method

The surveyed harnesses' own command templates and the internal repositories'
commands were read on 2026-09-20 for what a comparable command does, and the
platform's command documentation was fetched for the frontmatter fields the
surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against comparable
commands, and none of it is an observation.

## The hard part is that the record would be fiction

A repository that has been worked on for two years has requirements: they are
implicit in the code, in the tests, and in what the maintainers refuse to
change. It has decisions: they are in the structure. It has none of them
written down.

So the tempting move is to generate the record - write requirements from the
code, write decisions from the architecture - and every one of those documents
would be a reconstruction presented as a record. The method's whole value is
that a requirement is something somebody decided and a decision is something
somebody made, and a generated corpus destroys that in the first hour.

The honest form is the opposite: **the record starts nearly empty and states
that it does.** What exists is described as observed, nothing is described as
decided, and a requirement is written only when somebody affirms it.

## What can be derived, and what that derivation is

Some things are facts about the repository and reconstruct nobody's intent, and
those can be written down without anyone affirming them:

- **Which languages and toolchains are present**, from their markers. - **What
  the verbs resolve to**, from the runner's declarations or the language pack's
  detection. - **What checks currently exist** and whether they run. - **What
  the conventions visibly are** - commit message shape, branch naming,
  directory layout - stated as observed frequencies, which are not rules.

That last distinction is the useful one. _Ninety percent of commits use a
conventional prefix_ is a fact; _this project uses conventional commits_ is a
decision somebody has to make, and the command offers it for somebody to make.

## The first output is a gap report

The command outputs what is missing first: verbs that do not resolve, checks
that do not exist, conventions that are inconsistent, directories nobody can
explain.

That is immediately useful, costs nothing to be wrong about, and is the input
to deciding what to adopt. A record produced before it is a record nobody
trusts.

## Adoption is incremental, and the command has to make that visible

A repository does not adopt the method in one step. It adopts a verb, then a
gate, then a convention, then the chain.

So the command produces a sequence: here is what works now, here is the
smallest next thing, here is what that would let you do. That matches the
progressive-enhancement principle the design follows, applied here to adoption.

## What it must refuse

To generate requirements from code, because the result reads like a record and
is a reconstruction.

To assert a convention from a frequency.

To rewrite existing files to match a convention nobody adopted, which is the
single most damaging thing an onboarding command could do to a repository it
has just met.

To claim coverage. A repository with no requirements has no coverage, and
reporting zero honestly is better than reporting a generated hundred percent.

## Conclusions

1. The record starts nearly empty and says so, and nothing generates it from
   the codebase. 2. A requirement is written only when somebody affirms it,
   because a generated requirement is a reconstruction wearing a record's
   clothes. 3. Facts about the repository are derived and stated as observed:
   the languages present, what the verbs resolve to, which checks exist and
   run. 4. A convention is reported as a frequency and offered as a decision,
   never asserted as a rule. 5. The first output is a gap report, because it is
   useful immediately and is the input to deciding what to adopt. 6. Adoption
   is produced as a sequence, each step leaving the repository working, and
   never as a target state. 7. No existing file is rewritten to match an
   unadopted convention. 8. Coverage over an empty record is reported as zero,
   and never as complete. 9. The command is distinct from initialisation,
   because the questions differ: one asks what this repository already is, the
   other asks what this repository should be.

## Sources

All read 2026-09-20.

- [RES-0037-onboarding.md](RES-0037-onboarding.md) - onboarding an existing
  repository, the gap report, and adoption as a sequence. -
  [buildermethods/agent-os](https://github.com/buildermethods/agent-os) -
  standards discovered from the codebase, which nobody declared; the closest
  equivalent in the survey. - [RES-0058-init.md](RES-0058-init.md) - the
  initialisation command this one is distinguished from.
