---
id: ADR-1180
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-0522,
    REQ-0523,
    REQ-0548,
    REQ-0550,
    REQ-0575,
    REQ-0636,
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
supersedes: []
---

# 1180. The record grows by program: its indexes generated, its identifiers allocated and its content searched

## Decision

Three subcommands of `meow record` take the record's growth off a person's
hands:

- `index <kind> [--write]` generates a kind's index from the tree: one row per
  artifact ordered by identifier, carrying what the artifact concluded, taken
  from its own summary or statement, and its stored status only, with a view
  grouped by topic once the kind holds more than three dozen artifacts. With
  `--write` it replaces the block between `<!-- meow-method index -->` and
  `<!-- /meow-method index -->` in the kind's index file, and `check index`
  reports a block that differs from what `index` generates, so a change that
  adds a document and forgets its index fails in that change.
- `new <kind> [--topic <topic>]` prints the next identifier to allocate: for a
  requirement, the next free number after the topic's highest, keeping the gap
  its neighbours leave, and for every other kind the next block, ten above the
  highest, as this repository allocates. It never prints an identifier any
  file already carries, withdrawn ones included, because an identifier cited
  once resolves forever.
- `find <word>...` searches the record's titles, statements and summaries,
  and prints identifiers and headings first, ranked by how many words matched;
  a whole document is read by `show` on request.

The `method` skill searches the record with `find` before it writes anything,
follows or amends a decision it finds, and writes a durable finding back into
an artifact. The harness keeps no memory store of its own: the record is what
it remembers.

This repository's requirement and decision indexes move to generated blocks,
migrated as expand, migrate and contract, with the count of entries before and
after.

After this decision an index can't drift from the tree without the check
saying so, a new identifier comes from the program instead of a count by hand,
and a step starts from what the record already says. What still doesn't work:
the research index, RES-0001, is prose written by hand and stays so, and the
project index, `project/README.md`, keeps its prose paragraphs.

## Why

RES-0019 found that tooling over a structured Markdown corpus generates the
index and answers queries with identifiers before bodies, and every prior-art
tool it surveyed derived both. RES-0012 found that identifiers are allocated
in blocks per topic, and that a number becomes permanent at its first
reference, which allocation alone doesn't do. REQ-2694 asks that what a
program can settle be a check: an index's rows and the next free identifier
are both computable.

The strongest objection: generated indexes lose the prose a person writes
around a table. They do, for the rows, which is why the generated block sits
between markers and the file keeps whatever the author writes around it.

## Alternatives

| Option                                                  | Better at                                     | Why it lost                                                           |
| ------------------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------- |
| Generated blocks between markers, checked for drift     | Rows can't drift; the prose around them stays | Chosen                                                                |
| Whole index files generated                             | Nothing written by hand                       | Loses the prose that explains a kind to its reader                    |
| An index kept only by `show` and `find`, no file at all | Nothing to keep in step                       | A reader without the harness has no way into the record               |
| Do nothing: indexes and identifiers kept by hand        | Costs nothing                                 | The requirements index says 1073 obligations where 1,075 are in force |

## What it costs

Three subcommands and their fixtures, two skill rules, and migrating two
index files. The requirements index's hand-written grouping gives way to the
generated one.

## What would reverse it

- The generated rows lose information readers relied on, and the indexes go
  back to prose with a drift check instead.
- The record grows past what one read of the tree searches in about a second,
  and `find` needs a cached index.

## Consequences

- `meow record index`, `new` and `find` exist, with fixtures.
- `project/requirements/README.md` and `project/adrs/README.md` carry
  generated blocks.
- The `method` skill gains rules to search first, to follow or amend what it
  finds, and to write findings back.

## How I will know it was realised

1. Adding a decision without regenerating the decisions index fails `check
index`, and `index adr --write` clears it.
2. `new requirement --topic the-method` prints an identifier no file carries,
   next to the topic's highest.
3. `find approval gate` lists identifiers and headings of records about
   approvals, and no document bodies.
4. The requirements index lists every requirement in the tree, counted before
   and after the migration.
5. Every requirement ADR-1180 addresses lands in exactly one closed task.

## What this does not settle

- Generating the research index and the project index.
- Searching outside the record, such as code and documentation.
