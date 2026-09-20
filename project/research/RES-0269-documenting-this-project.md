---
id: RES-0269
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Documenting this project

## Summary

This repository holds two trees of prose, and only one of them is
documentation. The record under `project/` says what must be true and why it
was decided; `docs/` says how to use what ships. Today `docs/` describes a tree
that does not exist, gives record metadata to documents that are no part of the
record, and its seventeen-line index already names a path that moved. The
platform fixes most of the remaining shape: a catalogue entry's description is
the whole of what someone reads before installing, and its homepage field is
the only route to anything longer, so documentation is written per plugin. One
of the five readers is an agent, and that reader has a published convention.

Research for how this project documents itself: which documents it owes, who
reads each of them, and by what rules they are written.
[RES-0020-documentation.md](RES-0020-documentation.md) covers the four kinds,
the two style guides and the rules for writing any documentation at all, and
none of that is repeated here.

It does not cover release notes and the changelog, which are
[RES-0264-versioning-and-release.md](RES-0264-versioning-and-release.md), nor
the files a public repository owes a newcomer, which are
[RES-0066-public-repository.md](RES-0066-public-repository.md), nor the step
that keeps documentation current, which is
[RES-0054-document.md](RES-0054-document.md). The record's own templates are
[RES-0253-the-research-template.md](RES-0253-the-research-template.md) and its
neighbours.

## The question

The deliverable here is mostly prose, and prose about prose is easy to write
twice. Someone arriving at the repository today finds 126 research documents,
1,053 requirements and three draft pages under `docs/`, and nothing tells them
which of those was written for them.

So the question is which documents this project owes, to whom, and by what
rules they are written - while no plugin exists yet for any of them to
describe.

## Method

The three documents under `docs/` were read from the working tree on
2026-09-20, together with the four living documents at the root and under
`project/`, for what each currently claims and who it addresses. Those three
pages are uncommitted drafts, so a later reader will find them in no revision
of this repository, and the quotations here are the only record of them.

The platform's pages on discovering plugins and on creating a marketplace were
fetched and read on 2026-09-20, for the fields a catalogue entry carries and
for what someone sees before they install anything.

The `llms.txt` specification, the Good Docs Project's template catalogue, Write
the Docs' documentation principles and the changelog convention were fetched
and read on 2026-09-20.

Nothing was measured and no reader was asked. We found no published guidance on
documenting a plugin catalogue beyond the platform's own pages, so every
statement here about per-plugin documentation rests on what the platform
displays, and on no convention.

## Findings

### This tree has already merged the record with the documentation

The three documents under `docs/` carry front matter modelled on the record's.
`conventions.md` declares `id: REF-0001`, `artifact: reference`; `plugins.md`
declares `id: CAT-0001`, `artifact: catalogue`, `status: draft`. Two artifact
kinds were invented for two documents, and neither kind appears in the record's
own list of kinds. A draft status on a user-facing page says nothing to the
person reading it, because they have no approval to wait for.

The index above them drifted inside seventeen lines. It tells a reader that the
artifact record lives under `../specs/`, and links `../project/README.md`.
Whichever of the two is right, the other was written and never read again.

`conventions.md` describes a `spec/` directory of files holding "numbered
requirements embedded in" prose. The repository has no `spec/` directory, and
its requirements are one obligation per file. The page describes a design that
was considered and changed, and it reads as instruction.

### The platform shows one paragraph and one link

A marketplace entry may carry `displayName`, `description`, `version`,
`author`, `homepage`, `repository`, `license` and `keywords`, and the platform
states which of them a person sees: _"For an entry with any other source type,
users see only the entry's own fields until they install the plugin."_ Only an
entry whose plugin files sit inside the marketplace itself can fall back to the
plugin's own manifest.

The detail pane adds three things the entry does not carry: an estimate of what
the plugin costs in context on every turn, the date it was last updated, and a
list of the commands, skills, agents, hooks and servers it will install. The
platform then sends the reader away for anything else: _"Check each plugin's
details in the Discover tab to see the commands and skills it provides, or
visit its homepage for usage guidance."_

Two consequences follow. The description is the whole of the documentation
before an install, so it states what the plugin does for the reader. The
homepage field is the only route from the catalogue to a longer page, so every
plugin needs a page of its own and an entry that points at it.

### An agent is one of the readers, and has a published convention

`llms.txt` is a format for a file at `/llms.txt`, whose stated purpose is that
_"Agents are best served by concise, expert-level information gathered in a
single, accessible location."_ It requires an H1 with the project's name, which
is _"the only required section"_, then a blockquote summary, then H2 sections
holding lists of links, each a Markdown hyperlink with an optional note after a colon. A section named
`Optional` holds _"links an agent can skip when a shorter context is needed"_.

What the format supplies is a route and no second copy of the documentation.
Every entry is a link, and the summary exists so a reader knows what the links
lead to. That matches what this repository needs, because the material an agent
would load - skills, commands, the record - is already in the tree and
duplicating it would give the agent two versions to disagree about.

### The minimum set is seven content types, and the four kinds are not a checklist

Diátaxis sorts documents and does not enumerate them. The Good Docs Project
does enumerate, and names its Core pack as _"the core, fundamental content
types that every documentation project needs"_: concept, how-to, README,
reference, release notes, troubleshooting and tutorial. Its two further packs
hold a contributing guide, a code of conduct, a changelog and eleven others,
an installation guide and a glossary among them.

Seven is a checklist a project can be measured against, where four kinds only
sort what somebody already wrote. Six of the seven belong to this project
directly, and release notes are already settled elsewhere.

### Currency outranks completeness, and repetition is the price of it

Write the Docs states the trade directly: _"Consider incorrect documentation to
be worse than missing documentation."_ It also rejects the obvious economy,
under the name ARID: _"If you adhere strictly to this DRY principle when
writing documentation, you won't get far."_ Documentation repeats what the
source says, and the repetition is accepted so a reader finishes on one page.

Two further principles bear on where the pages live. Sources are stored _"as
close as possible to the code which they documents"_, so that one change
touches both. Structure lets readers _"identify and skip over concepts which
they already understand"_, which is why a page opens with what it answers.

For this project the proximity rule is concrete. A plugin's page ships with the
plugin, so that installing the plugin brings its documentation and changing the
plugin changes a file beside it.

### Documenting what does not exist is the failure this project is most exposed to

Nothing here ships yet, and three pages already describe it. The repository's
own prose states the rule it broke, in `conventions.md`: writing component
specifications early would specify components whose design is unapproved, and
"a speculative specification is worse than none because it is cited as
authority while being wrong."

The same sentence holds for documentation, and more sharply. A specification is
read by someone who knows the work is unfinished. A how-to guide is read by
someone trying to do the thing, and it offers no clue that the thing is
imaginary.

### The readers differ in what they arrive holding

Five readers can be distinguished by what each one has in hand when they
arrive. The first four come from the vision's audience table and from the
platform's install flow; the fifth comes from the `llms.txt` specification.

| Reader                          | Arrives with                   | Wants first                            |
| ------------------------------- | ------------------------------ | -------------------------------------- |
| Someone choosing a plugin       | A catalogue entry              | What it does, and what it costs        |
| Someone installing the harness  | A repository that already runs | The smallest install that works        |
| Someone adopting the method     | A way of working of their own  | The chain, one page per step           |
| Someone contributing to it      | A change they want to make     | Where the material lives, and the gate |
| An agent loading the repository | A task and a context budget    | A route, and what it may skip          |

The first two want a page each, short. The third wants the largest body of
documentation in the project, and it is the one nothing in the tree addresses
today. The fourth is served by the files a public repository already owes.

Naming the reader is what makes the kind decidable, since the same subject
yields a tutorial for one reader and reference for another.

## Conclusions

1. Documentation and the record are separate trees. A user-facing page carries
   no record identifier, no record artifact kind and no draft status, because
   none of the three means anything to the person reading it.
2. Documentation describes what ships. A page for unbuilt material is not
   written, and the index says the material is unbuilt.
3. Every plugin has a page of its own, and its catalogue entry links to that
   page, because the entry is the only route a reader has.
4. A catalogue entry carries the display fields the platform shows:
   description, homepage, repository, licence and keywords.
5. The entry's description says what the plugin does for the reader and what it
   costs to keep installed, because that description is the whole of the
   documentation before an install.
6. The repository carries a route file for agents, in the published format: a
   summary and link lists, with the skippable links marked optional.
7. The documented set is the six core types this project owes - a README, a
   tutorial, task-shaped how-to guides, reference, explanation and
   troubleshooting - plus release notes, which are settled elsewhere.
8. Documentation lives in the repository beside what it describes, and a
   plugin's page ships with the plugin.
9. Repetition between pages is accepted where a link would cost the reader a
   trip, and a user-facing page never sends a reader into the record for its
   explanation.
10. Incorrect documentation is treated as worse than missing documentation. A
    page that cannot be made current in the change that outdated it is deleted
    or marked stale in that same change.
11. Every page names its reader and its kind, because the kind is undecidable
    until the reader is named.
12. Every path, link and command a document names is checked mechanically, on
    the evidence that an index of seventeen lines drifted without anyone
    noticing.
13. The documentation index lists every page with what it answers and for whom,
    so a reader can tell which pages were written for them.

## Sources

All read 2026-09-20.

- `docs/README.md`, `docs/conventions.md` and `docs/plugins.md`, from the
  working tree - the invented artifact kinds, the draft status on a user-facing
  page, the stale `../specs/` reference, the description of a `spec/` tree that
  does not exist, and the sentence about speculative specifications.
- [Discover and install prebuilt plugins through marketplaces](https://code.claude.com/docs/en/discover-plugins):
  the detail pane's context cost, last-updated date and install list, and the
  instruction to visit a plugin's homepage for usage guidance.
- [Create and distribute a plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces):
  the fields an entry may carry, and which of them a person sees before
  installing.
- [The `/llms.txt` file](https://llmstxt.org/) - the required H1, the
  blockquote summary, the H2 link lists, the `Optional` section, and the stated
  purpose.
- [The Good Docs Project templates](https://www.thegooddocsproject.dev/template):
  the Core pack of seven content types, and what the Community and
  Miscellaneous packs add.
- [Documentation principles](https://www.writethedocs.org/guide/writing/docs-principles/),
  Write the Docs - ARID, skimmability, proximity to the code, and incorrect
  documentation being worse than missing documentation.
- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) - that a changelog is
  curated for people, read here only to confirm that it belongs with the
  release convention and no part of this set.
