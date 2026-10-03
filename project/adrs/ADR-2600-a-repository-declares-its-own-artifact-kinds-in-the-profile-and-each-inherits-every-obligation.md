---
id: ADR-2600
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [REQ-0660, REQ-0662, REQ-0664, REQ-0666, REQ-0667, REQ-0668, REQ-0670]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2600. A repository declares its own artifact kinds in the profile, and each inherits every obligation

## Decision

A repository declares a kind of its own in `.meowpaw/profile.toml`, under
`[record.kinds.<name>]`, without changing the harness (REQ-0666). Each
declaration states its identifier prefix, whether it is a record or living,
and the template it is written from, a path under `.meowpaw/templates/`
(REQ-0668). It may also list the kinds it outranks, and `paw check` reports
a conflict across that order and doesn't resolve it (REQ-0667). A declared
kind inherits every general obligation, the front matter, the identifier
rules, the relations and freezing on approval, and no key in the declaration
turns one off (REQ-0670).

A task's output may be a document and not code (REQ-0660). Where it is, the
task names the artifact in `produces:` and the artifact names the task in
`prompted-by:`, and `paw check` fails one side without the other (REQ-0662). A
produced document meets every obligation of its kind, the same as one a step
wrote (REQ-0664).

The new keys join the table of profile keys ADR-2370 created.

Once this is accepted, a game's narrative documents or a regulator's evidence
files can sit in the record and be checked like a requirement. What still
doesn't work: `paw index` writes an index only for the built-in kinds, so a
declared kind has no generated index until a later decision gives it one.

## Why

RES-0036 found that projects keep kinds of document the method didn't
foresee, and that a harness which lets them opt out of its rules by declaring
a kind has no rules. It found that two kinds can disagree about one fact and
need an order to settle which is stale. The vision states the same promise:
a declared kind buys no exemptions.

## Alternatives

| Option                       | Better at                         | Why it lost                                                       |
| ---------------------------- | --------------------------------- | ----------------------------------------------------------------- |
| Do nothing                   | No new keys                       | A project's own documents stay outside the record's checks        |
| Kinds declared in a plugin   | A kind shared across repositories | A repository then needs a plugin of its own for one document type |
| Let a kind set its own rules | Fits any document                 | Extensibility becomes the way out of the method                   |

## What it costs

`paw check` has to read kinds at run time instead of from a fixed list, and
each declared kind needs a template the repository writes.

## What would reverse it

- No repository declares a kind within a year of the release that ships
  this, which would show the need was foreseen and not felt.

## Consequences

`paw check` reads `[record.kinds]`. ADR-2370's key table gains it. The task
template gains `produces:` and the declared kinds' templates gain
`prompted-by:`.

## How I will know it was realised

1. A fixture repository declares a kind with prefix `NAR`, and `paw check`
   checks a `NAR-0001` file's front matter like a built-in kind's (REQ-0666,
   REQ-0670).
2. A declaration with no template fails `paw check` (REQ-0668).
3. A task with `produces:` whose artifact lacks `prompted-by:` fails
   (REQ-0662).

## What this does not settle

- A generated index for a declared kind.
