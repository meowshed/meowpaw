---
id: ADR-2490
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-2992]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2490. The public interface is one reference page that a check holds to the tool

## Decision

The harness declares its public interface on one reference page under
`docs/`. It names the five verbs and their outcomes, the artifact kinds and
their front matter, the record's paths and identifier formats, the profile's
keys, every subcommand of the native tool and the form of a piece of evidence
(REQ-2992). A change to anything on that page is a change to the interface,
and its commit is marked breaking where it removes or renames an entry.

A test in the crate reads the page and compares it with what the tool knows:
the verbs it resolves, the kinds it checks, the subcommands it parses and the
profile keys in the table ADR-2370 created. It fails where the two differ.

Once this is accepted, "is this part of the interface" has one answer, and
the release step can tell a breaking change from one that isn't. What still
doesn't work: the skills' wording isn't part of the interface, so a change to
how a skill reads breaks nothing on the page.

## Why

RES-0264 found that semantic versioning means nothing until a project says
what its public interface is, because a major version can't be bumped for a
break nobody can name. ADR-2480 keeps the harness at major version zero until
the interface stops moving, and the page is how anyone can tell it has.

## Alternatives

| Option                           | Better at               | Why it lost                                                    |
| -------------------------------- | ----------------------- | -------------------------------------------------------------- |
| Do nothing                       | No page to keep         | No release can tell whether a change breaks anything           |
| Generate the page from the tool  | It can't drift          | The page needs the reason for each entry, which the tool lacks |
| Declare it in each unit's README | Each unit owns its part | The interface crosses units, and the parts never meet          |

## What it costs

Each change to a verb, kind, key or subcommand edits the page in the same pull
request, or the test fails.

## What would reverse it

- The test finds the page out of date in more than one release in a row,
  which would show the page should be generated.

## Consequences

The document step writes the page. The crate gains the test. SPC-1080 cites
the page.

## How I will know it was realised

1. The page exists under `docs/` and names each of the six parts REQ-2992
   lists.
2. Adding a subcommand without an entry on the page fails the crate's tests.

## What this does not settle

- When the harness leaves major version zero.
