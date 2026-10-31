---
id: REQ-4128
artifact: requirement
topic: pi-packages
class: functional
status: withdrawn
revised: 2026-10-31
verification: behavioural
elaborates: RES-0340
---

# REQ-4128

**Withdrawn. Replaced by REQ-3684.**

It read: the record templates that `meow-flow` carries in `templates/` (research,
requirement, decision, specification, epic, task, defect) ship in the Pi
package's directory structure. The `paw template <kind>` command reads them
from `${CLAUDE_PLUGIN_ROOT}`, which the extension resolves to the package root.
No change to the template paths is needed.

Withdrawn by ADR-3090.
