---
id: vision
artifact: vision
status: live
revised: 2026-10-24
---

# meowpaw

## What it is

`meowpaw` is a harness for Claude Code: the instructions, skills, commands and
hooks that turn a general coding agent into one that works a particular way. It
packages one way of working - evidence-driven, traceable, human-gated - so you
install it in one command, where today you copy it by hand and watch it drift.

It exists because six repositories here already run six copies of roughly the
same harness, and the copies have diverged. Two of them share a specification
loop, a third arrived at nearly the same sequence on its own, and a fourth built
it again under different names. Two carry something nobody else has: edit-time
quality hooks in one, durable memory in the other. Fix one copy and you've fixed
one copy. They diverged because each documents its process in its own
`CLAUDE.md`, and you can't install, version or upgrade a document.

## The problem

Agents are now good enough that the bottleneck moved. The model writes the
code, and nobody can tell **whether what came back is true.**

- A harness reports that the tests passed, having guessed a command that exited
  zero.
- "The tests pass" is said twenty edits after they last ran, and nothing in the
  sentence tells you which of the two you're reading.
- A test is green and hollow: it passes whatever the code does.
- A specification is quietly reworded to match what was built, and the
  reasoning behind the original is gone.
- A plan says a step is done because somebody ticked it, and nothing records
  what proved it.
- Documentation describes what was proposed, the project shipped something
  else, and a reader cites the documentation anyway.
- The work was honest and the report wasn't. The one unresolved stage sits in
  the middle of a paragraph opening with a pleasantry and closing with an offer
  to help further, so the reviewer skims it and approves.

All seven are one failure: **an answer that wasn't earned, delivered with the
confidence of one that was.**

## Who it is for

| Audience                                    | Wants                                                         | What they do today instead                                   |
| ------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------ |
| Someone running an agent on a real codebase | Work they can hand to review without reading every line first | Reads every line, or doesn't, and finds out later            |
| A repository with an existing harness       | To stop maintaining a private copy of a method                | Copies a `CLAUDE.md` between projects and watches them drift |
| A team adopting agentic work                | A record of what was decided and why, that outlives the tool  | Decisions in chat logs and pull request threads              |
| Someone with no interest in any of this     | Formatting, linting and commit conventions, and nothing else  | A pre-commit hook and a style document nobody reads          |

The last row carries as much weight as the first, because a method you can't
adopt in part is a method nobody adopts.

## How it works

Six steps run in a chain, each writing one artifact, and each refusing to run
when its input is missing or unapproved:

```text
research -> requirements -> design -> spec -> implement -> review
```

Either somebody decided something, or something is broken, and all work traces
to a decision or to a defect. The harness derives what sort of work it is,
because a list of work types somebody maintains is a boundary argument that
never ends.

## Quality goals

In priority order. Where two goals pull against each other, the higher one
wins, and the tie-breaks below say how.

1. **Earned answers.** The harness reports what it didn't do. Guessing a
   command, substituting a text search for a language server and filling a
   template section instead of leaving it empty each look helpful and each
   produce a confident wrong result. An unresolved stage is reported as
   unresolved and never as passed, and evidence expires: a claim cites the
   command, its output and the tree revision it ran at.
2. **A record that outlives the tool.** Plain Markdown in the repository,
   readable with `cat` by someone who never installed any of this. No private
   directory, no tracker, no database. Three documents are living and describe
   the present. Everything else is a record, frozen on approval, and a later
   truth arrives as a new record.
3. **Approval is a stop.** Where a step ends in human approval, it produces its
   artifact, reports, and ends the turn. Everything else can be made faster and
   this can't, because the stopping is the value.
4. **Adoptable in part.** The chain, the record, the packs and the tools are
   opt-in, and each level of adoption is complete on its own.
5. **Completeness over brevity.** Brevity is the default and a real
   obligation, but it's presentation. The harness drops no stage from a
   verification report, no finding from a review and no hedge that carries real
   uncertainty.
6. **Speed.** Five stages carry everything mechanical, and `/meow-flow:run`
   changes how many times you type a command and never how many times you
   decide.

Tie-breaks: earned answers beat adoptability, so a unit that can't be adopted
without reporting a guess as a result isn't shipped. Adoptability beats the
record's reach, so a repository that keeps no record still gets the stages.
Where the method costs more than the change is worth, trivial work skips the
chain, because a method costing six steps for a one-line fix is one people
route around, and then it reports a process it never performed.

## What it will not do

- **Make you install or run anything yourself.** You install a plugin, and
  everything it needs arrives with it. A unit may carry a program, a server or
  a daemon of its own, because that costs you nothing past the install you
  chose. You never set up a second thing by hand, keep it running, or let it
  write its configuration into the repository you are working on. Where the
  harness can use a tool you already have, it uses it, and where that tool is
  missing it says so and does the work the expensive way.
- **Demand the full method for a typo.** The harness classifies work first, and
  trivial work skips the chain.
- **Oblige a repository to keep the record.** Three levels of adoption, each
  complete on its own.
- **Know what you're building.** Nothing that carries the method names a
  language, a framework or a build tool, and review checks that, because no
  program does yet.
- **Invent the intent behind code it's given.** Onboarding an existing
  repository recovers the specification, the constitution and most of the
  vision, because those describe what is and the code is right there. It
  recovers no requirements and no decisions, because code says what it does and
  never what it must do or which alternatives lost. Whatever it couldn't
  determine arrives as a gap list, which is a deliverable and not an omission.
- **Delete anything it hasn't placed.** Every existing document gets one of
  four outcomes - migrated, cited as a source, superseded, or discarded with
  the reason recorded - and a document with no outcome is one nobody read.
- **Ship personas.** A role that changes neither the tool set, the context nor
  the stopping point changes only the prose.
- **Put a dashboard in front of the record.** The artifacts are readable and a
  status command prints them. A separate tool beside the harness can render
  them as elaborately as it likes.

## Risks

- **The reply shape is opt-in today.** It is meant to apply to every reply of
  every plugin, and the platform doesn't yet hold it that way, which BUG-1040
  records. A report that hides the unresolved stage is the one that gets
  approved.
- **No prompt is measured.** ADR-2980 removed the harness's own runs and case
  sets, so review is all that holds a change to what a prompt says until a
  redesigned evaluation exists.
- **The test of success hasn't run.** The six repositories this came from are
  meant to drop their private copies and lose nothing, and no repository has
  yet been moved with its gate run before and after (ADR-2690).
- **An unattended run decides its own gates.** A run `meow-loop` holds approves,
  merges and releases without a person (ADR-2380), so the principles it decides
  against are the only gate left.
- **The catalogue of units isn't decided.** A claim about how many units exist
  goes stale, so none is made here.

## Where it is going

The harness ships as a marketplace of small plugins, and you install what you
want. A project can declare artifact kinds of its own - a game's narrative
documents, a regulator's evidence files - with a prefix, a lifetime and a
template, and a declared kind inherits every obligation a built-in kind
carries, so declaring one buys no exemptions.

The record stays plain files, and `paw`, the one native tool every unit
shares, makes it cheap to query and write (ADR-2880). `meow-github` projects a
decision or a defect onto its GitHub issue for people who want that (ADR-3090),
and where it's missing the method works the same.

One test decides whether this succeeded: **the six repositories it came from
drop their private copies and lose nothing.** Not that it's elegant, not that
it's complete. Six real projects, in five languages, each install a subset and
keep working the way they already work, with the method written down where
everyone can see it.
