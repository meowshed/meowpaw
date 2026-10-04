---
id: REQ-4118
artifact: requirement
status: draft
cites: RES-0340
---

# Native binaries ship alongside the Pi package

The compiled native binaries (`paw`, `meow-git`, `meow-prose-gate`,
`meow-loop`, `meow-github`, `meow-scm`, `meow-checks`, `meow-licence`,
`meow-author`, `meow-markdown`, `meow-mise`, `meow-gotask`,
`meow-unattended`) ship as platform-specific executables in the Pi package or
as a separate npm package that the Pi package depends on. The extension
resolves each binary's path relative to the package root.

Rationale: REQ-4106 requires shelling out to the existing binaries. They must
be findable at runtime. Pi packages can carry arbitrary files; platform-specific
executables go in `bin/` with the platform triple, as they do in the Claude
Code plugin. A separate package avoids duplicating the binaries when several
meowpaw Pi packages share them.
