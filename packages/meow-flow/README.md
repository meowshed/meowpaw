---
reader: someone installing or running meow-flow on Pi
answers: what meow-flow provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-flow@0.53.1]
---

# @meowshed/meow-flow

Runs the method's six steps from research to review, each refused by a native program until its input is approved, routes each request before work starts, drives the steps to the next approval gate with /meow-flow:run, and checks the record they write where .meowpaw/profile.toml declares it. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-flow
```

The paw executable ships with `@meowshed/meow-core` alone (REQ-4612): this
package's launchers run their subcommands through it, so install the core
package beside this one for the binary-backed checks. Without it, every
check reports unrun and lets the command through.

```bash
pi install npm:@meowshed/meow-core   # carries the binary the launchers run
```

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script.

## Upgrade a record from epics and tasks

Where your record holds `epics/` or `tasks/`, every `paw` command but `upgrade`
stops with one finding naming the upgrade, because a second working form would
never retire. Type `/meow-flow:upgrade`, which runs the two commands below and
stops between them for you to read what each will do.

```bash
paw upgrade                # previews each move and writes nothing
paw upgrade --write        # makes the moves
```

The upgrade moves `epics/` and `tasks/` to `archive/epics/` and
`archive/tasks/`, each file otherwise unchanged, and `paw` goes on reading them,
so a citation still resolves. It stores `done` on each decision and defect whose
tasks finished, because nothing can compute that once the marks are archived. It
adds each open task as a step of the `## Plan` of the live decision or defect
that authorises it, and writes `folded-into:` on the task. It archives an open
task with no live authority and reports it as needing a decision. It removes
`epic` from `[unattended] gates`. It leaves a template you override under
`.meowpaw/templates/` for a retired kind alone and reports it. Run it again on a
finished record and it says there is nothing to upgrade.

Review the result as one pull request with `paw count` before and after in its
body. Once it merges, run `meow-github upgrade` to retire the archived tasks'
issues, as `meow-github`'s page says.

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

## Have a change reviewed

The review step reads the record's pull request. Where the session wrote the
change, it sends the difference to an agent with read-only tools and fixes what
the agent finds in that pull request. It reports each test that would still pass against a wrong
implementation. Where the agent reports `BLOCKED`, because a tool it needed
was denied, the step reports the review as not run, and doesn't resume the
agent, send another under the same permissions or review the change itself. No agent reviews a record: you read it when you approve its
pull request.

The implement step hands work to another agent only to keep its own context
clean or to run independent tracks at once, never because the work is large.
It gives that agent the output of `paw brief <record>`, and declares
`isolation: worktree` where agents implement in parallel. A fresh agent, never
a fork of the session that did the work, reviews delegated work, and a third
fresh agent settles a disagreement between the two, given both positions and
the brief. The pull request names the record and `paw brief <record>`, and names
no agent, model or vendor.

## Write a status change in one command

A status change that touches several files is one command, so none of the
files is left out:

```bash
paw approve <id>...                      # draft to approved, where `paw check` reports nothing about it
paw done <record> --pr <number>          # done and `pr:` on a decision or defect, in the pull request that completes it
paw withdraw <requirement> --by <decision> --replaced-by <id>...
```

`approve` writes nothing and exits 1 where the check has a finding about a
record you named. `done` refuses a record that isn't approved, a decision that
addresses work with no plan, and a defect whose Closed by names no check.
`withdraw` writes the
tombstone, the status and today's date. Each command changes only the lines it
owns and regenerates the index of each kind it touched, and a result passes
`paw check` without the command, so you can still edit a record in your editor.

## Postpone requirements

A decision can postpone requirements you choose not to realise now. Give it
`postpones: [REQ-...]` beside or in place of `addresses:`, and say under What
would reverse it when they should be taken up. The requirements then read as
postponed in `show` and `status`, and stop reading as postponed once a later
decision closes them. A decision that only postpones needs no plan. `paw status` lists
every postponement under Postponed with its condition, the first entry under
the decision's What would reverse it, so you see them on each run.

## Tools

The `researcher` agent holds four tools, each for one step of its procedure:

- `Read`: step 1 reads the primary sources the brief names.
- `Grep`: step 1 finds where a source lives where the brief names no path.
- `Glob`: step 1 lists the paths that match a name the brief gives.
- `WebFetch`: step 1 reads a source the brief names by its address.

## Hooks

`status --waiting` stops nothing: at the start of a session it reports what waits at a gate, so the model sees a pending approval before it replies.

## Where it reads the record

The layout it reads each kind by is `packages/meow-flow/lib/layout.toml`.

## Commands

Each command sends its skill's instructions into the session, so the step
runs: the six step commands load the method skill, `/meow-flow:run` the
driver skill, and `/meow-flow:init`, `/meow-flow:onboard` and
`/meow-flow:upgrade` their own. Type
the command and its arguments, and the model carries out what the skill
says.

The researcher's nested call picks the model the `MEOW_NESTED_MODEL`
environment variable names before any other, so you choose what the draft
costs: it runs on glm 5.3 flash where the variable names nothing.
