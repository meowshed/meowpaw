---
reader: someone choosing or running meow-flow
answers: what meow-flow does, what it adds to a session and how to run it
kind: reference
describes: [meow-flow@0.39.1]
---

# meow-flow

`meow-flow` runs the method: ten steps from research to review, each
writing one artifact from an approved input. It keeps the record those steps
write, the research, requirements, decisions, specifications, epics, tasks and
defects, and checks it, reporting each finding with its file and line. It
installs on its own, with no other part of the `meowpaw` harness.

You run the record's command as `paw`, from the unit's `bin/` directory.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-flow@meowpaw
```

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

## Run the method

Type `/meow-flow:run` to be taken to the next approval gate. It reads where
the record stands, runs the next step, and stops where that step waits for
your approval, saying what the next run will do. A step that ends with no
approval, such as cover, doesn't stop it: it reads the record again and runs
the step after, so one run takes an approved task through cover and
implement. Run it again after you approve, and it carries on; run it with nothing approved, and it says what it
is waiting on.

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
| `document`     | an epic with every task done   | your documentation, updated |
| `verify`       | an epic with every task done   | the epic's verification     |
| `review`       | a verified epic                | findings, never a file      |

The document step writes to the documentation style you declare in
`.meowpaw/profile.toml`, as a path to your style guide or the name of an
installed unit that ships one:

```toml
[docs]
style = "docs/style.md"
```

Where you declare none, it says so and writes to the writing standard in
force. It names each page's kind before writing it, runs every example it
writes, and reports which of your verbs checked the documentation.

A defect authorises work as a decision does. Where the fix is one task, the
defect record carries it under `## Tasks`, with the same marks an epic uses,
and the task names `bug: BUG-NNNN` in place of `epic`. `paw status` counts the
tasks decisions authorised and the tasks defects did.

A task sits under its epic or its defect and nothing else, so `paw check`
reports a task, an epic or a defect carrying a grouping field, `milestone`,
`parent`, `project`, `sprint`, `iteration`, `label` or `labels`, whatever its
status, and an epic carrying `epic`.

A defect is reproduced before it is triaged, and its triage names in `enters`
the step it enters at: `cover`, `implement` or `design` where it violates a requirement,
`requirements` where the requirement is wrong or none covers the behaviour,
and `research` where the cause is unknown. `paw check` reports a triaged
draft with no `enters`, a defect entering at `cover`, `implement` or `design` with no
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

`paw ready cover` asks that of a task: the task and its epic or defect
approved, and each task under its `## Depends on` done. `paw ready implement`
asks the same and also reads the task's `## Cover` section, four lines naming
the checks, the kept run in which they failed, where they landed and each
criterion resting on judgement with its reason:

```text
- Checks: tests/test_a_task.py
- Failing run: evidence/a-failing-run.txt
- Landed in: #12
- Judgement: 2: whether the page reads well rests on a reader
```

It refuses while the section is missing or reads `Not yet.`, while a path
under `Checks` or `Failing run` names no file in the repository, while
the failing run lies outside the evidence directory or is a file git ignores,
while
`Landed in` reads `none` beside a named check, and while a `Judgement` number
has no reason. A task with no check to write reads `none` on the first three
lines and names every numbered acceptance criterion under `Judgement`. `ready`
reads only these lines, so it doesn't check that the run failed. The method
skill doesn't run the cover step yet, so until it does you write the Cover by
hand.

`paw status` prints where the record stands, leading with whatever waits for
your approval. For an epic with open tasks it names the first task it can
take, at `cover` while the task's Cover isn't filled and at `implement` once it
is. It counts the requirements in force by the state it derives from
the tasks closing them: verified, closed and not yet verified, in a task not
yet done, or checked by nothing. It calls an epic verified only while `check`
reports nothing on the epic, its decision or its tasks, and calls it drifted
otherwise. It counts the requirements in force by how each is verified, and
states how many rest on evaluation or judgement. Under "Only a new record can
fix" it lists what `check` can't ask a change to clear, because the artifact is
approved and frozen: an approved artifact over a rejected provider, a suspect
citation in an approved artifact, and an approved or living artifact that cites
nothing and that nothing cites. None of these makes it fail. Where the record's root is under no version control, it says the
record is local to this machine. When a session starts, a hook runs `paw status
--waiting`, so Claude opens with any draft waiting for you and says nothing
when none is. `paw show <id>` prints what an identifier names and every
artifact that cites it, grouped by the field that cites it, and for a
requirement each task closing it with its mark and its epic's verification.
It marks a citation as suspect where its target was revised after the citing
artifact, which is how an approved artifact's suspect citations are reported.
`paw count` prints each kind's number of artifacts by status and the number of
identifiers, which a migration runs before and after to show it lost nothing.
`paw find <word>...` lists the artifacts whose identifier, title or conclusion
carry the words, headings only and at most twenty. `paw new <kind> [--topic
<topic>]` prints the next identifier to allocate, never one any file already
carries. `paw index <kind> --write` regenerates a kind's index between its
`<!-- meow-flow index -->` markers, and `check index` reports one that has
fallen behind the tree. Since 0.32.0 an index carrying the markers from before
the unit's rename isn't read, and `--write` names the markers it needs.
`paw template <kind>` prints the template a step writes from: yours at
`.meowpaw/templates/<kind>.md` where you have one, and the unit's otherwise.

## Have a record reviewed

`meow-flow:record-reviewer` is an agent that reviews one record against fixed
questions for its kind, such as whether each alternative in a decision says why
it lost, and whether each rule in any record states its reason. It reads the
record and what the record cites, with `Read`, `Grep` and `Glob` alone, and
edits nothing. It asks nothing `paw check` already settles. Its report opens
with this line, because it is a model's judgement, which covers more than a
person's and can't say whether the work should exist:

```text
Agent review, not a person's approval; the reviewer may share the author's model family.
```

Ask Claude to use it on a path:

```text
Use the meow-flow:record-reviewer agent on project/adrs/ADR-0100-cache-in-redis.md
```

## Postpone requirements

A decision can postpone requirements you choose not to realise now. Give it
`postpones: [REQ-...]` beside or in place of `addresses:`, and say under What
would reverse it when they should be taken up. The requirements then read as
postponed in `show` and `status`, and stop reading as postponed once a task
closes them. A decision that only postpones needs no epic. Each time an epic
is verified, the verify step lists every postponement with its condition and
asks whether the condition now holds.

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
project/tasks/TSK-0001-a-task.md:4: status done is not one a task stores: draft, approved, withdrawn, rejected, superseded
front-matter: 1 finding
identifiers: 0 findings
relations: 0 findings
index: 0 findings
coverage: 0 findings
shape: 0 findings
rules: 0 findings
```

| Check          | Reports                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `front-matter` | A field the kind requires that's missing, a field the kind forbids, a status the kind doesn't store, a bad `revised`; a retired field or status, which `lib/layout.toml` lists with what replaced it                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `identifiers`  | A file whose name and `id` disagree, an identifier used twice, a cited requirement not found                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `relations`    | An identifier in a relation field with no file, one in a draft's prose outside code, and a link in the record to a missing file; a suspect citation in a draft or living artifact, one whose target was revised after it, or an epic or defect it cites that is withdrawn or superseded                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `index`        | A file its kind's index doesn't list, and an index entry with no file; a specification listed before one it cites                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `coverage`     | A requirement a decision addresses that lands in no task or in two, or no specification; a task whose Evidence section says it's done while its epic leaves it unmarked; a task closing a withdrawn requirement in an epic not yet verified; an approved or living artifact resting on a draft anywhere up its chain, and a draft or living one resting on a withdrawn, superseded or rejected provider, each with the chain named. It also states how many requirements in force land in a task, and calls an empty record's coverage zero. Where an onboarding report exists, a document the repository has that the report doesn't place exactly once, with one of four outcomes and a destination or reason |
| `shape`        | An artifact missing a section its kind carries, such as research without its conclusions; a withdrawn requirement cited in a living document outside a Withdrawn section; a record kept in an archive directory                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `rules`        | An undated source or a cited requirement in draft research, a requirement whose `verification` isn't `static`, `behavioural`, `evaluation` or `judgement`, a judged draft requirement with no verifier, a draft requirement carrying two keywords, leaning on a neighbour or written as "No X MUST Y", an epic realising other than one record, a decision's alternatives with no reason they lost; an epic task marked done with no evidence, or added or dropped with no reason; an onboarding report whose Adoption section has no numbered steps; an insight whose title carries a date or runs under four words, whose evidence holds no number or block, or that doesn't end with The pattern             |

`paw check frozen --base <rev>` reports each record approved at
`<rev>` and changed since, outside what its kind may change, unless the change
adds a line naming its authority, such as `**Amended by ADR-0120.**`: a change
to an approved record invalidates its approval. It runs only by name, because
it needs git and a base.

It exits 0 when no check found anything, 1 when any did or the root doesn't
exist, 2 for a check it doesn't know, and 3 when the record wasn't checked.

## What it costs you

The `method` skill's description and the `record-reviewer` agent's, 487
characters together, on every turn, so Claude knows when to load either. The driver costs nothing until you type it. The
program is a native binary shipped inside the unit, so it needs nothing
installed on the machine. On a machine the unit carries no binary for, it
reports the record as not checked and exits 3.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared
in `plugins/meow-flow/requires.toml`. It relies on these platform behaviours,
each documented by Claude Code:

- a skill loaded by its description, and one only a person invokes, with `disable-model-invocation`: [documentation](https://code.claude.com/docs/en/skills.md)
- a `SessionStart` command hook whose output reaches the model before its first reply: [documentation](https://code.claude.com/docs/en/hooks.md)
- a plugin's `bin/` programs, run by path: [documentation](https://code.claude.com/docs/en/plugins-reference.md)

## Where it reads the record

The layout it reads each kind by is `plugins/meow-flow/lib/layout.toml`.
