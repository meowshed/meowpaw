---
id: ADR-1400
artifact: adr
status: approved
revised: 2026-09-27
addresses:
  [
    REQ-1008,
    REQ-1016,
    REQ-1018,
    REQ-1020,
    REQ-1022,
    REQ-3058,
    REQ-3060,
    REQ-3062,
    REQ-3064,
    REQ-3066,
    REQ-3068,
    REQ-3070,
  ]
supersedes: []
---

# 1400. A licensing unit applies the header a repository declares, and a program checks that every file is covered

## Decision

A new unit, `meow-licence`, carries a skill and a program.

The skill, `meow-licence:header`, loads before Claude Code creates a file in a
repository that declares licensing. It adds the declared header to the new
file in the comment form the file's own format permits, a document included
(REQ-1008, REQ-1018, REQ-1020). It never rewrites, reflows or moves a header a
file already carries, because reformatting a legal notice is modifying it
(REQ-3068). Where the repository declares nothing, it writes nothing and says
so, and it never chooses a licence for the project (REQ-3066).

A repository declares its licensing in one of two ways, which the unit reads
in this order (REQ-1016):

1. a `REUSE.toml` at its root, whose annotations declare files in bulk, with
   headers in the files the annotations don't cover;
2. a `[licence]` table in `.meowpaw/profile.toml`, whose `header` lists the
   header's lines, such as
   `["SPDX-FileCopyrightText: 2026 A Person <a@example.org>", "SPDX-License-Identifier: Apache-2.0"]`.

Where both exist, the skill copies the form the repository's own files
already carry (REQ-3066).

The program, `meow-licence check`, reads the tracked files and reports, one
line each:

- a file covered by neither a header nor a bulk annotation (REQ-3058);
- a header or an annotation carrying the copyright without the licence
  identifier, or the identifier without the copyright (REQ-1022);
- a licence text in `LICENSES/` that no declaration uses, and an identifier in
  use whose text `LICENSES/` lacks, where the repository keeps that directory
  (REQ-3062).

It exits 0 when every file is covered, 1 on a finding and 3 when the
repository declares no licensing, which it reports as undeclared and never as
covered. It reports licensing alone, and never states who wrote a file or
where an artifact was built, because those are separate claims a licence
declaration can't make (REQ-3064). A repository runs it from its own `lint`
verb, as this one will.

A bulk declaration for prose carries its cost beside it: a document lifted
out of the repository carries no licensing (REQ-3060). This repository's
`REUSE.toml` already says so, and the check covers the files it misses today:
the crate under `crates/`, `.meowpaw/` and `LICENSE`.

The attribution ban `meow-scm` holds reaches only lines crediting a tool, and
a copyright line is no such credit, so `check-message` passes a message
carrying one (REQ-3070).

After this decision a repository that declares licensing gets the declared
header on every new file and a check that fails on a file nothing covers, and
one that declares nothing gets a report saying so. What still doesn't work:
the skill applies a header only when Claude Code creates a file, so a file a
person adds by hand is caught by the check and not headed automatically.

## Why

The research found the same rule applied in practice before anyone decided it
(RES-0268): code carries a header because a source file is copied out and the
declaration travels with it, prose is declared in bulk, and a licence text
nobody uses makes the project non-compliant with the convention it follows.
Whether a file is covered is mechanical, so a program settles it (REQ-1172),
and a pattern in a skill would be applied only when the model remembered to.

The header lives in the repository's own declaration, because the licence is
the project's decision and the harness must never make it (RES-0268). Reading
`REUSE.toml` first follows the convention this repository and most that
declare licensing in bulk already use, and the profile table covers a
repository with no bulk file.

The skill writes the comment form because only the file's format decides it,
and naming each language's comment syntax in the unit would put language
knowledge outside a pack (REQ-0072). The model knows the form for the file in
front of it; the program only checks what the header says.

The strongest objection: a new unit for one rule is a unit a repository has to
learn exists. The alternatives each put licensing somewhere a repository that
wants it alone can't install it alone, which REQ-0012 forbids.

## Alternatives

| Option                                       | Better at                                      | Why it lost                                                                                             |
| -------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Do nothing                                   | No unit to ship                                | Files go unheaded, and this repository's crate already has no declaration                               |
| A check in `tools/` for this repository only | No new unit                                    | Only this repository gets it, and the harness applies no header anywhere else                           |
| Add licensing to `meow-scm`                  | No new unit to learn                           | A repository wanting licensing alone installs a commit convention it may not want (REQ-0012)            |
| Run the `reuse` tool when it is installed    | The reference implementation of the convention | The method can't assume an outside tool is present (REQ-0086), and a repository without it gets nothing |
| A skill alone, no program                    | Nothing to build                               | Coverage is mechanical, and a skill checks only the file the model is looking at                        |

## What it costs

Another unit, with a skill description that costs characters in context on
every turn where it is installed, and a program in the native tool. A
repository that wants the header applied declares it once. The check reads
every tracked file, which grows with the repository.

## What would reverse it

- The platform gains a way to run a formatter on every file a session creates,
  so a header could be applied without the model loading a skill.
- A repository using the unit finds the check reporting a file its
  declaration covers, in two consecutive releases, which would show the program's
  reading of `REUSE.toml` drifting from the convention's.

## Consequences

- `plugins/meow-licence/` ships the skill, the launcher, a page and a budget.
- The native tool gains a `licence` subcommand.
- This repository's `REUSE.toml` covers `crates/`, `.meowpaw/` and `LICENSE`,
  and its `lint` verb runs `meow-licence check`.
- A fixture in `meow-scm` passes a message carrying a copyright line.

## How I will know it was realised

1. `meow-licence check` exits 0 on this repository, and fixtures show it exit
   1 on an uncovered file, on a header missing its identifier and on an
   unused licence text, and 3 on a repository declaring nothing.
2. The skill's rules carry REQ-1008, REQ-1018, REQ-1020, REQ-3066 and
   REQ-3068, traced in the task, and the prompt check passes on it.
3. A fixture shows `meow-scm check-message` passing a message that carries a
   copyright line.
4. Every requirement ADR-1400 addresses lands in exactly one closed task.

## What this does not settle

- Documentation on every publicly reachable declaration and executable
  examples (REQ-1010, REQ-1015), which belong with the implement step.
- Build provenance, which belongs with the release.
- Choosing a licence, which the project makes and the harness never does.
