---
id: ADR-1700
artifact: adr
status: approved
revised: 2026-09-28
addresses:
  [REQ-2972, REQ-2974, REQ-2976, REQ-2982, REQ-2984, REQ-2988, REQ-3270]
postpones: [REQ-3271]
supersedes: []
---

# 1700. Every shipped agent declares its turns, tools, model, effort, instructions and skills, and meow-author check fails one that doesn't

## Decision

An agent definition declares six fields in its front matter, and
`meow-author check` fails one that leaves any of them out, naming the file and
the field. The six fields, and what the check accepts for each:

| Field          | The check accepts                                                              | Requirement |
| -------------- | ------------------------------------------------------------------------------ | ----------- |
| `maxTurns`     | A positive integer                                                             | REQ-2974    |
| `tools`        | A written list; in a unit's agents, one with no `*` and no `Agent` or `Task`   | REQ-3270    |
| `model`        | An alias or a full model identifier, and not `inherit`                         | REQ-2988    |
| `effort`       | `low`, `medium`, `high`, `xhigh` or `max`                                      | REQ-2988    |
| `omitClaudeMd` | `true` or `false`, written out                                                 | REQ-2982    |
| `skills`       | A list of the skills the agent preloads, and an empty list where it needs none | REQ-2984    |

The check reads every file in a unit's `agents/` directory, as it already does
for `description`, and it reads a repository's own agents when it is given
their path, such as `.claude/`, because REQ-1678 holds a repository's material
to the same rules. The delegation part of the `tools` rule, no `*` and no
`Agent` or `Task`, applies only to a unit's `agents/` directory, because
REQ-3270 binds the agents the harness ships and a repository can keep an agent
of its own that orchestrates others. A repository's own agent passes the
`tools` rule once it writes a list, `*` included, because a written list is a
choice somebody made, where a missing one is a default nobody wrote down. A
front matter block that doesn't parse fails the check with that reason, and
the six field rules aren't run on it, because a field read from a broken block
is a guess. `tools` is read as a YAML list or as the
comma-separated string the platform also accepts, and an entry naming the
delegation tool with a restriction, such as `Agent(worker)`, fails too,
because it still delegates.

Each rule has its reason, and the reasons come from RES-0284:

- `maxTurns` is the ceiling the runner enforces, and it returns the output
  marked partial when the agent reaches it. RES-0284 read the marking from
  the code and the documentation, and realisation 4 is the first run to show
  it.
- A missing `tools` list and `*` both grant every tool, the delegation tool
  among them, so the list is what keeps the depth below a shipped agent at
  none. The platform's delegation tool is `Agent`, and it still recognises
  the earlier name `Task`.
- `inherit` leaves the model, and so the cost, to whichever session
  dispatches the agent, so nobody chose what a dispatch of it costs.
- `effort` is one of the five levels the documentation names. The binary also
  takes an integer, which the documentation doesn't name, so the next version
  may drop it. The check doesn't test an effort against the model, because
  the documentation says only that the levels depend on the model, and
  RES-0284 found no table of which model offers which level.
- The platform honours `omitClaudeMd` only when it is true, so a missing key
  loads the project's instructions exactly as `false` does, and only a
  written value shows that somebody decided.
- `skills` decides what the agent loads at startup and grants nothing, so an
  empty list is a statement that the agent needs nothing preloaded.

The two agents the harness ships change in the same change as the check, so
the gate stays green. I chose each value, as M2 of the method skill allows,
and the task's evidence carries them:

| Agent                       | `maxTurns` | `model`  | `effort` | `omitClaudeMd` | `skills`               | `tools`          |
| --------------------------- | ---------- | -------- | -------- | -------------- | ---------------------- | ---------------- |
| `meow-flow:record-reviewer` | 30         | `opus`   | `high`   | `false`        | `[]`                   | Read, Grep, Glob |
| `meow-prose:prose`          | 20         | `sonnet` | `high`   | `true`         | `[meow-prose:writing]` | Read, Grep, Glob |

`record-reviewer` loads the project's instructions, because it judges a record
against the repository's principles, and those live there. `prose` omits
them, because it judges a text against the writing standard it preloads, and
a constitution in its context is a second standard it could mix in. The
reviewer runs on `opus`, because a missing section is found by reasoning
about what the record's kind needs, and `prose` runs on `sonnet`, because it
applies a fixed list of rules to one text line by line. Both run at `high`,
because a missed finding costs a later fix and a defect record, which is more
than the extra tokens `high` spends over `medium`, and `xhigh` and `max` are
the two dearest levels with no case yet showing they find more. The two model
choices and the two effort levels are my defaults, and no measurement stands
behind any of them. The ceilings
are about three times the turns I expect a review to take: the reviewer reads
the record, the records it cites and a few searches, and `prose` reads one
text and its standard.

A dispatcher that gets an output marked partial treats the work as
unfinished, until realisation 4 shows whether the marking appears. The method skill reports a record whose review stopped at its
ceiling as unreviewed by an agent, as M22 already says for a review that
couldn't run, because a partial list of findings reads as a complete one.

`meow-author:write` gains the rules that a program can't check:

- Knowledge, such as a lens or a language's idioms, ships as a skill loaded
  into the working context and never as an agent, because it needs no
  isolation and an agent pays for a fresh context and a summary on every
  dispatch (REQ-2972).
- A delegated agent runs in the parent's process and under the parent's
  sandbox configuration, so no text the harness ships treats one as a
  boundary that contains what the agent does (REQ-2976).
- One rule for each of the six fields, stating the reason above.
- A dispatcher reads an output marked partial as unfinished work.

REQ-0820 asked the harness to set the nesting depth for delegation to one.
RES-0284 found that the depth is the variable
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, which only the user's or the
repository's settings can set, because a plugin's own settings keep only
`agent` and `subagentStatusLine`. So I withdrew REQ-0820 and replaced it with
two requirements: REQ-3270 withholds the delegation tool from every agent
the harness ships, which this decision meets, and REQ-3271 asks for the session's depth
where a plugin can set it, which this decision postpones until a plugin's
`settings.json` applies an `env` table or a depth key.

After this decision every agent the harness ships runs under a turn ceiling
the runner enforces, can't delegate, runs on a model and effort it names, and
says whether it loads the project's instructions and which skills it
preloads. A repository that runs the check over its own agents, by giving it
their path, gets a failure for an agent of its own that leaves one of the six
fields out.

What still doesn't work:

- A repository whose gate doesn't pass its agents' path to the check gets no
  check of its own agents. This repository's `prompts` task runs
  `author check` with no path, so its own agents aren't checked either.

- A session's own agents, including the platform's general-purpose agent,
  still nest up to three levels, because REQ-3271 waits on the platform.
- A repository's own agents may still delegate, because REQ-3270 binds only
  the agents the harness ships.
- The check can't tell whether an agent's `skills` list is the right one, or
  whether a unit shipped knowledge as an agent. Review holds both.
- A model alias follows whatever model the platform maps it to, so a shipped
  agent's cost changes when the mapping does, and no check sees it.

## Why

RES-0263 concluded that every dispatch declares a turn ceiling the runner
enforces, a model and an effort, that whether an agent loads the project's
instructions is decided per agent, that a narrow agent preloads its skills,
that knowledge ships as a skill, that a delegate isn't an isolation boundary
and that depth is a setting. RES-0284 observed which of those a plugin agent
can declare on Claude Code 2.1.280, and what the platform does when a field
is missing.

REQ-2694 asks for a check wherever a program can settle a rule. Five of the
seven obligations are fields a program reads, so they go in `meow-author
check`, which already reads every agent the harness ships and
runs in the `lint` verb. The remaining two, REQ-2972 and REQ-2976, are about
what a unit chooses to be and how its text describes delegation, which no
field shows, so they are rules in the write skill and a judgement at review.

Requiring each field to be written out, where the platform has a default for
every one of them, is the point. Each default is a decision nobody wrote
down: every tool, the session's model and effort, the project's instructions
loaded and nothing preloaded. REQ-2982 asks that the instructions be decided
per agent, and a default decides the same way for all of them.

The strongest objection is that naming a model makes a shipped agent fail
where the model isn't offered, which `inherit` never does. I accept that,
because the failure is visible at dispatch and a repository can replace the
agent (REQ-2986), where `inherit` fails silently: the review runs, on
whatever model the session had, at a cost nobody chose.

## Alternatives

| Option                                                                 | Better at                                            | Why it lost                                                                                                                       |
| ---------------------------------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Rules in the write skill only, and no check                            | No change to the program, no gate failing elsewhere  | REQ-2694 asks for a program where one can settle the rule, and a rule a model reads is followed most of the time                  |
| Require only the fields whose default is wrong, and keep `inherit`     | Fewer lines per agent, and a model the session chose | REQ-2988 asks every dispatch to state its model, and REQ-2982 asks for a choice per agent, which a default can't show             |
| Write the depth variable into the repository's `.claude/settings.json` | Sets the depth for the whole session                 | REQ-1563 forbids editing a file the repository keeps, and it reaches only a repository that ran the setup                         |
| The dispatching skill passes model and effort on each call             | No front matter change, and a call can pick per task | A call's arguments are in no file a check reads, and every skill that dispatches would have to repeat them                        |
| Check the fields in `paw check`                                        | One command for the record and the material          | `paw check` reads the record, and `meow-author` owns the authoring rules and already reads every agent                            |
| Withhold delegation with `disallowedTools: [Agent, Task]`              | Leaves every other tool granted, one line per agent  | RES-0284 found the loader reads the field but never read what it does at a dispatch, and REQ-3270 asks for a written list         |
| Do nothing                                                             | No work                                              | Both shipped agents can delegate, run to no ceiling and cost whatever the session costs, and six approved requirements stay unmet |

## What it costs

Whoever writes an agent writes six more lines, and in a repository that runs
`meow-author check` in its gate, each agent it already has fails until it
declares them. That is a breaking change to the check's result, released as
a minor version while `meow-author` is below 1.0, so the release notes name
the six fields and the reason for each.

A shipped agent that names `opus` fails to start where the account or a
gateway doesn't offer that model. A repository in that position replaces the
agent with its own, which REQ-2986 allows, and that is more work than a
default of `inherit` would have asked of it.

Naming `opus` for `record-reviewer` also sets its price. A repository whose
session runs on a cheaper model pays the difference between `opus` and that
model on every review, where `inherit` would have charged the session's rate.
That repository pays it on each dispatch, and it can lower it by replacing the
agent (REQ-2986). The platform's mapping of the alias can also change it, as
the last point under what still doesn't work says.

A review that reaches its ceiling ends unfinished, and the person waiting on
the gate gets "unreviewed by an agent" where a longer run might have finished.
Each ceiling is a budget I chose, not a limit the platform imposes, so raising
it is an edit to one agent.

## What would reverse it

- I would set the session's depth to one, and meet REQ-3271, once a plugin's
  `settings.json` applies an `env` table or a key for the depth.
- I would drop the `omitClaudeMd` rule if the platform started to load no
  project instructions by default, because the written `false` would then be
  the one decision anyone had to make.
- I would move `record-reviewer` to `sonnet` if a hand-run evaluation showed
  `sonnet` finding as many of the planted defects, because the cheaper model
  would then cost less for the same review.
- I would move `prose` to `opus` if a hand-run evaluation showed `opus`
  finding measurably more of the planted defects, because only a gain pays
  for the dearer model.
- I would move either agent's effort to `medium` if a hand-run evaluation
  showed it finding as many of the planted defects there, because the lower
  level would then cost less for the same review, and to `xhigh` if one
  showed `xhigh` finding measurably more.
- I would drop the `inherit` refusal if the platform let a dispatcher cap what
  a dispatch of an agent costs, because the cost reason would then be met
  without naming a model.
- I would go back to platform defaults for `model` if repositories replaced
  the shipped agents (REQ-2986) because a named model isn't offered to them,
  because the written field would then cost more dispatches than it makes
  deliberate.

## Consequences

- `crates/meow/src/author.rs` gains the six field rules in its agent branch,
  with fixtures for each, and `meow-author` takes a minor version.
- `plugins/meow-flow/agents/record-reviewer.md` and
  `plugins/meow-prose/agents/prose.md` gain the fields above, and `meow-flow`
  and `meow-prose` each take a patch version.
- `meow-author:write` gains the rules above, and the method skill gains the
  partial-output rule beside M22.
- SPC-1030 gains "What an agent declares" under its behaviour and six lines
  under "The check". SPC-1090 states the partial-output rule where the method
  dispatches `record-reviewer`.
- REQ-0820 is withdrawn, and REQ-3270 and REQ-3271 replace it.
- The fields are platform front matter and name no language, build tool or
  file extension, so the kernel, method and practice layers still name none.

## How I will know it was realised

1. Crate tests over fixture agents show the check failing, naming the file
   and the field, on an agent with no `maxTurns`, one with `maxTurns: 0`, one
   with no `tools`, one with `tools: "*"`, one listing `Agent`, one listing
   `Task`, one listing `Agent(worker)`, one naming `Agent` in a
   comma-separated `tools` string, one with no `model`, one with
   `model: inherit`, one with no `effort`, one with `effort: extreme`, one
   with no `omitClaudeMd` and one with no `skills`. They show it failing with
   that reason on a front matter block that doesn't parse, and passing on one
   declaring all six with `skills: []`, on a repository's own agent listing
   `Agent` and on a repository's own agent with `tools: "*"`. The
   passing fixture's declarations are added only after the failing ones are
   seen failing against the current check, so a rule that never fires isn't
   counted as covered.
2. `mise run prompts` exits 0 at the merge revision with both shipped agents
   declaring the fields in the table above.
3. A hand-run evaluation case under `plugins/meow-flow/evals/`, run by a
   person and never in CI, asks `record-reviewer` to hand part of its review
   to another agent, and its transcript shows no Agent call and the review
   done by the reviewer itself.
4. A hand-run case dispatches an agent defined with `maxTurns: 2` on work
   that needs more, and its output comes back marked as stopped at its
   ceiling.
5. A hand-run `meow-author` evaluation case asks for an agent that carries a
   language's idioms, and the write skill produces a skill.
6. `meow-prose:prose` and `meow-flow:record-reviewer`, each dispatched with a
   path alone, read the updated SPC-1030, SPC-1090 and write skill and report
   no sentence treating a delegated agent as a boundary, and the task's
   evidence names both as the judge for REQ-2976. A person reads both reports
   before the task closes, because the two agents may share the author's model
   family.
7. Every requirement this decision addresses lands in exactly one closed
   task, and REQ-3271 reads as postponed.

## What this does not settle

- A session's own nesting depth, which REQ-3271 postpones.
- A skill forked into an agent with `context: fork`, whose front matter isn't
  an agent definition and which the check doesn't read as one.
- `permissionMode`, `hooks` and `mcpServers`, which a plugin agent ignores
  and a project agent honours. RES-0284 found a reader would take them as
  enforced in a plugin agent, and no requirement asks for a rule yet.
- Whether an agent's `skills` list names the right skills, and whether its
  ceiling is large enough, which only a review or a run shows.
- Which model a repository should use for its own agents. The check asks
  that one is named and doesn't judge which.
