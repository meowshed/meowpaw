---
id: REQ-4128
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
verification: behavioural
elaborates: RES-0340
---

# REQ-4128

The record templates that `meow-flow` carries in `templates/` (research,
requirement, decision, specification, epic, task, defect) ship in the Pi
package's directory structure. The `paw template <kind>` command reads them
from `${CLAUDE_PLUGIN_ROOT}`, which the extension resolves to the package root.
No change to the template paths is needed.

Rationale: Templates are referenced by `paw template <kind>`, which resolves
them relative to the binary's installation location. As long as the binary and
the templates ship in the same package, the path resolution works identically.
