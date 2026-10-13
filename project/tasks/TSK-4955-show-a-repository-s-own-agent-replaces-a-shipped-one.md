---
id: TSK-4955
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2530
closes: [REQ-2986]
issue: 973
projected: de54de2140eb
tracked: c302ee7726f3
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Show that a repository's own agent replaces a shipped one of the same name

A fixture shows that an agent a repository defines in `.claude/agents/` under
a shipped agent's name is the one the platform loads, and each unit that
ships an agent says so on its page, as SPC-1030 states under "Delegation".
One task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository with `meow-flow` installed and a
   `.claude/agents/router.md` whose body differs from the unit's, when a
   session dispatches the router, then the dispatched agent is the
   repository's (REQ-2986). Closed by: a hand-run case under
   `plugins/meow-flow/evals/`, naming REQ-2986, which rests on judgement
   because the platform's choice can't be read by a fixture in CI.
2. Given `plugins/meow-flow/README.md` and `plugins/meow-prose/README.md`,
   when a test reads them, then each says how to replace its agent and that
   the repository's definition wins. Closed by: a test under `tools/`.

## What to do

Write the case and the two README sections. Where the platform loads the
plugin's agent under its namespaced name and the repository's under the bare
name, so that both exist, state on each page which name a dispatch uses and
record a defect against REQ-2986.

## Depends on

Nothing.

## Evidence

Not yet.

Criterion 1 rests on judgement, because a fixture in CI can't read which
definition the platform dispatches, and it can't be met as written: it names
`.claude/agents/router.md`, and `meow-flow` stopped shipping the router agent
when routing moved into the session. A case run by hand once on `sonnet`, for
the researcher agent the unit does ship, and not kept, as ADR-2980 asks, found that
the platform keeps both definitions: a dispatch of `meow-flow:researcher`
reached the unit's, and only `researcher` reached the repository's. That is
the case What to do names, so REQ-2986 needs a defect, which isn't recorded
yet.

Criterion 2 is checked by `ReplacingAnAgent` in
`tools/test_shipped_agents.py`, which holds each page to saying how to
replace its agent and which name reaches which definition. Neither page says
the repository's definition wins, because the run shows it doesn't.

## Left alone

The shipped agents' definitions, which stay as SPC-1030 states.
