---
id: ADR-2100
artifact: adr
status: done
revised: 2026-09-28
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
supersedes: []
---

# 2100. A read-only agent routes each request on the repository before work starts, and the route is reported before any edit

## Decision

`meow-flow` ships a router agent and a `route` skill that dispatches it. The
skill runs before any work on a request to change the repository (REQ-0330), and
the route it reports is the first thing in the reply. A route has a size and a
shape, because RES-0053 found the two independent: a classifier with size alone
runs one chain over three unrelated changes, and starts a defect where new work
starts. The size decides where the work enters the chain, except for a defect,
whose triage decides it. The shape decides what the first step reads, and for a
defect and for several changes it also changes what happens first.

Three sizes (REQ-0334):

- `none` writes no artifact. It covers the trivial work the constitution
  exempts, a typo, a formatting fix or a link, and only where the change alters
  no behaviour and no approved record, because an approved record is frozen and
  a change to it is never trivial.
- `reduced` writes only the records the work lacks: a task, and a defect record
  where the work is a defect. It applies where an approved record already
  authorises the work (ADR-1440). It enters at `implement` where an approved
  epic carries the work, and at `epic` where an approved decision covers it and
  no epic realises it yet. For a defect, the defect record it writes is the
  authorising record, and the step comes from its triage, as the defect shape
  says. For other work with no approved record
  behind it, `reduced` has no step to enter at, and the route is `full`.
- `full` runs the chain from `research`.

Four shapes:

- new work, which starts where its size says;
- work that extends records it names by identifier, such as a specification or a
  decision, which starts where its size says, with the named records as the
  first step's input;
- a defect, which starts at a reproduction, as ADR-1440 says. Its size is
  `reduced` where a requirement in force appears to cover the behaviour and
  `full` where none does, and the defect's triage may raise it. The
  reproduction and the triage are written into the defect record and aren't a
  step of the chain, so the step the defect enters at is the one its triage
  names in `enters`. For a defect, `enters` overrides the size, whichever step
  it names: a `full` defect whose triage names `implement` enters at
  `implement`, and a `reduced` one whose triage names `research` enters at
  `research`. The size only records whether a requirement in force appears to
  cover the behaviour, because triage reads the reproduction and the router
  reads only the request and the repository;
- several separate changes, each listed with its own size and shape (REQ-0344),
  which stops before any of them starts.

The agent, `plugins/meow-flow/agents/router.md`, sets `tools: Read, Grep, Glob`
and nothing else, so it can't write, edit or run a command (REQ-0346). RES-0304
observed that allowlist holding on Claude Code 2.1.280, in a foreground dispatch
from `claude -p`: the agent held those
three tools, found no tool that writes when asked to create a file, and left the
work tree clean. It reads the request and the repository together (REQ-0342):
`.meowpaw/profile.toml`, the record's indexes and specifications where the
profile declares a record, and the files the request would touch. Its reason
names at least one path or identifier it read, so a reason drawn from the
request's words alone shows as one, and the skill reports it as the table below
says. It returns the size, the shape, the reason,
whether the evidence was ambiguous, and the override words that would change the
route. The agent's own definition states those fields, because RES-0304 saw an
agent decline the reply-shape block the output style adds to a dispatch, so a
format that depends on the brief isn't one the skill can rely on.

Where the evidence points to two sizes, the agent takes the larger one
(REQ-0338), and the report says `ambiguous` and names the evidence on each side
(REQ-0340). RES-0053 found the cost asymmetric: routing down makes an
architectural change as a typo fix with no record, and routing up wastes an
hour.

The skill, `plugins/meow-flow/skills/route/SKILL.md`, reports the route and its
reason before any tool that writes runs (REQ-0332). For `none`, `reduced` and
`full` it then proceeds with no question, because a person who disagrees
overrides in one word, and a question on every request would be the cost that
gets the method bypassed. The stop for several changes is the only one:

- For `none`, it goes to the edit.
- For `reduced` or `full`, it runs `paw ready` for the step the route enters at,
  and the method skill takes over from there.
- For a defect, it hands the request to the method skill's defect path under
  ADR-1440, which writes the defect record, runs the reproduction and writes the
  triage. The route skill runs `paw ready` only once that record carries
  `enters`, and for the step `enters` names.
- For several changes, it reports the list and stops, because each entry becomes
  its own branch and pull request and their order is the person's to choose.

A person overrides the route with one instruction, `route none`, `route reduced`
or `route full`, in either direction, and the skill takes it with no further
question (REQ-0336). A size word sets the size and keeps the shape: given after
a several-changes route, it sets that size on every entry and keeps the list,
because running unrelated changes as one chain is the failure RES-0053 found in
a classifier with size alone. A fourth word, `route one`, overrides the shape:
it runs the listed changes as one change at the largest size among its entries,
because REQ-0338 takes the larger size where the evidence points to two, so a person who sees one change where the router saw several says so in one
instruction. No word splits one change into several, because the entries of
the list are what the person would have to write, and a person who wants the
split asks for each change on its own. A `route reduced` for work that no
approved record authorises reports as the table below says, because the
constitution runs no task that nothing authorises. The override applies to the
request it answers and not to later ones, because the next request may differ
in size, and an override that
stood for a session would be the silent bypass RES-0053 warns about. Given with
the request itself, it skips the dispatch, so a person who knows the route pays
nothing for routing. A parent agent that already routed the work passes its
route in the brief the same way, so a subagent doesn't route again.

Seven states would otherwise read as a route, and each reports as itself:

| State                                                              | Reported as                                                                               |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| The agent can't be dispatched                                      | `full`, `ambiguous`, "the router couldn't run", with the override words                   |
| The agent's reply names no size                                    | `full`, `ambiguous`, "the router's reply named no route", with the override words         |
| The agent's reason names no path or identifier                     | `full`, `ambiguous`, "the router's reason named nothing it read", with the override words |
| The repository declares no record                                  | The route as the agent gave it, and that no record is declared, so no step's gate runs    |
| A person overrode the router's route                               | The route as overridden, and the route the agent gave                                     |
| A person gave `route reduced` and no approved record authorises it | `full`, the `reduced` the person gave, and that no approved record authorises the work    |
| A route came with the request or the brief                         | The route as given, and that no router ran                                                |

Where two rows apply, the report carries both, and the sixth decides the route
over the seventh, because a route given with the request is still an override.
The first three resolve upward because a route with no evidence behind it is
ambiguous by REQ-0338's terms, and a person who disagrees answers in one word.
The fourth keeps routing available to a repository that keeps no record, as
REQ-0030 asks: the route still says how much method the change deserves, and the
skill proceeds to the work because the harness imposes no record the repository
never adopted. The fifth reports the agent's route beside the override, so a
person can see what they overrode. The sixth is the one override the skill
doesn't follow as given: `reduced` enters where an approved record already
authorises the work, and with none `reduced` has no step to enter, so the skill
starts at `research` and says why. A person who disagrees writes the
authorising record or gives `route none`.

After this decision every request to change a repository with `meow-flow`
installed starts with a stated route and its reason, a typo goes straight to its
edit, and a change the words make sound small but the repository shows is large
starts at research. What still doesn't work:

- Whether the skill loads before work on each model is unmeasured until the
  evaluations run, and until then the route depends on the description routing
  it, as RES-0272 measured for another skill.
- Nothing stops the main session writing before it dispatches the router. The
  skill's rule forbids it and the evaluations measure it, but no hook refuses
  it.
- Whether the allowlist holds in an interactive session is unmeasured.
  RES-0304 dispatched only from `claude -p`, and RES-0263 reads the
  documentation as running a subagent in the background there by default, with
  a smaller built-in tool set.
- The route leaves no trace in the record, so whether work took the route it was
  given is visible only in the conversation.

## Why

RES-0053 and RES-0031 found that a method costing the same for a typo and an
architectural change gets bypassed for the typo, then for everything. They found
that a keyword classifier fails the first time somebody describes an
architectural change in plain words, and that a model classifying on the
repository has to report its class and reason and accept a one-word override,
because it is non-deterministic. RES-0053 concluded that routing writes nothing,
because a classifier that writes a document makes the trivial path non-trivial.
RES-0304 observed that an agent's `tools` allowlist holds, so "writes nothing"
is a property of the agent's definition a program can check, where the main
session holds Write, Edit and Bash and only an instruction stops it. RES-0272
found that a description stating an obligation in the third person loads a skill
on Sonnet 5 where a hook naming it doesn't, which is how the skill reaches the
start of the work.

The strongest objection: every routed request pays a dispatch, a typo included,
and RES-0304 saw 12.8 s to 19.7 s and USD 0.05 to USD 0.10 in a one-file
repository, more in a real one. The route exists because a costly trivial path
gets worked around, and this makes the trivial path cost a dispatch it didn't
cost before. The real comparison is with the main session classifying under the
skill, which costs no dispatch. Both leave the window before the router runs
held by an instruction alone. What the dispatch buys is a classifier that can't
write, so the step REQ-0346 governs can't write by construction, and one that
reads the repository without the conversation that asked for the fix. I accept
12.8 s to 19.7 s for that, and the override given with the request skips the
dispatch where a person already knows the route. The evaluations measure the
cost on this repository, and the first reversal below names the figure that
would move the classification back into the main session.

## Alternatives

| Option                                                       | Better at                                                   | Why it lost                                                                                                                                                                                   |
| ------------------------------------------------------------ | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A `UserPromptSubmit` hook classifying on keywords            | Deterministic, runs on every prompt, no model               | Classifies on the request's words and not the repository, which REQ-0342 forbids and RES-0053 found fails first                                                                               |
| The main session classifies under the skill, no agent        | No dispatch, so a typo costs nothing extra                  | The classifier itself can write, held back only by an instruction, and it reads the conversation that asked for the fix (RES-0304)                                                            |
| A `PreToolUse` hook denying writes until a route is reported | Enforces "route before any edit", which the skill only asks | It would read the route from the transcript, which RES-0203 found lags the conversation, so it could deny a write after the route was given; it also runs on every tool call in every session |
| A command a person runs, `/meow-flow:route`                  | Costs nothing unless someone asks                           | Runs only when a person remembers, so work starts unrouted, which is the bypass RES-0031 describes                                                                                            |
| A hook reminding the session to route                        | Fires on every prompt without a description                 | RES-0272 saw a hook's line change no behaviour, and it would fire on questions that change nothing                                                                                            |
| A unit of its own, `meow-route`                              | Installed by a repository that wants no method              | Two of three sizes enter the chain, which `meow-flow` ships, and the third needs nothing a separate unit would add                                                                            |
| Do nothing                                                   | No dispatch and no description in context                   | Nine approved requirements stay unmet and the constitution's exemption stays prose that nothing applies                                                                                       |

## What it costs

Every repository that installs `meow-flow` keeps two more descriptions in
context on every turn: the skill's and the agent's, together about 450
characters. The unit's budget of 500 characters rises to what the budget check
measures plus about one sentence, at most 1,000.

Whoever asks for a change waits for one dispatch before the work starts, and
pays for the tokens the router reads. A person who knows the route skips both by
giving it with the request. A request that is several changes stops once, for
the person to choose the first, and that stop is the design's only interruption.

Whoever maintains the unit keeps the agent's allowlist to `Read`, `Grep` and
`Glob`, which a static test checks, and re-observes the allowlist when the unit states a
newer Claude Code version, because the platform sets which tools a subagent
holds, and RES-0304 saw 2.1.280 give a subagent tools its main session doesn't
list.

## What would reverse it

- If the median routing dispatch across the evaluation cases on this repository
  takes over 60 s or costs over USD 0.25, I would move the classification into
  the main session and accept an instruction in place of the allowlist. Both are
  budgets I chose, about three times what RES-0304 saw in one file, because a
  person waits on the dispatch before every change.
- If the evaluations show the main session classifying under the skill, with no
  agent, matching the agent's pass rate on every case and writing nothing before
  the report in every run, I would drop the agent and its dispatch.
- If Claude Code drops Grep and Glob from subagents and the router, left with
  Read, then fails the plain-words cases, I would move the classification into
  the main session.
- If a hook is observed reading the route from the conversation as it stands,
  not from a transcript that lags it, I would add a `PreToolUse` hook that
  refuses a write before the route is reported.

## Consequences

- The router's prompt states its reply fields itself, and the skill reads those
  fields and nothing the brief adds.
- The implementing task repeats RES-0304's run and its control on the Claude
  Code version `plugins/meow-flow/requires.toml` states, and records there the
  version on which the allowlist was last observed.
- An agent `router` and a skill `route` in `meow-flow`, each written to the
  prompt vocabulary `meow-author` sets, the skill's description worded as
  RES-0272 measured, and the unit's budget raised to cover both descriptions.
- A static test in `plugins/meow-flow/tests/` that fails where the router's
  `tools` names any tool outside `Read`, `Grep` and `Glob` or is missing, where
  its prompt doesn't name the three sizes and the several shape, or where the
  skill doesn't name the four override words.
- Evaluation cases under `plugins/meow-flow/evals/`, run by hand on Sonnet 5 and
  Opus 5.5 and never on a schedule or in CI, because each run calls a model,
  costs money and varies between runs, so it can't be a gate, with thresholds
  set before the first run (REQ-0159). Whether the skill loads is measured
  before what it says (REQ-3032), on change requests beside near misses such as
  a question in chat. Every case runs with `meow-core` enabled, so the router's
  brief carries the output style's block.
- SPC-1090 states the route as what comes before the chain's first step, and
  drops "classifying trivial work to a later decision" from its scope.
- The method skill's first step names the route as what came before it, and
  this repository's `CLAUDE.md` names the skill where it names trivial work.
  The constitution template names no trivial work, so it doesn't change.
- `meow-flow` raises its minor version, and its README says what the route does
  and costs.

## How I will know it was realised

1. The static test passes on the shipped agent and skill, and fails on a copy of
   the agent that names Write, Edit or Bash or drops `tools`.
2. A case asking to fix a typo routes `none`, reports the route and its reason
   before any tool that writes, and the router is the first agent the session
   dispatches.
3. A case asking in plain words for verbs to read tasks from a task runner, a
   change ADR-1070 governs, and one calling a change to how the profile is
   parsed a tiny fix, each route `full`, and each reason names a path or an
   identifier in the repository.
4. A case whose evidence points both ways routes to the larger size and says
   `ambiguous` with the evidence on each side.
5. A case asking for three unrelated changes reports three entries, each with
   its size and shape, and stops.
6. A request carrying `route none` dispatches no router and reports the route as
   given. A `route none` given after a `full` route, and a `route full` after a
   `none`, each change the route with no further question. A `route reduced`
   given for new work that no approved record authorises reports `full`, the
   `reduced` given, and that no approved record authorises the work. A
   `route full` after a several-changes route keeps the list with every entry
   `full`, and a `route one` after it reports one change at the largest size
   among the entries.
7. In every run of every case, the stream shows no Write, Edit, NotebookEdit or
   Bash call before the route is reported, which is the router's result where a
   router ran and the session's first reply where none did. Each run starts in a
   scratch repository where `git status --porcelain` prints nothing.
8. A question in chat that changes nothing dispatches no router.
9. Every requirement ADR-2100 addresses lands in exactly one closed task.

## What this does not settle

- Recording the route in the record, or checking afterwards that work took the
  route it was given.
- Unattended approval as a declared route, which REQ-2370 asks for and a later
  decision on unattended runs settles.
- A hook that refuses a write before the route is reported, because no hook yet
  reads the conversation as it stands (RES-0203).
- Routing a request that changes another repository, or no repository.
- Which model runs the router. The agent inherits the session's, until an
  evaluation shows a smaller model routes the cases as well.
