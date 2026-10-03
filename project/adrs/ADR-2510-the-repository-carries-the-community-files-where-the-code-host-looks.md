---
id: ADR-2510
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-2214, REQ-2216]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2510. The repository carries the community files where the code host looks

## Decision

This repository carries `CONTRIBUTING.md`, `SECURITY.md`,
`CODE_OF_CONDUCT.md`, `CODEOWNERS`, an issue template and a pull request
template (REQ-2214). Each sits under `.github/`, where GitHub reads it, and
not where it would read well (REQ-2216). `CONTRIBUTING.md` points at
`CLAUDE.md` for the rules and repeats none of them, because CLAUDE.md is the
only instruction file and a second copy drifts.

`tools/` gains a check, run by the `test` verb, that fails when one of the six
files is missing from `.github/`.

Once this is accepted, a newcomer finds how to contribute and how to report a
vulnerability where GitHub shows them. What still doesn't work: the harness
doesn't write these files into another repository. That is a later decision
if a repository asks for it.

## Why

RES-0066 concluded that a public repository carries a fixed set of files for
people who arrive later, code owners among them, in the place the platform
looks. Without a security policy, a vulnerability has no private route and
arrives as a public issue. Today `.github/` holds only `allowed_signers` and
the workflows.

## Alternatives

| Option                           | Better at                   | Why it lost                                                           |
| -------------------------------- | --------------------------- | --------------------------------------------------------------------- |
| Do nothing                       | No files to keep            | A vulnerability report arrives as a public issue                      |
| Put them at the root             | Visible in a directory list | REQ-2216 asks for the place the platform looks, and `.github/` is one |
| A unit that writes them anywhere | Every repository gets them  | No repository has asked, and the rules differ per project             |

## What it costs

Six files to keep current, and the security policy names an address the owner
has to watch.

## What would reverse it

- The code host stops reading community files from `.github/`.

## Consequences

The six files land under `.github/`. A `tools/` check holds their presence.

## How I will know it was realised

1. The check fails when any of the six files is removed from `.github/`
   (REQ-2214, REQ-2216).
2. GitHub's community profile for the repository lists each file as present.

## What this does not settle

- What the security policy promises about response time.
