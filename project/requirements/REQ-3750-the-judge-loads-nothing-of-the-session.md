---
id: REQ-3750
artifact: requirement
topic: prose-and-comments
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0330
source: the repository owner's request, and BUG-1230
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3750

The model call the gate makes MUST run with no hook, plugin, skill, MCP
server, project instruction or tool loaded.

A judge that loads plugins loads the gate's own hook again, and one that loads
the project's instructions takes them as its own (RES-0330). A judge reads a
text and answers, so it needs no tool.
