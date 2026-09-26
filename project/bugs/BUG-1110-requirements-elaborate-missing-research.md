---
id: BUG-1110
artifact: bug
status: approved
severity: minor
violates: REQ-0656
found: 2026-09-26
revised: 2026-09-26
issue: 164
---

# Eight requirements elaborate research that never existed

## Reproduction

With `meow-method` built from #144 in this repository:

```bash
plugins/meow-method/bin/meow-method check relations
```

It reports eight findings of one form, for example:

```text
project/requirements/REQ-1326-never-commit-unsigned.md:8: elaborates names RES-0045, which has no file
relations: 8 findings
```

## What the system does

REQ-0036, REQ-0038, REQ-0560, REQ-1314, REQ-1326, REQ-1662, REQ-2078 and
REQ-2630 name RES-0007, RES-0008, RES-0009, RES-0043 or RES-0045 in
`elaborates`. No file under `project/research/` carries those identifiers, and
`git log --all --name-only` shows none ever did. Each of the eight also
elaborates research that exists, so none is left without a source.

## What it should do, and why

REQ-0656 says checking the record must report a relation whose identifier
doesn't resolve, because a relation nobody can follow tells the reader where a
claim came from and then sends them nowhere. None of the four scripts in
`tools/` checked relations, so the defect sat in approved records unreported.

## Triage

Implementation. REQ-0656 is right, and `meow record`'s relations check, built
by TSK-1330, is what realises it. The records need the dangling identifiers
removed, as BUG-1080 repointed citations in approved records.

## Closed by

The five identifiers are gone from the eight requirements' `elaborates`, and
each keeps the research that exists. `meow-method check relations` on this
tree reports `relations: 0 findings`, and TSK-1330's relations fixture keeps
it as a regression check.
