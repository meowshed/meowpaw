---
reader: someone choosing or running meow-flow
answers: what meow-flow does, what it adds to a session and how to run it
kind: reference
describes: [meow-flow@0.53.0]
---

# meow-flow

`meow-flow` runs the method: seven steps from research to review, each
writing one artifact from an approved input. It keeps the record those steps
write, the research, requirements, decisions, specifications, epics, tasks and
defects, and checks it, reporting each finding with its file and line. It
installs on its own, with no other part of the `meowpaw` harness.

You run the record's command as `paw`, from the unit's `bin/` directory.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://paw.retran.me/meowpaw/marketplace.json
claude plugin install meow-flow@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone. It also enables `meow-prose`, whose writing skill the researcher agent preloads, and keeps `meow-prose` enabled while this unit is on.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

## Bring a repository in

Type `/meow-flow:init` in a repository with no `.meowpaw/profile.toml`. It
reads the repository and writes the profile from the template
`paw template profile` names, and a `CLAUDE.md` from the constitution
template where the repository has none. It writes nothing else, and it leaves
an existing `CLAUDE.md` untouched. Review both files before you commit them.

Then type `/meow-flow:onboard` to bring the repository's existing documents
into the record. It recovers the vision, the specifications and, where none
exists, the constitution, each statement ending with the file it came from and
a confidence. Where `meow-github` is installed it reads the repository's
issues, pull requests and comments too. Each obligation a document, an issue
or a pull request states becomes a draft requirement, and each choice
recorded with the alternative it rejected becomes a draft decision, citing
where it was stated; code alone yields neither, and you affirm each draft by
approving it. Without `meow-github`, the report says the history is unread. It
stops at `onboarding.md`, a draft report placing every document the
repository has, which `check coverage` holds, and waits for your approval.

Once you approve the report, run `paw onboarding remove` to finish.
It removes each document the report marks migrated, superseded or discarded,
keeps each one marked cited, and prints the count before and after. It
refuses, removing nothing, while the report isn't approved or where a
migrated document's destination doesn't exist, and it commits nothing, so you
review the removal as a change of its own.

## Declare where the record lives

Put it under `[record]` in `.meowpaw/profile.toml` at the repository's root:

```toml
[record]
root = "project"
```

`root` is relative to the repository's root, and it may lead outside it, to a
folder or to another repository's checkout. Where you declare none, the record
is at `project/`.

Each `paw` command that reads the record, except the session-start
`paw status --waiting`, prints the profile's state on standard error, `profile: absent`, `profile: unparseable` or
`profile: parsed`, and then `unknown key: <path>` for each key no unit reads.
It goes to standard error because standard output is what a step reads, such
as a template or an identifier. An unparseable profile stops the command with
the parser's message, and an unknown key changes no exit status.

## Declare your own kinds

Declare a kind of artifact the harness doesn't ship under
`[record.kinds.<name>]` in the same profile, and `paw check` holds its files to
the same rules as the built-in kinds:

```toml
[record.kinds.narrative]
prefix = "NAR"
lifetime = "record"
template = ".meowpaw/templates/narrative.md"
outranks = ["research"]
```

`prefix`, `lifetime` and `template` are required. `lifetime` is `record`, which
freezes a file on approval, or `living`, which you rewrite freely. `template`
is a path under `.meowpaw/templates/` to a file that exists. Files of the kind
sit in a directory named for the kind under the record's root, as
`project/narrative/NAR-0001-<slug>.md`, with the front matter every artifact
carries: `id`, `artifact` (the kind's name), `status` and `revised`.
`paw check` reports a declaration that lacks one of the three, a template that
doesn't exist and a prefix another kind uses. A key that would turn an
obligation off, such as `frozen = false`, is an unknown key, because a
declared kind is never exempt from the method. `paw index` writes no index
for a declared kind.

`outranks` is optional. Where two artifacts of kinds in that order cite each
other and state different values for a field of their own, `paw check`
reports the pair in `relations`, naming both files and the order. It doesn't
choose between them, and the fields every artifact carries and the relations
are left out of the comparison, because they describe the artifact and not
what it claims.

## Name the document a task produces

A task's output can be a document. Name it in the task's `produces:` and name
the task in the document's `prompted-by:`:

```yaml
# project/tasks/TSK-0001-write-the-finding.md
produces: [RES-0002]
# project/research/RES-0002-the-finding.md
prompted-by: TSK-0001
```

`paw check relations` reports either side without the other, naming both
artifacts, and a `produces:` that names no file. The document is held to its
kind as one a step wrote is, so research still needs its Summary, Method,
Conclusions and Sources. `prompted-by:` on research, a requirement or a
decision names a defect or a task.

## Run the method

Type `/meow-flow:run` to be taken to the next approval gate. It reads where
the record stands, runs the next step, and stops where that step waits for
your approval, saying what the next run will do. Run it again after you approve, and it carries on; run it with nothing approved, and it says what it
is waiting on.

To approve a whole decision at once, ask for it in one pull request. Claude
then writes the research, requirements, decision, specification changes, epic
and tasks in turn, checks each as a draft before marking it approved, and
stops once at the pull request, which it opens and names for you. Where your
repository declares no code host, it stops at the branch and names that.
Merging it is your approval, and nothing is
implemented before you do.

To run one step yourself, ask for it by name, such as "run the design step for
`REQ-0190`", and Claude loads the `method` skill. The steps, in order:

| Step           | Reads                          | Writes                      |
| -------------- | ------------------------------ | --------------------------- |
| `research`     | a question                     | a research record           |
| `requirements` | approved research              | requirement records         |
| `design`       | approved requirements          | a decision record           |
| `spec`         | an approved decision           | the specification, updated  |
| `epic`         | an approved decision or defect | an epic and its tasks       |
| `implement`    | an approved task               | the change and its evidence |
| `review`       | the epic's pull request        | findings, fixed in it       |

Where a decision adds a security-relevant boundary, the design step also
updates the threat model your specification keeps, so the new threats are
ranked among those it already lists. Where your specification keeps none, the
decision says so.

An epic's pull request carries the whole epic, and each of its tasks is a
group of commits on that branch: its tests first, in a commit of their own
where they fail, then the implementation, the documentation it changes and its
record marks. The pull request is ready to merge when the last task is done.

The implement step writes to the documentation style you declare in
`.meowpaw/profile.toml`, as a path to your style guide or the name of an
installed unit that ships one:

```toml
[docs]
style = "docs/style.md"
```

Where you declare none, it says so and writes to the writing standard in
force. It names each page's kind before writing it, runs every example it
writes, and reports which of your stages checked the documentation.

A defect authorises work as a decision does. Where the fix is one task, the
defect record carries it under `## Tasks`, with the same marks an epic uses,
and the task names `bug: BUG-NNNN` in place of `epic`. `paw status` counts the
tasks decisions authorised and the tasks defects did.

An epic's `## Tasks` entry carries no mark. A task is done once its Evidence
is written past `Not yet.` and dropped once it is withdrawn, rejected or
superseded. An approved epic that carries `[x]` and `[~]` marks keeps them, and
`paw` reads both forms, so `paw check` fails a draft epic that marks a task and
passes an approved one that does. The reading of marks stays until a decision migrates the approved epics.

A task sits under its epic or its defect and nothing else, so `paw check`
reports a task, an epic or a defect carrying a grouping field, `milestone`,
`parent`, `project`, `sprint`, `iteration`, `label` or `labels`, whatever its
status, and an epic carrying `epic`.

A defect is reproduced before it is triaged, and its triage names in `enters`
the step it enters at: `implement` or `design` where it violates a requirement,
`requirements` where the requirement is wrong or none covers the behaviour,
and `research` where the cause is unknown. `paw check` reports a triaged
draft with no `enters`, a defect entering at `implement` or `design` with no
`violates`, a triage with no reproduction, a rejected report with no
reasoning, a closed defect whose Closed by names no check, an epic for a
defect that one task would fix, and a `prompted-by` naming no defect.

A step refuses when its input is missing or not approved, because the program
checks that before the step writes anything:

```text
$ paw ready implement TSK-1430
paw ready implement: not ready
  TSK-1420, which TSK-1430 depends on, isn't done
```

`paw ready implement` asks that of a task: the task and its epic, defect or
decision approved or done, and each task under its `## Depends on` done. It reads the task's approval from the working tree, so a task approved on
the epic's own branch is ready before its change merges, and `paw status`
names it as next.
A decision
one task realises needs no epic: the task names `realises: ADR-NNNN` in place
of `epic:`, and it derives completion once its Evidence is written. A decision,
epic or task stores `status: done` in the same change, and `paw check` rejects
either a false `done` claim or derived completion left at `approved`.

`paw status` prints where the record stands, leading with whatever waits for
your approval. For an epic with open tasks it names the first task it can
take, at `implement`, and calls an epic closed once every task is done or dropped. It counts the
requirements in force by the state it derives from the tasks and defects
naming them: closed, in a task not yet done, reopened by a defect, postponed,
or named by no task. A requirement closes when a task naming it is done and
none naming it is open, and an open defect naming it in `violates` reopens it
until the defect closes. It counts the requirements in force by how each is verified, and
states how many rest on evaluation or judgement. Under "Only a new record can
fix" it lists what `check` can't ask a change to clear, because the artifact is
approved and frozen: an approved artifact over a rejected provider, a suspect
citation in an approved artifact, and an approved or living artifact that cites
nothing and that nothing cites. None of these makes it fail. Where the record's root is under no version control, it says the
record is local to this machine. `paw status --brief` prints the same
sections, but counts the closed decisions, the postponements and the frozen
findings in place of listing them, so `/meow-flow:run` reads a page and not
the whole record. When a session starts, a hook runs `paw status
--waiting`, so Claude opens with any draft waiting for you and says nothing
when none is, except on a machine with no binary, where it says the record
wasn't checked. `paw show <id>` prints what an identifier names and every
artifact that cites it, grouped by the field that cites it, and for a
requirement each task closing it with its mark and its epic.
It marks a citation as suspect where its target was revised after the citing
artifact, which is how an approved artifact's suspect citations are reported.
`paw brief <task> [--agent <unit>:<agent>]` prints the brief a delegated
agent gets for a task, built from the record and never from a conversation:
what to build, the constraints, the interfaces it touches and what to report
back, each under its own heading. It copies each constraint word for word,
inside a fence, from the requirements the task closes and from the task's
Acceptance criteria and Left alone. Its first line names the agent definition
the brief is written for, `general-purpose` unless you pass `--agent`, because
that's the platform's agent the implement step dispatches, and no unit ships an
implementer. A task naming `realises:` has its decision read where an epic
would be. It writes nothing, and it exits 1 for an identifier that names no
task.
`paw count` prints each kind's number of artifacts by status and the number of
identifiers, which a migration runs before and after to show it lost nothing.
`paw find <word>...` lists the artifacts whose identifier, title or conclusion
carry the words, headings only and at most twenty. Its first line,
`exhaustive: read <n> artifacts`, says it read every artifact, so a miss
means no artifact's identifier, title or conclusion carries the words. A
conclusion is a requirement's statement, the first sentence of a research
record's Summary, and otherwise the title, so a word elsewhere in a document
needs a search of the files. Each hit ends with its file and `front matter`
or the section it matched in, and the last line, `artifacts matched: <n>`,
counts the artifacts past the twentieth too. `paw new <kind> [--topic
<topic>]` prints the next identifier to allocate, never one any file already
carries. `paw index <kind> --write` regenerates a kind's index between its
`<!-- meow-flow index -->` markers, and `check index` reports one that has
fallen behind the tree. Since 0.32.0 an index carrying the markers from before
the unit's rename isn't read, and `--write` names the markers it needs.
`paw template <kind>` prints the template a step writes from: yours at
`.meowpaw/templates/<kind>.md` where you have one, and the unit's otherwise.

`paw --help` lists every subcommand, and `paw <subcommand> --help` prints what
it determines, a `by hand:` line naming what you read to reach the same answer
without the tool, and a `lines:` line stating the first word of each kind of
line it prints. Tests run each subcommand on a fixture record and fail a
line whose first word the help doesn't state.

## Have a change reviewed

The review step reads the epic's pull request. Where the session wrote the
change, it sends the difference to an agent with read-only tools, fixes what
the agent finds in that pull request, and writes one sentence on it in the
task's Evidence. It reports each test that would still pass against a wrong
implementation. Where the agent reports `BLOCKED`, because a tool it needed
was denied, the step reports the review as not run, and doesn't resume the
agent, send another under the same permissions or review the change itself. No agent reviews a record: you read it when you approve its
pull request.

The implement step hands a task to another agent only to keep its own context
clean or to run independent tracks at once, never because the task is large.
It gives that agent the output of `paw brief <task>`, and declares
`isolation: worktree` where agents implement in parallel. A fresh agent, never
a fork of the session that did the work, reviews delegated work, and a third
fresh agent settles a disagreement between the two, given both positions and
the brief. The pull request names the task and `paw brief <task>`, and names
no agent, model or vendor.

## Write a status change in one command

A status change that touches several files is one command, so none of the
files is left out:

```bash
paw approve <id>...                      # draft to approved, where `paw check` reports nothing about it
paw done <task> --pr <number>            # done in the task, marked in its epic or defect, closed up the chain
paw withdraw <requirement> --by <decision> --replaced-by <id>...
```

`approve` writes nothing and exits 1 where the check has a finding about a
record you named. `done` refuses a task whose Evidence still opens with
`Not yet.`, marks the entry with the pull request you give, and stores `done`
in the epic and the decision once the last task is done. `withdraw` writes the
tombstone, the status and today's date. Each command changes only the lines it
owns and regenerates the index of each kind it touched, and a result passes
`paw check` without the command, so you can still edit a record in your editor.

## Postpone requirements

A decision can postpone requirements you choose not to realise now. Give it
`postpones: [REQ-...]` beside or in place of `addresses:`, and say under What
would reverse it when they should be taken up. The requirements then read as
postponed in `show` and `status`, and stop reading as postponed once a task
closes them. A decision that only postpones needs no epic. `paw status` lists
every postponement under Postponed with its condition, the first entry under
the decision's What would reverse it, so you see them on each run.

## Check the record

From the repository, run every check, or one by name:

```bash
paw check
paw check relations
```

A run with one finding prints it and each check's count. A draft is held to
every rule of its kind, and an approved record to the rules it was approved
under, because an approved record is frozen:

```text
project/bugs/BUG-0001-a-defect.md:4: status done is not one a defect stores: draft, approved, withdrawn, rejected, superseded
front-matter: 1 finding
identifiers: 0 findings
relations: 0 findings
index: 0 findings
coverage: 0 findings
shape: 0 findings
rules: 0 findings
```

| Check          | Reports                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `front-matter` | A field the kind requires that's missing, a field the kind forbids, a status the kind doesn't store, a bad `revised`; a retired field or status, which `lib/layout.toml` lists with what replaced it; a decision, epic or task whose stored `done` disagrees with derived completion; a kind declared under `[record.kinds]` that lacks a prefix, lifetime or template                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `identifiers`  | A file whose name and `id` disagree, an identifier used twice, a second file carrying `id: vision`, a cited requirement not found                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `relations`    | An identifier in a relation field with no file, one in a draft's prose outside code, and a link in the record to a missing file; a suspect citation in a draft or living artifact, one whose target was revised after it, or an epic or defect it cites that is withdrawn or superseded; two artifacts across a declared kind's `outranks` order that cite each other and disagree on a field; a task and the document it `produces` that don't name each other                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `index`        | A file its kind's index doesn't list, and an index entry with no file; a specification listed before one it cites                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `coverage`     | A requirement a decision addresses that lands in no task, or in no specification; a task whose Evidence section says it's done while its epic leaves it unmarked; an open task closing a withdrawn requirement; an approved or living artifact resting on a draft anywhere up its chain, and a draft or living one resting on a withdrawn, superseded or rejected provider, each with the chain named. It also states how many requirements in force land in a task, and calls an empty record's coverage zero. Where an onboarding report exists, a document the repository has that the report doesn't place exactly once, with one of four outcomes and a destination or reason                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `shape`        | An artifact missing a section its kind carries, such as research without its conclusions; a section the layout retired, such as `## Cover`; a withdrawn requirement cited in a living document outside a Withdrawn section; a record kept in an archive directory; a vision missing Who it is for, Quality goals, What it will not do or Risks                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `rules`        | An undated source or a cited requirement in draft research, a requirement whose `verification` isn't `static`, `behavioural`, `evaluation` or `judgement`, a judged draft requirement with no verifier, a draft requirement carrying two keywords, leaning on a neighbour or written as "No X MUST Y", an epic realising other than one record, a decision's alternatives with no reason they lost; an epic task marked done with no evidence, or added or dropped with no reason; an onboarding report whose Adoption section has no numbered steps; a vision carrying a date, a requirement stated as an obligation or a body over 2,000 words; a specification carrying struck text, a heading naming a tombstone or a withdrawal, or a phrase from `history_phrases` in `lib/layout.toml` such as "previously"; a withdrawn record whose first line under its title names no record; a draft epic marking a task with a checkbox or a Status column, because a task's state is read from the task; an insight whose title carries a date or runs under four words, whose evidence holds no number or block, or that doesn't end with The pattern |

`paw check frozen --base <rev>` reports each record approved at
`<rev>` and changed since, outside what its kind may change: a task's Evidence,
an epic's Tasks, a defect's Tasks and Closed by. It passes a change that only
removes a retired field or section, and one that
adds a line naming its authority, such as `**Amended by ADR-0120.**`: a change
to an approved record invalidates its approval. It runs only by name, because
it needs git and a base.

It exits 0 when no check found anything, 1 when any did or the root doesn't
exist, 2 for a check it doesn't know, and 3 when the record wasn't checked.

After the checks, `paw check` counts the lines of `CLAUDE.md` at the
repository's root. Over 200 it prints
`CLAUDE.md: over its target of 200 lines at <n>; cut it`. The line is advice:
it changes no check's count and no exit status, because 200 lines is a target
and a hard limit would cut rules to fit a number. A repository with no
`CLAUDE.md` gets no line.

## Replace the researcher

To use a researcher of your own, put its definition in
`.claude/agents/researcher.md` in your repository. Claude Code loads it under
the bare name `researcher`, beside the unit's `meow-flow:researcher`, and
keeps both. The research step dispatches `meow-flow:researcher`, so it still
gets the unit's definition, and only a dispatch that names `researcher` gets
yours. So your definition doesn't win over the unit's name, and you ask for
`researcher` by name when you want yours.

## Tools

The `researcher` agent holds four tools, each for one step of its procedure:

- `Read`: step 1 reads the primary sources the brief names.
- `Grep`: step 1 finds where a source lives where the brief names no path.
- `Glob`: step 1 lists the paths that match a name the brief gives.
- `WebFetch`: step 1 reads a source the brief names by its address.

## What it costs you

The `method` and `route` skills' descriptions, the driver's and the
`researcher` agent's, on every turn, so Claude knows when to load each. The
program is a native binary shipped inside the unit, so it needs nothing
installed on the machine. On a machine the unit carries no binary for, it
reports the record as not checked and exits 3, and its session-start hook says
so and names `claude plugin install meow-core@meowpaw` and exits 0, so the
session begins.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared
in `plugins/meow-flow/requires.toml`. It relies on these platform behaviours,
each documented by Claude Code:

- a skill loaded by its description, and one only a person invokes, with `disable-model-invocation`: [documentation](https://code.claude.com/docs/en/skills.md)
- a `SessionStart` command hook whose output reaches the model before its first reply: [documentation](https://code.claude.com/docs/en/hooks.md)
- a plugin's `bin/` programs, run by path: [documentation](https://code.claude.com/docs/en/plugins-reference.md)

## Hooks

`status --waiting` stops nothing: at the start of a session it reports what waits at a gate, so the model sees a pending approval before it replies.

## Where it reads the record

The layout it reads each kind by is `plugins/meow-flow/lib/layout.toml`.
