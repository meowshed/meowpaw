---
id: REQ-4138
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
verification: behavioural
elaborates: RES-0340, BUG-1403
---

# REQ-4138

The platform binaries an install script downloads into a package's `bin/`
directory are ignored by the repository's source control, so no commit
carries a binary that was fetched at install time. The shell wrappers and
the install script are the committed source; the platform directory beside
them is not.

Rationale: BUG-1403's reproduction left a downloaded archive inside
`bin/`, and a binary fetched per machine inside a committed directory will
be committed the first time someone runs `git add` after an install. The
Claude Code plugins already ignore their `bin/*-*/` directories for the
same reason, and the Pi packages hold to the same line.
