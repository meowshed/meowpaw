---
id: RES-0111
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0005
---

# Markdown

## Summary

Markdown is the only language here where the checkable part and the part that
matters barely overlap: a document can pass every rule and say nothing. No
single Markdown exists, so the target renderer is part of the contract. One
tool crosses into prose and is careful about what it claims: consistency
against a declared style, and never whether the writing is good. That is the
same division this method already draws, arrived at here from a tool.

Research for one supported language, and the one every repository contains. A
toolchain is a set of tools, and this one splits along a line the other
languages do not have: some of these tools check the document's structure, and
one of them checks its prose.

It covers what the verbs mean for prose, what a linter settles and what it
cannot, and why the renderer is part of the language. It also covers how a
diagram is checked, what the pack authors, and what the skill has to contain.

It does not cover the writing standard the prose is held to, which is
[RES-0027-prose.md](RES-0027-prose.md), nor what every toolchain document
shares, which is [RES-0006-toolchains.md](RES-0006-toolchains.md).

## The question

Markdown is the language this corpus is written in, so getting it wrong shows
here before anywhere else. It is also the only language where the checkable
part and the part that matters barely overlap: a document can pass every rule
and say nothing.

So the question is what the verbs are honestly for, and what the one tool that
reaches further can and cannot do.

## Method

We fetched and read the tools' own documentation on 2026-09-20. The structural
linter's repository gave its configuration behaviour, and the prose linter's
documentation gave what it claims and what it declines to claim. The link
checker's page and the diagram validator's repository supplied the rest.

The prose linter's statement that it is not a general writing aid is quoted in
full, because it is the boundary the conclusions rest on.

One search was used to find how these tools are combined in practice. Nothing
was installed or run.

## Findings

### No single Markdown exists, and the renderer decides which one this is

A document renders differently on a forge, in a static site generator and in a
note-taking application. They disagree about front matter, admonitions,
footnotes and diagram blocks: a fenced `mermaid` block is a picture in one and
a code listing in another.

So the target renderer is part of the document's contract, and a check that
does not know it is checking a dialect nobody uses. This is the same shape as
the Scheme implementation problem, in a language nobody thinks of as having
implementations.

### The toolchain, tool by tool

| Role      | Tool                                     | What it checks                                             |
| --------- | ---------------------------------------- | ---------------------------------------------------------- |
| Format    | `prettier`, `mdformat`                   | The canonical form                                         |
| Structure | `markdownlint-cli2`                      | The MD0xx rule set: headings, lists, fences, line length   |
| Structure | `remark-lint`, `textlint`                | The same territory through different plugin ecosystems     |
| Prose     | `vale`                                   | Style rules over the prose, with markup understood         |
| Spelling  | `codespell`, `typos`, `cspell`           | Misspellings, against a dictionary and a project word list |
| Links     | `lychee`                                 | Whether the links resolve                                  |
| Diagrams  | `mermaid-lint`                           | Whether a fenced diagram parses                            |
| Build     | `mkdocs`, `mdbook`, `hugo`, `docusaurus` | Whether the site builds                                    |

### The linter is configuration-driven, and the configuration is the interesting part

`markdownlint-cli2` is described by its own repository as a fast, flexible,
configuration-based interface to the markdownlint library. It reads
`.markdownlint-cli2.jsonc` natively, where the earlier `markdownlint-cli`
ignores the commented JSON form. That is a real trap: a repository that
configured the newer tool and runs the older one in continuous integration is
running with no configuration, and nothing tells it.

The configuration covers rules, severity, globs, output formats, per-path
overrides and whether `.gitignore` is honoured.

The rules it ships are structural: heading increments, list indentation,
duplicate headings, missing language tags on fences, line length. Every one is
a true mechanical property, and none is about whether the document is any good.

The document states that split, and assumes none of it. A Markdown `lint` verb
checks the structure of the document; a review checks the document.

### One tool crosses into prose, and it is careful about what it claims

Vale is the exception and deserves the space, because it is the closest
published thing to what this project's own writing standard does mechanically.

It is a command-line tool that applies code-like linting to prose, and it is
explicit that it is _not_ a general writing aid. It focuses on _"ensuring
consistency across multiple authors (according to customizable guidelines)"_
and never on correctness, which is what separates it from a grammar checker.

Two properties keep it usable, where a prose linter is usually noisy. It is
syntax- and context-aware: it assigns scopes to regions - headings, links, list
items, code blocks - and _"block and inline code are ignored by default"_. And
its rules are data, written in YAML, so a project's own standard can be
expressed rather than approximated by somebody else's.

The limit is the one the tool states about itself. Consistency is checkable;
whether the prose is good is not, and a style linter that claimed otherwise
would produce findings nobody should act on. That is the same division this
method already draws between the mechanical half of a writing standard and the
half that is a review criterion, arrived at here from a tool.

### Links and spelling reach outside the file, which changes which verb they are

`lychee` is a fast asynchronous link checker written in Rust, covering Markdown
and HTML and reporting broken hyperlinks and mail addresses. `codespell`,
`typos` and `cspell` cover misspellings against a dictionary plus a project
word list.

Link checking is unusual among checks in that it can fail for reasons outside
the repository. A link to a site that is down is a failing check and no defect
in the document. So the offline behaviour, the retry policy and the cached
result are part of what a pack configures, and no afterthought.

Spelling has the opposite problem: the project word list _is_ the
configuration, and a spell check with no word list produces findings on every
proper noun in the repository.

### A diagram is content and can be checked

Plain Markdown linters do not validate a diagram's body - to them a fenced
block is an opaque region. `mermaid-lint` closes that by parsing the diagram
with the official parser and plugging into the linters already running:
markdownlint, remark and textlint each gain the rule.

That makes a broken diagram a lint failure beside the others, and nobody
discovers it when the page renders. It is the mechanism that lets the diagram
decision hold: a diagram that fails to parse is a failing check rather than a
rendering curiosity.

### The verbs

| Verb        | Command                                                               |
| ----------- | --------------------------------------------------------------------- |
| `fmt`       | `prettier --write` on `*.md`, else `mdformat`                         |
| `lint`      | `markdownlint-cli2`, plus `vale` where the project configures a style |
| `typecheck` | unresolved - prose has no types                                       |
| `test`      | a link check such as `lychee`, and a spell check such as `codespell`  |
| `build`     | the site generator where one exists, otherwise unresolved             |

The link check sits under `test`, and never under `lint`, which is deliberate.
`lint` reads the file; `test` reaches the network and can fail for reasons the
author did not cause, and those belong in different reports.

### What the pack authors

`.markdownlint-cli2.jsonc` with the rule set and the per-path overrides. A
`.vale.ini` and a style directory where the project has a writing standard. A
project word list for the spell checker, and a link-checker configuration with
the exclusions and the cache policy.

The word list is the one a pack maintains continuously, and never writes once.
Every new proper noun in the repository is a new entry, and a spell check
nobody maintains is one somebody disables.

### What a reviewer needs that no command reports

Heading hierarchy as the document's real structure - the linter checks that
levels increment and cannot tell whether the resulting outline is the
document's argument.

Tables against lists, which is a question about what the reader is comparing.

Code fences with a language tag, which the linter checks, and the _right_
language tag, which it does not.

Reference links for anything cited more than twice, so the prose stays readable
in its source form.

Relative links that survive a file being moved, which is a property of the link
style, and the target has nothing to do with it.

Whether a diagram asserts something the prose does not, which is the one thing
`mermaid-lint` cannot ask.

### What the skill has to contain

In the body, in this order:

1. The renderer, first. Which target this repository's Markdown is for, and
   what that decides about front matter, admonitions and diagrams.
2. Verb resolution, with the link and spell checks placed under `test` and
   the reason given.
3. What the linter does not check. Structure is not quality, and a clean
   lint is never offered as evidence that a document is good.
4. Where prose linting stops. Vale checks consistency against a declared
   style; it does not check whether the writing is good, and the report says
   which of the two ran.
5. What must never happen. Running `markdownlint-cli` against a
   `.markdownlint-cli2.jsonc`. Failing a build on an unreachable link without
   saying it was unreachable. Reporting a spell check with no project word list
   as meaningful.

In supporting files: the tool inventory; configuration templates for the
linter, Vale and the link checker; the diagram-validation wiring; the
reviewer's knowledge; and the dated facts with what to re-check.

## Conclusions

1. The target renderer is declared, because front matter, admonitions,
   footnotes and diagram blocks differ between them and a check without a
   target is checking a dialect nobody uses. 2. `lint` resolves to
   `markdownlint-cli2`, reading `.markdownlint-cli2.jsonc`, which the earlier
   command-line tool does not. 3. A repository configured for the newer tool
   and checked with the older one is reported, since the configuration is
   silently ignored and the run looks clean. 4. What the linter checks is
   structure, and it is reported as structure, so a clean lint is never offered
   as evidence that the document is good. 5. Prose linting is a separate tool
   with a narrower claim. Vale checks consistency against a declared style,
   understands markup well enough to skip code, and does not claim to judge
   writing. 6. A style is expressed as rules, where borrowing somebody else's
   only approximates it, since the rules are data and a project's own standard
   can be written down. 7. The report says which kind of check ran - structure,
   style, spelling, links - because they answer different questions and a
   single pass or fail hides which one. 8. The link check and the spell check
   are `test`, and never `lint`, because they reach outside the file and can
   fail for reasons the author did not cause. 9. A check that can fail for an
   external reason declares its offline behaviour, retries and cache, since a
   link to a site that is down is not a defect in the document. 10. A spell
   check without a project word list is not run, because it produces a finding
   for every proper noun and is disabled within a week. 11. A fenced diagram is
   parsed as part of the lint, through a rule that plugs into the Markdown
   linter, so a broken diagram fails a check rather than surfacing when the
   page renders. 12. `typecheck` is unresolved because the language has no
   types, and no tool is missing. 13. `build` is the site generator where one
   exists and unresolved otherwise, and is never guessed. 14. The reviewer's
   knowledge is recorded with the pack: whether the heading outline is the
   argument, tables against lists, the right language tag, where any tag
   satisfies the linter, reference links for repeated citations, link styles
   that survive a move, and whether a diagram asserts what the prose does not. 15. The skill body carries the renderer, verb resolution, the limits of the
   structural linter, the limits of the prose linter, and the prohibitions, in
   that order.

## Sources

All read 2026-09-20.

- [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) - a
  fast, flexible, configuration-based interface to the markdownlint library;
  native reading of `.markdownlint-cli2.jsonc` where `markdownlint-cli` ignores
  the commented form; and configuration covering rules, severity, globs, output
  formats, per-path overrides and whether `.gitignore` is honoured. - [Vale
  documentation](https://docs.vale.sh/) - a command-line tool applying
  code-like linting to prose; its explicit position that it is not a general
  writing aid and aims at consistency across multiple authors according to
  customisable guidelines, and never at correctness; syntax- and context-aware
  scoping over headings, links, list items and code blocks, with block and
  inline code ignored by default; and custom rules written in YAML. -
  [lychee](https://lychee.cli.rs/) - a fast asynchronous link checker written
  in Rust, covering Markdown and HTML and reporting broken hyperlinks and mail
  addresses. - [mermaid-lint](https://github.com/jasonworden/mermaid-lint) -
  validating Mermaid diagram bodies with the official parser, and plugging into
  markdownlint, remark and textlint so a broken diagram appears beside the
  existing Markdown lint failures, and never at render time. - [Creating
  diagrams on
  GitHub](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)
  - the syntaxes one renderer treats as pictures, read here as evidence that
    the same fenced block is a diagram in one target and a code listing in
    another.
