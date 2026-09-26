---
id: ADR-1290
artifact: adr
status: draft
revised: 2026-09-26
addresses:
  [REQ-2556, REQ-2558, REQ-2560, REQ-2564, REQ-2826, REQ-2832, REQ-2906]
supersedes: []
---

# 1290. A GitHub pack reads a repository's history, and writes nothing

## Decision

The harness gains a pack, `meow-github`, whose program reads a GitHub
repository's history as structured data and changes nothing on the forge.
`meow-github history [<owner>/<name>]` prints one JSON document holding:

- every issue and pull request, with its number, title, body, state, author,
  address and labels, and for a pull request whether it was merged;
- every conversation comment and every review comment, with the issue or pull
  request it belongs to.

It reads through `gh api`, the interface beneath GitHub's own client, with
`--paginate --slurp` so every page is read, and `--cache 1h` so a repeated
read costs no quota. It takes each field it prints from the response by name,
and a field the response lacks fails by that name. Where `gh` is missing, not
signed in, or refuses a read, it reports the history as unread, names the
listing that failed and what would supply it, and prints no partial document
as if it were whole.

The pack is a unit like the others: it installs alone, its program ships in
its `bin/` for each of the six targets, and it's on the Bash tool's `PATH`
while installed.

After this decision a person, or a step, can read a repository's whole
GitHub history in one command. What still doesn't work: onboarding doesn't
read it yet, which a later decision takes, and the pack projects nothing onto the
tracker.

## Why

RES-0277 found that a repository's issues and pull requests state what its
code can't, and that the whole history of this repository read in 6 requests
of 5,000. It found the listings, `merged_at` telling a merged pull request
from a rejected one, and `gh api --paginate`, `--slurp` and `--cache`. RES-0023
found that a plugin's `bin/` is on the Bash tool's `PATH`, so another unit
runs the program by its name and never by a path into this one. The method
names no forge, so this knowledge lives in a pack.

The strongest objection: shelling out to `gh` makes the pack depend on a tool
the person must install and sign in to. It does, and in exchange the pack
never handles a credential, and a person who can read the repository in `gh`
can read it here; a missing `gh` is reported with what would supply it.

## Alternatives

| Option                            | Better at                              | Why it lost                                                     |
| --------------------------------- | -------------------------------------- | --------------------------------------------------------------- |
| A pack reading through `gh api`   | No credential handled, structured data | Chosen                                                          |
| An HTTP client in the native tool | No external tool                       | The pack would store and send a credential, and grow the binary |
| Reading `gh issue list` output    | Shorter                                | Output meant for a person, which REQ-2558 forbids parsing       |
| Do nothing                        | Costs nothing                          | Onboarding can't read what the history states                   |

## What it costs

A unit with a launcher, a feature in the native tool, a docs page, and a
marketplace entry.

## What would reverse it

- A second forge arrives, and the history's shape moves into a contract both
  packs print.

## Consequences

- `meow-github history` prints a repository's whole history as JSON.
- The marketplace lists `meow-github`.

## How I will know it was realised

1. Fixtures with a stand-in `gh` show `history` printing issues, pull requests
   with `merged`, and both kinds of comment, reading every page, requesting
   the cache, and failing by name on a missing field.
2. A fixture shows a refused read reported as unread, naming the listing,
   with no document printed.
3. `meow-github` installs alone: `check_standalone.py` passes, and its
   launcher runs its binary.
4. Every requirement ADR-1290 addresses lands in exactly one closed task.

## What this does not settle

- Onboarding reading the history, which a later decision takes.
- Projecting the record onto a tracker.
