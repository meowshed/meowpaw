---
id: vision
artifact: vision
status: live
revised: 2026-09-20
---

# meowpaw

## What it is

`meowpaw` is a harness for Claude Code: the instructions, skills, commands and
hooks that turn a general coding agent into one that works a particular way. It
packages one way of working - evidence-driven, traceable, human-gated - so you
can install it in one command, where today you copy it by hand and watch it
drift.

It exists because six repositories here already run six copies of roughly the
same harness, and the copies have diverged. `meowctl` and `meowg1k` share a
specification loop; `vlie` arrived at nearly the same sequence on its own;
`meowhub` built it a third time under different names; `hephaestus` has
edit-time quality hooks nobody else has; `meowary` has durable memory nobody
else has. Fix one of them and you've fixed one of them.

They diverged because there was nothing to diverge _from_. Each documents its
process in its own `CLAUDE.md`, and you can't install, version or upgrade a
document.

## The problem

Agents are now good enough that the bottleneck moved. The model can write the
code; what nobody can tell is **whether what came back is true.**

Seven specific versions of that, each one observed here or in the survey:

- A harness reports that the tests passed, having guessed a command that exited
  zero. None of the ten public harnesses surveyed treats "I could not determine
  how to test this" as an outcome separate from success.
- "The tests pass" is said twenty edits after they last ran, and nothing in the
  sentence tells you which of the two you're reading.
- A test is green and hollow. Model-generated tests score around 20% on
  mutation testing, and mutants survive 15-25% more often on AI-generated code
  at the same coverage.
- A specification is quietly reworded to match what was built, and the
  reasoning behind the original is gone.
- A plan says a task is done because somebody ticked it, and nothing records
  what proved it.
- Documentation describes what was proposed, the project shipped something
  else, and a reader cites the documentation anyway.
- The work was honest and the report wasn't: the one unresolved verb sits in
  the middle of a paragraph that opens with a pleasantry and closes with an
  offer to help further, so the reviewer skims it and approves.

All seven are one failure: **an answer that wasn't earned, delivered with the
confidence of one that was.** The whole design exists to make that failure
hard. The seventh is on the list because you can solve the first six and still
lose everything through the sentence a reviewer actually reads.

## Who it is for

| Audience                                    | Wants                                                         | What they do today                                           |
| ------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------ |
| Someone running an agent on a real codebase | Work they can hand to review without reading every line first | Reads every line, or doesn't, and finds out later            |
| A repository with an existing harness       | To stop maintaining a private copy of a method                | Copies a `CLAUDE.md` between projects and watches them drift |
| A team adopting agentic work                | A record of what was decided and why, that outlives the tool  | Decisions in chat logs and pull request threads              |
| Someone with no interest in any of this     | Formatting, linting and commit conventions, and nothing else  | A pre-commit hook and a style document nobody reads          |

The last row carries as much weight as the first, because a method you can't
adopt in part is a method nobody adopts.

## How it works

Nine steps run in a chain, each writing one artifact, and each refusing to run
when its input is missing or unapproved:

```text
research -> requirements -> design -> spec -> epic
         -> implement -> document -> verify -> review
```

`/meow:run` drives all nine and stops at every gate. It changes how many times
you type a command, and it never changes how many times you decide.

Three documents live and everything else is a record. The vision, the
constitution and the specifications describe the present, and you rewrite them
freely. Research, requirements, decisions, epics, tasks and defects are
records: open while a record is a draft, frozen when someone approves it, and
from then on a later truth arrives as a new record. That's event sourcing
applied to documents - an append-only journal and a projection over it - so
rewriting the projection loses nothing, because the journal is still there.

Two records authorise work, and the harness keeps no taxonomy of work types.
Either somebody decided something, or something is broken. Every task traces to
a decision or to a defect, and every kind of work in both taxonomies surveyed
routes through one of the two. The harness derives what sort of work it is,
because a list of work types somebody maintains is a boundary argument that
never ends.

Five verbs carry everything mechanical: `fmt`, `lint`, `typecheck`, `test`,
`build`. A verb resolves from the repository's own declaration, then from an
installed language pack, and then it stops. The harness reports an unresolved
verb as unresolved and never as passed, which no other harness surveyed does.

Evidence expires. A claim cites the command, its output and the tree revision
it ran at, and every edit advances the revision, so evidence gathered before a
change can't satisfy a claim made after it.

Reports put the failure where you'll see it. The command and the path lead, the
harness computes the state from the artifacts instead of recalling it, a
failure arrives as cause, location and fix with no drama in front of it, and a
stop names the command that resumes it. We measured this shape against an
unshaped baseline: it improved correctness as well as brevity, and it gained
most on progress reports and error reports, which is nearly everything this
method produces.

**This one rule is unconditional.** The chain, the record, the packs and the
tools are all opt-in; the reply shape ships in the kernel, applies to every
reply of every plugin, and a repository can't turn it off. It's the last stage
of every honest-failure rule in the harness, and a rule that only some replies
follow shapes nothing, because the one report that hides the unresolved verb is
the one that gets approved.

## What it will not do

- **Depend on a program.** No service, no daemon, nothing you install before
  the chain can run. The artifacts are Markdown and the steps are prose. Tools
  are welcome and there'll be several - a command-line tool over the record,
  helpers shipped inside the plugins - and each of them can make work cheaper
  while none of them can make it possible. Where a tool is missing, the harness
  says so and does the work the expensive way.
- **Demand the full method for a typo.** The harness classifies work first, and
  trivial work skips the chain. A harness that costs nine steps for a one-line
  fix is one you work around, and then it reports a process it never performed.
- **Oblige a repository to keep the record.** Three levels of adoption, each
  complete on its own.
- **Know what you're building.** Nothing that carries the method names a
  language, a framework or a build tool, and `grep` checks that instead of
  taste.
- **Invent the intent behind code it's given.** Onboarding an existing
  repository recovers the specification, the constitution and most of the
  vision, because those describe what is and the code is right there. It
  recovers no requirements and no decisions, because code says what it does and
  never what it must do or which alternatives lost. Whatever it couldn't
  determine arrives as a gap list, which is a deliverable and not an omission.
- **Delete anything it hasn't placed.** Every existing document gets one of
  four outcomes - migrated, cited as a source, superseded, or discarded with
  the reason recorded - and a document with no outcome is one nobody read.
  Moving material to a directory nobody opens again is deletion with extra
  steps, and it's worse than deletion, because the tree goes on claiming the
  material is maintained.
- **Ship personas.** A role that changes neither the tool set, the context nor
  the stopping point changes only the prose.
- **Put a dashboard in the harness.** That would make the harness a program
  with a server in it, which is what `claude-code-spec-workflow` ships,
  WebSocket and tunnel included. The artifacts are readable, a status command
  prints them, and a separate tool beside the harness can render them as
  elaborately as it likes, because none of that lands in a context window.

## Where it is going

The harness ships as a marketplace of small plugins, and you install what you
want. A project can declare artifact kinds of its own - a game's narrative
documents, a regulator's evidence files - with a prefix, a lifetime and a
template, and a declared kind inherits every obligation a built-in kind
carries, so declaring one buys no exemptions.

Beside it, `meow-book` - a separate Rust tool - makes the same record cheap to
query and projects tasks onto GitHub or Linear, for people who want that.
Nothing requires it: where it's missing, the harness syncs by hand and says so,
and the method works either way.

One specific test decides whether this succeeded: **the six repositories it
came from drop their private copies and lose nothing.** Not that it's elegant,
not that it's complete. Six real projects, in five languages, with five
different ideas of what counts, each install a subset and keep working the way
they already work, with the method written down where everyone can see it.

We mean to run that test rather than assert it, and the smaller ones too: put a
change to how the harness reports, or to what a skill says, to a case set with
a rubric and a blind judge, and publish the delta. A harness that asks for
evidence everywhere else holds its own claims to the same standard.

This document gets rewritten when a decision contradicts it. A decision that
conflicts with what's written here means one of the two is stale, and the
design step asks which - a cheap question, because this document is short.

## What it will not trade away

An unearned answer is the enemy, and every convenience is measured against it.
Guessing a command looks helpful. Substituting a text search for a language
server looks helpful. Filling a template section instead of leaving it empty
looks helpful. Each one produces a confident wrong result, so the harness
reports what it didn't do.

Completeness outranks brevity. Brevity is the default and a real obligation,
but it's presentation. The harness drops no verb from a verification report, no
finding from a review, no question from a gap list, and no hedge that carries
real uncertainty, because deleting the last of those manufactures confidence.
Where a rule of shape would delete part of an answer, the answer wins and the
shape yields.

The record outlives the tool. Plain Markdown in the repository, readable with
`cat` by someone who never installed any of this. No private directory, no
tracker, no database.

Approval is a stop. Where a step ends in human approval, it produces its
artifact, reports, and ends the turn. Everything else here can be made faster;
this can't, because the stopping is the value.
