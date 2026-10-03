---
id: ADR-2640
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-0070,
    REQ-0072,
    REQ-0080,
    REQ-0082,
    REQ-0084,
    REQ-0085,
    REQ-0086,
    REQ-0088,
    REQ-3050,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2640. A check holds the method to naming no language, and every pack stays optional

## Decision

`tools/` gains a check, run by the `test` verb, that reads every prompt,
template and page in the kernel, method and practice units and fails on a
programming language, a framework, a build tool, a package manager or a file
extension from its word list (REQ-0070). The units it reads are listed in the
check, beside the kernel list `tools/check_kernel.py` keeps, because the
catalogue isn't decided and no manifest field names a unit's layer. A unit's
own program is exempt, as ADR-1070 says, and a code sample in a fenced block
that shows a pack's output is exempt where the fence's info string names it.
CLAUDE.md's `the_method_names_no_language` says no check enforces the rule,
and this decision turns that sentence false, so the change that lands the
check also rewrites the sentence.

Knowledge of a language, a platform or a tool lives in a pack a repository
may leave out, and the tools the harness itself uses, such as `git`, `gh` and
`mise`, live in packs of the same kind (REQ-0072, REQ-0084). No step, gate or
obligation needs a pack: the method finishes with none installed, and a
missing pack's capability is reported as unresolved (REQ-0086, REQ-0088). A
pack states the toolchain versions it is current as of, in its README
(REQ-0085), and may write and amend its tool's configuration to the
project's conventions, which the mise and Markdown packs already print for a
person to commit (REQ-0082). Work that isn't code, a specification, a
document, a decision or a configuration, goes through the same steps and
gates (REQ-0080), which this repository already does for its record.

A unit's description leads with the words a request would contain
(REQ-3050), and `meow-author check`'s description rule, which ADR-1050
decided, gains that test.

Once this is accepted, the oldest unenforced rule in CLAUDE.md has a check.
What still doesn't work: the word list catches the names it holds, so a new
language name passes until it joins the list.

## Why

RES-0006 and RES-0001 found that a method written with one language in mind
fails the repository in another, and that only a pack a repository can omit
keeps language knowledge out of the method. RES-0023 found that a method which
assumes a tool is present breaks where it is missing. CLAUDE.md states that
review holds REQ-0070 and calls that weaker.

## Alternatives

| Option                     | Better at                  | Why it lost                                                |
| -------------------------- | -------------------------- | ---------------------------------------------------------- |
| Do nothing                 | No check to keep           | CLAUDE.md keeps saying no check enforces the rule          |
| A model reads for the rule | Catches names off the list | A model call in the gate is what the owner keeps out of CI |
| A layer field per unit     | The check needs no list    | The catalogue isn't decided, so the field would be guessed |

## What it costs

The word list needs an entry for each new language or tool, and an exempt
fence has to name itself.

## What would reverse it

- The check reports a false positive in more than one pull request a month,
  which would show the word list is too broad to keep.

## Consequences

`tools/` gains the check, joined to the `test` verb. CLAUDE.md's sentence
changes in the same pull request. Each pack's README states its toolchain
versions.

## How I will know it was realised

1. The check fails a fixture method prompt that names a language from the
   list (REQ-0070).
2. The method's steps run on a fixture repository with no pack installed and
   report each verb as unresolved (REQ-0088).
3. Each pack's README states the versions it is current as of (REQ-0085).

## What this does not settle

- Which units are kernel, method and practice. The check lists them, and the
  catalogue decision would replace the list.
