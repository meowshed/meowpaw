---
id: REQ-4124
artifact: requirement
topic: pi-packages
class: functional
status: withdrawn
revised: 2026-10-11
verification: static
elaborates: RES-0340
---

# REQ-4124

**Withdrawn by ADR-2980 on 2026-10-11. No replacement.**

The eval suites that Claude Code plugins carry (`meow-core/evals/`,

It made the measurement of a prompt obligatory, and ADR-2980 removed prompt
evaluation whole, because the owner will redesign it in future.

`meow-prose/evals/`, `meow-author/evals/`, `meow-flow/evals/`,
`meow-prose-gate/evals/`) have no Pi equivalent. They are not carried in the
initial Pi packages. A future extension may register a `paw eval` command that
runs prompt suites with graders, reproducing `claude plugin eval`.

Rationale: Pi has no eval infrastructure. Building one is a separate decision
with its own requirements. The existing eval suites remain in the repository
for use with the Claude Code plugins and for a future Pi eval runner to
consume.
