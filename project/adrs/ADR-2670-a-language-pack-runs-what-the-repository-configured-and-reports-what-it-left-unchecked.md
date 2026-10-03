---
id: ADR-2670
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-2410,
    REQ-2412,
    REQ-2414,
    REQ-2416,
    REQ-2418,
    REQ-2420,
    REQ-2422,
    REQ-2426,
    REQ-2428,
    REQ-2430,
    REQ-2432,
    REQ-2436,
    REQ-2440,
    REQ-2442,
    REQ-2444,
    REQ-2446,
    REQ-2448,
    REQ-2450,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2670. A language pack runs what the repository configured, and reports what it left unchecked

## Decision

SPC-1190 gains these rules for every language pack, so each pack ADR-2660
lists meets them from its first release.

A pack runs what the repository configured, and nothing it chose:

- It binds a verb to the tool the repository configured where several serve
  it, and never picks one itself (REQ-2420).
- It turns on no lint group, strictness or analysis level the repository
  didn't ask for (REQ-2422).
- It runs tools through the environment or package manager the project
  declares (REQ-2426), under the toolchain version the repository pins, and
  reports a difference from what is installed (REQ-2428).
- It detects which host or implementation evaluates the language before it
  binds, and reports every verb unresolved until it has (REQ-2446).
- It performs a build prerequisite that another form of the step does
  implicitly (REQ-2448).

A pack reports what it didn't check:

- Where the bound tool covers less than the ecosystem's default, the pack runs
  the rest or names what is no longer checked (REQ-2410).
- Where the language runs documentation examples as tests, `test` runs them
  (REQ-2412).
- Where the language ships a detector for its most common defect class, such
  as a race detector, `test` turns it on, and a repository turning it off has
  that recorded (REQ-2414).
- A clean report names the rule groups enabled (REQ-2432) and the severity
  level it ran at (REQ-2444).
- A supply-chain check says whether it covers transitive dependencies and
  whether it reports presence or reachability (REQ-2436).

A pack changes nothing it wasn't asked to:

- It never applies a fix its tool marks unsafe (REQ-2430).
- It reports a suggestion to use a newer language feature and applies none
  (REQ-2440).
- It leaves no file in the working tree, and points any default output
  outside it (REQ-2442).

A pack keeps what the run produced:

- It collects results in the ecosystem's machine-readable format where one
  exists, and says the evidence is captured output where none does
  (REQ-2416).
- It asks for files its tool deletes unless asked, and names where it kept
  them (REQ-2418).
- It states which generated files are project state to commit and which are
  cache to ignore (REQ-2450).

Once this is accepted, every language pack has one set of rules to meet, and
a pack's tests hold each one. What still doesn't work: no language pack
except Markdown ships, so the rules bind the packs ADR-2660 orders as each
lands.

## Why

RES-0101 to RES-0110 read each language's toolchain and found the same
failures across them: a faster runner that silently skips documentation
tests, a detector left off by default, a fix applied that the tool called
unsafe, output written into the tree, and a clean report that hides how little
was enabled. Stating the rules once in SPC-1190 keeps the nine packs from
learning them nine times.

## Alternatives

| Option                   | Better at                         | Why it lost                                                            |
| ------------------------ | --------------------------------- | ---------------------------------------------------------------------- |
| Do nothing               | No rules to state                 | Each pack rediscovers the same failures                                |
| Rules per pack only      | Each fits its language exactly    | The common rules then differ by wording and drift apart                |
| Packs pick the best tool | Better defaults for a new project | It changes what the repository checks without asking, against REQ-2420 |

## What it costs

Each pack needs a fixture per rule that applies to its language, which makes
a pack's tests the largest part of its work.

## What would reverse it

- A pack meets every rule and its users still report a check it hid, which
  would show the rules miss a class of failure.

## Consequences

SPC-1190 gains the rules. Each pack's task cites the rules that apply to its
language.

## How I will know it was realised

1. SPC-1190 states each rule with its requirement.
2. The Rust pack's tests include a fixture for documentation tests, a pinned
   toolchain and output kept outside the tree (REQ-2412, REQ-2428,
   REQ-2442).

## What this does not settle

- Which tool each pack binds, which each pack's specification states.
