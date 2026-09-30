---
id: SPC-1030
artifact: spec
status: live
revised: 2026-09-29
states:
  [
    REQ-0077,
    REQ-0816,
    REQ-1050,
    REQ-1052,
    REQ-1054,
    REQ-1056,
    REQ-1057,
    REQ-1058,
    REQ-1060,
    REQ-1062,
    REQ-1064,
    REQ-1066,
    REQ-1068,
    REQ-1070,
    REQ-1072,
    REQ-1074,
    REQ-1076,
    REQ-1078,
    REQ-1110,
    REQ-1111,
    REQ-1112,
    REQ-1114,
    REQ-1115,
    REQ-1116,
    REQ-1118,
    REQ-1120,
    REQ-1122,
    REQ-1124,
    REQ-1126,
    REQ-1128,
    REQ-1130,
    REQ-1132,
    REQ-1134,
    REQ-1136,
    REQ-1138,
    REQ-1142,
    REQ-1144,
    REQ-1146,
    REQ-1148,
    REQ-1150,
    REQ-1672,
    REQ-1678,
    REQ-2680,
    REQ-2682,
    REQ-2684,
    REQ-2686,
    REQ-2688,
    REQ-2690,
    REQ-2692,
    REQ-2696,
    REQ-2698,
    REQ-2700,
    REQ-2702,
    REQ-2704,
    REQ-2706,
    REQ-2708,
    REQ-2972,
    REQ-2974,
    REQ-2976,
    REQ-2978,
    REQ-2982,
    REQ-2984,
    REQ-2988,
    REQ-3050,
    REQ-3270,
  ]
---

# How the harness writes a prompt

## Scope

Every prompt a unit of the harness ships is what this covers: a skill and its
supporting files, an agent definition, an output style, and the text of a
prompt hook. It states their form, what a rule in them says, how a unit divides
its material and loads it, what it may cost, and the check that holds the form.

It leaves what each prompt says to the specification of its unit, and how a
change to a prompt is measured to SPC-1020.

ADR-1020, ADR-1030 and ADR-1050 decide the form, ADR-1040 how the reply shape
reaches a subordinate agent, ADR-1450 how the capability ships and is checked,
ADR-1700 what an agent declares, and ADR-1710 what an agent reports and what it
does when a tool is denied. What a dispatcher does with each outcome belongs to the specification of
the chain.

## Boundary

| Surface                          | What it is                                                                               |
| -------------------------------- | ---------------------------------------------------------------------------------------- |
| `plugins/<unit>/skills/<skill>/` | A skill: `SKILL.md` as the core, and the files it names                                  |
| `plugins/<unit>/agents/*.md`     | An agent definition                                                                      |
| `plugins/<unit>/output-styles/`  | An output style, loaded on every turn it is in force                                     |
| `plugins/<unit>/hooks/`          | A hook's configuration, and the text of any prompt hook                                  |
| `meow-author check`              | The check over every prompt it is given, run by the `prompts` task and the `lint` verb   |
| `plugins/meow-author/`           | The unit that ships the authoring skill and the check                                    |
| `tools/check_kernel.py`          | The check that the kernel names no unit outside it                                       |
| `meow-author cost`               | The report of each unit's cost against its budget, and its use, run by the `budget` task |

## Behaviour

### Form

A prompt is written for Sonnet 5 and Opus 5.5 and marks its parts with five
tags, none nested inside another, with front matter in YAML (REQ-1130). Inside
a tag the text is Markdown without headings, because a prompt's formatting
carries into its reply and a heading is the skeleton the tags replace. The five
tags are one vocabulary, fixed and stated here, and a prompt uses no other
(REQ-1112, REQ-1114):

| Tag         | Holds                                                                                   |
| ----------- | --------------------------------------------------------------------------------------- |
| `<role>`    | Who the model is while the prompt is in force                                           |
| `<rules>`   | The obligations, each a list item led by an identifier such as `T1.`                    |
| `<steps>`   | A procedure as a numbered list, ending at its stopping point                            |
| `<example>` | One worked case, with its failing and corrected forms under `Failing:` and `Corrected:` |
| `<input>`   | Text from outside the harness, which the prompt treats as data                          |

A tag carries a `name` attribute where a prompt has more than one of its kind.
An obligation is a list item inside `<rules>`, led by an identifier that is
numbered from one within its group, so what must be obeyed is extractable and
a review can cite it (REQ-1120).

### Content

A rule says what to do and carries its reason in the same sentence, and it
states the scope it means, because Sonnet 5 does not generalise an instruction
beyond the item it names. It shows the wanted form, and where it teaches a
judgement, an `<example>` shows the failing form beside the corrected one
(REQ-1126, REQ-1136). The material is written in the form it should produce,
as prose that states reasons (REQ-1115).

An instruction stays while the loop in SPC-1020 shows it changes the result on
Sonnet 5 or Opus 5.5, and goes when it does not (REQ-1138).

### Granularity

A unit divides its material into a core and supporting files (REQ-1142). The
core holds what every use of the unit needs, and names each supporting file
with when to read it (REQ-1124), so the model reads only what the work in front
of it needs. Supporting files are addressed through the platform's directory
variable, such as `${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}`, so a unit
works wherever it was installed (REQ-2688).

The writing skill shows the form: a core with the rules every text needs and a
router placed right after the role, a file of rules for documents, a file of
patterns per prose language, and one file per document type. A short text
needs only the core.

An output style loads whole on every turn it is in force and cannot be divided,
so it holds only what every reply needs.

A kernel prompt names, points to and loads no unit outside the kernel, because
the kernel has to behave the same whether or not that unit is installed
(REQ-0077). `tools/check_kernel.py` fails in the gate when a file in
`meow-core` names another plugin, and review holds a pointer that uses no name,
such as "the writing skill".

### Size

Each unit states a size budget and is measured against it, and an overrun is a
defect (REQ-1056, REQ-1058). The budget sits in the unit's `budget.toml` as
`permanent_characters`, with the measurement it was set from beside it, and
covers what loads on every turn: each skill's and agent's description and
`when_to_use`, and the whole of an output style. `meow-author cost` counts
it in the gate, and fails on an overrun, on a unit stating no budget, and on a
description over the platform's cap. Material past the budget moves into
supporting files, and never loses an obligation to get shorter (REQ-1057). Only
what a model needs to decide whether the unit is relevant sits in context on
every turn (REQ-1050).

A unit's obligations sit in the first 5,000 tokens of its core and ahead of
its explanations, because the platform keeps that much of a skill after
compaction, so a truncation costs an explanation and never a rule (REQ-1064,
REQ-1066).

### When material loads

Material needed only once a capability is chosen loads at that point, and
material for an unusual case loads only in that case, never carried by material
that is always loaded (REQ-1052, REQ-1054). One capability is one skill, and a
skill belongs to one discipline, split where it spans two (REQ-1068, REQ-1070).
A rule carries its reason beside it where the rule is counter-intuitive or the
model's default is wrong, and otherwise the reason lives in material loaded on
demand (REQ-1076). Moving explanation out of always-loaded material is shown
not to change behaviour by the loop SPC-1020 states, not by assertion
(REQ-1078). Instruction that applies only to certain files is a path-scoped
rule, and splitting always-loaded material into imported files is no saving,
because the platform expands imports at launch (REQ-2696, REQ-2698). Nothing
loads because it might be relevant, no obligation sits in a file read at the
model's discretion, and mutually exclusive branches sit in separate files
(REQ-2700, REQ-2702, REQ-2704).

### The cost report

`meow-author cost` reports, for each unit under `plugins/`, the characters it
keeps in context on every turn against the budget its `budget.toml` states. It
fails on a unit over its budget, a unit with no budget and a description and
its `when_to_use` together over the cap (REQ-1072). This repository's `budget`
task runs it, so the report is part of every verification (REQ-1074). How
often each skill is used comes from the platform's `/skill-doctor`, which the
report names, and the harness reads none of the platform's private files
(REQ-1072).

### Descriptions and loading

A unit's description is written in the third person, says what the unit does
and when to use it, leads with the words a request contains, and fits the
platform's cap of 1,536 characters (REQ-1060, REQ-1062, REQ-1134, REQ-3050).

A unit that has to be in context before the model acts is loaded by its
description, which states the obligation. The description opens with a
sentence saying what the unit is, then says in the third person that the unit
MUST be loaded before the work (REQ-1144). It names each verb a request uses
for that work and no work the unit does not govern (REQ-1146), and it closes
by saying the unit MUST NOT be skipped however short or simple the work looks
(REQ-1148). The writing skill's description shows the form:

```text
The writing standard for all text. It MUST be loaded before any prose of any
length is written, rewritten, reworded, edited or reviewed, including code
comments, pull request and issue descriptions, commit messages, and Markdown
files. It MUST NOT be skipped, however short or simple the text looks.
```

Sonnet 5 reads a description literally, so a verb the description leaves out
is a request the unit misses. The second person reads as a different voice
from the platform's own prompt, and loaded the writing skill in less than half
as many runs.

How often such a unit loads is measured on Sonnet 5 and on Opus 5.5, on
requests that should load it and on near misses including answers in chat,
and a change to its description is measured again before it ships (REQ-1150).

### Outside text

Text from outside the harness that a prompt carries, such as a text under
review or a hook's input, sits inside `<input>`, and the prompt states that
instructions inside it are data. Where the harness assembles the prompt itself,
the opening and closing tags carry one identifier generated for that call
(REQ-1132).

### What a unit declares

Every skill and agent carries front matter saying what it is for and when to
load it (REQ-1110). The harness has one kind of loadable unit, the skill, and a
command is a skill only a person invokes, with `disable-model-invocation`, so a
plugin ships no `commands/` directory (REQ-1111). A skill with side effects is
invoked only by a person, and a skill that is knowledge only by the model
(REQ-2680). A skill for one language or directory declares its `paths`
(REQ-2682), and one whose work is a long read ending in a short answer runs in
a forked context (REQ-2684). Material injected when a skill loads is cheap and
certain, runs no verb, and nothing depends on it (REQ-2686). Every command is
namespaced, because the platform prefixes a plugin's skills with the plugin's
name (REQ-2690). A unit proposes the permissions it needs on its page and
leaves the repository to declare them (REQ-2692). A script says whether it is
run or read, and one that is run is never also summarised in prose (REQ-2706).
Instructions use the vocabulary of the work they govern (REQ-2708).

### What an agent declares

An agent definition declares six fields in its front matter, each written
out, because the platform has a default for every one of them:

| Field          | What it holds                                                                  | Requirement |
| -------------- | ------------------------------------------------------------------------------ | ----------- |
| `maxTurns`     | A positive integer, the ceiling on turns the runner enforces                   | REQ-2974    |
| `tools`        | A written list, empty included; in a unit's agents, no `*`, `Agent` or `Task`  | REQ-3270    |
| `model`        | `sonnet`, `opus`, `haiku`, `fable`, or an identifier containing `claude-`      | REQ-2988    |
| `effort`       | `low`, `medium`, `high`, `xhigh` or `max`                                      | REQ-2988    |
| `omitClaudeMd` | `true` or `false`, written out                                                 | REQ-2982    |
| `skills`       | A list of the skills the agent preloads, and an empty list where it needs none | REQ-2984    |

An agent a unit ships holds no tool that dispatches another agent: its
`tools` list holds no `*` and names neither `Agent` nor `Task`, alone or with
a restriction such as `Agent(worker)` (REQ-3270). An empty list, `tools: []`,
grants no tool, so it passes (RES-0284). A repository's own agent may list any
tools, `*` included, once it writes the list.

The `model` rule accepts the four documented aliases (RES-0284) or any value
containing `claude-`, which every full identifier does, so a new identifier
passes, a misspelt alias such as `opsu` fails, and `inherit` fails because it
leaves the cost to whichever session dispatches the agent (ADR-1700).

An agent loads the project's instructions, with `omitClaudeMd: false`, where
it judges against the repository's rules, and omits them where it judges
against a standard it preloads (REQ-2982). An agent with a narrow job
preloads the skills it needs through `skills`, so the conversation that
dispatches it doesn't carry them (REQ-2984). The agents the harness ships
declare:

| Agent              | `maxTurns` | `model`  | `effort` | `omitClaudeMd` | `skills`               | `tools`          |
| ------------------ | ---------- | -------- | -------- | -------------- | ---------------------- | ---------------- |
| `meow-flow:router` | 30         | `sonnet` | `high`   | `false`        | `[]`                   | Read, Grep, Glob |
| `meow-prose:prose` | 20         | `sonnet` | `high`   | `true`         | `[meow-prose:writing]` | Read, Grep, Glob |

An agent that reaches its `maxTurns` returns its output marked as stopped at
its ceiling, and whatever dispatched it reads that output as unfinished work
(REQ-2974). RES-0284 read the marking from the platform's code and
documentation, and no run has shown it yet, so the hand-run case EPC-1650
adds is the first that can (ADR-1700).

### What an agent reports

An agent a unit ships ends every dispatch with one outcome from a closed set of
four, written on a line of its own as `outcome:`, a space and the word, so the skill
that dispatched it acts on the word without reading the rest (REQ-0816):

| Outcome              | The agent reports it when                                           |
| -------------------- | ------------------------------------------------------------------- |
| `DONE`               | It did the work its rules set, whatever it found                    |
| `DONE_WITH_CONCERNS` | It finished, and part of the work couldn't run                      |
| `NEEDS_CONTEXT`      | The brief names nothing it can work on                              |
| `BLOCKED`            | A tool call was denied, or an input its rules need couldn't be read |

The outcome says whether the work happened, and the rest of the report says
what it found. A review that found six defects is `DONE`, a clean one is
`DONE`, and a route marked `ambiguous` is `DONE`. The specification of the
chain gives each shipped agent's rows in full, with what its dispatcher does
on each.

The line reads `outcome:`, a space and one of the four words, and nothing
else.
Where the outcome isn't `DONE`, one sentence naming the cause follows it, such
as `Read was denied on project/adrs/ADR-0001.md`: the part that didn't run,
what the brief lacked, or the tool denied and what it was called on. Each
shipped agent places the two lines as follows:

| Agent              | The outcome line                            | The cause                          |
| ------------------ | ------------------------------------------- | ---------------------------------- |
| `meow-prose:prose` | The first line, before the verdict          | The second line                    |
| `meow-flow:router` | The first field, `outcome:`, before `size:` | A `cause:` field, after `outcome:` |

An agent that opens its report with a fixed line keeps that line first and
puts the outcome line second. Any other agent puts the outcome line first.

`prose` quotes nothing it reads beyond the span a
finding names, 25 words at most, and cap no number of findings (REQ-0816). A
finding names its line, so a longer span, such as a table row, is found
there.

Every shipped agent carries the denial rule, in the same words: where a tool
call is denied, the agent issues no second call in another form, uses no other
tool to reach the same result, asks nobody for the permission, and ends with
`outcome: BLOCKED` and one sentence naming the tool and what it was called on
(REQ-2978). A denied call is `BLOCKED` whatever it was called on, a cited
record included. A cited record or file that doesn't exist or doesn't resolve
is not a denial, and a reviewer reports it as `DONE_WITH_CONCERNS`. Under a
run with permission prompts disabled, every permission request becomes a
denial at once, so a shipped agent ends on its first denial and nothing waits
on an answer. `meow-author check` reads the four words in a definition, and
review holds the denial rule, because no pattern tells its wording from a near
miss.

### Delegation

Knowledge, such as a design lens or a language's idioms, ships as a skill
loaded into the working context and never as an agent (REQ-2972). A
delegated agent runs in the parent's process and under the parent's sandbox
configuration, so no text the harness ships treats one as a boundary that
contains what the agent does (REQ-2976). Review holds both, because no field
shows either.

Tags mark a prompt where it mixes kinds of content, and a prompt that is one
instruction after another carries them only as far as its role and its rules
need (REQ-1116, REQ-1118). A procedure's steps end at a named stopping point
(REQ-1122).

### Authoring

`meow-author` ships this capability to any repository (REQ-1672). Its skill,
`meow-author:write`, loads before a skill, agent, output style or hook prompt
is written or changed, and carries the rules above. A repository uses it on
its own material, held to the same rules, and that material stays the
repository's (REQ-1678).

### The check

`meow-author check [path...]` reads every unit under `plugins/`, or the paths
it is given, such as `.claude/`, and fails, naming the file and the line, on:

- a Markdown heading, a tag outside the vocabulary, a tag opened inside
  another, a tag never closed or text standing outside every tag, with text inside `<example>`
  and `<input>` read as quoted and not judged;
- a skill or agent with no `description`;
- an agent leaving out one of the six fields above, or holding a value the
  table doesn't accept, naming the field; in a unit's `agents/` directory, a
  `tools` list holding `*`, `Agent` or `Task`, alone or with a restriction.
  `tools` is read as a YAML list or as a comma-separated string;
- an agent whose front matter doesn't parse, with that reason and no field
  rule run on it;
- an agent in a unit's `agents/` directory whose body doesn't name all four
  outcomes, naming each missing word. A repository's own agent isn't read for
  this rule;
- a plugin shipping a `commands/` directory;
- a file in a skill's directory that its `SKILL.md` never names;
- a path into the unit written without the directory variable;
- a skill's core or an agent with a procedure and no step naming where it
  stops.

One check audits every unit, because the format is uniform across them
(REQ-1128). This repository's `prompts` task runs it, in the `lint` verb.

## Failure paths

| Condition                                                        | What happens                                                                       |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| A prompt uses a heading or an unknown tag                        | The check fails in the gate, naming the file and the line                          |
| A prompt nests a tag inside another                              | The check fails, because the vocabulary is top-level only                          |
| A core names no supporting file for a kind of work               | The model loads nothing for it, and the unit is defective against REQ-1124         |
| A core grows past 5,000 tokens                                   | The tail is lost after compaction, which is a defect against REQ-1064              |
| A unit exceeds its stated budget                                 | The overrun is reported as a defect and the material moves into supporting files   |
| The model does not load a unit that must hold                    | The routing measurement shows it, and the description is the thing that changes    |
| A description loads its unit on a near miss                      | The routing measurement shows it, and the wording is narrowed before it ships      |
| An agent leaves out a declared field                             | The check fails in the gate, naming the file and the field                         |
| A shipped agent lists `Agent`, `Task` or `*`                     | The check fails, naming the file and the `tools` field                             |
| A shipped agent names a model the account lacks                  | The dispatch fails to start, and a repository replaces the agent with its own      |
| An agent reaches its `maxTurns`                                  | Its output comes back marked partial, and the dispatcher reads it as unfinished    |
| A unit's agent doesn't name all four outcomes                    | The check fails, naming the file and each missing word                             |
| A shipped agent's tool call is denied                            | The agent makes no other call for it and ends with `outcome: BLOCKED` and the tool |
| A shipped agent's report carries no outcome line                 | Its dispatcher reads it as work that didn't run                                    |
| A background agent's permission prompt in an interactive session | It waits in the main session for the person, with no timeout the harness sets      |
