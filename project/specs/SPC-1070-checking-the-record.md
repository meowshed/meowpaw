---
id: SPC-1070
artifact: spec
status: live
revised: 2026-10-31
states:
  [
    REQ-3678,
    REQ-4602,
    REQ-0137,
    REQ-0145,
    REQ-0216,
    REQ-0219,
    REQ-0223,
    REQ-0234,
    REQ-0246,
    REQ-0247,
    REQ-3668,
    REQ-3672,
    REQ-0396,
    REQ-0398,
    REQ-4002,
    REQ-0512,
    REQ-0514,
    REQ-0520,
    REQ-0521,
    REQ-0524,
    REQ-0525,
    REQ-0530,
    REQ-0540,
    REQ-0552,
    REQ-0554,
    REQ-0555,
    REQ-0556,
    REQ-0558,
    REQ-0560,
    REQ-0562,
    REQ-0568,
    REQ-0569,
    REQ-0570,
    REQ-0571,
    REQ-0572,
    REQ-0573,
    REQ-0574,
    REQ-0576,
    REQ-0577,
    REQ-0578,
    REQ-0580,
    REQ-0587,
    REQ-0588,
    REQ-0589,
    REQ-0590,
    REQ-0592,
    REQ-0593,
    REQ-0594,
    REQ-0622,
    REQ-0626,
    REQ-0630,
    REQ-3676,
    REQ-0656,
    REQ-1664,
    REQ-1673,
    REQ-2668,
    REQ-2864,
    REQ-2866,
    REQ-2868,
    REQ-2878,
    REQ-2880,
    REQ-2882,
    REQ-2884,
    REQ-2886,
    REQ-2912,
    REQ-2914,
    REQ-2923,
    REQ-2924,
    REQ-3004,
    REQ-3008,
    REQ-3009,
    REQ-3010,
    REQ-3011,
    REQ-3012,
    REQ-3014,
    REQ-3016,
    REQ-3018,
    REQ-3019,
    REQ-3020,
    REQ-3102,
    REQ-3168,
    REQ-3190,
    REQ-3654,
    REQ-0610,
    REQ-0612,
    REQ-0628,
    REQ-0632,
    REQ-0666,
    REQ-0667,
    REQ-0668,
    REQ-0670,
    REQ-2662,
    REQ-1662,
    REQ-3046,
    REQ-3680,
    REQ-3684,
    REQ-5302,
    REQ-5304,
    REQ-5306,
    REQ-5308,
    REQ-5310,
    REQ-5312,
    REQ-5314,
  ]
---

# Checking the record

## Scope

This covers `paw check`, the program that checks a repository's
record: where it finds the record, the layout it reads it by, what each check
reports, and how it exits.

It leaves transitive coverage, suspect citations, orphaned artifacts and
records that contradict the tree to later decisions, which ADR-1100 names. The documentation index and links outside the
record are this repository's, and `tools/` keeps checking them.

ADR-1100 decides it. ADR-1140 adds the content rules, ADR-1800 adds the
grouping fields, ADR-2590 adds the rules that hold the living kinds apart from
the records, ADR-2600 adds the kinds a repository declares, ADR-2610 pins an
approved insight as frozen, ADR-2630 adds the concern check, ADR-2650 keeps the
record at the root of a repository with parts, ADR-2690 pins the layout and the
four kinds of check, and ADR-3090 adds the plan, the stored `done`, the archive
and the upgrade.

## Boundary

| Surface                             | What it is                                                 |
| ----------------------------------- | ---------------------------------------------------------- |
| `.meowpaw/profile.toml`, `[record]` | Where the record lives                                     |
| `plugins/meow-flow/bin/paw`         | The program: `check`, `check <name>`, `done` and `upgrade` |
| `crates/meow/src/record.rs`         | The program's source, `meow record`                        |
| `plugins/meow-flow/lib/layout.toml` | The record's layout, as data                               |
| `plugins/meow-flow/README.md`       | The unit's documentation page                              |

## Behaviour

### Where the record lives

```toml
[record]
root = "project"
```

`root` is a path relative to the repository's root, and it may lead outside it,
to a folder or to another repository's checkout (REQ-0520, REQ-0521). Where it
isn't declared, the record is at `project/`. Where the path doesn't exist, the
program says so and checks nothing, and exits 1: a record that can't be found
isn't a clean one.

### The layout

The unit carries the layout `CLAUDE.md` states, as data: for each kind, its
prefix, its directory under `root`, its required front matter fields, its
status vocabulary, the file that indexes it if one does, and the sections it
must carry if any. The kinds are the vision, specifications, research,
requirements, decisions, defects and insights. Two more, the epic and the task,
are archived kinds, which "Archived kinds" below states.

For each kind the layout also declares its content rules, and the scope of
each: every record of the kind, or drafts only (ADR-1140). A rule applies to
drafts only where the approved record already breaks it, because an approved
record is frozen and a check that fails on it can't be fixed without rewriting
what someone accepted. `verification-kind` reaches every requirement, because
none breaks it and `paw status` reads every approved requirement's value to
report how much rests on judgement (ADR-1510).

| Kind        | Every record                                                                                                                                                                                                                                                                                                                                         | Drafts only                                                                                                                                                |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| research    | sections Summary, Method, Conclusions and Sources, opening with Summary (REQ-0216, REQ-0219, REQ-2864, REQ-2866); the kind's own index is exempt from its sections                                                                                                                                                                                   | each source line carries a date (REQ-2868); the body cites no requirement (REQ-0223)                                                                       |
| requirement | no `priority`, `owner` or `difficulty` field (REQ-2878); `verification` holds one of `static`, `behavioural`, `evaluation` and `judgement` (REQ-1664) (ADR-1510)                                                                                                                                                                                     | one verified by judgement carries `verifier` (REQ-2882); its statement carries one keyword, leans on no neighbour and prohibits with `MUST NOT` (REQ-2880) |
| decision    | `addresses` names a requirement (REQ-0234); sections Decision, Why, Alternatives, What it costs, What would reverse it and Consequences (REQ-0247, REQ-0556, REQ-0560, REQ-0562); the alternatives table has a column saying why each lost (REQ-0558); a draft or approved one that addresses work carries a `## Plan` (`plan-where-work`, REQ-3672) | sections How I will know it was realised and What this does not settle (REQ-2884, REQ-2886)                                                                |
| defect      | sections Reproduction, What the system does, What it should do and why, Triage and Closed by (REQ-2912, REQ-2914, REQ-2924); no `priority` field (REQ-2923); no grouping field (REQ-3668); a done one names the check that closed it (`closed-names-check`)                                                                                          | one entering at implement carries a `## Plan` (`plan-where-implement`, REQ-3674)                                                                           |
| insight     | sections Evidence, What looked right and The pattern (REQ-0576); a title stating the claim, with no date and at least four words (REQ-0569); evidence holding a digit or a fenced block (REQ-0574); The pattern as the last section (REQ-0571)                                                                                                       |                                                                                                                                                            |

One file holds one artifact named for its identifier, in the directory of its
kind, with its kind, status and revision in its front matter (REQ-0512,
REQ-0514). A decision or a defect is the one unit of work (REQ-3668). The
numbered kinds are research, requirement, decision, defect and insight, the
archived epic and task keep their numbers, and the vision is named (REQ-0540).
The stored statuses come from one vocabulary, `draft`, `approved`, `done`,
`withdrawn`, `rejected`, `superseded` and `live`, and each kind declares which
it stores. Of the live kinds, only decisions and defects declare `done`, which
`paw done` stores (REQ-3678). Observed statuses such as `open`, `in-progress` and `closed` are
never stored (REQ-0587, REQ-0588, REQ-0589, REQ-0592, REQ-0593, REQ-2668).

An insight, `INS-NNNN` in `insights/`, holds one generalisable lesson apart
from decisions, requirements and history (REQ-0568). Its title states the
claim with no date and at least four words, its Evidence section holds a digit
or a fenced block, it records under What looked right each refuted hypothesis
with why it seemed correct, and it ends with The pattern (REQ-0569, REQ-0571,
REQ-0574, REQ-0576). The `method` skill writes one only when something was
learned and never on a schedule, keeps activity in the history, and finds one
with `find` and never by default; a decision records a prediction under How I
will know it was realised before the work that tests it (REQ-0570, REQ-0572,
REQ-0577, REQ-0578, REQ-0580) (ADR-1220).

The specifications' index lists each specification after every specification
it cites, so reading it in order never needs a forward reference (REQ-0525).
A living document cites no withdrawn requirement: the withdrawn statement
stays in its own record, which names what replaced it, so it never interrupts
the living document. No directory under the root is named for an archive,
because a superseded record carries its status and names its replacement,
except the directories the layout declares for an archived kind (REQ-0552,
REQ-0554, REQ-0555). A draft requirement's statement carries one
keyword, leans on no neighbour, and prohibits with `MUST NOT` (REQ-2880). The
constitution outranks every artifact (REQ-0530) (ADR-1230).

A grouping field is one of `milestone`, `parent`, `project`, `sprint`,
`iteration`, `label` and `labels`, and the layout forbids each on the defect
kind, so a record carrying one is reported whatever its status: a defect is its
own unit of work, and nothing else groups it (REQ-3668). A grouping written under a field name outside that list isn't
reported (ADR-1800).

Three kinds are living, the vision, the specification and the constitution,
and the check fails a record of any other kind that declares `status: live`
(REQ-0610). An index file in a kind's directory is generated from the tree and
is no kind of its own, so it keeps `status: live`. A specification carries no
history (REQ-0612, REQ-0632): the check fails one that carries `~~struck~~`
text, a heading naming a tombstone or a withdrawal, or a sentence naming an
earlier version, which a list of phrases in the layout matches. A phrase
outside the list passes until it joins the list. A withdrawn record opens its body with a line naming the
record that withdrew it, as `**Withdrawn by ADR-1800. Replaced by
REQ-4002.**`, and the check fails a withdrawn record whose first line under
its title names no identifier (REQ-0628).

The layout records every retired front matter field, status value and section with what
replaced it, and the check refuses a record or a kind carrying one, so a
retired name is never reused (REQ-3010, REQ-3011). `paw count` prints
each kind's count by status and the number of identifiers, which a migration's
evidence carries before and after (REQ-3020). The `method` skill runs a change
to the record's shape as expand, migrate and contract, names the release that
removes the old form, migrates or grandfathers a new obligation, edits
structured data as structured data, and splits a migration into reviewable
parts with the mechanical apart from the editorial (REQ-3008, REQ-3009,
REQ-3012, REQ-3014, REQ-3016, REQ-3018, REQ-3019) (ADR-1240).

### Kinds a repository declares

A repository declares a kind of its own in `.meowpaw/profile.toml`, without
changing the harness (REQ-0666):

```toml
[record.kinds.narrative]
prefix = "NAR"
lifetime = "record"
template = ".meowpaw/templates/narrative.md"
outranks = ["research"]
```

`prefix` is the identifier's prefix, `lifetime` is `record` or `living`, and
`template` is a path under `.meowpaw/templates/`; a declaration that lacks
any of the three, or whose template doesn't exist, is a finding (REQ-0668).
Files of a declared kind sit in a directory named for the kind under the
record's root. A declared kind inherits every general obligation: its front
matter, its identifiers, its relations and, as a record, its freezing on
approval, and the declaration carries no key that turns one off (REQ-0670).
`outranks` is optional, and lists the kinds the declared kind wins over.
Where two artifacts of kinds in that order cite each other and state
different values for one front matter field, `paw check` reports the
conflict, naming both and the order, and doesn't choose (REQ-0667).
`paw index` writes no index for a declared kind.

### Archived kinds

The layout declares the epic and the task as archived kinds, in
`archive/epics/` and `archive/tasks/`, with `archived = true`. `paw` reads both,
so an `EPC-` or `TSK-` citation still resolves, `paw show` prints the record, and
a done archived task still counts towards closing a requirement (REQ-3680).
`paw new epic` and `paw new task` refuse with exit 1, and `paw template` knows
neither kind, so neither can be written (REQ-3684). No content rule reads an
archived record, and `paw check frozen` doesn't compare one.

A record still holding `epics/` or `tasks/` at its root is in a form the harness
retired. Every `paw` command but `upgrade` reports the one finding `the record
holds epics or tasks, a form ADR-3090 retired; run paw upgrade` and exits 1,
because a second working form would never retire. `paw status --waiting` is the
exception, because it runs at the start of every session and must say nothing
unless something waits.

### The upgrade

`paw upgrade` moves a record to the form the harness requires (REQ-5300). With
no flag it reports each move and writes nothing, and exits 0 (REQ-5302).
`paw upgrade --write` makes the moves:

1. It adds each open task as a step of the `## Plan` of its live authority, the
   draft or approved decision or defect that authorises it directly or through
   its epic, naming the archived task, and writes `folded-into:` on the task
   (REQ-5306). It opens a `## Plan` where the record has none.
2. It reports an open task with no live authority as needing a decision, leaves
   it with no `folded-into:` and places it nowhere, because placing it would
   invent an authorisation (REQ-5308).
3. It stores `done` on each approved decision and defect the old marks derive as
   complete, because nothing can compute that once the marks are archived
   (REQ-5310). The tasks' marks, an epic's Not covered section and a defect's
   Closed by feed that one reading, which `crates/meow/src/record/upgrade.rs`
   holds.
4. It moves `epics/` and `tasks/` to `archive/epics/` and `archive/tasks/`, each
   file otherwise unchanged (REQ-5304).
5. It removes `epic` from `[unattended] gates` in the profile, touching only that
   list (REQ-5312).

The directories move last, so a run that stops leaves a record the next run
finishes. A template under `.meowpaw/templates/` for a retired kind is reported
and left alone, because it is the repository's own file. On a record already in
the form, the command prints `nothing to upgrade` and changes nothing
(REQ-5314).

### The checks

| Check        | Reports                                                                                                                                                                                                                                    | Replaces                       |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------ |
| front matter | A missing field its kind requires, a revision that isn't a past date, and a status outside its kind's vocabulary (REQ-0573, REQ-0590)                                                                                                      | `check_front_matter`, extended |
| identifiers  | A file whose name and identifier disagree, an identifier used twice, and a cited requirement that has no file                                                                                                                              | `check_ids`, over every kind   |
| relations    | An identifier in a relation field that doesn't resolve, and a link inside the record whose target doesn't exist (REQ-0656)                                                                                                                 | new                            |
| index        | A file its kind's index doesn't list, and an index entry with no file (REQ-0524)                                                                                                                                                           | new                            |
| coverage     | A requirement an approved decision addresses that no specification states (REQ-0246)                                                                                                                                                       | `check_coverage`               |
| shape        | An artifact missing a section its kind requires, not opening with the one it must (REQ-0145), or carrying a section the layout retired (REQ-3684)                                                                                          | `check_research`               |
| rules        | A named rule a section or field can't express: an undated source, research citing a requirement, a judged requirement with no verifier, a decision or defect with no plan where it needs one, an alternatives table with no reason it lost | new                            |

The front matter check also reports a field its kind must not carry, and a
field its kind must fill that is empty. The coverage check is the
decomposition's named coverage check, and `check` runs it on every change
(REQ-3102, REQ-3680). A decision may address any number of requirements, and any
number of decisions may address one requirement (REQ-3680).

Each finding names the file, and the line where there is one. `paw
check` runs every check and exits 0 when none found anything and 1 when any
did. `paw check <name>` runs one. No check writes a file (REQ-0137).

### The frozen check

`paw check frozen --base <rev>` reads each record whose stored status
was `approved` at `<rev>`, through git, and compares it with the current file
(ADR-1170). A change is reported, naming the record, as one that invalidates
its approval (REQ-0396, REQ-0398, REQ-0626, REQ-0630, REQ-3676), unless it is
one its kind allows:

| Kind               | May change after approval                                                                                                                                                                                                                 |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| decision or defect | until it is done: its `## Plan`, `## Tasks` and `## Closed by` sections and its `issue`, `projected`, `tracked`, `pr` and `revised` fields (REQ-3676); and its status from `approved` to `done`. A done record is frozen whole (REQ-0594) |
| every record       | the removal of a field or a section the layout retired, which is a change of format and not of what was approved (REQ-3684); a record still carrying one is compared whole                                                                |
| every record       | its status to `withdrawn` or `superseded`, and any change that adds a line naming its authority: `Amended by` or `Corrected by` a decision or defect                                                                                      |
| living document    | anything: the vision, a specification and an index are never frozen (REQ-0622)                                                                                                                                                            |

An insight is a record like any other, so its whole file is frozen once
approved, and a later lesson on the same subject is a new insight that cites
it (REQ-2662). A test pins that a change to an approved insight is reported. An archived record
isn't compared, because `paw upgrade` writes `folded-into:` on it.

Without `--base`, the check compares with `HEAD`. It isn't among the checks
`paw check` runs with no name, because it needs a base and git.

### Writing the record

A status change that implies an edit to another record is one command
(REQ-3678, ADR-2880). `paw approve <id>...` moves a draft to `approved` where
`paw check` reports nothing about it. `paw done <record> --pr <number>` stores
`done` and `pr:` on an approved decision or defect, in the pull request that
completes it, so the merge closes it (REQ-3678). It refuses a decision that
addresses work and carries no plan, and a defect whose Closed by is empty or
opens with "Not" or "Open". `paw withdraw <requirement> --by <decision> --replaced-by <id>...` writes the
tombstone and the status. Each command changes the lines it owns and leaves the
rest of the file as it found it, and its result passes `paw check` without the
command, so a hand edit stays valid (REQ-4602, REQ-0030).

A requirement closes when a done decision addresses it or a done archived task
closes it, and no approved decision still in work addresses it (REQ-3680).

### This repository

`.meowpaw/profile.toml` declares `root = "project"`, and the `test` stage runs
`paw check` in place of the four scripts it replaces, which are
deleted (REQ-1673). `tools/check_index.py`, `tools/check_links.py` and the
checks over the harness's own units stay.

Every requirement is checkable by one of the four kinds of check its
`verification` field names, as the layout states, and a test pins that the
front matter check fails any other value (REQ-1662). The record stays at the repository's
root in a repository with parts, and only the specification divides by part,
because one record answers what the project decided for every part
(REQ-3046).

### The program

The program is `meow record`, the `record` subcommand of the native tool, built
with the unit's own feature as SPC-1080 states. A person runs it as `paw`, the
name of the unit's launcher, and every usage line and message it prints names
it `paw` (REQ-3168). The unit is `meow-flow` (REQ-3190). The `meow-method` stub that
told an install to move stayed one release (REQ-3004) and has left the
marketplace (REQ-3654). The launcher runs the binary for the machine, and the binary
reads `lib/layout.toml` from the unit it ships in. Where there is no binary for
the machine, or the layout can't be read, the record is reported as not checked
and the program exits 3, never 0.

The checks are named `front-matter`, `identifiers`, `relations`, `index`,
`coverage` and `shape`. Each finding is printed as `<file>:<line>: <what>`, or
`<file>: <what>` where no one line holds it, with the file relative to the
repository's root, or absolute where the record lies outside it. Each check
ends with a line counting its findings. The identifiers check reads citations
of requirements in the record and in the repository's other Markdown, as
`check_ids` did.

## Failure paths

| Condition                                                                                                | What happens                                                             |
| -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| No profile, or no `[record]` table                                                                       | The record is looked for at `project/`                                   |
| `root` doesn't exist                                                                                     | Nothing is checked; the missing path is named, exit 1                    |
| A file of no known kind under `root`                                                                     | Reported as an artifact of no known kind                                 |
| A declared kind without its template                                                                     | A finding naming the kind and the missing key or file                    |
| The record holds `epics/` or `tasks/`                                                                    | One finding naming the upgrade, exit 1, from every command but `upgrade` |
| Two ranked kinds disagree                                                                                | A conflict naming both artifacts and the order                           |
| A decision's concern framed nowhere                                                                      | A finding naming the decision and the concern                            |
| `paw new epic` or `paw new task`                                                                         | Refused, naming ADR-3090, exit 1                                         |
| `paw done` on a record not approved, a decision with no plan, or a defect whose Closed by names no check | Refused, with the reason, exit 1                                         |
| An unknown check named                                                                                   | An error naming the seven checks, exit 2                                 |
| No binary for the machine                                                                                | The record is reported as not checked, exit 3                            |

## Questions

Answer each question from what this document states, or leave `unanswered`,
because a gap left visible is one a reader can act on, and a gap left out
reads as covered.

### What the part is for

Checks a repository's record: its layout, front matter, identifiers, relations, coverage and rules.

### What it depends on

`meow-flow` lists `meow-core`, `meow-prose` in its `requires.toml`.

### What depends on it

`meow-loop` list `meow-flow` in their `requires.toml`.

### Where its data lives

The record under the root `[record] root` names, `project/` by default, read by the layout in `lib/layout.toml`.

### What crosses a trust boundary

unanswered

### How it fails

Stated under "Failure paths" in this document.

### How it is deployed

`meow-flow` installs as a plugin from the marketplace, `plugins/meow-flow/`, and ships as the Pi package `packages/meow-flow/`.
