---
id: RES-0037
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Onboarding an existing repository

## Summary

A repository with its own documentation, harness and code yields a recovered
specification, and no requirements and no decisions. Code shows what is, and
never what must be. So every recovered statement is traceable to a file and
anything untraceable is deleted and never softened, confidence is marked, and
the gaps are a deliverable that omits nothing. The diagnostic runs first,
because how a project is built and checked is the first thing that blocks
everything else.

Research for a process that takes a repository with its own documentation, its
own harness and its own code, and produces the method's artifacts from them -
then removes what is no longer needed without losing anything that mattered.

It covers what can be recovered from an existing repository and what cannot,
how confidence is expressed, and the deletion problem. It does not cover
`/meow:init`, which writes a profile into a repository and stops
([RES-0058-init.md](RES-0058-init.md)).

## Method

The published work on reverse documentation engineering was fetched and read
on 2026-09-20 for what can and cannot be recovered from an existing system.

The internal repositories were read as the worked examples, since each of them
is a repository that would have to be onboarded.

Nothing was onboarded. No recovery was attempted here, so the claim that
requirements cannot be recovered rests on the argument and on the sources, and
on no failed attempt.

## The asymmetry that decides the whole design

The specification describes the present. Requirements and decisions are
history.

That single distinction settles what onboarding can and cannot do:

| Artifact      | Recoverable from code? | Why                                                                                       |
| ------------- | ---------------------- | ----------------------------------------------------------------------------------------- |
| Specification | **Yes**                | It states what the system does now, and the system is right there                         |
| Vision        | Partly                 | From the README, the product docs, and what the code is clearly for                       |
| Constitution  | **Yes**                | From the existing harness, the linter configuration, the commit history's conventions     |
| Requirements  | **No**                 | Code says what it does, never what it must do                                             |
| Decisions     | **No**                 | An implementation shows the choice that was made, never the alternatives or why they lost |
| Defects       | Partly                 | From an issue tracker, if one exists                                                      |

So onboarding writes the three living documents and recovers the records only
where a record already exists somewhere. Everything else is a **gap**, and
never a guess.

## The failure this exists to prevent

The literature on AI-assisted legacy recovery names it precisely:

> AI can confidently invent intent that sounds right but isn't.

Which is this harness's own characteristic failure - an answer that was not
earned, delivered with the confidence of one that was
([RES-0001-synthesis.md](RES-0001-synthesis.md)) - arriving in the place where it is most
expensive. A fabricated requirement is worse than a missing one: it will be
cited, defended, and built against.

The same source keeps business-logic reconstruction human-led **on purpose** for
this reason, even while reporting that the mechanical analysis of a
ten-thousand-line module drops from six weeks to two.

## What a recovery framework produces

`Reversa`, the most developed published framework for this, splits into a
discovery stage and a migration stage. Its discovery artifacts make a good
checklist: inventory, code analysis, architecture, domain model, state
machines, dependencies, **questions**, **gaps**, and confidence reports.

Three of those are the interesting ones, and all three are about what is _not_
known. Its stated goal for the output is the sentence to copy:

> operational specifications that are traceable to code, marked by confidence
> levels, and accompanied by gaps that require human validation.

Three obligations fall out:

1. Traceable. Every statement names the file and, where it matters, the line.
   The codebase-onboarding guidance puts it more bluntly: _delete every claim
   you cannot trace to a file and a line._ 2. Confidence-marked. A statement
   read off a single function is not the same as one confirmed by tests, three
   call sites and a comment. The distinction must survive into the artifact. 3.
   Gaps are output. What could not be determined is a deliverable that omits
   nothing - and it is the list a person works through.

## Reading order

The onboarding literature converges on mapping the perimeter before anything
else: entry points, the build and test commands that actually run,
configuration, external boundaries. Then one real path traced end to end. The
fastest readers find the few files that carry the most meaning and read those
first - entry point, core domain logic, then the most-changed files - rather
than reading alphabetically.

For this harness there is a shortcut nobody else has. **Run `/meow:doctor`
first.** Which verbs resolve, to what, and from where is the fastest possible
answer to "how is this project actually built and checked", and the harness
computes it, where reading answers nothing.

## The old harness is evidence

A repository being onboarded usually has one: a `CLAUDE.md`, an `AGENTS.md`,
some skills, some commands. Treating that as something to replace wastes the
best source in the repository.

It is the **constitution's first draft**, already written by someone who knew
the project: its principles, its conventions, its prohibitions, and - most
valuable - the defects those prohibitions exist to prevent. `meowctl`'s
principles each name the bug that justifies them; nothing recoverable from the
code carries that.

Its permission allow-list is a second gift: the tasks a project trusts an agent
to run are the tasks that matter, which is most of the gate.

So: read it, map it, and keep what it knows. The harness replaces its _shape_,
not its content.

## The deletion problem

Removing what is no longer needed without losing anything important is the hard
half, and it has a clean rule.

Nothing is deleted until it has been placed. Every existing document is
assigned exactly one of four outcomes, and the assignment is the artifact:

| Outcome        | Means                                                                          |
| -------------- | ------------------------------------------------------------------------------ |
| **Migrated**   | Its content is now in a named artifact, whose identifier is recorded           |
| **Source**     | A research artifact cites it, so it stays or its content is quoted with a date |
| **Superseded** | Something newer says it better, and the superseding artifact is named          |
| **Discarded**  | Nothing needed it, and **the reason is recorded**                              |

A document with no outcome is not deleted, because an unassigned document is one
nobody read.

Two things make this safer than it sounds. **Git is the archive** - deletion
removes a file from the working tree and never from history, so the question is
never "is this gone" but "will anyone find it". And that is exactly what the
fourth row answers: a discard with a recorded reason is findable by searching
for the reason, which is how someone actually looks for it later.

The failure to avoid is the opposite of hoarding: a `docs/legacy/` or
`docs/archive/` directory that everything is moved into and nothing is ever read
from again. That is deletion with extra steps, and it is worse because the tree
now claims the material is maintained. Where old design material genuinely must
stay, it is moved to a **named frozen state** that says it is
historical and must not be cited as current - which `vlie` already does with
`docs/dev/initial-design/`.

## Where onboarding stops

At an approval, like every other step that produces something for a person to
read. What it hands over:

- The three living documents, drafted.
- A specification traceable to code, with confidence marks.
- A recovered constitution, from the old harness.
- **The gap list** - what could not be determined, as questions.
- **The disposition of every existing document**, with its outcome.

And it does not write requirements or decisions it could not recover. The empty
requirements document is the honest output, and it fills as the first real unit
of work goes through the chain.

## Conclusions

1. The specification is recovered; requirements and decisions are not. Code
   shows what is, never what must be. 2. Every recovered statement is traceable
   to a file, and anything untraceable is deleted and never softened. 3.
   Confidence is marked, and gaps are a deliverable that omits nothing. 4. The
   existing harness is read as evidence, and its principles carry reasons
   nothing else in the repository has. 5. `doctor` runs first, because how a
   project is built and checked is computable. 6. Nothing is deleted until it
   is placed - migrated, cited, superseded or discarded with a reason. 7. No
   archive directory. A frozen state is named and says it is historical;
   anything else is deletion pretending to be preservation. 8. Onboarding stops
   at approval, handing over gaps and guessing at nothing.

## Sources

All read 2026-09-20.

- [Reversa: a reverse documentation engineering framework for converting legacy
  software into operational specifications for AI
  agents](https://arxiv.org/html/2605.18684v1) - the discovery and migration
  stages, the artifact set including questions, gaps and confidence reports,
  and the stated goal of specifications "traceable to code, marked by
  confidence levels, and accompanied by gaps that require human validation". -
  [AI-native legacy
  recovery](https://firstlinesoftware.com/ai-native-legacy-recovery-re-engineer-mode/)
  - the measured reduction in analysis time, and why business-logic
    reconstruction stays human-led: "AI can confidently invent intent that sounds
    right but isn't". - [Software reverse engineering to requirement engineering
    for evolution of legacy
    systems](https://ieeexplore.ieee.org/document/7293021/) - the discipline's
    own framing of the recovery problem. - [Onboarding an AI coding agent to an
    unfamiliar
    codebase](https://www.matthewswong.com/en/blog/ai-agent-onboarding-unfamiliar-codebase/)
  - map the perimeter first, write findings to a committed instruction file,
    and "delete every claim you cannot trace to a file and a line". - [Onboarding
    to a new codebase with AI tools in
    2026](https://theroadtoenterprise.com/blog/onboarding-to-new-codebase-with-ai-tools)
    and [How to read a codebase you didn't
    write](https://repowise.dev/blog/use-cases/how-to-read-a-codebase-you-didnt-write)
  - the phased reading order, and finding the few files that carry the most
    meaning, where reading alphabetically finds nothing. -
    [buildermethods/agent-os](https://buildermethods.com/agent-os/standards) -
    `/discover-standards` extracting conventions from an existing codebase rather
    than asking for them. - `~/workspace/meowctl/CLAUDE.md` and
    `~/workspace/vlie/docs/dev/initial-design/` - an existing harness whose
    principles each name the defect that justifies them, and a named frozen state
    for superseded design material.
