---
id: SPC-1110
artifact: spec
status: live
revised: 2026-09-30
states:
  [
    REQ-3632,
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
---

# The documentation

## Scope

This covers the documentation `meowpaw` writes for the people and agents using
it: each unit's page, the introduction, the tutorial, the troubleshooting page,
the route file for agents and the catalogue fields a reader sees before an
install. It states where each page lives, the front matter every page carries
and what `tools/check_docs.py` holds.

It leaves the record under `project/` to SPC-1070 and SPC-1100, the document
step's obligations on a repository's own documentation and release notes to
later decisions.

ADR-1370 decides this part.

## Boundary

| Surface                                     | What it is                                                                    |
| ------------------------------------------- | ----------------------------------------------------------------------------- |
| `plugins/<unit>/README.md`                  | The unit's page: what it does, what it adds to a session and how to invoke it |
| `docs/README.md`                            | The introduction and the index of every page                                  |
| `docs/tutorial.md`                          | From an empty repository to a first verified change                           |
| `docs/troubleshooting.md`                   | The failures each unit reports, each with its cause and fix                   |
| `llms.txt`                                  | The route file for agents, at the repository root                             |
| `plugins/<unit>/.claude-plugin/plugin.json` | The unit's catalogue fields, written once                                     |
| `tools/check_docs.py`                       | The program that holds the documentation to the tree, run in the `test` verb  |

## Behaviour

### Where a page lives

Each unit's page is `README.md` at the root of the unit's directory, so
installing the unit brings it and a change to the unit sits beside it
(REQ-3136, REQ-3138). The page states what the unit does, what it adds to a
session and how to invoke it. Pages that describe the harness as a whole live
in `docs/`. A user-facing page is each unit's `README.md` and every Markdown
file under `docs/`.

A user-facing page carries no record identifier, no record artifact kind and no
record status in its prose or front matter, and it never names or links a
record's path under `project/` (REQ-3130, REQ-3148). An identifier inside code
is an example of the record's own syntax, which the pages of the units that
read the record need, and is no citation. It can link the constitution,
`CLAUDE.md`, which sits at the repository root.

### Front matter

Every user-facing page opens with four fields:

| Field       | Holds                                                                                         |
| ----------- | --------------------------------------------------------------------------------------------- |
| `reader`    | Who the page is written for (REQ-3142)                                                        |
| `answers`   | The question the page answers                                                                 |
| `kind`      | One of `introduction`, `tutorial`, `how-to`, `reference`, `explanation` and `troubleshooting` |
| `describes` | Each unit the page describes, as `<unit>@<version>` (REQ-2838)                                |

A page's `describes` names each unit at the version in that unit's
`plugin.json`. Whoever bumps a unit's version restamps every page describing
that unit in the same change, after reading the page again (REQ-3152).

### What the documentation covers

The documentation covers all six values of `kind` (REQ-3140). `docs/README.md`
is the introduction, each unit's page is reference, `docs/tutorial.md` is the
tutorial and `docs/troubleshooting.md` is troubleshooting. A kind no page
carries is listed in `docs/README.md` under `## Not written`, with the reason.

`docs/README.md` lists every page in a table generated from the pages' front
matter, stating what each answers and which reader it is for (REQ-3154). It
names every part of the harness that is planned and unbuilt, under
`## Planned`, so a reader doesn't infer it from a missing page (REQ-3134).

A page describes what ships and nothing planned (REQ-3132). A page can repeat
what another states, where a link would cost the reader the page they are on
(REQ-3150). The review step holds both, because each needs a reader's
judgement.

### The route file for agents

`llms.txt` is the route file and no user-facing page, so it carries no front
matter and may link into `project/`. It follows the `/llms.txt` format RES-0269
records: an H1 naming the project, a blockquote summary and H2 sections holding
lists of links, each with an optional note after a colon. A section named
`Optional` holds the links an agent can skip, which are the specifications and
the record (REQ-3144). Every entry is a link to material held elsewhere in the
repository, and the file restates none of it (REQ-3146).

### The catalogue fields

Each unit's `plugin.json` carries `description`, `homepage`, `repository`,
`license` and `keywords`. `homepage` points at the unit's own page on the
repository's default branch (REQ-3160). The description states what the unit
does for the reader and what keeping it installed costs them, and names the
ceiling from the unit's `budget.toml` as characters of context on every turn
(REQ-3164).

The committed `.claude-plugin/marketplace.json` names each unit, its source
and its homepage. The release workflow copies `description`, `repository`,
`license` and `keywords` from each unit's `plugin.json` into the served entry,
so the entry a reader sees before an install carries all five fields
(REQ-3162).

### The check

`python3 tools/check_docs.py` reads every user-facing page, each unit's
`plugin.json` and `budget.toml`, `docs/README.md`, `llms.txt`, the root
`README.md`, `CLAUDE.md`, `project/vision.md` and the method skill, and prints
one line per failure and a count. It exits 1 on any failure and 0 otherwise.
It fails when:

- a unit has no `README.md`, or a page lacks a field or carries a `kind`
  outside the six;
- a page's `describes` names a unit that doesn't exist or a version other than
  the unit's own;
- a page carries a record identifier, a record artifact kind or a record
  status, or links into `project/`;
- a `plugin.json` lacks a catalogue field, its `homepage` doesn't point at the
  unit's page, or its description doesn't name the unit's ceiling;
- the generated table in `docs/README.md` differs from the pages, or a kind is
  neither carried nor listed under `## Not written`;
- `llms.txt` lacks its H1 or summary, links to a path that doesn't exist, or
  carries a line that is neither a heading, the summary nor a link;
- a page, the root `README.md`, `CLAUDE.md`, `project/vision.md` or `llms.txt`
  states a number of the method's steps other than the number the method
  skill names (REQ-3632).

The step count is read from the method skill's list, "The steps, in order, are
a, b, ... and z.", however that sentence wraps, and never from a constant. The
skill is the first `plugins/*/skills/method/SKILL.md` by name. A skill whose
list can't be read, that isn't UTF-8, or that names a step that isn't one
lower-case word, is a failure, because a count nobody could read must never
pass as one that agreed. A repository shipping no method skill has no count
to hold.

A statement of the count is one of the forms that name the method, the harness
or the chain: "through the same N steps", "the method's N steps", "the method:
N steps", "the method has N steps" (each also with "a method"), "a method or
harness that costs, costing or demands N steps", "N steps run in a chain", "N
steps from research" and "the N-step chain". N is a whole word up to twenty,
or digits. A statement is read across line wraps within a paragraph, inside a
quoted block and through emphasis marks, and not inside fenced code, a code
span on one line or a comment on one line. One statement is one failure, named
at the line the number is on. A count of anything else, such as "install it
in three steps" or "this install method has three steps", isn't read. One of
the root files that isn't UTF-8 is a failure of its own, and the check goes on.

`python3 tools/check_docs.py --write` rewrites the table between the
`<!-- check_docs index -->` and `<!-- /check_docs index -->` markers in
`docs/README.md` from the pages, and changes nothing else.

## Failure paths

Each failure prints one line, and the check goes on to report the rest.

| Failure                              | What the reader sees                                                 | What fixes it                                                            |
| ------------------------------------ | -------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| A unit with no page                  | `<unit>: has no README.md`                                           | Write the unit's page                                                    |
| A page missing a field               | `<page>: front matter lacks <field>`                                 | Add the field                                                            |
| A `kind` outside the six             | `<page>: kind <kind> is not one of the six`                          | Choose one of the six                                                    |
| A `describes` naming no unit         | `<page>: describes <unit>, which doesn't exist`                      | Name an existing unit                                                    |
| A version bump without a restamp     | `<page>: describes <unit>@<old>, the unit is at <new>`               | Read the page again and restamp it                                       |
| A page citing the record             | `<page>:<line>: cites the record: <text>`                            | State the fact on the page, without the identifier, kind, status or link |
| A page stating the wrong step count  | `<page>:<line>: states <n> steps, and the method names <m>`          | State the number the method skill names                                  |
| A method skill with no readable list | `<skill>: names no step list, ...` or `names the step "<name>", ...` | Write the list as "The steps, in order, are a, b, ... and z."            |
| A root file that isn't UTF-8         | `<file>: isn't UTF-8`                                                | Save the file as UTF-8                                                   |
| A missing catalogue field            | `<unit>: plugin.json lacks <field>`                                  | Add the field to `plugin.json`                                           |
| A homepage elsewhere                 | `<unit>: homepage doesn't point at plugins/<unit>/README.md`         | Point `homepage` at the unit's page                                      |
| A description without the ceiling    | `<unit>: the description doesn't name its ceiling, <n>`              | Add the ceiling from `budget.toml` to the description                    |
| A stale index                        | `docs/README.md: the table is out of date; run --write`              | `python3 tools/check_docs.py --write`                                    |
| A kind neither carried nor recorded  | `docs/README.md: no page is <kind>, and Not written doesn't list it` | Write the page, or list the kind with its reason                         |
| `llms.txt` without its H1 or summary | `llms.txt: lacks its <part>`                                         | Add the H1 or the blockquote summary                                     |
| An `llms.txt` link to a missing path | `llms.txt:<line>: links to <path>, which doesn't exist`              | Point the link at the page, or remove the entry                          |
| A line of prose in `llms.txt`        | `llms.txt:<line>: neither a heading, the summary nor a link`         | Move the prose to a page and link it                                     |
