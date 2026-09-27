---
id: SPC-1120
artifact: spec
status: live
revised: 2026-09-27
checked-at:
states:
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
---

# The licensing unit

## Scope

This covers `meow-licence`, the unit that applies the licence header a
repository declares and checks that every file the repository tracks is
covered by a licensing declaration. It states where a repository declares its
licensing, what the skill does, what the program checks, and how each
failure reads.

It leaves the attribution ban to SPC-1050, which `meow-scm` implements, and
build provenance to the release.

ADR-1400 decides this part.

## Boundary

| Surface                                       | What it is                                                       |
| --------------------------------------------- | ---------------------------------------------------------------- |
| `REUSE.toml` at the repository's root         | A bulk declaration: annotations naming paths and their licensing |
| `.meowpaw/profile.toml`, `[licence]`          | The header's lines, for a repository with no bulk declaration    |
| `LICENSES/<identifier>.txt`                   | A licence's text, where the repository keeps that directory      |
| `plugins/meow-licence/skills/header/SKILL.md` | The skill that adds the declared header to a new file            |
| `plugins/meow-licence/bin/meow-licence`       | The program: `check`                                             |
| `plugins/meow-licence/README.md`              | The unit's page                                                  |

## Behaviour

### Where a repository declares its licensing

A repository declares its licensing in one of two ways (REQ-1016). The first
is `REUSE.toml` at its root: each `[[annotations]]` table names `path`, a
glob or a list of globs relative to the root, with `SPDX-FileCopyrightText`
and `SPDX-License-Identifier`, and files no annotation covers carry a header.
The second is a `[licence]` table in `.meowpaw/profile.toml`:

```toml
[licence]
header = [
  "SPDX-FileCopyrightText: 2026 A Person <a@example.org>",
  "SPDX-License-Identifier: Apache-2.0",
]
```

A header is the declared lines, each on a line of its own within a file's
first 20 lines, in whatever comment form the file's format permits. A file
that can't carry a comment is covered by an annotation, or by a file beside it
named `<file>.license` that carries the header. Prose can be declared in bulk,
and the declaration states its cost beside it: a document lifted out of the
repository carries no licensing (REQ-3060).

### The skill

`meow-licence:header` loads before Claude Code creates a file in a repository
that declares licensing. It adds the declared header to the new file in the
comment form the file's format permits, a document included, copying the form
the repository's own files already carry where they carry one (REQ-1008,
REQ-1018, REQ-1020, REQ-3066). It skips a file an annotation already covers.
It never rewrites, reflows or moves a header a file already carries
(REQ-3068). Where the repository declares nothing, it writes nothing, says
so, and never chooses a licence (REQ-3066).

### The check

`meow-licence check` reads the files git tracks under the repository's root
and prints one line per finding, then a count. A finding is one of:

- a file that no annotation covers and that carries no header, directly or
  in a `.license` file beside it (REQ-3058);
- a header or an annotation carrying the copyright without the licence
  identifier, or the identifier without the copyright (REQ-1022);
- a text in `LICENSES/` whose identifier no declaration uses, or an identifier
  in use whose text `LICENSES/` lacks, where the repository keeps that
  directory (REQ-3062).

It reports licensing alone. It never states who wrote a file or where an
artifact was built, because those are claims a licence declaration can't
make (REQ-3064). `meow-scm`'s attribution ban reaches only lines crediting a
tool, so a copyright line passes it (REQ-3070).

## Failure paths

| Failure                             | What the reader sees                                                  | Exit |
| ----------------------------------- | --------------------------------------------------------------------- | ---- |
| A file nothing covers               | `<file>: no licensing declaration covers it`                          | 1    |
| A header missing its identifier     | `<file>: the header names a copyright and no licence identifier`      | 1    |
| An annotation missing its copyright | `REUSE.toml: an annotation names a licence and no copyright`          | 1    |
| An unused licence text              | `LICENSES/<id>.txt: no declaration uses <id>`                         | 1    |
| A licence in use with no text       | `LICENSES/: <id> is in use and has no text`                           | 1    |
| Nothing declared                    | `licensing is undeclared: no REUSE.toml, no [licence], and no header` | 3    |
| No git, or not a repository         | `unchecked: the tracked files can't be listed`                        | 3    |
| No binary for the machine           | `unchecked: no meow binary was found for this machine`                | 3    |
