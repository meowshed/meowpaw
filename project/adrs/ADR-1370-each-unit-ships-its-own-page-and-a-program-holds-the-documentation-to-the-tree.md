---
id: ADR-1370
artifact: adr
status: done
revised: 2026-09-27
addresses:
  [
    REQ-2838,
    REQ-3130,
    REQ-3132,
    REQ-3134,
    REQ-3136,
    REQ-3138,
    REQ-3140,
    REQ-3142,
    REQ-3144,
    REQ-3146,
    REQ-3148,
    REQ-3150,
    REQ-3152,
    REQ-3154,
    REQ-3160,
    REQ-3162,
    REQ-3164,
  ]
supersedes: []
---

# 1370. Each unit ships its own page, and a program holds the documentation to the tree

## Decision

Each unit's page moves from `docs/<unit>.md` to `plugins/<unit>/README.md`,
so installing the unit brings its page and changing the unit changes a file
beside it (REQ-3136, REQ-3138). The page states what the unit does, what it
adds to a session and how to invoke it.

A user-facing page is each unit's `README.md` and every Markdown file under
`docs/`. Every user-facing page opens with front matter that a program reads
and that anyone reading the file sees first:

```yaml
---
reader: someone choosing or running meow-verbs
answers: what meow-verbs does, what it adds to a session and how to run it
kind: reference
describes: [meow-verbs@0.2.1]
---
```

`reader` and `answers` name who the page is for and what it answers
(REQ-3142). `kind` is one of `introduction`, `tutorial`, `how-to`,
`reference`, `explanation` and `troubleshooting`. `describes` names each unit
the page describes, at the version it describes (REQ-2838).

A new program, `tools/check_docs.py`, runs in the `test` verb on every change
and fails when:

- a unit has no `README.md`, or a user-facing page lacks one of the four
  fields or carries a `kind` outside the six;
- a page's `describes` names a unit that doesn't exist, or a version other
  than the one in the unit's `plugin.json`, so a change that bumps a unit
  fails until whoever bumps it re-reads and restamps every page describing it
  (REQ-2838, REQ-3152);
- a user-facing page carries a record identifier, a record artifact kind or a
  record status, or links to anything under `project/` (REQ-3130, REQ-3148);
- a unit's `plugin.json` lacks `description`, `homepage`, `repository`,
  `license` or `keywords`, its `homepage` doesn't point at the unit's own
  page, or its description doesn't state the unit's ceiling from
  `budget.toml` as characters of context on every turn (REQ-3160, REQ-3162,
  REQ-3164);
- the generated table in `docs/README.md` differs from the pages' front
  matter, or a kind from the six is neither carried by a page nor listed as
  absent with its reason (REQ-3140, REQ-3154);
- `llms.txt` at the repository root lacks its H1 or its summary, links to a
  path that doesn't exist, or carries a line that is neither a heading, the
  summary nor a link (REQ-3144, REQ-3146).

`llms.txt` is a route file and no user-facing page, so it carries no front
matter and may link into `project/`. `python3 tools/check_docs.py --write`
regenerates the index table from the pages, so nobody keeps it by hand.

The release workflow copies `description`, `repository`, `license` and
`keywords` from each unit's `plugin.json` into the served catalogue entry,
beside the `homepage` the entry already carries. It copies them because a
served entry is an archive, and the platform shows only an archive entry's own
fields before an install (RES-0269). `plugin.json` stays the one place those
fields are written.

`docs/README.md` becomes the introduction. It lists every page with its
reader and what it answers, states which parts of the harness are planned and
unbuilt, and records each absent kind with its reason (REQ-3134, REQ-3140).
Two pages join it: a tutorial, `docs/tutorial.md`, taking a reader from an
empty repository to a first verified change, and a troubleshooting page,
`docs/troubleshooting.md`, for the failures each unit reports. `llms.txt`
routes an agent to the introduction, the unit pages and the constitution,
with the specifications and the record under `Optional` (REQ-3144).

A page describes what ships and nothing planned (REQ-3132), and it can repeat
another page where a link would cost the reader the page they are on
(REQ-3150).

After this decision a reader who finds a unit in the catalogue sees what it
does and what it costs before installing it, and gets its page with it. A
change that bumps a unit fails the gate until its pages are restamped. What
still doesn't work: a change that outdates a page without bumping its unit's
version passes. The document step's own obligations on a repository's
documentation, such as naming the kind before writing, are a later decision.

## Why

Today the served entries carry a name, a source and a homepage, so a reader
choosing a unit sees no description at all. The homepage is the only route
from the catalogue to a longer page, and the page it reaches lives in
`docs/`, where installing the unit doesn't bring it.

The research found an index of seventeen lines drifting without anyone
noticing (RES-0269), which is why every claim a program can settle goes to
`tools/check_docs.py`. A page's reader, what it answers, the version it
describes, the fields an entry carries and the paths it links are all facts in
files, so the check reads them. Whether a page describes something unbuilt,
and whether a repetition earns its place, need a reader, so the review step
holds them (REQ-0147).

I stamp the version because it moves exactly when shipped behaviour does. A
page's last commit date moves on every edit, formatting included, so a date
can't tell a page someone re-read from one someone reflowed. The stamp misses
a change made without a version bump, but such a change doesn't reach a
reader who installs the unit either: the release reuses the archive already
published under that version, so the page and what ships still agree.

The strongest objection: front matter on a user-facing page looks like the
record's, and RES-0269 found this tree's documentation already merged with the
record, down to invented record kinds and a draft status on a user-facing
page, which REQ-3130 forbids. The fields differ, though. None of them is an
identifier, a record kind or a status, and each one tells the reader
something: who the page is for, what it answers and which version it
describes.

## Alternatives

| Option                                                           | Better at                                         | Why it lost                                                                                                                                             |
| ---------------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                                       | No page moves, and no check to keep               | Entries show no description, pages don't ship with their units, and no check detects a stale page                                                       |
| Pages in the unit, held by review alone                          | No program to write                               | The index already drifted under review, and every fact here is one a program reads                                                                      |
| Pages in the unit, fields written into `marketplace.json`        | The committed catalogue is exactly what is served | Two copies of every description, one of them edited by hand, where the release can copy from `plugin.json`                                              |
| Keep pages in `docs/`, and link each entry there                 | Nothing moves                                     | Installing a unit wouldn't bring its page, against REQ-3138                                                                                             |
| A page's reader and kind in its first sentence, not front matter | Nothing that looks like the record's front matter | A check would match patterns over prose, which fires on the wrong sentence and gets switched off, the reason ADR-1010 gave for rejecting one (REQ-0147) |
| Staleness from the page's last commit date against the unit's    | No field to restamp                               | A date moves on any edit, formatting included, so it can't tell a re-read page from a reflowed one                                                      |

## What it costs

Eight pages move, and every link to them changes once. Every change that
bumps a unit also restamps each page describing it: one line per page, and
the re-read the stamp exists to force. Two new pages need writing and keeping.
The check is a program of its own in `tools/`, where the constitution names
three.

## What would reverse it

- The platform starts showing a plugin's own manifest fields for an archive
  source before install, so the release no longer needs to copy them.
- A verification finds a page stamped at its unit's current version that
  describes behaviour the unit no longer has, in two epics, which would show
  the stamp is being moved without the re-read it exists to force.

## Consequences

- `plugins/<unit>/README.md` holds each unit's page, and `docs/<unit>.md`
  goes.
- Each unit's `plugin.json` homepage points at its own page, and its
  description ends with the unit's ceiling in characters of context on every
  turn.
- `docs/README.md`, `docs/tutorial.md` and `docs/troubleshooting.md` carry
  the same front matter, and `llms.txt` sits at the repository root.
- `tools/check_docs.py` runs in the `test` verb, and `CLAUDE.md` names four
  checks in `tools/` where it names three.
- The release workflow copies four fields into each served entry.
- `tools/check_index.py` walks the unit pages, which it skips today.

## How I will know it was realised

1. `tools/check_docs.py` passes on the tree and fails on a probe for each
   condition it lists, among them a unit with no page, a page missing
   `reader`, a stale `describes` version, a page citing a record identifier,
   a `plugin.json` missing `license` and an `llms.txt` link to a missing
   file.
2. Every unit's page is `plugins/<unit>/README.md`, and no `docs/<unit>.md`
   remains.
3. The release workflow, run over the committed catalogue, produces entries
   carrying `description`, `homepage`, `repository`, `license` and
   `keywords` for every unit.
4. `docs/README.md` lists every page with its reader and what it answers,
   names the planned and unbuilt parts, and records each absent kind with its
   reason.
5. Every requirement ADR-1370 addresses lands in exactly one closed task.

## What this does not settle

- The document step's obligations on a repository's own documentation:
  naming the kind before writing, one kind per page, generated reference,
  runnable examples and following a quick start on a clean machine
  (REQ-1950 to REQ-1964, REQ-0287, REQ-0289, REQ-2834, REQ-2836).
- The files a public repository owes a newcomer, such as a contributing guide
  and a security policy.
- Release notes and the changelog.
- A change that outdates a page without bumping a version.
