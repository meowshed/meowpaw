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
documentation, and the review step's file carries two on what the review
reads. Each is a labelled rule, as ADR-1160 decided for every step, and none
names a language or a tool.

The document step:

- names each page's kind before writing it, from the six kinds SPC-1110
  lists, and keeps to one kind per page (REQ-1950, REQ-1952);
- gives a how-to guide no justification, linking the explanation or the
  decision instead (REQ-1954);
- organises pages around what the reader is trying to do, and never around
  the source tree (REQ-1958);
- opens the repository's introduction with what the project is, followed by a
  quick start, with no promotional material (REQ-1960);
- takes reference for a public interface from the repository's verbs where one
  of them generates it, and where none does, reports the reference as written
  by hand and unchecked against the interface (REQ-1956);
- writes to the documentation style the repository declares as
  `[docs] style` in `.meowpaw/profile.toml`, either a path to its own style
  guide or the name of an installed unit that ships one (REQ-1962);
- says so where the repository declares no style, and writes to the writing
  standard in force (REQ-1962);
- edits documentation written for the project's users and never the epic, its
  tasks or any other record (REQ-1964);
- runs the repository's verbs after editing, reports which verb checked the
  documentation it changed, and reports that documentation as unchecked where
  no verb covers it, never running a check of its own (REQ-0287, REQ-0289);
- runs every example it writes or changes, as written, and marks one it
  couldn't run as not run (REQ-2836).

The review step:

- follows a changed quick start from an empty directory, and where it can't,
  reports that it read the quick start and didn't run it (REQ-2834);
- judges each changed page against the kind it names, reporting a page that
  serves two kinds or a how-to that justifies itself as a finding.

`meow-method` reads nothing new: the model running the step reads the
`[docs]` table from the profile it already reads for the verbs.

After this decision a repository running the document step gets pages of one
kind each, written to its declared style, with examples that ran and a report
naming the verb that checked them. What still doesn't work: no program checks
that a page keeps to one kind or that a how-to carries no justification,
which the review step judges. A repository with no documentation verb gets
its documentation reported as unchecked.

## Why

The document step today carries three rules: bring the documentation into
agreement with the epic, report what was left alone, and don't report an epic
finished while stale pages are published. The step says nothing about what a
repository's documentation must be, so a model running it writes whatever it
would write anyway.

The four kinds of tutorial, how-to, reference and explanation come from
Diátaxis, and the introduction and troubleshooting page from the Good Docs
Project's core set (RES-0020, RES-0269). The rule against mixing them comes
from what happens when they mix: a reference that editorialises fails the
reader looking something up, and a tutorial that explains architecture fails
the reader learning a first task (RES-0020). The step names the kind first,
because the kind decides the page's shape, and choosing it afterwards means
rewriting.

A documentation check runs as one of the five verbs, because RES-0020 found
that documentation held by the same checks as the code turns drift into a
failing check, and because the verbs already report an unresolved check as
unresolved. A repository that checks its links in its `lint` verb gets them
checked by the document step with no new command. The step never runs a
check of its own, because a check the repository didn't declare is a command
the harness guessed, which the constitution forbids.

Reference generated from the documentation comments on an interface can't
drift from the interface (RES-0020). Which generator produces it is language
knowledge, which belongs in a pack (REQ-0072), so the step takes reference
from whichever verb the repository runs it through, and reports reference
written by hand as unchecked against the interface.

The strongest objection: most of these rules can't be checked by a program,
so they rest on the model following a step file, which ADR-1050 found works
only when the obligation is in front of it. The `method` skill reads the
step's file before the step writes anything, so the obligation is in front of
the model when it writes. Whether a page keeps to one kind needs a reader, so
the review step judges it and declares the result as a judgement (REQ-0147).

## Alternatives

| Option                                           | Better at                                               | Why it lost                                                                                                               |
| ------------------------------------------------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                       | The step stays three rules long                         | A repository's documentation gets no kind, no style and no check from the step that writes it                             |
| Rules in the step file, checks through the verbs | No new program, and documentation fails as code does    | Chosen                                                                                                                    |
| A documentation checker shipped by `meow-method` | One command checks links and examples in any repository | It would guess what an example needs to run and which links matter, and it would be a sixth check beside the five verbs   |
| Front matter naming the kind, checked by `paw`   | A program could check that the kind was named           | It imposes the harness's own front matter on a repository's documentation, which the repository never asked for           |
| A profile key naming the reference generator     | The step would know the generator without a verb        | A generator is a command, and commands already resolve through the verbs, so a second place would disagree with the first |

## What it costs

The document step's file grows by the rules above, which the step loads only
when it runs, and the review step's by two. A repository that wants its
reference generated or its documentation checked declares a verb it might not
have today. Following a quick start in an empty directory costs the review
whatever the quick start installs.

## What would reverse it

- A run of the document step over a case set, with the rules and without
  them, scores the same on Sonnet 5 and Opus 5.5, which would show the rules
  don't change what the step writes.

## Consequences

- `plugins/meow-method/skills/method/steps/document.md` and
  `plugins/meow-method/skills/method/steps/review.md` carry the new rules.
- `.meowpaw/profile.toml` can carry `[docs] style`, and this repository
  declares its own.
- SPC-1090 states the document step's obligations and the `[docs] style`
  declaration.

## How I will know it was realised

1. Each requirement ADR-1380 addresses is carried by a labelled rule in
   `steps/document.md` or `steps/review.md`, traced in the evidence of the
   task that closes it, and no rule names a requirement, a language or a
   tool.
2. The `prompts` check passes on both step files.
3. This repository's profile declares `[docs] style`, and the document step,
   run on the epic that realises this decision, reports the verb that checked
   its documentation.
4. Every requirement ADR-1380 addresses lands in exactly one closed task.

## What this does not settle

- Which generator produces reference for which language, which is a pack's.
- A program that checks one kind per page.
- The files a public repository owes a newcomer.
