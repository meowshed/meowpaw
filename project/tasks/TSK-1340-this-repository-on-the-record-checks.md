---
id: TSK-1340
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1070
closes: [REQ-1673]
issue: 145
---

# Move this repository onto the record checks the harness ships

One task, one branch, one pull request, one review.

## What to do

Declare `root = "project"` under `[record]` in `.meowpaw/profile.toml`, run
`meow-method check` from the `test` verb in place of `check_coverage.py`,
`check_front_matter.py`, `check_ids.py` and `check_research.py`, and delete
those four (REQ-1673). Change `CLAUDE.md`'s gate section to name the unit where
it names them. Add the unit's page, its entry in the marketplace and in
`docs/README.md`.

## Depends on

TSK-1330, because the verb runs the program and parity has to hold before the
scripts go.

## Evidence

`.meowpaw/profile.toml` declares `root = "project"` under `[record]`, the
`test` verb runs `meow-method check` where it ran the four scripts, and the
four are deleted. `CLAUDE.md`'s gate section names the unit, and the unit has
its page, its marketplace entry and its row in `docs/README.md`.

```text
$ meow-verbs run test
passed, exit status 0 after 6.3s
Ran 12 tests ... OK    Ran 14 tests ... OK    Ran 12 tests ... OK    Ran 18 tests ... OK
front-matter: 0 findings    identifiers: 0 findings    relations: 0 findings
index: 0 findings           coverage: 0 findings       shape: 0 findings
7 documents, 0 index failures
0 dangling links
summary: test passed

$ grep -rln -E 'check_(coverage|front_matter|ids|research)' . --exclude-dir=.git --exclude-dir=target --exclude-dir=project | wc -l
0
```

The record still names the four scripts where it recorded what they reported,
which is history and stays as written.

## Left alone

`tools/check_index.py`, `tools/check_links.py` and the checks over the
harness's own units.
