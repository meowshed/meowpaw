---
id: ADR-1060
artifact: adr
status: approved
revised: 2026-09-23
addresses: [REQ-0077]
supersedes: []
---

# 1060. The kernel names no unit outside it

## Decision

No prompt, hook or manifest in `meow-core` names, points to or loads a unit
outside the kernel (REQ-0077). A unit outside the kernel may name the kernel,
because the kernel is always installed. The check `tools/check_kernel.py`
runs in the gate and fails when a file in `meow-core` names another plugin in
`plugins/`.

## Why

A proposed R9 told the model to load the writing skill before its first reply,
and yielded when the skill wasn't installed. That satisfied REQ-0076, and it
still made the reply shape depend on whether `meow-prose` was installed, which
is the coupling the layers exist to prevent. The pull request was closed
without merging.

## Alternatives

| Option                                | Better at                               | Why it lost                                                          |
| ------------------------------------- | --------------------------------------- | -------------------------------------------------------------------- |
| The kernel names no unit outside it   | Behaving the same with any set of units | Chosen                                                               |
| Naming an optional unit, with a yield | Reaching the unit from every session    | The kernel's behaviour then depends on what else is installed        |
| Leaving it to review                  | Costing no program                      | REQ-2260 asks for a check wherever a program can settle the property |
| Do nothing                            | Costing nothing                         | The next change to the kernel repeats the proposal                   |

## What it costs

A reply in a session without `meow-prose` and a reply in one with it get the
same kernel instructions, so the kernel can't route a reply to the writing
standard. The standard reaches a reply only through its own description.

The check knows the kernel as `meow-core`. When another kernel unit is added,
the check's list of kernel units changes with it.

## What would reverse it

- The platform lets a unit declare an optional dependency and loads the
  kernel's instruction only when that dependency is present. The kernel could
  then point at the unit without behaving differently where it's missing.

## Consequences

- `tools/check_kernel.py` joins the gate as `mise run kernel`.
- SPC-1030 states the rule for kernel prompts.

## How I will know it was realised

1. `mise run all` runs the kernel check and passes on the tree as it stands.
2. The check fails on a probe that adds `meow-prose` to a file in `meow-core`,
   naming the file and the line.

## What this does not settle

- A kernel prompt pointing at a unit without naming it, such as "the writing
  skill". The check reads names, so review holds that case (REQ-2262).
