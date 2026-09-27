---
id: TSK-2030
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1350
closes: [REQ-2838, REQ-3130, REQ-3136, REQ-3138, REQ-3142, REQ-3148, REQ-3152]
issue: 414
projected: 491a4a6a0861
---

# Each unit ships its own page, and a program checks every page's front matter

Each unit's page moves into the unit as `README.md`, every user-facing page
names its reader and the version it describes, and `tools/check_docs.py`
fails the `test` verb when a page is missing, stale or cites the record. One
task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the tree after the change, when `find plugins -maxdepth 2 -name
README.md` and `ls docs` run, then every unit has a `README.md` and no
   `docs/<unit>.md` remains. Closed by: the command's output.
2. Given the tree, when `python3 tools/check_docs.py` runs, then it exits 0.
   Given a copy with a unit's `README.md` removed, with `reader` removed from
   one page, with one page's `describes` naming an older version, or with a
   page citing `REQ-0010`, then it exits 1 and names the page and the failure.
   Closed by: fixtures in `tools/test_check_docs.py`, each naming its
   requirement, seen failing first.
3. Given the `test` verb in `.meowpaw/profile.toml`, when it runs, then it runs
   `tools/check_docs.py` and its fixtures. Closed by: the verb's output.

## What to do

Move `docs/<unit>.md` to `plugins/<unit>/README.md` for all eight units and
give every user-facing page, the unit pages and `docs/README.md`, the front
matter SPC-1110 states: `reader`, `answers`, `kind` and `describes`. Remove
every record identifier and every link into `project/` from those pages,
stating the fact on the page where the identifier stood for one (REQ-3130,
REQ-3148).

Write `tools/check_docs.py` with the checks SPC-1110 lists for pages, the
unit's page and `describes`, and its fixtures, and add both to the `test`
verb. `tools/check_index.py` walks the unit pages too, and every link to a
moved page changes, the specifications' boundary tables included.
`CLAUDE.md` names four checks in `tools/` where it names three.

## Depends on

Nothing. ADR-1370 is approved.

## Evidence

Each unit's page moved to `plugins/<unit>/README.md`, and `docs/` holds only
`README.md`. Every page opens with `reader`, `answers`, `kind` and
`describes`, stamped at each unit's version in `plugin.json`. Each page's
"Where the rules come from" section, which only sent the reader into the
record, is gone, and the two measurements the pages cited now state their
facts without the citation. The homepages in `plugin.json` and the committed
catalogue point at the moved pages, and SPC-1040 to SPC-1070 name them.

`tools/check_docs.py` holds the pages, and the `test` verb runs it and its
fixtures. Six of the nine fixtures in `tools/test_check_docs.py`, each naming
its requirement, failed against a program that reports nothing, and all nine
pass against the check:

```text
$ CHECK_DOCS=stub.py python3 -m unittest tools/test_check_docs.py
FAILED (failures=6)
$ python3 -m unittest tools/test_check_docs.py
Ran 9 tests
OK
$ python3 tools/check_docs.py
9 pages, 0 documentation failures
$ meow-verbs run fmt lint test
summary: fmt passed, lint passed, test passed
```

A record identifier inside code counts as an example of the record's syntax,
which `meow-method` and `meow-github` show on their pages, and SPC-1110 says
so. `meow-method`'s check for its old command name read the index marker on
its page once the page shipped inside the unit, so it skips the marker
ADR-1350 keeps. `CLAUDE.md` names four checks in `tools/`.

## Left alone

The catalogue fields, the generated index and `llms.txt`, which TSK-2040,
TSK-2050 and TSK-2060 do.
