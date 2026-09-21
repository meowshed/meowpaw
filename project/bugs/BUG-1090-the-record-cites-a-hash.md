---
id: BUG-1090
artifact: bug
status: approved
severity: minor
violates: REQ-2552
found: 2026-09-21
revised: 2026-09-21
issue: 44
---

# The record cites a commit hash where the pull request survives

## Reproduction

As #43 left the tree:

```bash
grep -rn '`[0-9a-f]\{7\}`\|checked-at:' project/ --include="*.md" \
  | grep -v '^project/research'
```

Twenty-seven lines: evidence in five task records, reproductions in seven
defect records, two `checked-at` fields, and two sentences in
`project/README.md`.

## What the system does

Every one of those cites a commit hash. Two rewrites of `main` this session
replaced every commit, so the citations died twice, and BUG-1080 repaired them
by pointing at the new hashes, which will die at the third rewrite.

The forge offers a number that survived both rewrites: the pull request. It
also reaches the commits it merged, so it loses nothing a hash carried.

## What it should do, and why

REQ-2552 already covers this. Where a tool provides an identifier surviving a
rewrite of the change it names, the harness cites that identifier and not the
one that does not. I read that requirement after the second rewrite rather
than before the first.

REQ-3176 now states the concrete form, so that somebody following the method
does not have to derive it: a record cites the pull request, including in a
field naming the revision a check ran at.

## Triage

Implementation, and a requirement worth stating. REQ-2552 was right and too
general to stop the habit, so REQ-3176 names the identifier and the field.

## Closed by

Every citation in the record is a pull request number. `checked-at` on EPC-1000
and SPC-1000 reads `"#27"`, which names the change that left the tree in the
state the verification read.

The four merged pull request bodies citing old hashes stand as they are, which
BUG-1080 already recorded: GitHub keeps them as text, and they say what was
true when they were written.
