# meow-method

`meow-method` runs the method: nine steps from research to review, each
writing one artifact from an approved input. It keeps the record those steps
write, the research, requirements, decisions, specifications, epics, tasks and
defects, and checks it, reporting each finding with its file and line. It
installs on its own, with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-method@meowpaw
```

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

Type `/meow-method:run` to be taken to the next approval gate. It reads where
the record stands, runs the next step, and stops where that step waits for
your approval, saying what the next run will do. Run it again after you
approve, and it carries on; run it with nothing approved, and it says what it
is waiting on.

To run one step yourself, ask for it by name, such as "run the design step for
REQ-0190", and Claude loads the `method` skill. The steps, in order:

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

A step refuses when its input is missing or not approved, because the program
checks that before the step writes anything:

```text
$ meow-method ready implement TSK-1430
meow-method ready implement: not ready
  TSK-1420, which TSK-1430 depends on, isn't done
```

`meow-method status` prints where the record stands, leading with whatever
waits for your approval. When a session starts, a hook runs `meow-method
status --waiting`, so Claude opens with any draft waiting for you and says
nothing when none is. `meow-method show <id>` prints what an identifier
names and every artifact that cites it, grouped by the field that cites it.
`meow-method find <word>...` lists the artifacts whose identifier, title or
conclusion carry the words, headings only and at most twenty.
`meow-method new <kind> [--topic <topic>]` prints the next identifier to
allocate, never one any file already carries. `meow-method index <kind> --write` regenerates a kind's index between its
`<!-- meow-method index -->` markers, and `check index` reports one that has
fallen behind the tree. `meow-method template <kind>` prints the template a
step writes from: yours at `.meowpaw/templates/<kind>.md` where you have one,
and the unit's otherwise.

## Check the record

From the repository, run every check, or one by name:

```bash
meow-method check
meow-method check relations
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

| Check          | Reports                                                                                                                                                                                                                                                                             |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `front-matter` | A field the kind requires that's missing, a status the kind doesn't store, a bad `revised`                                                                                                                                                                                          |
| `identifiers`  | A file whose name and `id` disagree, an identifier used twice, a cited requirement not found                                                                                                                                                                                        |
| `relations`    | An identifier in a relation field with no file, and a link in the record to a missing file                                                                                                                                                                                          |
| `index`        | A file its kind's index doesn't list, and an index entry with no file                                                                                                                                                                                                               |
| `coverage`     | A requirement a decision addresses that lands in no task or in two, or no specification                                                                                                                                                                                             |
| `shape`        | An artifact missing a section its kind carries, such as research without its conclusions                                                                                                                                                                                            |
| `rules`        | An undated source or a cited requirement in draft research, a judged draft requirement with no verifier, an epic realising other than one record, a decision's alternatives with no reason they lost; an epic task marked done with no evidence, or added or dropped with no reason |

`meow-method check frozen --base <rev>` reports each record approved at
`<rev>` and changed since, outside what its kind may change, unless the change
adds a line naming its authority, such as `**Amended by ADR-0120.**`: a change
to an approved record invalidates its approval. It runs only by name, because
it needs git and a base.

It exits 0 when no check found anything, 1 when any did or the root doesn't
exist, 2 for a check it doesn't know, and 3 when the record wasn't checked.

## What it costs you

The `method` skill's description, 385 characters, on every turn, so Claude
knows when to load it. The driver costs nothing until you type it. The
program is a native binary shipped inside the unit, so it needs nothing
installed on the machine. On a machine the unit carries no binary for, it
reports the record as not checked and exits 3.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared
in `plugins/meow-method/requires.toml`. It relies on these platform behaviours,
each documented by Claude Code:

- a skill loaded by its description, and one only a person invokes, with `disable-model-invocation`: [documentation](https://code.claude.com/docs/en/skills.md)
- a `SessionStart` command hook whose output reaches the model before its first reply: [documentation](https://code.claude.com/docs/en/hooks.md)
- a plugin's `bin/` programs, run by path: [documentation](https://code.claude.com/docs/en/plugins-reference.md)

## Where the rules come from

The decisions are
`project/adrs/ADR-1100-the-record-is-checked-by-a-unit-the-harness-ships.md`
and `project/adrs/ADR-1130-the-chain-runs-as-steps-a-program-can-gate.md`, and
the unit is specified in `project/specs/SPC-1070-checking-the-record.md` and
`project/specs/SPC-1090-the-chain.md`.
The layout it reads each kind by is `plugins/meow-method/lib/layout.toml`.
