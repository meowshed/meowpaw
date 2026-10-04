---
id: TSK-5208
artifact: task
status: approved
revised: 2026-10-04
realises: ADR-2790
fixes: [BUG-1403]
closes: [REQ-4136, REQ-4138, REQ-4118]
---

# Hold the installer and the downloads

Each package's install script names its own unit's release archive,
extracts the platform binary, removes the archive, runs on ESM with no
`require`, and exits 0 on any failure. The repository ignores the platform
directories the scripts fill.

## Acceptance criteria

1. Given each package's install script, when its `const UNIT` line is read,
   then it names the package's own unit. Closed by: reading the six scripts.
2. Given the kernel package's install script run twice, when it finishes,
   then no `.tmp-*.zip` remains in `bin/`. Closed by: running the script
   twice and listing the directory.
3. Given the install script on a machine it cannot download for, when the
   download fails, then the script exits 0 and prints a warning. Closed by:
   running the script with an unreachable URL.
4. Given a clean clone after an install, when `git status` runs, then no
   platform binary or archive is reported. Closed by: installing into a
   clean clone and running `git status`.
