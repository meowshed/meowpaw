---
id: SPC-1100
artifact: spec
status: live
revised: 2026-09-26
checked-at: "#259"
states:
  [
    REQ-0237,
    REQ-0522,
    REQ-0523,
    REQ-0548,
    REQ-0550,
    REQ-0575,
    REQ-0636,
    REQ-0638,
    REQ-0640,
    REQ-0642,
    REQ-0644,
    REQ-0646,
    REQ-0648,
    REQ-0650,
    REQ-0652,
    REQ-0654,
    REQ-0658,
    REQ-1600,
    REQ-1601,
    REQ-1602,
    REQ-1604,
    REQ-1606,
    REQ-1608,
    REQ-2870,
    REQ-2871,
    REQ-2872,
    REQ-2873,
  ]
---

# The record's relations

## Scope

This covers how artifacts name one another: the identifiers, the relation
fields, and resolving an identifier to its artifact and to what cites it. It
leaves checking that a relation resolves to SPC-1070's relations check.

ADR-1150 and ADR-1180 decide it, EPC-1150 and EPC-1180 realise them, and
`meow-method` implements it, verified under issue 259.

## Boundary

| Surface                          | What it is                                          |
| -------------------------------- | --------------------------------------------------- |
| `relations` in `lib/layout.toml` | The fixed vocabulary of relation fields             |
| `meow-method show <id>`          | The artifact an identifier names, and what cites it |

## Behaviour

### Identifiers

Every artifact carries an identifier of its own, `<PREFIX>-NNNN` for a numbered
kind, allocated once and never reused, and the prefix names the kind, so a
citation says what it cites without resolving it (REQ-0638, REQ-0640).

### Relations

An artifact names what it came from in its front matter, as bare identifiers
in one of the fields `relations` lists: `elaborates`, `addresses`,
`supersedes`, `realises`, `epic`, `closes`, `states` and `violates` (REQ-0644,
REQ-0646). Only that upward direction is written, and a decision names the
requirements it addresses, never the reverse (REQ-0237, REQ-0648). Every
identifier in a relation resolves to an artifact that exists (REQ-0654).

### Resolving an identifier

`meow-method show <id>` resolves an identifier alone, with no path, and prints
(REQ-0642, REQ-0652):

```text
REQ-0190 requirement, approved: project/requirements/REQ-0190-nine-steps.md
The method MUST proceed through nine named steps ...

Names
  elaborates: RES-0001

Cited by
  addresses: ADR-1130
  states: SPC-1090
  closes: TSK-1440
  body: project/README.md
```

`Names` lists the artifact's own relation fields. `Cited by` is derived each
run from every other artifact's relation fields, grouped by field, with a
mention in a body listed under `body` (REQ-0650). A withdrawn or superseded
artifact resolves and prints its status, so an identifier resolves forever
(REQ-0658).

### Indexes

`meow-method index <kind>` prints a kind's index generated from the tree: a
table with one row per artifact, ordered by identifier, each row naming the
artifact, what it concluded, taken from its own summary or statement, and its
stored status only (REQ-0522, REQ-2870, REQ-2872, REQ-2873). Once a kind holds
more than 36 artifacts, a view grouped by topic follows, where the kind has a
`topic` field (REQ-2871). With `--write`, it replaces the block between
`<!-- meow-method index -->` and `<!-- /meow-method index -->` in the kind's
index file, and leaves the rest of the file as its author wrote it. `check
index` reports a generated block that differs from what `index` prints, so a
change adding or removing an artifact without its index fails in that change
(REQ-0523, REQ-0575).

### Allocating identifiers

`meow-method new <kind> [--topic <topic>]` prints the next identifier to
allocate (REQ-0550). A requirement gets the next free number above its topic's
highest, stepping by two as the topic's neighbours do, and a requirement in a
new topic starts a block a hundred above the highest in use. Every other kind
gets the next block of ten above its highest, and research the next number. No
identifier any file carries is printed again, withdrawn ones included, because
an identifier becomes permanent at its first reference (REQ-0548).

### Searching

`meow-method find <word>...` searches identifiers, titles, statements and
summaries across the record and prints one line per match, `ID kind status:
title`, ranked by the number of words matched, at most twenty, and never a
document's body, which `show` prints on request (REQ-1601, REQ-1602). The
record grows, and it is answered by search and never by deleting what it holds
(REQ-0636). The `method` skill searches before it writes, follows or amends a
decision it finds, and writes a durable finding back into an artifact; the
harness keeps no memory store apart from the record (REQ-1600, REQ-1604,
REQ-1606, REQ-1608).

## Failure paths

| Condition                                                        | What happens                                   |
| ---------------------------------------------------------------- | ---------------------------------------------- |
| An identifier with no artifact                                   | `show` says it resolves to nothing and exits 1 |
| No identifier given                                              | Usage, exit 2                                  |
| `index` for a kind with no index file, or a file with no markers | Prints the table; `--write` refuses, exit 1    |
| `new` for a kind it doesn't know                                 | Usage naming the kinds, exit 2                 |
| `find` with no word                                              | Usage, exit 2                                  |
| The record's root doesn't exist                                  | `show` says so and exits 1, as `check` does    |
