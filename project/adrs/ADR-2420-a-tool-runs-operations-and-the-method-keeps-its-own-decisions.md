---
id: ADR-2420
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [REQ-2608, REQ-2610, REQ-2612, REQ-2614, REQ-2616, REQ-2618, REQ-2620]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2420. A tool runs operations, and the method keeps its own decisions

## Decision

Where a tool such as a worktree manager documents no machine-readable output,
the harness uses it only to run an operation and reads the resulting state
from git, the tool that owns it (REQ-2608). The harness calls no command that
writes a message, commits, rebases and removes a tree in one go, because each
of those is a decision the method makes on its own (REQ-2610).

A commit message is written by the commit skill and checked by
`meow-scm check-message`. The harness never takes a message a tool generated
(REQ-2612). Where commits must be signed, the harness uses no workflow that
rebases on its own, and treats a rebase after signing as a change that needs
signing again (REQ-2614). A model-written summary is never cited as
evidence. It may appear only where a person reads a list (REQ-2616).

The harness removes a working tree only in the foreground, when the person or
the step that made it asks, and never from a background job (REQ-2618).
Where trees share files, only ignored build output is shared, never tracked
source, and the harness reports a filesystem that can't share it (REQ-2620).

Once this is accepted, the harness's use of a worktree manager is bounded to
operations. What still doesn't work: no check enforces these rules, so review
holds them, and the commit skill and `meow-scm` are the only programs that
cover REQ-2612.

## Why

RES-0143 read worktrunk and found a merge command that writes a message,
commits, rebases and removes the tree together, and a background removal
that leaves a running process in a missing directory. Each of these hides a
decision the method assigns to a step, and the failure it causes is hard to
attribute. CLAUDE.md already requires signed commits and a message checked
by `meow-scm`.

## Alternatives

| Option                             | Better at               | Why it lost                                                               |
| ---------------------------------- | ----------------------- | ------------------------------------------------------------------------- |
| Do nothing                         | No rules to hold        | A composite command can merge with a message nobody checked               |
| Ban every external worktree tool   | Nothing to bound        | It costs the parallel work REQ-2364 asks for                              |
| Wrap the tool in a unit of its own | One place for the rules | A wrapper reads state from the same undocumented output it should not use |

## What it costs

A person using worktrunk loses its one-step merge inside the harness and runs
the steps separately. A background cleanup has to be run by hand.

## What would reverse it

- A worktree manager documents a machine-readable output and a merge that
  stops before each decision the method owns.

## Consequences

The commit skill names the composite commands it never runs. The git unit's
skill states that a tree is removed in the foreground only.

## How I will know it was realised

1. The commit skill lists the composite commands it refuses, and a fixture
   reads the list (REQ-2610).
2. `meow-scm check-message` runs on every message the harness uses, and a
   generated message fails the commit skill's steps (REQ-2612).
3. The git unit's skill says a tree is removed in the foreground and shares
   only ignored output (REQ-2618, REQ-2620).

## What this does not settle

- Whether the harness supports a worktree manager at all, which ADR-2660
  decides under REQ-2364.
