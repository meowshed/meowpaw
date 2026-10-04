---
id: REQ-4120
artifact: requirement
status: draft
cites: RES-0340, RES-0341
---

# A Pi package carries a budget.toml for documentation

Each Pi package carries a `budget.toml` stating the permanent character cost
its skills and commands add to the system prompt, as the Claude Code plugins
do. Pi does not enforce this budget; the file documents the cost for the
package author and the installer.

Rationale: The budget is a real cost that affects model behaviour. Even though
Pi does not enforce it, recording it prevents the cost from growing unnoticed
and lets a repository decide whether to install a layer. The values are the
same as the Claude Code plugins state, because the skills and their
descriptions are unchanged.
