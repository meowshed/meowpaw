---
id: RES-0062
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:status`

## Summary

Two harnesses have a status command and one ships a dashboard. The file wins
for the three reasons that put artifacts in the repository: readable without
the harness, diffable, and outliving the tool. So the command prints from the
files, which makes it a view and no source. It leads with the pending gate,
because that is the only item requiring a person, and it reports disagreement
between the plan and the tracker, reconciling nothing.

The read-only command that reports where the work stands. Its sibling
[RES-0160-doctor-command.md](RES-0160-doctor-command.md) answers a different
question - whether the repository can be worked on at all.

## Who has an equivalent

| Harness        | Command        | Reports                                                                          |
| -------------- | -------------- | -------------------------------------------------------------------------------- |
| spec-workflow  | `/spec-status` | Progress per spec, plus a WebSocket dashboard with git integration and analytics |
| meowhub        | `/spec-status` | An overview of all specs and their status                                        |
| harness4claude | -              | State lives in `state.json` and `signals.json`; no command reads them out        |
| everyone else  | -              |                                                                                  |

Nobody has an equivalent of the sibling command either.

## Method

We fetched and read the surveyed harnesses' own command templates on
2026-09-20, because the mechanisms live in the templates and the readmes only
describe them, alongside the internal repositories' commands read from their
working trees.

The platform's documentation on commands was fetched for the frontmatter
fields the surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against what comparable
commands do.

## Why a file beats a dashboard

spec-workflow ships a dashboard with a tunnel and optional passwords.
`meowhub` writes the same information into `project/README.md` as a table and has
a command that prints it.

The file wins for three reasons, and they are the same three that put artifacts
in the repository: it is readable without the harness, it is
diffable, and it survives the tool. A dashboard duplicates what the artifacts
already say, adds a service to run, and is the first thing to rot.

So `status` **reads and prints**; it is not a source of anything. Where the
information lives in a file - the plan's marks, the artifact front matter - the
file is the source and `status` is a view.

## What `status` prints

- The route and the class, if a unit of work is in progress.
- The current step, and the step that comes next.
- **Any pending gate, first** - the artifact, the step, and how long it has been
  waiting.
- Open questions and what each blocks.
- The evidence ledger: what has been proved, at which revision, and what is now
  stale.
- Where the plan and the tracker disagree.

The ordering is the design: a pending gate goes first because it is the only
item that requires a human, and burying it under a progress report is how a
gate gets missed.

## Conclusions

1. It prints from the files and is a view, never a source. Where the
   information lives in a file, the file is what the command reads. 2. It leads
   with the pending gate, because that is the only item requiring a person and
   burying it under a progress report is how a gate is missed. 3. It reports
   disagreement between the plan and the tracker and reconciles nothing, since
   reconciling silently destroys the evidence that they diverged. 4. It reports
   evidence as proved at a revision, and stale where the tree has moved, so a
   green result from three commits ago is not read as current. 5. It writes
   nothing.

## Sources

All read 2026-09-20.

- [Pimzino/claude-code-spec-workflow](https://github.com/Pimzino/claude-code-spec-workflow)
  - `/spec-status`, the WebSocket dashboard, tunnel sharing and analytics. -
    [Lharden/harness4claude](https://github.com/Lharden/harness4claude) -
    `state.json` and `signals.json` with no command that reads them out. -
    `~/workspace/meowhub/project/README.md` - the status table as a file that any
    reader opens, where a command would run.
