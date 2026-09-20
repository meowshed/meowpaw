---
id: RES-0025
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# meow-book: a tool over the record

## Summary

A local-first management tool over the same Markdown corpus is possible and is
deliberately not part of the harness. The corpus stays the record and the
tracker is a projection. A program performs the synchronisation and no prompt
does, because it has to be deterministic, idempotent and testable per failure
mode. Conflict authority is per field, and disagreement on a
repository-authoritative field is reported and never resolved.

Research for **meow-book**, a tool outside the harness. It is a local-first
project management system over the same Markdown corpus, with a command-line
interface, a terminal interface, and optional synchronisation to GitHub or
Linear. Written in Rust, released as its own project.

It is researched here because the harness's design has to be right whether or
not it exists, and because the division of labour between them is a genuine
architectural question that packaging settles nothing about.

## Method

We fetched and read the comparable tools on 2026-09-20 for how each stores its
records and what it derives: the terminal interface library, the
Markdown-backed trackers, and the synchronisation tools. We paid attention to
which of them treat files as the source of truth.

Nothing was installed or run. This document describes a tool that does not
exist, so every claim in it is a design claim and no observation. That is the
largest limitation in the corpus, and it is why the tool sits outside the
harness.

## The shape

```text
            the repository                        optional
    ┌──────────────────────────┐        ┌────────────────────────┐
    │ project/tasks/*.md       │        │  GitHub issues         │
    │ project/epics/*.md       │◄──────►│  or Linear issues      │
    │ .meowpaw/profile.toml    │  sync  │                        │
    └──────────────────────────┘        └────────────────────────┘
              ▲         ▲
              │         │
        ┌─────┴───┐ ┌───┴──────────────────┐
        │ harness │ │  meow-book             │
        │ (agent) │ │  CLI  ─── for the agent│
        │         │ │  TUI  ─── for a person │
        └────┬────┘ └───┬──────────────────┘
             └──────────┘
          the agent drives the CLI
```

Two readers of one corpus, and one optional projection outward. The files are
the record;
everything else is a view or a copy.

## Prior art, and the distinction that matters

Two families exist and they are not the same thing.

Views over a tracker. `gh-dash` is the reference implementation: a Go and
Bubble Tea terminal dashboard that calls the `gh` CLI. It has vim keybindings,
custom actions that launch `lazygit` or trigger a workflow, and panes for pull
requests, issues and notifications. `gh-tuissue` adds a Kanban view and reads a
linked GitHub Project's columns. `tea-dash` is the same idea for Gitea and
Forgejo.

These are excellent and they are the _opposite_ architecture: the tracker is the
record and the terminal is a window onto it. Offline, they show nothing.

Files as the record. `Backlog.md` is the closest prior art to what is wanted
here: a Markdown-native task manager that turns any git repository into a
self-contained board. Every task is a `.md` file with YAML front matter under
`backlog/`, and every change is a commit. It ships a terminal Kanban board and
a web interface, and it is built for collaboration between people and agents:
"Claude, please take over task 33".

What `Backlog.md` does not have is the part this project needs: a specification
chain above the tasks, and a projection outward to a tracker other people use.

Requirements as files is the third family and is covered in
[RES-0019-document-tooling.md](RES-0019-document-tooling.md): Doorstop, StrictDoc, Sphinx-Needs
and OpenFastTrace have managed requirements in version control for a decade,
with identifiers, links and derived traceability.

The system described here is the union: `Backlog.md`'s file-native board, the
requirements family's traceability, and a tracker projection that neither has.

## One binary, two faces

The tool is a **CLI first and a TUI second**, and that ordering is the design,
which no implementation detail decides.

The agent never drives a terminal interface. It runs commands and reads
structured output - `--json` on everything, exit codes that distinguish
outcomes, one determination per subcommand. That is the helper contract from
[RES-0023-helpers.md](RES-0023-helpers.md), and it means every capability the tool has is
available to the harness without the harness knowing anything about panes or
keybindings.

The TUI is the same library with a person attached: it renders what the CLI
computes and calls the same code paths for writes. It adds no capability. If it
did, the agent would be locked out of that capability, and the tool would have
two behaviours to keep consistent.

This also settles what the harness's packs contain. `meow-gh` and `meow-linear`
become thin: detect the tool, call it, read its output, and know the conventions
an issue follows. Where the tool is absent they fall back to the underlying CLI
and say the work is being done the expensive way.

## Rust

The tool is Rust, which changes nothing about the design and two things about
the choices.

- **TUI**: `ratatui` with `crossterm`. The Ink and OpenTUI comparison in
  [RES-0019-document-tooling.md](RES-0019-document-tooling.md) applies to helpers shipped inside
  plugins, where the platform installs Node dependencies. It does not apply to a
  standalone binary, and a single static binary with no runtime is a better
  answer for something installed per machine.
- **Distribution**: one binary, installable through the machine's own
  provisioning, with no runtime to manage. That is what makes "optional" cheap
  enough to be true.

The rest of the stack follows: `clap` for the command surface, `serde` with a
YAML front-matter parser for the corpus, a CommonMark parser for the bodies,
`octocrab` for GitHub, a GraphQL client for Linear.

The harness's own plugin helpers stay TypeScript
([RES-0023-helpers.md](RES-0023-helpers.md)) for the reason stated there - it
is the only language the plugin platform installs dependencies for. Two
languages for two deployment models is a decision somebody took, and no
inconsistency.

## The finding: the sync belongs to the tool

This conclusion is what the research produced.

Synchronising a corpus with a tracker is **entirely mechanical**. Reading the
plan, diffing it against the tracker, creating what is missing, updating what
changed, reading state back, recording the mapping - none of it needs
judgement. It fits the definition of a determination, and no decision is
involved.

Doing it in the agent costs three things:

- **Turns.** Each `gh` call is a tool round-trip, and the JSON it returns lands
  in context whole.
- **Determinism.** The same plan synced twice by a model is not guaranteed to
  produce the same tracker state. Synced twice by a program, it is.
- **Testability.** A sync in prose cannot be tested. A sync in code can have a
  fixture per failure mode, which matters because the failure modes are the
  whole difficulty (below).

Doing it in a tool costs one thing - the tool has to exist - and that cost is
bounded by the helper contract: the method completes without it.

Which means the agent must be able to do it by hand, and this is not a grudging
fallback. Creating an issue, putting the identifier in the branch name, writing
the closing keyword, reading the link back and recording the mapping are all
ordinary commands. Without the tool you lose turns and determinism, and no
capability.

The obligation that makes the fallback safe: **by hand it must produce the same
mapping file and the same links a tool would**. Otherwise installing
`meow-book` later finds a ledger it has to reconcile, where it should find one
it can continue, and the first thing the optimisation does is create work.

So the division is:

|                                                                 | The tool   | The harness |
| --------------------------------------------------------------- | ---------- | ----------- |
| Create issues from an approved epic                             | yes faster | yes by hand |
| Read tracker state back into the corpus                         | yes faster | yes by hand |
| Maintain the identifier mapping                                 | yes faster | yes by hand |
| Detect and report divergence                                    | yes faster | yes by hand |
| Decide **what** an issue should say                             | -          | yes         |
| Decide **when** the plan is ready to project                    | -          | yes         |
| Judge whether divergence means the plan or the tracker is wrong | -          | yes         |

`meow-gh` and `meow-linear` shrink accordingly. Their job becomes: know the
tool exists, know how to read what it produced, and know the conventions an
issue follows. Where the tool is not installed, they fall back to the `gh` or
Linear CLI directly and say that the work is being done the expensive way.

The whole capability is conditional on two things being present - the tool
installed, and the matching plugin enabled. Neither is required for the method,
and a repository with neither loses only the projection.

## The file format

The corpus has to be readable by three things - a person with `cat`, the
harness, and the tool - and none of them may need the others. That constrains
the format more than any feature does.

Front matter is the interface. YAML, because every Markdown ecosystem
already parses it. Fields are additive: a document with unknown keys is valid,
so the harness and the tool can evolve without lockstep releases.

```yaml
---
artifact:
  epic # research | requirement | adr | spec | epic |
  # task | bug | index | vision
status: draft # stored status only; realisation is derived
revised: 2026-09-20 # when a human last changed it
checked-at: r417 # the tree revision it was last verified against
elaborates: RES-0006 # what this was drawn from, upward only
supersedes: [] # identifiers this replaces
---
```

A requirement is a file. The prior art divides on this, and the division
teaches something. Doorstop splits one requirement per file, and StrictDoc and
Sphinx-Needs deliberately do not. The reason those two give is that a
requirement is legible only beside the prose that motivates it
([RES-0019-document-tooling.md](RES-0019-document-tooling.md)).

That reason does not hold here, because in this method the motivating prose is
not beside the requirement at all. The research carries the evidence and the
decision carries the reasoning, so a requirement is a bare obligation with
nothing to be separated from. Once that is true, the file wins on three counts.
Its metadata is front matter, where a line carries a convention. Its history is
its own, where a line shares a large document's. And reading one costs the
tokens of one obligation, where reading a line costs every obligation beside
it. The last is the decisive one for an agent, and it is the opposite of the
consideration that decided it for StrictDoc.

So a requirement is a file named for its identifier, with the obligation as its
whole body:

```markdown
---
id: REQ-NNNN
artifact: requirement
topic: verification
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0006
verification: behavioural
---

# REQ-NNNN

When a verb resolves to no command, the harness MUST report it as unresolved,
MUST NOT report the check as passed, and MUST NOT substitute a guessed command.
```

A task is a line too, and the format extends spec-kit's, which already
carries four facts:

```markdown
- [x] TSK-0014 [P] Resolve a verb from the profile
      closes: REQ-NNNN, REQ-NNNN
      path: plugins/meow-core/bin/resolve.ts
      evidence: tests/gate/resolution.sh, 11 passed, r417
      issue: meowshed/meowpaw#42
```

The mark is the state - `[ ]`, `[x]`, `[>]`, `[~]` dropped, `[+]` added after
approval. `[P]` means parallelisable. The attribute lines are optional and
order-free. `issue:` is the projection, and its absence means unprojected.

The mapping lives on the task, and no registry holds it. A first draft of this
put the task-to-item mapping in a committed `.meowpaw/tracker.toml`, for two
reasons: a sync needs the reverse direction, and it needs a content fingerprint
for idempotency. Both are real, and neither justifies a second file.

The argument against is this document's own, three sections later: no
identifier registry file, because the identifiers are in the documents and a
registry is a second source that drifts. A mapping registry is that registry
wearing a different name. It also fails in a way a per-task attribute cannot. A
task moved between epics, renamed or deleted leaves its row behind, and an
orphan row is indistinguishable from a mapping for a task nobody has written
yet.

So the task carries both facts:

```markdown
- [x] TSK-0014 [P] Resolve a verb from the profile
      closes: REQ-NNNN, REQ-NNNN
      path: plugins/meow-core/bin/resolve.ts
      evidence: tests/gate/resolution.sh, 11 passed, r417
      issue: meowshed/meowpaw#42
      fingerprint: 9f2c
```

`issue:` is the projection and `fingerprint:` is the content hash at the version
last projected. Together they are the idempotency key, and an absent `issue:`
means unprojected.

Sync state is computed, and nothing stores it. The first draft also kept
`synced`, `pending` or `error` per item. That is derived state - the comparison
of `fingerprint:` against the item as the tracker currently reports it - and
storing derived state is what the rest of the method refuses to do. It is also
the field that would churn: written on every sync, into the artifact files
themselves, which is diff noise on the record and one more thing echo
suppression has to get right.

What is lost is honest: the reverse direction, "which task is issue 42",
becomes a scan of the task files, where a registry would answer with a lookup.
That is a helper's problem and not a format decision, and a scan over a
directory of tasks is cheap enough that buying it with a second source of truth
would be a poor trade.

What the format deliberately does not do:

- No identifier registry file. The identifiers are in the documents, and a
  registry is a second source that drifts.
- No generated index checked in beside the real one - the index _is_ generated,
  and a check fails when it disagrees.
- No embedded HTML, no directives, no custom syntax. The corpus renders on a
  forge and in an editor with no plugin, which is the plain-text rule.
- No per-requirement files, for the reason above.

The rule that keeps the format honest: every structured element is either
in front matter or at the start of a line, and everything else is prose. A
parser that needs to understand a sentence is a parser that will disagree with
the next writer.

## The sync design, where the difficulty actually is

Local-first synchronisation is a studied problem, and the 2026 patterns
transfer directly.

An outbox, drained in causal order. A local change appends an intent; a sync
pass drains the outbox to the API in order and applies the response back. This
is what makes a partial failure recoverable, where otherwise half a plan stays
projected.

Idempotency keys. An idempotency key combining the external identifier with a
content fingerprint makes each intended version addressable, so a replayed sync
does nothing and duplicates nothing. The harness has natural keys already - the
task identifier and the unit's number - and a content hash of the task's text
gives the second half.

Per-item sync state. Each task carries `synced`, `pending` or `error`
against the tracker, which is what lets the TUI show what is out of step
without a full comparison.

Echo suppression. A sync that writes back into the corpus must not trigger
another sync. `Specbound/sdd-harness` solved the analogous problem for automatic
documentation commits by giving them a `docs: auto-sync` subject that the hook
refuses to fire on - and that one detail is what stops the loop. The same shape
applies here: writes originating from a sync are marked, and marked writes do
not enqueue.

A conflict policy stated per field, and never globally. Last-write-wins on a
timestamp is the default in the literature and is wrong here, because the two
sides are authoritative about different things:

| Field                                        | Authority          | Why                                                                               |
| -------------------------------------------- | ------------------ | --------------------------------------------------------------------------------- |
| Title, body, requirement links, dependencies | **The repository** | It is the record; an issue edited into disagreement is drift, reported not merged |
| State: open, in progress, closed             | **The tracker**    | That is what a tracker is for, and where people actually change it                |
| Assignee, labels, milestone                  | **The tracker**    | Same                                                                              |
| Existence                                    | **The repository** | An issue with no task is reported; a task with no issue is created                |

That table is the sync engine's whole conflict resolution, and it follows from
the system-of-record decision, which no sync framework supplies. Where the two
disagree about a repository-authoritative field, the tool **reports** rather
than overwrites - the harness decides which side is wrong, because that is a
judgement.

Identity mapping lives on the task. `issue:` and `fingerprint:` are
attributes of the task, in the task's own file. The mapping must be recoverable
from the repository alone, and keeping it on the artifact it describes is how -
without a registry that outlives the tasks it maps.

Pull by default, and never push. Webhooks need a service; the design has no
service. Polling on demand - when the tool opens, when a sync is asked for - is
enough for a backlog that changes a few times a day, and it keeps the
no-service rule intact.

## What the TUI is for

A person's view of the same corpus, keyboard-first.

- **Units of work** with their step, their status, and any pending gate.
- **The plan** as a board or a list: done, ready, blocked, dropped, added.
- **Requirements**: status, coverage, and what cites each.
- **Drift**: artifacts whose recorded state contradicts the tree, and tasks
  whose tracker state disagrees with the plan.
- **Sync**: what would change, then what changed.

`gh-dash`'s interaction model is the one to copy - vim keys, panes, and
configurable actions that launch other tools and reimplement none of them.

Rendered with `ratatui`, and rendering only what the CLI already computes.

### The rule that keeps it safe

The TUI edits files; it does not edit the tracker directly. A change is made
in the corpus and then projected, never the reverse. Otherwise there are two
writers to the tracker with no shared ordering, and the mapping stops being
trustworthy.

The one exception: marking something done. It is the one action people
genuinely want from a board, and the tracker is authoritative for state anyway

- so it is written to the tracker and read back, and no file round-trips it.

## Why it must be a separate tool

Four reasons, and each is a rule the harness already has:

- **No service, no daemon, nothing to install for the method to work**. A dashboard inside the harness makes the harness a program.
- **Optional by construction**. Its absence changes nothing.
- **It has a budget the harness does not.** A TUI can be as elaborate as it
  likes; none of it lands in a context window.
- **Different release cadence and different language.** A Rust binary with its
  own versioning and its own release process. The harness is Markdown and
  shell.

The precedent against: `claude-code-spec-workflow` ships its dashboard inside
the harness, with a WebSocket server, a tunnel and optional passwords - which is
exactly the dependency the design rejects.

## Conclusions

1. The corpus is the record; the tracker is a projection - already decided
   already. 2. A program performs the sync, and no prompt does. Deterministic,
   idempotent, testable per failure mode - and driven by the agent through the
   CLI, with nothing reimplemented in prompts. 2a. **CLI first, TUI second.**
   Every capability is available as a command with structured output; the
   terminal interface adds none of its own. 3. Conflict authority is per field,
   following from the record decision, and disagreement on a
   repository-authoritative field is reported and never merged. 4. The mapping
   lives on the task, so the tracker can be lost without losing knowledge and a
   deleted task takes its mapping with it. Sync state is computed from the
   fingerprint, and nothing stores it. 5. Writes flow corpus -> tracker, with
   state read back; marking done is the single allowed exception. 6. Echo
   suppression is explicit, or the sync loops. 7. Poll on demand; no service. 8. The tool is separate, optional, and required by nothing - the capability
   exists only where both it and the matching plugin are installed.

## Sources

- [ratatui](https://ratatui.rs/), read 2026-09-20 - the Rust terminal interface
  library, and `crossterm` as its backend.
- [MrLesk/Backlog.md](https://github.com/MrLesk/Backlog.md), read 2026-09-20 -
  Markdown files with YAML front matter under `backlog/`, terminal Kanban, web
  UI, git-native, explicitly built for human-and-agent collaboration.
- [Transform project management with Git and AI: backlog.md](https://dev.to/thedavestack/transform-project-management-with-git-and-ai-backlogmd-28d0),
  read 2026-09-20 - its storage model and workflow in practice.
- [dlvhdr/gh-dash](https://github.com/dlvhdr/gh-dash) and
  [gh-dash on Terminal Trove](https://terminaltrove.com/gh-dash/), read
  2026-09-20 - Bubble Tea over the `gh` CLI, vim keybindings, configurable
  actions, and the pane model.
- [gh-tuissue](https://masamichhhi.com/blog/gh-tuissue-en/) and
  [tea-dash](https://github.com/gbarany/tea-dash), read 2026-09-20 - the Kanban
  variant and the Gitea equivalent.
- [Local-first architecture V: bidirectional sync and conflict resolution](https://www.welcomedeveloper.com/posts/local-first-architecture-5-bidirectional-sync/),
  read 2026-09-20 - the outbox pattern, causal-order draining, per-row sync
  state, and the rule that reconciliation never lives in UI or network code.
- [Offline-first architecture: sync, conflicts and security](https://thetechtower.com/offline-first-app-architecture/),
  read 2026-09-20 - idempotency keys as external identifier plus content
  fingerprint, client-generated identifiers, and per-field merge against
  last-write-wins.
- [Linear GitHub integration](https://linear.app/integrations/github), read
  2026-09-20 - branch-name linking, and closing behaviour that depends on
  workspace settings.
- [Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue),
  read 2026-09-20 - the default-branch constraint on closing keywords.
- [Specbound/sdd-harness](https://github.com/Specbound/sdd-harness), read
  2026-09-20 - the `docs: auto-sync` commit subject that prevents a sync hook
  from re-firing.
- [Pimzino/claude-code-spec-workflow](https://github.com/Pimzino/claude-code-spec-workflow),
  read 2026-09-20 - the in-harness dashboard this document argues against.
