---
id: REQ-4100
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
verification: behavioural
elaborates: RES-0340
---

# REQ-4100

The kernel, method, practice and pack layers each ship as a Pi package
containing the extensions, skills and supporting files for that layer. A Pi
package is an npm package or git repository with a `package.json` that declares
its resources under the `pi` key and its runtime dependencies in
`peerDependencies`.

Rationale: Pi installs and loads packages, not individual plugins. A package
per layer keeps the dependency direction (kernel → method → practice → packs)
and lets a repository install only the layers it needs, which is the same
install-only-what-you-need property the Claude Code marketplace provides.
