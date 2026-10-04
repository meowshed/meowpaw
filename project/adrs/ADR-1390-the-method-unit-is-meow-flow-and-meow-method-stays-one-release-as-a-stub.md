---
id: ADR-1390
artifact: adr
status: done
revised: 2026-09-27
addresses: [REQ-3004, REQ-3168, REQ-3190]
supersedes: []
---

# 1390. The method's unit is `meow-flow`, and `meow-method` stays one release as a stub that says so

## Decision

The unit that runs the method and checks the record is named `meow-flow`
(REQ-3190). Its directory is `plugins/meow-flow/`, its catalogue entry and
manifest name it `meow-flow`, and its skills and commands are
`meow-flow:method`, `/meow-flow:run`, `/meow-flow:init` and
`/meow-flow:onboard`. The record's command stays `paw` (REQ-3168). Every
shipped file, specification and page, the constitution and the profile name
`meow-flow`. Approved records keep the name they were written with, because
they are history (the constitution's `living_and_record`).

`meow-flow` ships at 0.31.0, the version `meow-method` reached without a
release, because a renamed unit breaks every command and skill name a person
typed, which is a minor change while the harness is at major version zero. It
ships `bin/paw` alone. The `bin/meow-method` alias ADR-1350 kept for one
release never shipped, since no release carried 0.30, and after the move
`plugins/meow-method/bin/` no longer exists, so a script calling that path
finds no file, and an alias inside `plugins/meow-flow/` can't answer it.

The index markers become `<!-- meow-flow index -->` and `<!-- /meow-flow index
-->`. `paw` 0.31.0 reads both forms and writes the new one, this repository's
indexes migrate in the same change, and `meow-flow` 0.32.0 stops reading the
old form, following ADR-1240: accept both forms, move every record, then remove
the old one.

`meow-method` stays in the catalogue for one release as a stub, 0.30.0, so a
person who has it installed learns where it went (REQ-3004). The stub carries a
page and a `SessionStart` hook that tells the session `meow-method` is now
`meow-flow` and prints the two commands that move an install, `claude plugin
install meow-flow@meowpaw` and `claude plugin uninstall meow-method@meowpaw`.
It carries no skill and no program, because a second copy of the unit installed
beside `meow-flow` would load every skill twice. The release that ships
`meow-flow` 0.32.0 removes the stub.

After this decision a person installs and runs `meow-flow`, and one who had
`meow-method` installed sees at the start of each session what to install in
its place. What still doesn't work: the stub can't move an install by itself,
so a person who updates and ignores the notice has only the stub under the old
name, with no skill and no `paw`, until they act.

## Why

I decided the name on 2026-09-27, and REQ-3190 records it. A unit's name is
part of what people use: they type its commands and skills, and the catalogue
installs it by name. REQ-3166 said the unit keeps the name `meow-method`, so it
is withdrawn, and REQ-3168 keeps the one obligation of it that still holds, the
command's name. A deprecation is announced in one release and removed in a
later one (REQ-3004, RES-0264), so the old name can't vanish from the catalogue
while people have it installed. The deprecated surface is the catalogue entry:
it announces the rename in 0.30.0 and leaves in a later release. The old
commands and skills go in 0.30.0 itself, because keeping them means shipping
the unit twice, and that cost is stated under What it costs.

The platform installs a unit by its catalogue name and offers no alias, so the
announcement has to come from a unit still installed under the old name. A
`SessionStart` hook reaches the model before its first reply, which the unit
already relies on for pending approvals (ADR-1170), so the notice arrives
where a person working in the session will see it.

The index markers move with the name, because a marker naming a unit that no
longer exists sends a reader looking for it. ADR-1240 fixed how the record's
shape changes: accept both forms, move every record, then remove the old one
in a named release.

The strongest objection: a stub unit is an extra catalogue entry nobody will
install new,
and it could outlive its release. It names its removal release on its page,
and the release that removes it is the one after `meow-flow` 0.31.0, which is
when a person who updated once has seen the notice.

## Alternatives

| Option                                                    | Better at                                          | Why it lost                                                                               |
| --------------------------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Do nothing                                                | No change for anyone                               | The owner decided the name                                                                |
| Rename, with a stub for one release                       | An installed `meow-method` says where it went      | Chosen                                                                                    |
| Rename, and drop `meow-method` from the catalogue at once | One name from the first day, and nothing to remove | An installed `meow-method` stops updating with no word why, against REQ-3004              |
| Rename the unit, keep the old index markers               | No record migrates                                 | Markers naming a unit that no longer exists, so the rename stops short of the indexes     |
| Keep `bin/meow-method` in `meow-flow` as ADR-1350 planned | Keeps the plan as written                          | It never shipped, and a script calling the old unit's path finds no file whatever it does |

## What it costs

Every shipped file, specification and page naming the unit changes once, and
every index in this repository migrates its markers. A person with
`meow-method` installed runs two commands, and between updating and running
them has no skill and no `paw` under the old name. The stub is a unit to ship
for one release and remove in the next.

## What would reverse it

- The platform gains a way to rename an installed plugin, or to alias one, so
  a stub is no longer needed to announce a move.

## Consequences

- `plugins/meow-flow/` holds the unit at 0.31.0, and `plugins/meow-method/`
  holds the stub at 0.30.0.
- `paw` reads and writes `<!-- meow-flow index -->`, and reads the old marker
  until 0.32.0.
- ADR-1350 is amended: the unit is `meow-flow`, and no `bin/meow-method`
  alias ships.
- A task in the release that ships `meow-flow` 0.32.0 removes the stub and
  the old marker, written when 0.31.0 is released.

## How I will know it was realised

1. `claude plugin install meow-flow@meowpaw` installs the unit from the
   committed catalogue, and `/meow-flow:run` and `paw check` run.
2. No shipped file, specification or page, the constitution or the profile
   names `meow-method`, apart from the stub, the old marker `paw` still reads,
   and approved records.
3. `paw index` writes `<!-- meow-flow index -->`, a fixture shows it reading
   an index with the old marker, and this repository's indexes carry the new
   one.
4. The stub's `SessionStart` hook prints that `meow-method` is now
   `meow-flow`, with `claude plugin install meow-flow@meowpaw` and
   `claude plugin uninstall meow-method@meowpaw`, in a fixture.
5. REQ-3004, REQ-3168 and REQ-3190 land in exactly one closed task each.

## What this does not settle

- The record's command, which ADR-1350 named `paw`; this record carries
  REQ-3168 forward and doesn't rename it.
- The names of the other units.
- The task that removes the stub and the old marker, which is written when
  0.31.0 is released.
