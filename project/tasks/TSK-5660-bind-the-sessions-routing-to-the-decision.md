---
id: TSK-5660
artifact: task
status: approved
revised: 2026-10-11
realises: ADR-2930
closes: []
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Bind the session's routing to the decision that decided it

ADR-2930 drops the router agent and has the session route each request under
the `route` skill, and the behaviour holds: no router agent ships,
`test_route.py` holds the skill's wording, and SPC-1090's "The route" section
states the classification the session makes. The task binds the decision to
what holds the behaviour, so the record names its plan (REQ-3902).

## Acceptance criteria

1. Given `plugins/meow-flow/`, when a test reads its agents, then no
   `router.md` ships, and the `route` skill does. Closed by:
   `plugins/meow-flow/tests/test_route.py`.
2. Given the specification, when a reader reads SPC-1090's "The route"
   section, then it states the session classifies the request itself and
   reports the route before any tool that writes runs. Closed by: the
   section's own text.

## What to do

Write the task's Evidence citing both. The behaviour, the specification and
the tests already hold, and this task writes none of them again.

## Depends on

Nothing.

## Evidence

Criterion 1 closes with `plugins/meow-flow/tests/test_route.py`, which
holds that no router agent ships and the `route` skill does. Criterion 2
closes with SPC-1090's "The route" section, which states the session
classifies the request itself and reports the route before any tool that
writes runs.

The five stages passed at tree `4364d882ff98`, each bound by `meow-checks run` and
confirmed by `meow-checks evidence`, exit 0: format `fcdc5ab700f0`, check
`c6bd6909315a`, lint `19fafec9381e`, test `fb6e4836449c`, build `a982d16b0043`.

## Left alone

The router's allowlist tests, which ADR-2100 held and ADR-2930 deleted with
the agent.
