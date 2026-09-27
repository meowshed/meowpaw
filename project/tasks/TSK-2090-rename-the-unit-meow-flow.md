---
id: TSK-2090
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1370
closes: [REQ-3168, REQ-3190]
issue: 436
projected: 956c371b6999
---

# The unit ships as `meow-flow`, and the indexes carry its marker

The method's unit moves to `plugins/meow-flow/` and is named `meow-flow`
everywhere outside the approved records, its command stays `paw`, and `paw`
writes the new index marker while reading the old one. One task, one branch,
one pull request, one review.

## Acceptance criteria

1. Given the committed catalogue, when `meow-flow` is installed from it, then
   `/meow-flow:run` and `paw check` run. Closed by: the catalogue entry, and
   `plugins/meow-flow/bin/paw check` exiting 0.
2. Given the tree, when every shipped file, specification, page, `CLAUDE.md`
   and the profile are searched for `meow-method`, then nothing is found
   outside the old marker `paw` still reads. Closed by: the search's output,
   and a fixture in the unit searching what it ships.
3. Given an index carrying `<!-- meow-method index -->`, when `paw check index`
   and `paw index --write` run, then the first reads it and the second writes
   `<!-- meow-flow index -->`. Closed by: fixtures, seen failing first.

## What to do

Move `plugins/meow-method/` to `plugins/meow-flow/`, rename the unit in its
manifest, the catalogue, its skills and commands, its page and every link to
it, and in the specifications, the introduction, `llms.txt`, `CLAUDE.md`, the
profile, `REUSE.toml` and the tests. Keep `paw`, and delete `bin/meow-method`,
which never shipped. Make `paw` read both markers and write the new one, and
migrate this repository's indexes. The unit ships at 0.31.0.

State REQ-3190 in SPC-1070, where REQ-3168 is stated.

## Depends on

Nothing. ADR-1390 is approved.

## Evidence

Not yet.

## Left alone

Approved records, which keep the name they were written with, and the stub,
which TSK-2100 ships.
