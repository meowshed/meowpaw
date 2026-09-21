---
id: BUG-1080
artifact: bug
status: approved
severity: major
violates: REQ-0692
found: 2026-09-21
revised: 2026-09-21
issue: 42
---

# The records cite commits the message rewrite replaced

## Reproduction

After rewriting every commit message on `main`, at `233e109`:

```bash
for h in $(grep -rhoE '`[0-9a-f]{7}`' project/ --include="*.md" | tr -d '`' | sort -u); do
  git cat-file -e "$h^{commit}" 2>/dev/null || echo "$h is gone"
done
```

Eleven hashes named commits that no longer existed. A twelfth, `fad8d0e` in
BUG-1000, resolves in this working copy and is unreachable from `main`, so a
fresh clone would not find it either.

## What the system does

Rewriting a message rebuilds the commit, so all 27 commits on `main` were
replaced and every hash in the record went stale. Those hashes are evidence
lines: TSK-1010 to TSK-1050 cite the commit that closed each task, EPC-1000 and
SPC-1000 carry `checked-at`, and five defect records cite the commit that
closed them.

An evidence line pointing at a commit nobody can fetch is evidence in name
only, which is what REQ-0692 forbids: a completed task records what closed it.

## What it should do, and why

A rewrite of published history is a decision with a cost, and the cost is
exactly this: every identifier derived from the old history has to be found and
repointed. REQ-2552 makes the same point for tools, by asking the harness to
cite an identifier that survives a rewrite where one exists.

Git offers no such identifier for a commit, so the record pays the cost by
hand, once per rewrite.

## Triage

Implementation. The requirements were right and the record went stale
underneath them.

## Closed by

Fifteen files repointed at the commits that now carry the work, checked with
the loop above, which reports nothing missing. BUG-1000's reference to
`fad8d0e` names the commit that replaced it.

What this does not fix: the four merged pull requests whose bodies cite the old
hashes. GitHub keeps them as text, and rewriting them again for hashes alone
would cost more attention than it returns, so they stand as a record of what
was true when they were written.
