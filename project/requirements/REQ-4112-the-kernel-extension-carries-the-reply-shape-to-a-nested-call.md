---
id: REQ-4112
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
verification: behavioural
elaborates: RES-0340
---

# REQ-4112

Where the output style's rule R10 says to include the reply shape in any prompt
that dispatches a subordinate agent, the kernel extension's tool (or any tool
that makes a nested model call) includes the reply shape in the nested call's
messages. The extension reads the reply shape once on load and provides it to
every nested call that the meow-flow extension's router tool or skeptic tool
makes.

Rationale: A nested model call runs its own system prompt and does not inherit
the session's. Rule R10 of the reply shape is load-bearing: without it, a
dispatched agent answers in whatever shape it likes. The extension enforces
this by construction.
