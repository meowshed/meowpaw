---
id: REQ-4136
artifact: requirement
status: approved
cites: RES-0340, BUG-1403
---

# The installer names its own unit and cleans up after itself

Each package's install script names its own unit's release archive as its
download source, extracts the platform binary for the machine it runs on,
removes the archive it downloaded, and exits 0 where any step fails,
leaving the shell wrappers to report each check as unrun. The script runs
on ESM, so it imports what it calls and never names `require`.

Rationale: BUG-1403 found a `require` call inside a `.mjs` file and four
packages naming another unit's release, so the cleanup silently failed and
the log named a unit whose release the package does not ship. A failed
download must stop no install, because the wrappers' unrun report is the
designed behaviour for a missing binary, not an error.
