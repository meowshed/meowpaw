---
id: ADR-2720
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-2992]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2720. The interface reference page is generated from documentation comments, and checked against the tool

## Decision

This amends ADR-2490 to follow REQ-1956, which is closed and in force:
reference material for a public interface is generated from the
documentation comments on it, never written by hand. The page ADR-2490
places under `docs/` stays the one declaration of the public interface, and
it names the same six parts REQ-2992 lists. What changes is where its text
comes from.

The native tool generates the page from the documentation comments on what
it already parses and reads: each subcommand, each verb and its outcomes,
each artifact kind and its front matter fields, the record's paths and
identifier formats, each key in the profile's table of keys, and the form of
a piece of evidence. Each entry's reason is the comment on its item, so the
page carries the reason ADR-2490 wanted without a hand-written copy of it.
The generated page is committed, and a test in the crate generates it again
and fails where the committed page differs, so an entry the tool gains or
loses fails the gate until the page is regenerated.

ADR-2490 named "the document step" as the writer of the page. That step is
retired, so the task that builds the generator writes the page, and every
later change regenerates it in its own pull request. The rest of ADR-2490
stands: one page, a change to an entry is a change to the interface, and a
removed or renamed entry is marked breaking. ADR-2490's file stays as it was
approved, and no requirement is withdrawn.

Once this is accepted, the interface page can't drift from the tool, and
REQ-2992 and REQ-1956 are held by one test. What still doesn't work: an item
whose comment is missing or empty generates an entry with no reason, so the
test also fails an entry with no comment.

## Why

REQ-1956 elaborates RES-0020 and RES-0054, which found that reference
material written by hand drifts from the interface it describes, and that
the comment beside the code is the copy a change reaches. ADR-2490 chose a
hand-written page held by a test, which meets REQ-2992 and breaks REQ-1956.
Generating the page from comments keeps the test ADR-2490 asked for and the
reasons it wanted on the page, and RES-0264's point stands: the interface
has one place where anyone can read it.

## Alternatives

| Option                                    | Better at                                 | Why it lost                                                             |
| ----------------------------------------- | ----------------------------------------- | ----------------------------------------------------------------------- |
| Generate from comments, test the page     | It can't drift, and each entry has reason | Chosen                                                                  |
| Do nothing                                | No generator to build                     | ADR-2490's hand-written page breaks REQ-1956, which is in force         |
| Generate it in the release, not commit it | No generated file in the tree             | A reviewer then can't see a change to the interface in the pull request |

## What it costs

The crate gains a generator and a test, and each item on the interface needs
a documentation comment that reads as a reason. A change to an entry
regenerates the page in the same pull request, or the test fails.

## What would reverse it

- REQ-1956 is withdrawn, which would leave ADR-2490's hand-written page
  meeting every requirement in force.

## Consequences

SPC-1110 states the page as generated, and SPC-1080 states the generator and
its test. The task realising ADR-2490 builds the generator and commits the
first page.

## How I will know it was realised

1. The page exists under `docs/`, names each of the six parts REQ-2992 lists,
   and is the generator's output byte for byte.
2. Adding a subcommand with a documentation comment and without regenerating
   the page fails the crate's tests.
3. Adding a profile key with no documentation comment fails the crate's tests.

## What this does not settle

- When the harness leaves major version zero, which ADR-2490 leaves open.
- The page's layout beyond the six parts, which the task chooses.
