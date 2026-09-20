---
id: RES-0267
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0071, RES-0261
---

# Monorepos and large repositories

## Summary

Several documents in this corpus assume one repository has one answer - one
profile, one set of verbs, one record - and a monorepo has several. The
platform has already solved most of it, and the solutions are asymmetric.
Instruction files inherit from parent directories and project settings do not,
so a per-package configuration has to be self-contained where a per-package
instruction file does not. The starting directory decides what loads, which
makes it a choice somebody takes deliberately. And a sparse worktree with
symbolic links to shared dependencies is what makes parallel agents affordable
in a large tree.

Research for how the harness behaves when a repository holds many parts. It
does not cover how the specification divides, which is
[RES-0071-specification-granularity.md](RES-0071-specification-granularity.md),
nor the profile itself, which is
[RES-0261-the-profile.md](RES-0261-the-profile.md).

## The question

The specification already divides by the system's own parts. The verbs do not:
one profile declares what `test` means, and in a monorepo it means four
different commands in four packages.

The same question repeats for the record, for the gate's scope, for which
instructions load, and for what a delegated agent checks out.

## Method

We fetched and read the platform's guidance for large codebases in full on
2026-09-20. It supplied the layering rules, the exclusion and deny settings,
the sparse worktree mechanism, the two additional-directory mechanisms and how
they differ, and the skill-scoping options.

The language and tool research already in this corpus supplied the ecosystem
side: which toolchains have a workspace concept and what each declares.

Nothing was configured or run. No monorepo was set up to test the behaviour
described, so every statement is taken from the documentation.

## Findings

### Instructions inherit and settings do not, which is the asymmetry to build around

Instruction files load from the working directory and every parent at launch,
and a subdirectory's file loads on demand when a file there is read. A root file
sets repository-wide rules and each subdirectory adds its own.

Project settings behave differently, and the documentation states it plainly.
They _"aren't inherited from parent directories the way CLAUDE.md files are"_,
and each subdirectory's settings file _"must be self-contained rather than
layered on a root file."_

For the harness this decides the shape of the profile in a monorepo. A per-part
profile cannot assume the root's; it repeats what it needs or it does not have
it. That argues for the harness reading the profile itself, because it can
layer where the platform's settings inheritance will not.

### The starting directory is a choice with consequences, and it is usually made by accident

Starting at the repository root gives access to every file and loads only the
root instruction file, with subdirectory files arriving as they are read.
Starting in a subdirectory gives access to that subtree only and loads that
directory's instruction file plus every ancestor's.

So the same repository presents two different environments depending on where
the session began, and the documentation is explicit that this determines which
settings apply.

The harness has to notice which it is in. A gate run from a package resolves
that package's verbs; the same gate from the root has a different scope. A
report that does not say which was used is ambiguous, and a run that silently
changes scope between invocations is worse.

### The scoping mechanisms, and what each actually does

Four mechanisms, and the differences between them are the finding:

| Mechanism                                | Effect                                              |
| ---------------------------------------- | --------------------------------------------------- |
| Per-directory instruction files          | Conventions load with the code they describe        |
| Path-scoped rules in a central directory | The same targeting, held centrally, matched by glob |
| Exclusions by path or glob               | Named instruction files never load at all           |
| Read denials                             | The model cannot open generated or vendored paths   |

The choice between the first two turns on ownership, and both do the job.
Per-directory files suit directory owners maintaining their own conventions
versioned with the code. Central path-scoped rules suit keeping everything in
one place, or applying one rule to scattered paths.

The exclusion mechanism has one property that carries over: it is static, and
no per-task switch flips it. The documentation's own advice for focusing on one
package today and another tomorrow is to start the session there.

And one thing the deny rules do not do, which the source states plainly. A
shell search over a directory containing denied files still includes them in
its output, and subprocesses that open files themselves are not covered. So a
denial is a strong default and not a boundary.

### Skills scope by placement or by path, and the list has a ceiling

A skill can live in a directory and apply to work there, or live centrally and
declare the paths it applies to. From the repository root, skills accumulate
from every subdirectory touched during a session - _"which can accumulate into
the hundreds."_

The consequence is the one the progressive-disclosure research predicted from
the other side. Names always load, and past a certain number some skills lose
their descriptions entirely, which strips the keywords the model uses to decide
whether a skill applies.

That is a hard ceiling on a catalogue, and it lands directly on this project's
plugin design. A harness shipping thirty plugins into a monorepo that already
has per-package skills is competing for a list that degrades under pressure.
The mitigation is the documented one - short descriptions leading with the
words a request would contain - plus the harness's own rule that a pack loads
only where its marker is present.

### Sparse worktrees are what make parallel agents affordable

A worktree checks out the whole repository by default. A sparse setting writes
only the listed directories plus root-level files, so a worktree starts faster
and uses less space. A companion setting symlinks large dependency directories
back to the main checkout, so nothing duplicates them.

The documentation names the case this project cares about: subagent worktree
isolation, where each parallel agent gets a lightweight checkout and no full
tree. One caveat comes with it: all worktrees in a session share the same
sparse paths, so every directory any agent needs has to be listed.

Two operational details matter. The root-level `.claude` directory is not
included unless listed, so a worktree without it has none of the repository's
own configuration. And after creation the working directory is the worktree
root, so settings load from there and never from the directory the session
started in. Anything needed inside a worktree therefore belongs in the
repository root's settings.

### Cross-part access has two mechanisms and they differ in what they load

A setting or a flag grants access to a sibling package, and what differs
between them is the context, not the access. The setting grants file access
alone and loads neither instructions nor skills. The flag loads skills, and
loads instructions only where an environment variable says so.

For the harness that is a real distinction. A task that spans two parts needs
the second part's conventions as well as its files, so the mechanism that loads
them is the right one. The setting covers the case where those files are inputs
to the work.

### What the harness has to decide

Reading the above against this corpus:

Verb resolution is per part. The profile declares verbs per part, and the
gate's scope is the part it was invoked for. That was already half-decided -
the gate takes a scope argument - and this makes it the normal case, which no
option turns on.

The record stays at the root. Requirements, decisions and research are
project-wide; only the specification divides by part, which the granularity
research already settled. A per-package record would duplicate identifiers and
split the trace.

A pack activates per part. Detection runs where the marker is, so a
four-language monorepo loads four packs and each applies where it matched.

The harness reports the scope it used, every time, because the same command
from two directories does two different things.

## Conclusions

1. The harness layers the profile itself, because platform settings inheritance
   will not, because project settings are not inherited from parent directories
   while instruction files are. 2. A per-part profile declares what it needs
   and does not assume the root's, which follows from the same asymmetry. 3.
   Verb resolution is per part, and the gate's scope is the part it was invoked
   for. 4. Every report names the scope it ran in, since the same command from
   the root and from a package does different things. 5. The starting directory
   is recorded as part of the run's state, because it decides file access,
   which instructions load and which settings apply. 6. The record stays at the
   repository root. Requirements, decisions and research are project-wide; only
   the specification divides by part. 7. A pack activates where its marker is,
   so a repository with four languages loads four packs, each applying where it
   matched. 8. A pack's skill declares the paths it applies to where it lives
   centrally, because a root session accumulates skills from every directory it
   touches and descriptions are dropped when the list grows. 9. Descriptions
   lead with the words a request would contain, which is the documented
   mitigation for a crowded list and matters most here. 10. Parallel agents use
   sparse worktrees with shared dependency directories symlinked, and every
   directory any agent needs is listed, because all worktrees in a session
   share the same paths. 11. The configuration directory is listed in the
   sparse paths, or a worktree has none of the repository's own configuration. 12. Settings needed inside a worktree live in the repository root's settings
   file, since a worktree session loads from the worktree root. 13. Cross-part
   work uses the mechanism that loads the other part's conventions as well as
   its files. 14. A read denial is a strong default and no boundary, because a
   shell search over a directory containing denied files still returns them. 15. Focusing on a different part is done by starting the session there,
   because the exclusions are static by design.

## Sources

All read 2026-09-20.

- [Set up Claude Code in a monorepo or large
  codebase](https://code.claude.com/docs/en/large-codebases) - instruction
  files loading from the working directory and every parent at launch with
  subdirectory files on demand; project settings not being inherited and each
  subdirectory's file having to be self-contained; the starting-directory table
  for file access, instruction loading and settings; per-directory instruction
  files against central path-scoped rules and the ownership argument between
  them; exclusions as static and never per-task, with the advice to start the
  session elsewhere; read denials and their stated limits around shell searches
  and subprocesses; skills scoped by placement or by a paths field, the
  accumulation into the hundreds from a root session, and descriptions being
  cut when the list grows; sparse worktree paths with symlinked dependency
  directories, the shared paths across a session's worktrees, the need to list
  the configuration directory, and settings loading from the worktree root
  after creation; and the two cross-directory mechanisms differing in whether
  they load instructions and skills. -
  [RES-0071-specification-granularity.md](RES-0071-specification-granularity.md)
  - the division of the specification by the system's own parts, which this
    document extends to verb resolution and pack activation. -
    [RES-0202-progressive-disclosure.md](RES-0202-progressive-disclosure.md) -
    the description as the only part charged every turn, which is what makes a
    crowded skill list expensive. -
    [RES-0263-agent-definitions.md](RES-0263-agent-definitions.md) - worktree
    isolation for delegated agents, which is what the sparse paths serve.
