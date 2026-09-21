---
id: BUG-1005
artifact: bug
status: approved
severity: minor
violates: REQ-0704
found: 2026-09-21
revised: 2026-09-21
issue: 12
---

# The constitution cited deleted pages and overstated what verifies a commit

**This record was written after the work, from #12, its pull request and
`998117f`, and not from the work as it happened.** BUG-1020 says why that is
worse: a record written later is written from memory. It exists because #12
mapped to no record at all, which REQ-1360 forbids, and the choice was between
a late record and none.

## Reproduction

Before `998117f`:

```bash
grep -n "docs/plugins.md" CLAUDE.md          # two citations
ls docs/                                      # the tree does not exist
git log --show-signature -1 main | head -3    # a key that is not in allowed_signers
```

## What the system does

`CLAUDE.md` named `docs/plugins.md` twice: once as the document proposing the
plugin catalogue, and once as a file to update when the plugin list changes,
"and the count in all three". The `docs/` tree had been deleted on the owner's
instruction, so both citations resolved to nothing, and the second asked an
author to keep one count in three places, which is the defect BUG-1000 closed
in the same file.

`CLAUDE.md` also said every commit is cryptographically signed and
`.github/allowed_signers` names the key that verifies it. GitHub rebuilds a
commit when it squashes a pull request and signs it with its own web-flow key,
so the tip of `main` verified against GitHub and not against the named key.

## What it should do, and why

Checking the record reports artifacts whose recorded state contradicts the tree
(REQ-0704). A citation of a deleted file is exactly that, and no check reaches
the constitution's prose, so nothing caught either statement.

A rule that overstates what holds teaches a reader to discount the rules that
do hold. The signing rule was true of the commits a person writes and false of
the commit the forge builds, and it stated neither boundary.

## Triage

Implementation. The requirements were right and the file was wrong.

## Closed by

`998117f`, which removed both citations, replaced the maintenance entry with
one that names the plugins in a single place, and narrowed the signing rule to
state what holds on a branch and what the forge does on a squash merge. The
owner accepts the forge signing merges.
