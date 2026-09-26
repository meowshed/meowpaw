---
id: ADR-1240
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-3008,
    REQ-3009,
    REQ-3010,
    REQ-3011,
    REQ-3012,
    REQ-3014,
    REQ-3016,
    REQ-3018,
    REQ-3019,
    REQ-3020,
  ]
supersedes: []
---

# 1240. A change to the record's shape migrates what exists, and a retired name stays retired

## Decision

A change to the record's shape runs as expand, migrate and contract, and the
program holds the two parts of it a program can:

- `lib/layout.toml` records every retired front matter field and status value
  with what replaced it, starting with the three this record has retired: the
  field `unit` and the statuses `proposed` and `current`. `check front-matter`
  reports a record carrying a retired name, and a layout whose kind declares
  one, so a retired name is never reused with a new meaning.
- `meow-method count` prints the number of artifacts of each kind by status,
  and the number of identifiers, so a migration's evidence carries the count
  before and after.

The `method` skill gains the rules no program settles: expand, migrate and
contract, naming the release that removes the old form when the new one
arrives; a new obligation on existing records either migrated or grandfathered
as a draft rule; structured data edited as structured data and links as links,
never by text substitution; a migration made smaller where no parser exists,
split into parts reviewed separately, its mechanical part apart from its
editorial part; and its count taken before and after.

After this decision a retired name fails the check wherever it reappears, and
a migration can show it lost nothing. What still doesn't work: the program
doesn't run a migration, which stays the author's, reviewed part by part.

## Why

RES-0265 found that this project changed the record's shape three times with
no rule deciding what happens to what existed: a template changed and 117
documents were rewritten by hand, two kinds were renamed, and a status
vocabulary was unified. Twice an unreviewed bulk rewrite corrupted the sources.
It found expand, migrate and contract to be the established answer, a retired
name reserved because reuse reinterprets old data and fails for nobody, and a
count before and after as the one addition a migration needs, because a lost
artifact is lost silently and every check still passes.

The history of this record shows the retired names: 358 records dropped
`unit`, 584 carried `proposed` and 49 `current`, and none carries any of them
now.

The strongest objection: a program that runs migrations would be safer than
rules a model follows. It would be for a rename, and RES-0265 found the
editorial part is what goes wrong, which no program can review; the program
supplies the count and the check, and the rest stays reviewable by a person.

## Alternatives

| Option                                             | Better at                          | Why it lost                                                   |
| -------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------- |
| Retired names checked, a count, rules for the rest | Each part held by what can hold it | Chosen                                                        |
| A `migrate` command that rewrites the record       | One command                        | The large unreviewed change RES-0265 found corrupting sources |
| Retired names in a document                        | Nothing to build                   | Folklore: nothing fails when a retired name is reused         |
| Do nothing                                         | Costs nothing                      | The next shape change repeats the three RES-0265 recorded     |

## What it costs

A table in the layout and a finding in `front-matter`, a `count` command, and
rules in the skill.

## What would reverse it

- Shape changes become frequent enough that a migration command pays for its
  review cost, and the rules move into it.

## Consequences

- `check front-matter` fails on a retired field or status value.
- `meow-method count` prints the record's counts.
- The `method` skill carries the migration rules.

## How I will know it was realised

1. Fixtures show `check front-matter` reporting a record carrying `unit` or
   `status: proposed`, and a layout declaring a retired status.
2. A fixture shows `count` printing each kind's count by status and the
   number of identifiers, identical on two runs.
3. Each rule ADR-1240 places in the skill maps to its requirement in the task
   that closes it.
4. Every requirement ADR-1240 addresses lands in exactly one closed task.

## What this does not settle

- A command that runs a migration.
