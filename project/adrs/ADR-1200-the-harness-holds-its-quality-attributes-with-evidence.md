---
id: ADR-1200
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-1720,
    REQ-1722,
    REQ-1724,
    REQ-1726,
    REQ-1728,
    REQ-1730,
    REQ-1732,
    REQ-1734,
    REQ-1736,
    REQ-1740,
    REQ-1742,
    REQ-1744,
    REQ-1746,
    REQ-1748,
    REQ-1750,
    REQ-1752,
    REQ-1754,
    REQ-1756,
    REQ-1758,
    REQ-1762,
    REQ-1766,
  ]
supersedes: []
---

# 1200. The harness holds its quality attributes, each with a check or a stated piece of evidence

## Decision

Each quality attribute the requirements ask of the harness itself is held by a
check where a program can settle it, and by evidence recorded once where it
can't:

- The commands that read the record, `check`, `status`, `ready`, `template`,
  `show`, `index` without `--write`, `new` and `find`, write nothing, which a
  fixture proves by hashing the tree around each. Every one of them prints the
  same text run twice with nothing changed, and a step's state is read from
  the artifacts alone, never a session or a cache.
- `index --write` writes to a temporary file and renames it into place, so an
  interrupted write leaves the old index or the new one and never half of it.
- Each unit declares the Claude Code version it needs in `requires.toml`, the
  version it was tested on, because Claude Code's plugin manifest has no field
  for one, and its documentation page names the platform behaviours it relies
  on with where each is documented.
- The `method` skill separates what it verified from what it assumed in every
  report it writes.
- The rest is evidence of what already holds: an optional unit that fails
  degrades alone, through its launcher's fallback; the record's shape changes
  by expand, migrate and contract with drafts-only rules for what the frozen
  record predates; the kernel works installed alone; a unit's description says
  its job and its cost; the record renders on a forge with no syntax of its
  own; every check runs locally by the command CI runs; each fixture is seen
  failing against a program that returns nothing; tools are declared in
  `mise.toml`; and no spend happens without a person present.

After this decision each attribute has a check or a named piece of evidence.
What still doesn't work: a unit can't tell which Claude Code version runs it,
so an older platform isn't refused with a diagnostic, REQ-1738; the harness's
own material isn't measured by evaluation, REQ-1759; and delegated work isn't
attributed, REQ-1764, which the delegation increment decides.

## Why

REQ-2694 asks that what a program can settle be checked, and REQ-1728's "a
read-only command writes nothing" is a tree hash away. The rest are properties
the work of ADR-1110 to ADR-1190 already gave the harness; recording where each
is shown keeps a later change from breaking one silently. Claude Code's plugin
manifest reference, read on 2026-09-26, lists no field for a minimum platform
version, which is why the declaration is a file of the unit's own.

The strongest objection: evidence recorded once goes stale when the code moves
on. It does, which is why every attribute a program can settle becomes a
fixture, and only the ones no program settles are left as recorded evidence.

## Alternatives

| Option                                                 | Better at                                            | Why it lost                                                       |
| ------------------------------------------------------ | ---------------------------------------------------- | ----------------------------------------------------------------- |
| A check where a program settles it, evidence elsewhere | Each attribute held by the strongest means available | Chosen                                                            |
| A minimum version in `plugin.json`                     | One file per unit                                    | Claude Code strips an unknown field and warns                     |
| Evidence only, no new checks                           | Nothing to build                                     | "Writes nothing" is settleable, and REQ-2694 asks for the check   |
| Do nothing                                             | Costs nothing                                        | The attributes hold today by accident of how the code was written |

## What it costs

A fixture across the read-only commands, an atomic write, a `requires.toml` per
unit and a line per unit page, a rule in the skill, and one task of gathering
evidence.

## What would reverse it

- Claude Code gains a manifest field for the minimum platform version, and
  `requires.toml` moves into it.
- A hook's input gains the platform version, and REQ-1738's diagnostic becomes
  possible.

## Consequences

- A fixture proves the read-only commands write nothing and repeat themselves.
- `index --write` writes atomically.
- Each unit carries `requires.toml`, and its page names the platform behaviours
  it relies on.

## How I will know it was realised

1. Each read-only command leaves the tree's hashes unchanged, and prints the
   same text twice.
2. Every unit has a `requires.toml` naming a Claude Code version, and its page
   names the behaviours it relies on with their documentation.
3. Each remaining attribute ADR-1200 addresses has its evidence recorded in the
   task that closes it.
4. Every requirement ADR-1200 addresses lands in exactly one closed task.

## What this does not settle

- Refusing an older platform with a diagnostic, REQ-1738.
- Measuring the harness's own material by evaluation, REQ-1759.
- Attributing delegated work, REQ-1764.
