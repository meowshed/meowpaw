---
id: REQ-4124
artifact: requirement
status: approved
cites: RES-0340
---

# Evals have no Pi equivalent and are deferred

The eval suites that Claude Code plugins carry (`meow-core/evals/`,
`meow-prose/evals/`, `meow-author/evals/`, `meow-flow/evals/`,
`meow-prose-gate/evals/`) have no Pi equivalent. They are not carried in the
initial Pi packages. A future extension may register a `paw eval` command that
runs prompt suites with graders, reproducing `claude plugin eval`.

Rationale: Pi has no eval infrastructure. Building one is a separate decision
with its own requirements. The existing eval suites remain in the repository
for use with the Claude Code plugins and for a future Pi eval runner to
consume.
