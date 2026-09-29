---
id: REQ-3271
artifact: requirement
topic: delegation
class: functional
status: approved
revised: 2026-09-29
elaborates: RES-0016, RES-0263, RES-0284
verification: behavioural
---

# REQ-3271

Where a plugin's settings can set the session's nesting depth for delegation,
and the platform ranks them below the user's and the repository's settings,
the harness MUST set the depth so that no subagent the main conversation
dispatches can dispatch another, in addition to each shipped agent withholding
the delegation tool (REQ-3270). A depth set in the user's or the repository's
settings then wins over the harness's. In Claude Code 2.1.280 (RES-0284) the
setting that gives that result is `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` set
to `1`.

A subagent does the work it was given itself and doesn't delegate again
(RES-0263), because nested delegation is where cost and incoherence grow
without a matching gain (RES-0016). An agent the harness doesn't ship, such as
the platform's general-purpose agent, otherwise nests up to three levels by
default (RES-0284). The harness's setting ranks below the user's and the
repository's, because theirs is their choice, and overwriting it would take
the choice away without telling them. RES-0284 found that the variable
overrides the platform's remote feature flag and read no other place the
depth can be set, so any other place, such as the shell environment, is
outside this requirement.

RES-0284 found that a plugin can't set the depth today, because a plugin's
`settings.json` keeps only `agent` and `subagentStatusLine`. Until both
conditions above hold, the check reports unresolved and never passed, because
an obligation nothing can meet yet hasn't been shown met
(`unresolved_is_not_a_pass` in the constitution).
