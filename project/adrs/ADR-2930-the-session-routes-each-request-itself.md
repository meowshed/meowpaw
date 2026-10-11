---
id: ADR-2930
artifact: adr
status: approved
revised: 2026-10-11
addresses:
  [
    REQ-0330,
    REQ-0332,
    REQ-0334,
    REQ-0336,
    REQ-0338,
    REQ-0340,
    REQ-0342,
    REQ-0344,
    REQ-0346,
  ]
supersedes: [ADR-2100]
---

# 2930. The session routes each request itself under the route skill, and no dispatch runs before work

## Decision

`meow-flow` keeps the `route` skill and drops the router agent and every
dispatch behind it. The session that receives a request to change the
repository classifies it itself, under the skill, and reports the route and
its reason as the first thing in its reply, before any tool that writes runs
(REQ-0330, REQ-0332). The three sizes and four shapes are ADR-2100's, carried
unchanged (REQ-0334, REQ-0344); the override words stand (REQ-0336); where the
evidence points to two sizes the route takes the larger and says `ambiguous`
with the evidence on each side (REQ-0338, REQ-0340); the classification reads
the request and the repository together, and its reason names at least one
path or identifier it read (REQ-0342); and the classification writes no
artifact (REQ-0346).

What the route loses is the classifier that cannot write by construction. The
skill holds the session back with an instruction alone, and the session reads
the conversation that asked for the fix. What it gains is a route that costs
no dispatch, fails into a working classifier, and holds one guarantee on both
platforms.

On Claude Code the router agent, `plugins/meow-flow/agents/router.md`, is
deleted, with the static tests that hold its allowlist. On Pi the
`meow-router` tool is deleted with the nested model call behind it
(`packages/meow-flow/extensions/flow.ts`, `packages/meow-flow/lib/router.mjs`,
`packages/meow-flow/prompts/router.md`), and REQ-4110, which mapped the agent
to that tool, is withdrawn. The route skill carries the same text on both
platforms, as REQ-4614 asks.

After this decision every request to change a repository still starts with a
stated route and its reason, a typo goes straight to its edit, and a change
the words make sound small but the repository shows is large starts at
research. What still doesn't work is what ADR-2100 already named for the main
session: nothing stops the session writing before it reports the route, and
the route leaves no trace in the record.

## Why

ADR-2100 weighed the main session classifying under the skill and rejected it
for two reasons: the classifier could write, held back only by an instruction,
and it read the conversation that asked for the fix. Both reasons weaken, and
one of them has since failed in the field.

The dispatch sat on the critical path of every request, and the failure this
repository watched was not slower routing but no routing: on Pi the nested
call behind `meow-router` answered `content.some is not a function` for the
session's whole catalogue (BUG-1620), so every request fell to the safe
default and paid the full chain for a typo. A classifier whose failure mode is
the most expensive route costs more than the bias it prevents. The read-only
allowlist the dispatch bought exists only on Claude Code: Pi's nested call
never had tools to allowlist, so the parity REQ-4614 asks kept a weaker copy
of the guarantee on one side, and the stronger one broke. The remaining
difference between the two mechanisms is the instruction, and ADR-2100's own
reversal triggers name that trade: it would move the classification into the
main session when the dispatch costs more than it buys, and it measured the
dispatch at 12.8 s to 19.7 s and USD 0.05 to USD 0.10 per request in a
one-file repository.

The bias the dispatch guarded against is real and is held where it is cheap:
the route is still the first thing in the reply, the person still overrides in
one word, and in a run the transcript still shows what the route was. What is
given up is the guarantee that the classifier cannot write, in exchange for a
guarantee that routing happens at all.

## Alternatives

| Option                                                | Better at                                     | Why it lost                                                                                                                                    |
| ----------------------------------------------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Keep the dispatch, fix the nested call                | Keeps the read-only classifier on Claude Code | The nested call's throw is Pi's adapter, outside this repository, and a fixed call still pays the dispatch per request                         |
| A hook that classifies on keywords                    | Deterministic, no model                       | RES-0053 found a keyword classifier fails the first time somebody describes an architectural change in plain words                             |
| A hook denying writes until a route is reported       | Enforces report-before-edit by construction   | RES-0203 found the transcript a hook reads lags the conversation, and it would run on every tool call in every session                         |
| Keep the agent on Claude Code and drop the tool on Pi | Keeps the stronger guarantee where it exists  | REQ-4614 holds a unit's contract equal across the two distributions, and a route that behaves differently per platform is two methods, not one |

## What it costs

The session classifies with its own context, so a route can be framed by the
conversation that asked for the change, and nothing but the skill's
instruction and the person's override stands against it. The route evals lose
the tool-order grader that measured route-before-edit through the dispatch;
the regex grader that replaces it measures that the reply carries the route
fields, and the ordering rests on the instruction and the hand-run cases.

## What would reverse it

- If a hand-run of the route cases shows the session writing before it reports
  the route more often than it reports first, or routing a plain-words
  architectural change as a typo fix, I would bring a classifier back, as a
  hook that can read the conversation as it stands rather than a dispatch.
- If a route-reporting hook becomes possible because the platform lets a hook
  read the conversation as it stands, I would reconsider the hook ADR-2100
  rejected.

## Consequences

- The route skill states the sizes, the shapes, the report and the overrides,
  and no step dispatches anything; its description keeps the wording
  RES-0272 measured.
- `agents/router.md` and its static tests are deleted; the unit's budget drops
  to what the check measures without the agent's description.
- Pi carries no `meow-router` tool and no nested call in `meow-flow`; the
  router module and the two prompt files it read are deleted with it.
- SPC-1090's route section states the session classifying under the skill, and
  SPC-1300's agent mapping names no router.
- BUG-1620 is withdrawn, naming this decision, because the tool it reported is
  gone; the task that fixed it is withdrawn with it.
- ADR-2100 is superseded, and its nine requirements stay in force: this
  decision meets them by the session's own act.

## How I will know it was realised

1. A case asking to fix a typo reports the route and its reason as text before
   the edit, with no dispatch, and the same holds for the plain-words and
   ambiguous cases on both platforms.
2. `plugins/meow-flow/` carries no `agents/router.md`, and `packages/meow-flow/`
   registers no `meow-router` tool.
3. The unit's budget check measures fewer permanent characters than before.
4. The route evals pass on a hand run, with the regex grader measuring the
   route fields in the reply.
5. Every requirement this decision addresses is met by the route skill's text,
   and REQ-4110 is withdrawn naming it.

## What this does not settle

- A record of the route taken, which ADR-2100 also left unsettled.
- A hook that enforces report-before-edit, which waits on the platform reading
  the conversation as it stands.
- The Pi mapping for the prose reviewer, which ADR-2950 states in the same
  change: the reviewer keeps its subagent and maps to a Pi tool.
