---
id: TSK-2090
artifact: task
status: done
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

The unit is `plugins/meow-flow/`, named `meow-flow` in its manifest at 0.31.0
and in the committed catalogue, with `/meow-flow:run`, `/meow-flow:init` and
`/meow-flow:onboard`. `bin/meow-method`, which never shipped, is gone, and
`bin/paw` is the unit's one launcher. `claude plugin validate` passes on the
catalogue and on the unit, and `plugins/meow-flow/bin/paw check` exits 0. I
didn't install the unit into the owner's Claude Code, because that changes
their configuration, so installation rests on the validator.

`paw` writes `<!-- meow-flow index -->` and reads the old markers until
0.32.0, and this repository's indexes carry the new ones. Two fixtures, run
against `main`'s `paw`, failed, and pass against this one:

```text
$ MEOW_FLOW_BIN=<main's paw> python3 -m unittest ... -k old_markers -k writing_an_index
FAIL: test_an_index_with_the_old_markers_is_read_and_moved_to_the_new
FAIL: test_writing_an_index_leaves_no_temporary_file
FAILED (failures=2)
$ meow-verbs run fmt lint test
summary: fmt passed, lint passed, test passed
```

A search for `meow-method` outside the approved records finds it only where
ADR-1390 allows it: the old markers in the program, a fixture and SPC-1100,
the stub in SPC-1070, and the titles of approved records quoted in the
indexes. `test_nothing_the_unit_ships_names_the_old_unit` holds the unit's
own files to that. SPC-1070 states REQ-3190.

## Left alone

Approved records, which keep the name they were written with, and the stub,
which TSK-2100 ships.
