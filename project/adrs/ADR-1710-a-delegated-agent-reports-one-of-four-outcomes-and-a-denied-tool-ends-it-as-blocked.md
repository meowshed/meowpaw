---
id: ADR-1710
artifact: adr
status: approved
revised: 2026-09-29
addresses: [REQ-0816, REQ-2978]
postpones: []
supersedes: []
---

# 1710. A delegated agent reports one of four outcomes, and a denied tool ends it as BLOCKED

## Decision

Every agent the harness ships ends its dispatch with one outcome from a
closed set, written on a line of its own as `outcome:`, a space and the word, and the
skill that dispatched it acts on that word before it reads anything else
(REQ-0816). A denied tool call ends the dispatch as `BLOCKED`, naming the tool
and what it was called on, and neither the agent nor its dispatcher retries
it or waits for an answer (REQ-2978).

The set is the four outcomes RES-0016 found: `DONE`, `DONE_WITH_CONCERNS`,
`NEEDS_CONTEXT` and `BLOCKED`. RES-0285 found that the source defined them for
an implementer, so the tables below say what each means for the three agents
the harness ships today, `meow-flow:record-reviewer`, `meow-prose:prose` and
`meow-flow:router`, and what their dispatcher does with it.

The outcome and the verdict are separate. A review that ran and found six
defects is `DONE`, a clean record is `DONE` too, and a route marked
`ambiguous` is `DONE`, because the outcome says whether the work happened and
the rest of the report says what it found.

### The two reviewers

| Outcome              | The agent reports it when                                                                                                  | The dispatcher                                                                                                                                |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `DONE`               | It worked through every question its rules set, whatever it found                                                          | Acts on the findings, as M20 and M21 of the method skill say                                                                                  |
| `DONE_WITH_CONCERNS` | It finished, and part of the review couldn't run: a cited record it couldn't reach, or a kind with no question set         | Acts on the findings, and names the part that didn't run in the gate report, because a partial review read as whole hides what nobody checked |
| `NEEDS_CONTEXT`      | The brief names nothing it can review: the path doesn't exist, or holds no record or text                                  | Corrects the brief and dispatches once more, which doesn't count as a repair round because nothing was reviewed                               |
| `BLOCKED`            | A tool call was denied, or, for `prose`, a file of its standard couldn't be read, so the review can't be done to its rules | Reports the record as unreviewed by an agent, naming the tool and the input, as M22 says for a review that couldn't run                       |

For `prose` the rows read as follows. A scope the request narrowed, such as
a proofread, is `DONE`, because the review ran to the scope it was asked for.
A review for the default reader, where neither the text nor the request
names one, is `DONE` too, because the verdict already says which reader it
assumed. `DONE_WITH_CONCERNS` is a review of a change to code in which a file
the change touched couldn't be read, so part of the change went unread. A
file of the standard that couldn't be read, which `prose` now reports as
unrun, is `BLOCKED`.

The method skill dispatches only `record-reviewer`. The review step's W13
names no agent today, so `prose` is dispatched either by a session on its
description or by W13 on whatever agent the session picks. This decision
gives W13 a rule for the texts inside the change under review: it dispatches
`record-reviewer` for each record the change writes and `prose` for each
other prose text, such as a documentation page, a commit message or a pull
request body, because both follow the outcome rule and an agent the session
picks might follow none. W13 is then the one shipped dispatcher that reads
`prose`'s outcome, and it acts on each row as the table says, with the text in
place of the record.

The rule doesn't reach the code in the change. The review step judges code
for conformance and quality (W3) and for structure (W10), and `prose` reads a
code change's comments and only as prose, so handing it the code would pass a
review that judged the writing alone. For code, W13 keeps today's rule: it
dispatches an agent with read-only tools that the session picks, and where
none can be dispatched it reports the verdict as self-assessed. No shipped
agent reviews code, so that agent follows no outcome rule, and W13 reads its
return as it does today. The fail-closed reading below covers only the
dispatches of `record-reviewer` and `prose`, because a picked agent that was
never told of the outcome line would otherwise have every code review
reported as not run.

The dispatcher dispatches again after `NEEDS_CONTEXT` once only. If the
second dispatch returns `NEEDS_CONTEXT` too, the dispatcher reports the record
as unreviewed by an agent, as it does for `BLOCKED`, naming the brief it sent,
because a brief that fails twice needs a person to correct it. Any other
outcome from the second dispatch is handled as its own row says.

A cited record or file the agent couldn't reach, in the `DONE_WITH_CONCERNS`
rows, is one that doesn't exist or doesn't resolve. A call that was denied is
`BLOCKED` whatever it was called on, a cited record included, because the
denial came from a rule or a person that the review mustn't go round, and an
agent that carried on past it would finish a review whose reach nobody
granted.

### The router

ADR-2100 decided that the `route` skill dispatches `router`, and it already
names what the skill reports when the router gives it no route. Each outcome
maps onto one of those rows, so this decision adds no new route result:

| Outcome              | The router reports it when                                                                            | The `route` skill                                                                                                                                                          |
| -------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DONE`               | It gave every change the request asks for a size and a shape                                          | Reads the fields, as ADR-2100 says                                                                                                                                         |
| `DONE_WITH_CONCERNS` | It routed, and a file or index its steps name couldn't be found, so it decided on less than they read | Reads the fields, and names what the router couldn't find beside the route, because a route decided on less than its steps read looks the same as one decided on all of it |
| `NEEDS_CONTEXT`      | The request names no change it can route                                                              | Reports ADR-2100's row for a reply that names no size: `full`, `ambiguous`, with the override words                                                                        |
| `BLOCKED`            | A tool call was denied                                                                                | Reports ADR-2100's row for an agent that can't be dispatched: `full`, `ambiguous`, "the router couldn't run"                                                               |

The `route` skill doesn't dispatch again after the router's `NEEDS_CONTEXT`,
because ADR-2100 routes a question that changes nothing with no dispatch, and
a person who sees `full` and `ambiguous` has the override words to correct
it.

A router reply with no outcome line from the set gets ADR-2100's row for a
reply that names no size, `full` and `ambiguous`, even where it carries a
`size:` field, because the skill can't tell a route from a denial described
in prose, and ADR-2100 already chose routing up over routing down where the
evidence is unsure.

### Where the outcome goes

The outcome line reads `outcome:`, a space and one of the four words, and
nothing else. I chose the field form over a bare word so that one line reads
the same in each agent, the router's fields included, and a grader matches
it with one pattern.

- `record-reviewer` keeps its label, which ADR-1490 fixed, as the report's
  first line, so its R7 still holds. The outcome line is the second line.
  For any outcome but `DONE`, the third line is one sentence naming the
  cause, such as `Read was denied on project/adrs/ADR-0001.md`, because the
  dispatcher needs it to act: the gate report names the part that didn't run
  or the tool that was denied, and a corrected brief fixes what the cause
  names. The findings follow, as R8 already says.
- `prose` puts the outcome line first, the cause second where the outcome
  isn't `DONE`, and its verdict after, because `prose` has no fixed label line
  to keep above it.
- `router` gives `outcome:` as its first field, before `size:`, and the cause
  as a `cause:` field where the outcome isn't `DONE`. Its R6 already says
  that nothing comes before the fields, and the outcome is one of them.
- An agent shipped later whose report opens with a fixed line, such as the
  skeptic ADR-2200 decided, keeps that line first and puts the outcome line
  second, because the fixed line is there for the person reading the report,
  and the dispatcher finds the outcome on the line below it. Any other agent
  puts the outcome line first. The skeptic's
  per-requirement states, `refuted`, `not refuted` and `not judged`, are its
  verdict, and its outcome says whether it could judge at all.

A dispatcher reads the outcome line allowing leading space, because RES-0285
found that the platform's foreground hand-back indents every line of the
report by two spaces. It acts on the word itself and never asks a model to
relay the report first, because RES-0285 saw a parent asked to relay a report
verbatim drop the outcome line.

### The rules each agent gains

The two reviewers gain one rule each: the report quotes nothing it read
beyond the span a finding names, which `prose` already caps at 25 words under
V1 and `record-reviewer` gets at the same length, because a report that
restates the record refills the context the dispatch was meant to spare
(REQ-0816). A finding already names its line, so a longer span, such as a
table row, is found there and needs no quoting in full. The router needs no
such rule, because its reason is one or two sentences. I don't cap the number
of findings, because the constitution puts completeness above brevity and a
capped list drops a defect the author then never sees.

All three agents gain the denial rule, in the same words: where a tool call
is denied, the agent issues no second call in another form, reaches the same
result with no other tool, asks nobody for the permission, and ends with
`outcome: BLOCKED` and one sentence naming the tool and what it was called on.
RES-0285 observed an agent without the rule ask the user for the permission
and another retry the call in a second form, and the platform's denial text
for a missing permission invites a third, another tool. In a session with no
person in it the question waits for nothing, and a workaround reaches what
the permission withheld, which the dispatcher can't see. RES-0285 then ran the
rule in an agent's definition: each of the three denied agents made one call
and ended as `BLOCKED`, under each of the three denial texts it met, the one
inviting another tool included. Each ran once on a small model, so the rule
has one success per denial text behind it and no rate.

### How the dispatcher expects the denial

The method skill treats `BLOCKED` as the end of that dispatch. It doesn't
resume the agent, although the platform's hand-back offers `SendMessage` to
continue it (RES-0285), because the resumed agent's next call meets the same
rule. It doesn't dispatch the agent again under the same permissions in that
session, for the same reason. And it doesn't review the record itself,
because a session reviewing its own record is the bias M22 and W13 exist to
avoid, and a session that can read the record where the agent was denied has
gone round the denial. It
treats a return with no outcome line from the set as unreviewed by an agent,
because RES-0285 found that returns with no outcome describe failures in
prose a reader can take for a report. That reading also covers an agent
stopped at its turn ceiling before it wrote the line, which M23 already
reports as unreviewed, so the new rule sits beside M22 and M23 and agrees with
both.

The review step's W13, which after this decision dispatches the review of the
records in the session's own change to `record-reviewer` and of its other
prose texts to `prose`, names what to review by its path alone, as
M19 already does for the method skill, because a brief carrying the text lets
the agent review without reading and hides a denial the text's path would
meet. For a change spanning several files W13 names each path. A text that
exists in no file, such as a commit message or a pull request body, goes in
the brief as text, because it has no path to name, and the agent can still
be denied a file of its standard. Nothing has to be written to a file first,
so the rule costs no extra step. W13 reads the outcome of those two agents
the same way and reports a `BLOCKED` review as not run, never as
self-assessed and never as passed. It reports a return from either with no
outcome line from the set as not run too, for the reason the method skill
does. The review of the code goes to a picked agent as W13 says today.
The `route` skill reads the router's outcome by the table above.

`meow-author:write` gains a rule beside D9: an agent a unit ships names the
four outcomes, says when it reports each, and carries the denial rule,
because the author writing a new agent reads that skill and not this record.

### What the check enforces

`meow-author check` fails an agent in a unit's `agents/` directory whose body
doesn't name all four outcomes, naming the file and each missing word. The
rule sits beside the six fields ADR-1700 made the check require. It doesn't
read a repository's own agents for this rule, because the method dispatches
only the agents a unit ships, and a repository agent that replaces one
(REQ-2986) is held by the fail-closed reading above. The check is a static
proxy: it shows the words are in the definition, and the evaluation cases
show whether the agent writes them.

### What works after this

After this decision each of the three shipped agents reports one of four
outcomes on a line a dispatcher reads without parsing prose. A denied tool
ends any of them as `BLOCKED` naming the tool. The method skill reports that
record as unreviewed by an agent, and W13 reports that review as not run.
Once the `route` skill ships, it reports a blocked router's route as `full`
and `ambiguous`. A unit that ships an agent naming fewer than all four
outcomes fails `meow-author check`.

I read REQ-2978's "session with no person in it" as a run with permission
prompts disabled, where RES-0285 saw every request become a denial at once.
That reading is the scope of the research REQ-2978 elaborates: RES-0263's
seventh conclusion says a background agent's request, "under a
non-interactive run with prompts disabled", "is denied and nobody answers
it". In an interactive session a person is present by definition, and a prompt that waits in it is the platform asking that person,
which the requirement doesn't forbid. Under that reading the denial rule in
each shipped agent meets REQ-2978 for every dispatch of it, a direct one
included, because the agent ends on the first denial and nothing waits. The
dispatcher rules add acting on the word, which REQ-0816 asks for.

What still doesn't work:

- An agent that hides a denial and reports `DONE` isn't caught. The parent's
  `permission_denials` records every denial under `claude -p` (RES-0285),
  but no program the harness ships reads it, because no unattended runner
  exists yet.
- In an interactive session a background agent's permission prompt waits in
  the main session for the person, with no timeout the documentation names,
  and a person who stepped away leaves it waiting. The harness can't tell
  whether the person is there, and this decision leaves that case outside
  REQ-2978 by the reading above. The shipped agents hold only `Read`, `Grep`
  and `Glob`, so a prompt arises only where a call reaches outside what the
  session already allows.
- A session that dispatches `prose` on its description, outside the review
  step, follows no shipped rule for acting on the outcome, so only the person
  reading the report's first line acts on it. The agent still ends on a
  denial, so nothing waits, but the session may read a `BLOCKED` report as a
  review.
- The `route` skill ADR-2100 decided hasn't shipped at this decision's
  revision. Whichever of its task and this decision's task lands second
  writes the router's rows into the skill. Until the skill ships, only a
  person reads the router's outcome line.
- The four meanings in the tables fit a reviewer and a router. An agent that
  implements work, which the method doesn't ship yet, needs its own meanings
  for the same four words, written in the decision that ships it.
- The check reads words in a definition and can't tell whether the agent
  writes them in a report. Only the evaluation cases show that.
- Nothing checks that a unit's agent carries the denial rule. The check looks
  only for the four outcome words, and the rule is a sentence whose wording
  an author may vary, so a pattern for it would either miss a paraphrase or
  pass a near miss. A unit agent shipped later without the rule passes the
  check and can leave a denied dispatch waiting or worked round, which
  REQ-2978 forbids, and only `meow-author:write` and review stand between
  the author and that.
- No shipped agent reviews code, so W13 dispatches the review of the code in
  a change to an agent the session picks, and no shipped rule reads that
  agent's outcome. A denied tool in that review can come back as a finished
  review or as a question, as RES-0285 saw for agents without the rule.

## Why

RES-0016 concluded that the return is a short structured status from a fixed
set, because a fixed set lets the dispatcher decide without reading. RES-0285
observed what happens without one on Claude Code 2.1.280: the platform
marked every dispatch completed, denied or not, and the three agents denied a
tool with no rule for it returned a question, a retry followed by prose, and
prose. None of those tells a dispatcher, without reading, that nothing was
done. With the rule in their definitions, the agents in RES-0285's later runs
each opened with the outcome line, `DONE` once and `BLOCKED` three times.

A field on a line of its own is the least the dispatcher can read and still
be sure. A report is read by the dispatching skill, by a person at the gate
and by the evaluation graders, and a line with one of four words serves all
three, where a structured object serves only the program.

The agent reports the denial, not the platform, because the platform's
denial reaches the dispatcher in two different places depending on how the
session runs, and in an interactive session in neither. The agent is the one
party that knows the denial in every mode.

The strongest objection is that a `BLOCKED` review leaves the gate with no
review where a retry by another tool might have finished one. I accept that,
because the denial came from a rule or a person, and a review that reached
its input by going round the rule is one the person approving can't trust.

## Alternatives

| Option                                                                        | Better at                                                         | Why it lost                                                                                                                                                                                 |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The report ends in a JSON object carrying the outcome                         | A program parses it with no convention about lines                | The platform enforces JSON no more than a line, and a person at the gate and the graders read the report as text                                                                            |
| The outcome as a bare word alone on its line                                  | One token shorter                                                 | The router's reply is fields, and a bare word among them breaks the form its R6 states, so the agents would need two shapes and the graders two patterns                                    |
| A reviewer's own set, such as reviewed, partial and unreviewed                | Words that fit a review with no translation from an implementer's | The router isn't a reviewer and would need a third set, and each set costs its own grader pattern and its own `meow-author check` rule, where the four words carry every row in both tables |
| The verdict is the outcome: clean, or findings                                | One line fewer, as `superpowers`' reviewer returns verdicts       | A verdict can't say the review didn't run, which is the case REQ-2978 needs reported                                                                                                        |
| Two outcomes, done and blocked                                                | Fewer words to define and to check                                | A missing brief and a partial review each ask the dispatcher for a different action, and folding them into done or blocked hides which                                                      |
| The dispatcher reads `permission_denials` and the agent reports nothing extra | Mechanical, and an agent can't hide a denial                      | Only a `claude -p` run with structured output has the list, and the method skill running in a session never sees it                                                                         |
| A return with no outcome line is read as a finished report                    | Nothing to review by hand when a finished agent forgets the line  | RES-0285 found that returns with no outcome describe failures in prose a reader can take for a report, so a denied review would pass the gate as reviewed                                   |
| Declare `permissionMode: dontAsk` on each shipped agent                       | Denies at the platform, with no instruction to follow             | The platform ignores `permissionMode` in a plugin's agent (RES-0285), and it would still leave the agent's reaction to the denial unwritten                                                 |
| Do nothing                                                                    | No work                                                           | The observed returns were a question to nobody, a retry followed by prose, and prose, the dispatcher reads each as finished, and two approved requirements stay unmet                       |

## What it costs

Every agent a unit ships carries four more words and two more rules, and a
repository that ships units with agents and runs `meow-author check` in its
gate fails until each agent names the set. That is a breaking change to the
check's result, released as a minor version while `meow-author` is below 1.0.

Each report grows by one or two lines. The reviewer's `BLOCKED` costs the
person waiting on the gate a review: they get "unreviewed by an agent" and
either review the record themselves or grant the permission and run it
again, where an agent that went round the denial might have handed them a
finished one. The router's `BLOCKED`, and a router reply with no outcome
line, cost the person a route: they get `full` and `ambiguous` and either
accept the full chain or give the override words, and a person who doesn't
read the route runs the full chain on a change that might have been a typo.

The fail-closed reading has a cost of its own. A shipped agent that finishes
its work and leaves out the outcome line gets its record reported as
unreviewed by an agent, and the person at the gate pays for it with a review
by hand or a run again. RES-0285 saw one finished run, which wrote the line,
so how often a finished agent leaves it out is unmeasured. The evaluation
cases below accept one run in three without the line, so the rate could be
that high when this lands. That doesn't meet the third reversal below. Three
runs tell a line the agent writes from one it doesn't, and they can't measure
a rate. The third reversal is where the rate gets measured, over fifteen
finished reviews.

A dispatcher that reads the outcome word also refuses a replacement agent
(REQ-2986) that doesn't write one, so a repository that replaced a shipped
agent before this change gets its records reported as unreviewed until the
replacement adds the line.

## What would reverse it

- I would move the outcome into the platform's field and drop the line rule
  if the platform's hand-back gained a status that tells a denied or
  unfinished dispatch from a finished one, because a field the runner fills
  can't be forgotten by the model. The `completed` status it carries today
  doesn't, because RES-0285 saw it on denied dispatches.
- I would drop the agents' denial rule if hand runs on a later platform
  version showed agents without it ending on their first denial and naming
  the tool in three runs of three under each of the three denial texts
  RES-0285 met, on the models the shipped agents declare, because the rule
  would then repeat what the platform already makes the agent do. RES-0285
  saw behaviour without the rule change with the denial text, so a run under
  one text says nothing about the others.
- I would make the dispatcher ask the agent once for its outcome before it
  fails closed, if hand runs over at least fifteen finished reviews showed
  the shipped agents leaving out the line in more than one run in five,
  because at that rate the person at the gate reviews by hand often enough
  that failing closed costs more than the unreviewed record it guards
  against.
- I would widen the reading of REQ-2978 to interactive sessions, and give
  the dispatcher a rule for a permission prompt left waiting, if the platform
  gave a background agent's prompt a timeout or showed a session whether a
  person is present, because either would let the harness tell a prompt
  nobody will answer from one a person is about to.
- I would give the implementing agent a set of its own if its decision found
  that the four words can't carry what a dispatcher does after an
  implementation, because one set across agents is worth keeping only while
  it fits them.

## Consequences

- `plugins/meow-flow/agents/record-reviewer.md`,
  `plugins/meow-flow/agents/router.md` and
  `plugins/meow-prose/agents/prose.md` gain the outcome line and the denial
  rule, and the two reviewers gain the quoting rule. `meow-flow` and
  `meow-prose` each take a minor version. `prose`'s set-up step that reports a
  review as unrun reports `BLOCKED` instead.
- `plugins/meow-flow/skills/method/SKILL.md` gains a rule beside M22 and M23
  for acting on each outcome and for a return with none, and
  `plugins/meow-flow/skills/method/steps/review.md` W13 dispatches
  `record-reviewer` for each record in the change and `prose` for each other
  prose text in it, keeps its present rule for the code, names what
  it reviews by its path, and reads the outcome of the review it dispatches
  by the table, reporting a return with no outcome line as not run.
- The `route` skill reads the router's outcome by its table, in whichever
  change lands second, as What still doesn't work says.
- `plugins/meow-author/skills/write/SKILL.md` gains the rule beside D9, and
  `crates/meow/src/author.rs` gains the outcome rule for a unit's agents,
  with fixtures. `meow-author` takes a minor version.
- The evaluation cases `clean-requirement` and `decision-missing-its-reasons`
  in `plugins/meow-flow/evals/`, `decision-without-reason` in
  `plugins/meow-prose/evals/` and `route-a-tiny-fix` in
  `plugins/meow-flow/evals/` each gain a regex grader for the outcome line.
  The three reviewer cases also gain one for the report's length.
- SPC-1030 gains the outcome rule under what an agent declares and under the
  check, and SPC-1090 gains the dispatcher's tables where the method
  dispatches `record-reviewer` and where the `route` skill dispatches the
  router.
- The outcomes are words in a report and name no language, build tool or file
  extension, so the kernel, method and practice layers still name none.

## How I will know it was realised

1. Crate tests over fixture agents show `meow-author check` failing, naming
   the file and the word, on a unit agent that names none of the four and on
   one missing only `BLOCKED`, and passing on a unit agent naming all four
   and on a repository agent naming none. The failing fixtures are seen
   failing against the current check before the rule lands.
2. `mise run prompts` and `meow-author check` exit 0 at the merge revision
   with all three shipped agents naming the set.
3. Hand-run evaluation cases, run by a person and never in CI, match the
   outcome line with
   `^\s*outcome: (DONE|DONE_WITH_CONCERNS|NEEDS_CONTEXT|BLOCKED)$`. They show
   it on the second line of `record-reviewer`'s report on `clean-requirement`
   and `decision-missing-its-reasons`, and on the first line of `prose`'s on
   `decision-without-reason` and of `router`'s on `route-a-tiny-fix`, each in
   at least two runs of three. Three runs is the platform's default that
   ADR-1500 works from, a hand-run result is a smoke check and not a rate, and
   a majority of three tells a line the agent writes from one it doesn't
   without failing on a single stray run. The same runs show each reviewer's
   report under 4,000 characters, a ceiling I chose, about three times the
   longest report I expect from the decision case's four planted defects.
4. A hand-run case starts, in a fresh session, the method skill's review of a
   record already in the fixture repository under
   `claude -p --permission-prompts none`, so the skill dispatches
   `record-reviewer`, with a settings file whose deny rule names the record's
   path, so the agent's `Read` is denied, as RES-0285's fourth and fifth
   probes were. The agent makes exactly one tool call, the denied `Read`,
   before its report. Its report carries `outcome: BLOCKED` and names `Read`
   and the path, the result's `permission_denials` lists one `Read`, and the
   method skill's gate report calls the record unreviewed by an agent. The
   case holds because M19 hands the reviewer the path alone and the method
   skill doesn't read the record before it dispatches. The deny rule covers
   the whole session, so a skill that read the record first would be denied
   before the agent.
5. A hand-run case under the same flags starts the review step on a verified
   epic in the fixture repository, named by its identifier as this session's
   work, whose change adds a documentation page, so W13 dispatches `prose` for
   that page by its rule. A deny rule names the page's path. The report
   carries `outcome: BLOCKED` on its first line and names `Read` and the
   path, `permission_denials` lists one `Read`, and the session reports the
   review of that page as not run. The case holds because W13 hands `prose`
   the path alone. The session sees the page's lines in the change's
   difference, which the deny rule on `Read` doesn't cover, so the case tests
   the agent's report and W13's reading of it, and a session that opens the
   page with `Read` first is denied before the agent, which fails the case.
6. A hand-run case under the same flags starts the method skill's review of
   a record path that doesn't exist, so `record-reviewer` has nothing to
   review. The stream shows exactly two dispatches of `record-reviewer`, each
   report carrying `outcome: NEEDS_CONTEXT`, and the gate report calls the
   record unreviewed by an agent and names the brief it sent.
7. A hand-run case under the same flags replaces `record-reviewer` with a
   repository agent (REQ-2986) whose definition asks for a review and says
   nothing of an outcome, and starts the method skill's review of a record.
   The agent's report holds no line matching the pattern in criterion 3, and
   the gate report calls the record unreviewed by an agent.
8. Every requirement this decision addresses lands in exactly one closed task.

## What this does not settle

- What the four outcomes mean for an agent that implements work, which the
  decision that ships one settles.
- A check of an agent's outcome against `permission_denials`, which waits for
  a program that runs the harness unattended.
- Whether the method gives up on a record after a `BLOCKED` review or asks
  the person to grant the permission. The gate report names the tool, and the
  person decides.
- How short a report must be for an agent other than the two reviewers. The
  4,000-character ceiling holds for their evaluation cases and nowhere else.

## Open review findings

An agent reviewed this record twice. The second review raised eight
findings: that REQ-2978's scope was unstated for a direct dispatch and an
interactive session, that the `route` skill's result was listed as working
before the skill ships, that W13's path rule said nothing of a text with no
file, that no alternative offered a reviewer's own set, that the denial
rule's reversal rested on one run, that the first reversal could read as met
already, that `record-reviewer` has no standard file to fail on, and that
one sentence in What it costs carried three claims. I made a change for each,
and no reviewer has read the changes, because the method bounds repair at two
rounds. The reading of REQ-2978 in What works after this is the change a
person approving this record most needs to check.

A third review raised three findings to fix and two preferences: that W13
had no rule picking `prose`, that the reading of REQ-2978 cited no source
and nothing reversed it, that no criterion tested the second dispatch after
`NEEDS_CONTEXT` or a return with no outcome line, and that two rules, the
router's `DONE_WITH_CONCERNS` row and the fixed opening line, gave no reason
of their own. I made a change for each, and none is left open.

A fourth review raised three findings to fix and three preferences: that W13
would hand the review of code to `prose`, that criterion 5 couldn't start the
review step on a lone text, that nothing checks a unit agent for the denial
rule, that criterion 4 left open whether the record was already in the
session's context, that the cause line gave no reason, and that the
alternatives had no row for reading a return with no outcome line as
finished. I made a change for each, and none is left open. No reviewer has
read these changes, because the method bounds repair at two rounds.
