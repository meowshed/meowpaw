---
id: SPC-1070
artifact: spec
status: live
revised: 2026-09-26
checked-at: "#296"
states:
  [
    REQ-0137,
    REQ-0145,
    REQ-0216,
    REQ-0219,
    REQ-0223,
    REQ-0234,
    REQ-0246,
    REQ-0247,
    REQ-0262,
    REQ-0266,
    REQ-0309,
    REQ-0396,
    REQ-0398,
    REQ-0512,
    REQ-0514,
    REQ-0520,
    REQ-0521,
    REQ-0524,
    REQ-0538,
    REQ-0540,
    REQ-0546,
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
    REQ-0622,
    REQ-0626,
    REQ-0630,
    REQ-0634,
    REQ-0635,
    REQ-0656,
    REQ-0692,
    REQ-0698,
    REQ-0700,
    REQ-0702,
    REQ-1673,
    REQ-2668,
    REQ-2864,
    REQ-2866,
    REQ-2868,
    REQ-2878,
    REQ-2882,
    REQ-2884,
    REQ-2886,
    REQ-2898,
    REQ-2912,
    REQ-2914,
    REQ-2923,
    REQ-2924,
    REQ-3102,
  ]
---

# Checking the record

## Scope

This covers `meow-method check`, the program that checks a repository's
record: where it finds the record, the layout it reads it by, what each check
reports, and how it exits.

It leaves declared kinds of a repository's own, transitive coverage, suspect
citations, orphaned artifacts and records that contradict the tree to later
decisions, which ADR-1100 names. The documentation index and links outside the
record are this repository's, and `tools/` keeps checking them.

ADR-1100 decides it and EPC-1070 realised it, verified under issue 168.
ADR-1140 adds the content rules, and EPC-1110 realised them, verified under
issue 206.

## Boundary

| Surface                               | What it is                              |
| ------------------------------------- | --------------------------------------- |
| `.meowpaw/profile.toml`, `[record]`   | Where the record lives                  |
| `plugins/meow-method/bin/meow-method` | The program: `check` and `check <name>` |
| `crates/meow/src/record.rs`           | The program's source, `meow record`     |
| `plugins/meow-method/lib/layout.toml` | The record's layout, as data            |
| `docs/meow-method.md`                 | The unit's documentation page           |

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
requirements, decisions, epics, tasks, defects and insights.

For each kind the layout also declares its content rules, and the scope of
each: every record of the kind, or drafts only (ADR-1140). A rule applies to
drafts only where the approved record already breaks it, because an approved
record is frozen and a check that fails on it can't be fixed without rewriting
what someone accepted.

| Kind        | Every record                                                                                                                                                                                                                                                                                                         | Drafts only                                                                                 |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| research    | sections Summary, Method, Conclusions and Sources, opening with Summary (REQ-0216, REQ-0219, REQ-2864, REQ-2866); the kind's own index is exempt from its sections                                                                                                                                                   | each source line carries a date (REQ-2868); the body cites no requirement (REQ-0223)        |
| requirement | no `priority`, `owner` or `difficulty` field (REQ-2878)                                                                                                                                                                                                                                                              | one verified by judgement carries `verifier` (REQ-2882)                                     |
| decision    | `addresses` names a requirement (REQ-0234); sections Decision, Why, Alternatives, What it costs, What would reverse it and Consequences (REQ-0247, REQ-0556, REQ-0560, REQ-0562); the alternatives table has a column saying why each lost (REQ-0558)                                                                | sections How I will know it was realised and What this does not settle (REQ-2884, REQ-2886) |
| epic        | `realises` names exactly one decision or defect (REQ-0262); sections Acceptance criteria, Tasks, Coverage and Not covered (REQ-0309, REQ-2898); a task marked `[x]` has evidence past "Not yet." (REQ-0692), one marked `[+]` an `added:` line and one marked `[~]` a `dropped:` line (REQ-0698, REQ-0700, REQ-0702) |                                                                                             |
| defect      | sections Reproduction, What the system does, What it should do and why, Triage and Closed by (REQ-2912, REQ-2914, REQ-2924); no `priority` field (REQ-2923)                                                                                                                                                          |                                                                                             |
| insight     | sections Evidence, What looked right and The pattern (REQ-0576); a title stating the claim, with no date and at least four words (REQ-0569); evidence holding a digit or a fenced block (REQ-0574); The pattern as the last section (REQ-0571)                                                                       |                                                                                             |

One file holds one artifact named for its identifier, in the directory of its
kind, with its kind, status and revision in its front matter (REQ-0512,
REQ-0514, REQ-0546). Six kinds carry numbers, research, requirement, decision,
epic, task and defect, and the vision is named (REQ-0538, REQ-0540). The
stored statuses come from one vocabulary, `draft`, `approved`, `withdrawn`,
`rejected`, `superseded` and `live`, each kind declares which it stores, and
the observed statuses, `implemented`, `verified`, `in-progress` and `done`,
are never stored (REQ-0587, REQ-0588, REQ-0589, REQ-0592, REQ-0593,
REQ-2668).

An insight, `INS-NNNN` in `insights/`, holds one generalisable lesson apart
from decisions, requirements and history (REQ-0568). Its title states the
claim with no date and at least four words, its Evidence section holds a digit
or a fenced block, it records under What looked right each refuted hypothesis
with why it seemed correct, and it ends with The pattern (REQ-0569, REQ-0571,
REQ-0574, REQ-0576). The `method` skill writes one only when something was
learned and never on a schedule, keeps activity in the history, and finds one
with `find` and never by default; a task records a prediction under its
acceptance criteria before the work that tests it (REQ-0570, REQ-0572,
REQ-0577, REQ-0578, REQ-0580) (ADR-1220).

### The checks

| Check        | Reports                                                                                                                                                                                                                       | Replaces                       |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| front matter | A missing field its kind requires, a revision that isn't a past date, and a status outside its kind's vocabulary (REQ-0573, REQ-0590)                                                                                         | `check_front_matter`, extended |
| identifiers  | A file whose name and identifier disagree, an identifier used twice, and a cited requirement that has no file                                                                                                                 | `check_ids`, over every kind   |
| relations    | An identifier in a relation field that doesn't resolve, and a link inside the record whose target doesn't exist (REQ-0656)                                                                                                    | new                            |
| index        | A file its kind's index doesn't list, and an index entry with no file (REQ-0524)                                                                                                                                              | new                            |
| coverage     | A requirement a decision addresses in no task or in two, and one in force that no specification states (REQ-0246)                                                                                                             | `check_coverage`               |
| shape        | An artifact missing a section its kind requires, or not opening with the one it must (REQ-0145)                                                                                                                               | `check_research`               |
| rules        | A named rule a section or field can't express: an undated source, research citing a requirement, a judged requirement with no verifier, an epic realising other than one record, an alternatives table with no reason it lost | new                            |

The front matter check also reports a field its kind must not carry, and a
field its kind must fill that is empty. The coverage check is the
decomposition's named coverage check, and `check` runs it on every change
(REQ-0266, REQ-3102).

Each finding names the file, and the line where there is one. `meow-method
check` runs every check and exits 0 when none found anything and 1 when any
did. `meow-method check <name>` runs one. No check writes a file (REQ-0137).

### The frozen check

`meow-method check frozen --base <rev>` reads each record whose stored status
was `approved` at `<rev>`, through git, and compares it with the current file
(ADR-1170). A change is reported, naming the record, as one that invalidates
its approval (REQ-0396, REQ-0398, REQ-0626, REQ-0630, REQ-0635), unless it is
one its kind allows:

| Kind            | May change after approval                                                                                                                                  |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| task            | its `## Evidence` section and its `issue`                                                                                                                  |
| epic            | anything, until its `checked-at` is set (REQ-0634)                                                                                                         |
| every record    | its status to `withdrawn` or `superseded`, and any change that adds a line naming its authority: `Amended by` or `Corrected by` a decision, defect or epic |
| living document | anything: the vision, a specification and an index are never frozen (REQ-0622)                                                                             |

Without `--base`, the check compares with `HEAD`. It isn't among the checks
`meow-method check` runs with no name, because it needs a base and git.

### This repository

`.meowpaw/profile.toml` declares `root = "project"`, and the `test` verb runs
`meow-method check` in place of the four scripts it replaces, which are
deleted (REQ-1673). `tools/check_index.py`, `tools/check_links.py` and the
checks over the harness's own units stay.

### The program

The program is `meow record`, the `record` subcommand of the native tool, built
with the unit's own feature as SPC-1080 states. The launcher runs the binary
for the machine, and the binary reads `lib/layout.toml` from the unit it ships
in. Where there is no binary for the machine, or the layout can't be read, the
record is reported as not checked and the program exits 3, never 0.

The checks are named `front-matter`, `identifiers`, `relations`, `index`,
`coverage` and `shape`. Each finding is printed as `<file>:<line>: <what>`, or
`<file>: <what>` where no one line holds it, with the file relative to the
repository's root, or absolute where the record lies outside it. Each check
ends with a line counting its findings. The identifiers check reads citations
of requirements in the record and in the repository's other Markdown, as
`check_ids` did.

## Failure paths

| Condition                            | What happens                                          |
| ------------------------------------ | ----------------------------------------------------- |
| No profile, or no `[record]` table   | The record is looked for at `project/`                |
| `root` doesn't exist                 | Nothing is checked; the missing path is named, exit 1 |
| A file of no known kind under `root` | Reported as an artifact of no known kind              |
| An unknown check named               | An error naming the seven checks, exit 2              |
| No binary for the machine            | The record is reported as not checked, exit 3         |
