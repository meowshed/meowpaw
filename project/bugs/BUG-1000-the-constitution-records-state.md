---
id: BUG-1000
artifact: bug
status: approved
severity: major
violates: REQ-0704
found: 2026-09-21
revised: 2026-09-21
issue: 10
---

# The constitution records state, and part of it is false

## Reproduction

Read the second and third paragraphs of `CLAUDE.md`, then check each fact
against the tree:

```bash
git ls-tree -r --name-only pre-squash-backup | grep -c "ADR-"   # 0
ls project/research/*.md | wc -l                                # 126
grep -rhoE "REQ-[0-9]{4}" project/requirements/*.md | sort -u | wc -l   # 1053
```

The first command contradicts the sentence saying `pre-squash-backup` holds the
deleted decision records. The second and third agree with the counts today, and
they agreed with different counts a day ago.

## What the system does

`CLAUDE.md` states the milestone, the count of research documents, the count of
requirements, which decision is in force, which specification exists, and which
paths do not exist yet. It also states that `pre-squash-backup` holds the fifty
deleted decision records.

The branch holds no such record. Those records lived in `project/adrs/_archive/`,
which `.gitignore` matched, so they were never committed and no branch carries
them. The sentence was written on 2026-09-21 and merged as part of `fad8d0e`.

`project/README.md`, `project/adrs/README.md` and
`project/requirements/README.md` carry the same facts, next to the artifacts
they describe, and they are updated by the change that moves the work.

## What it should do, and why

A stored status is updated in the same change that moves the work it describes
(REQ-0690). Checking the record reports artifacts whose recorded state
contradicts the tree (REQ-0704). Neither check reaches the constitution,
because no identifier ties its prose to an artifact, so nothing notices when a
count or a claim stops being true.

The constitution's own layout section already states the rule it breaks: the
harness computes an observed status from the tree and never writes one into a
file. What `CLAUDE.md` should carry is the rules, and what it should say about
state is where to read it.

## Triage

A requirement in force covers it, so this enters at implementation and needs no
amendment. The correction is a `fix` change: remove the state, add the rule
that keeps it out, and record the defect here.

## Closed by

The reproduction, now passing: `CLAUDE.md` carries no count, no milestone, no
list of what is in force, no "doesn't exist yet" and no claim about
`pre-squash-backup`. The regression check is the first command above, which
returns zero and has nothing left to contradict.

`docs/README.md` and the three indexes under `project/` remain the place where
state is read.
