---
id: REQ-3271
artifact: requirement
topic: delegation
class: functional
status: approved
revised: 2026-09-28
elaborates: RES-0016, RES-0263, RES-0284
verification: behavioural
---

# REQ-3271

Where a plugin's settings can set the session's nesting depth for delegation,
the harness MUST set it so that no subagent the main conversation dispatches
can dispatch another, in addition to each shipped agent withholding the
delegation tool (REQ-3270). A depth set anywhere other than the harness's own
settings wins, and the harness leaves it as it is: the user's, the
repository's or the repository-local settings, managed policy settings, or
the variable exported in the shell that starts the session. Today the way to
get that result is `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` set to `1`.

A subagent does the work it was given itself and doesn't delegate again
(RES-0263), because nested delegation is where cost and incoherence grow
without a matching gain (RES-0016). An agent the harness doesn't ship, such as
the platform's general-purpose agent, otherwise nests up to three levels
(RES-0284). The harness leaves a depth somebody else set, because that
setting is their choice, and overwriting it would take the choice away without
telling them.

RES-0284 found that a plugin can't set the depth today. The obligation holds
once a plugin's `settings.json` keeps an `env` key carrying
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, or a key for the depth, and the
platform ranks a plugin's settings below every other source named above. Where
the platform ranks them above any of those sources, a static entry would
replace a depth somebody else set, so the harness has to detect an existing
value before it sets one. Until a plugin can set the depth, the check reports
unresolved and never passed.
