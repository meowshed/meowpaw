---
id: TSK-5200
artifact: task
status: done
revised: 2026-10-04
realises: ADR-2780
closes: [REQ-4100, REQ-4102, REQ-4104, REQ-4106, REQ-4108, REQ-4110, REQ-4112, REQ-4114, REQ-4116, REQ-4118, REQ-4120, REQ-4122, REQ-4124, REQ-4126, REQ-4128]
issue: 835
---

# Write the research, requirements, decision and specification for the Pi packages

RES-0340 records what Pi provides as a platform. RES-0341 maps each meowpaw
plugin to its Pi analogue. REQ-4100–4128 state the obligations. ADR-2780
decides how the harness ships on Pi. SPC-1300 specifies the packages,
extensions, event handlers, commands, tools and the dual-platform contract.

## Acceptance criteria

1. RES-0340 covers Pi's extension, skill, package and event systems, the
   Claude Code analogue for each, what Pi provides that Claude Code does not,
   and what Claude Code provides that Pi does not. Closed by: the research
   document exists and cites its sources.
2. RES-0341 maps all sixteen plugins component by component and groups them
   into layer packages. Closed by: the mapping document exists and covers
   every plugin.
3. REQ-4100–4128 state one obligation each, each citing its research source.
   Closed by: the requirement files exist and their front matter is well
   formed.
4. ADR-2780 addresses every requirement, states the decision, the
   alternatives, the cost and the reversal conditions. Closed by: the ADR
   exists and its front matter lists every addressed requirement.
5. SPC-1300 states the package structure, the mapping, the dual-platform
   contract and what it does not cover. Closed by: the specification exists
   and lists every stated requirement.
6. EPC-2700 names the tasks that close the requirements and carries
   acceptance criteria from the ADR. Closed by: the epic exists and its task
   marks cover the work.
