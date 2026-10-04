---
id: REQ-4114
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
verification: static
elaborates: RES-0340
---

# REQ-4114

Each meowpaw Pi package declares `@earendil-works/pi-coding-agent` and the
other host packages Pi supplies (`@earendil-works/pi-ai`,
`@earendil-works/pi-agent-core`, `@earendil-works/pi-tui`, `typebox`) in
`peerDependencies` with a `"*"` range. It does not list them in
`dependencies`, because a physical copy creates duplicate classes and
registries.

Rationale: Pi supplies these packages to extensions and skills at runtime.
Listing them in `dependencies` would install a second copy under the package's
own `node_modules`, which Pi detects and reports as a warning. The `"*"` range
accepts whatever Pi provides.
