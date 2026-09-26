---
id: BUG-1120
artifact: bug
status: approved
severity: major
violates: REQ-3178
found: 2026-09-26
revised: 2026-09-26
issue: 170
---

# The install instructions gave a unit without its binary

## Reproduction

Follow the install section of `docs/meow-scm.md` as #169 left it:

```bash
claude plugin marketplace add meowshed/meowpaw
claude plugin install meow-scm@meowpaw
printf 'feat: add a thing\n' | "$(ls -d ~/.claude/plugins/cache/meowpaw/meow-scm/*)"/bin/meow-scm check-message
```

The check prints `unchecked (no meow binary was found for this machine)` and
exits 3.

## What the system does

Six pages under `docs/` and the root `README.md` said to add the marketplace
from `meowshed/meowpaw`, which Claude Code clones as a git repository. The git
tree carries no binaries, because `.gitignore` excludes `plugins/*/bin/*-*-*/`
and only a release builds them, so `meow-verbs`, `meow-scm` and `meow-git`
installed this way report every check unrun or unchecked. The root `README.md`
also said the harness wasn't installable, and named `meow-rust`, which doesn't
exist.

## What it should do, and why

REQ-3178 says the harness must not require anything a person installs
separately from the units it ships. A unit whose binary isn't there needs a
Rust toolchain and a build, which is exactly that. The released marketplace
carries each unit with its binaries, and RES-0274 records how a person adds it.

## Triage

Implementation, in the documentation. TSK-1380 changed `docs/README.md` and
SPC-1080 to the released form and left the unit pages as they were.

## Closed by

Every page's install section and the root `README.md` download the released
`marketplace.json` and add it by its path, so a person following any of them
gets the same marketplace, named `meowpaw`, with the binaries in it.
`grep -rn 'marketplace add meowshed' --include='*.md' --exclude-dir=project .`
finds nothing.
