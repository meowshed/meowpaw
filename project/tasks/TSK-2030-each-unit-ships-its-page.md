---
id: TSK-2030
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1350
closes: [REQ-2838, REQ-3130, REQ-3136, REQ-3138, REQ-3142, REQ-3148, REQ-3152]
issue:
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

Not yet.

## Left alone

The catalogue fields, the generated index and `llms.txt`, which TSK-2040,
TSK-2050 and TSK-2060 do.
