---
id: ADR-2650
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-0078,
    REQ-0133,
    REQ-0343,
    REQ-3040,
    REQ-3042,
    REQ-3043,
    REQ-3044,
    REQ-3046,
    REQ-3048,
    REQ-3052,
    REQ-3054,
    REQ-3056,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2650. A repository declares its parts, and each verb resolves per part, where a pack's marker is

## Decision

A repository declares its parts in the root profile, under `[parts]`, as a
name and a directory each, because only the project knows what it is built
from, and a part isn't assumed to be a unit of installation (REQ-0343). A
part may carry its own `.meowpaw/profile.toml` in its directory. The harness
layers the two itself: the part's profile is read over the root's, and a part
declares each verb it needs and assumes none from the root (REQ-3040). This
extends ADR-2370, which reads the root's profile only and never one above it.

A verb resolves per part, and a gate run for a part covers that part only
(REQ-0078, REQ-3042). A pack identifies the toolchain it serves by a marker
file, such as a manifest or a lockfile, and activates for each directory that
holds one, not once for the repository (REQ-0133, REQ-3048). Every report
names the part, or the whole repository, it ran for (REQ-3043), and the run's
state records the directory it started in (REQ-3044).

The record stays at the repository root, and only the specification divides
by part (REQ-3046). Where parallel agents work in sparse trees, the sparse
paths list every directory any of them needs, the `.meowpaw/` and
`.claude/` directories included (REQ-3052). Settings that must apply in a
working tree live in the root's `.claude/settings.json`, because a session
started in a tree loads that tree's root (REQ-3054). A read denial in
settings is a strong default and not a boundary, because a shell search in a
directory with denied files still returns them (REQ-3056).

Once this is accepted, a repository with a Rust crate and a TypeScript site
resolves `test` differently in each. What still doesn't work: a repository
that declares no `[parts]` is one part, which is today's behaviour, and the
harness doesn't guess parts from markers alone.

## Why

RES-0267 found that instruction files inherit from parent directories and
project settings don't, so the harness has to layer its own profile. It
found that a sparse worktree needs every directory an agent reads listed, and
that a read denial doesn't stop a shell search. RES-0071 found
that only the specification needs to divide by part, and the record stays
whole.

## Alternatives

| Option                         | Better at               | Why it lost                                                            |
| ------------------------------ | ----------------------- | ---------------------------------------------------------------------- |
| Do nothing                     | No new keys             | A repository with two languages resolves one `test` for both           |
| Detect parts from markers only | No declaration to write | A marker says what tool a directory uses, not what the project is      |
| A profile walk up the tree     | No `[parts]` table      | ADR-2370 reads the root only, and a repository has one answer per part |

## What it costs

A repository with parts writes the `[parts]` table and a profile per part,
and each report grows a scope line.

## What would reverse it

- The platform starts layering settings from parent directories, which would
  let the harness drop its own layering.

## Consequences

The profile reader layers a part's profile. ADR-2370's key table gains
`[parts]`. Every verb report gains a scope line. The run state records its
starting directory.

## How I will know it was realised

1. A fixture repository with two parts resolves `test` to a different command
   in each (REQ-3042).
2. A pack whose marker sits in one part reports for that part only
   (REQ-3048).
3. Every verb report names its scope (REQ-3043).

## What this does not settle

- How a cross-part change is gated, which a later decision takes up when a
  repository has one.
