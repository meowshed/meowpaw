---
id: ADR-1380
artifact: adr
status: approved
revised: 2026-09-27
addresses:
  [
    REQ-0287,
    REQ-0289,
    REQ-1950,
    REQ-1952,
    REQ-1954,
    REQ-1956,
    REQ-1958,
    REQ-1960,
    REQ-1962,
    REQ-1964,
    REQ-2834,
    REQ-2836,
  ]
supersedes: []
---

# 1380. The document step writes one kind per page to the declared style, and checks documentation through the verbs

## Decision

The document step's file carries the obligations on a repository's own
documentation, and the review step's file carries the one on its quick start.
Each is a labelled rule, as ADR-1160 decided for every step, and none names a
language or a tool.

The document step:

1. names each page's kind before writing it, from the six SPC-1110 lists, and
   keeps to one kind per page (REQ-1950, REQ-1952);
2. gives a how-to guide no justification, linking the explanation or the
   decision instead (REQ-1954);
3. organises pages around what the reader is trying to do, and never around
   the source tree (REQ-1958);
4. opens the repository's introduction with what the project is, followed by a
   quick start, with no promotional material (REQ-1960);
5. writes reference for a public interface from the generator the repository
   declares, and where none is declared, reports the reference as written by
   hand and unchecked against the interface (REQ-1956);
6. writes to the documentation style the repository declares as
   `[docs] style` in `.meowpaw/profile.toml`, either a path to its own style
   guide or the name of an installed unit that ships one, and where none is
   declared, says so and uses the writing standard in force (REQ-1962);
7. edits documentation written for the project's users and never the epic,
   its tasks or any other record (REQ-1964);
8. runs the repository's verbs after editing, reports which verb covers the
   documentation, and reports the documentation as unchecked where no verb
   does, never running a check of its own (REQ-0287, REQ-0289);
9. runs every example it writes or changes, as written, and marks one it
   couldn't run as not run (REQ-2836).

The review step follows a changed quick start from an empty directory, and
where it can't, reports that it read the quick start and didn't run it
(REQ-2834).

`meow-method` reads nothing new: the `[docs]` table is read by the model that
runs the step, from the profile it already reads for the verbs.

After this decision a repository running the document step gets pages of one
kind each, written to its declared style, with examples that ran and a report
naming the verb that checked them. What still doesn't work: no program checks
that a page keeps to one kind or that a how-to carries no justification,
which the review step holds, and a repository with no documentation verb gets
documentation reported as unchecked, not checked.

## Why

The document step today carries three rules: bring the documentation into
agreement with the epic, report what was left alone, and don't report an epic
finished while stale pages are published. Everything a repository's
documentation must be is missing from it, so a model running the step writes
to whatever it would write anyway.

The kinds come from Diátaxis, and the rule against mixing them comes from what
happens when they mix: a reference that editorialises and a tutorial that
explains architecture each fail both readers (RES-0020). The step names the
kind first because the kind decides the page's shape, and choosing it
afterwards means rewriting.

A documentation check runs as one of the five verbs because documentation
that fails differently from code gets ignored differently (RES-0020), and
because the verbs already report an unresolved check as unresolved. A
repository that checks its links in its `lint` verb gets them checked by the
document step with no new mechanism. The step never runs a check of its own,
because a check the repository didn't declare is a command the harness
guessed, which the constitution forbids.

Reference generated from the documentation comments on an interface can't
drift from the interface (RES-0020). Which generator produces it is language
knowledge, which belongs in a pack (REQ-0072), so the step asks the
repository which one it declared and reports hand-written reference as
unchecked where it declared none.

The strongest objection: most of these rules can't be checked by a program,
so they rest on the model following a step file, which ADR-1050 found works
only when the obligation is in front of it. The rules are in the step's own
file, which `paw ready` gates before the step runs, so the obligation is in
front of it. Whether a page keeps to one kind needs a reader, and the review
step is that reader (REQ-0147).

## Alternatives

| Option                                           | Better at                                               | Why it lost                                                                                                            |
| ------------------------------------------------ | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                       | The step stays three rules long                         | A repository's documentation gets no kind, no style and no check from the step that writes it                          |
| Rules in the step file, checks through the verbs | No new program, and documentation fails as code does    | Chosen                                                                                                                 |
| A documentation checker shipped by `meow-method` | One command checks links and examples in any repository | It would guess what an example needs to run and which links matter, and it would be a sixth mechanism beside the verbs |
| Front matter naming the kind, checked by `paw`   | A program could check that the kind was named           | It imposes the harness's own front matter on a repository's documentation, which the repository never asked for        |

## What it costs

The document step's file grows by nine rules, which the step loads only when
it runs. The review step grows by one. A repository that wants its reference
generated or its documentation checked declares a verb or a generator it may
not have today. A quick start followed in an empty directory costs the review
a few minutes and whatever the quick start installs.

## What would reverse it

- The step's rules measurably fail to change what the step writes: a run of
  the document step over a case set, with the rules and without them, scoring
  the same on both models.
- A pack arrives that generates reference for its language, making the
  generator a pack's business and the profile key unnecessary for that
  language.

## Consequences

- `steps/document.md` carries nine new rules, and `steps/review.md` one.
- `.meowpaw/profile.toml` may carry `[docs] style`, and this repository
  declares its own.
- SPC-1090 states the document step's obligations, and SPC-1110 the
  repository's declared style.

## How I will know it was realised

1. Each requirement ADR-1380 addresses is carried by a labelled rule in
   `steps/document.md` or `steps/review.md`, traced in the task's evidence,
   and no rule names a requirement, a language or a tool.
2. The prompt check passes on both step files.
3. This repository's profile declares `[docs] style`, and the document step,
   run on the epic that realises this decision, reports the verb that checked
   its documentation.
4. Every requirement ADR-1380 addresses lands in exactly one closed task.

## What this does not settle

- Which generator produces reference for which language, which is a pack's.
- A program that checks one kind per page.
- The files a public repository owes a newcomer.
