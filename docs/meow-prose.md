# meow-prose

`meow-prose` holds everything Claude Code writes for you to one writing
standard: documents, commit messages, pull request and issue bodies, review
comments, code comments and replies. It installs on its own and needs no other
part of the `meowpaw` harness.

## What you get

A skill that loads before Claude writes, so the standard shapes the first draft
instead of a rewrite afterwards. It asks for the answer first and the reason
beside it, one term for one thing, sentences a second-language reader can
follow, and the skeleton each kind of document needs. It also lists the shapes
of text to rewrite on sight, such as a bold sentence opening a paragraph or an
opener announcing how many items follow, each with a failing and a corrected
example and the words that find it, in English and in Russian.

Ask Claude to review a text somebody else wrote, and it reports each finding
with its line, what is wrong, the fix and the reason, and rewrites the text
only if you ask.

The standard is British English unless your repository declares another
language. To declare one, add it to `.meowpaw/profile.toml`:

```toml
[prose]
language = "en-US"
```

Claude then writes that language across the repository. A technical term
keeps the spelling its own domain uses, and a quotation keeps its author's
wording, whatever you declare.

## What it costs you

The skill's description sits in context on every turn so that Claude knows when
to load it, which costs 299 characters. Claude loads the skill whenever it
writes, rewrites, edits or reviews prose, a one-line commit message included:
in every writing request measured on Sonnet 5 and Opus 5.5, and on none that
only changes code. On Opus 5.5 it also loads for some answers in chat.

When it loads, its core costs about 4,400 tokens on Sonnet 5 and carries the
rules every text needs, which is all a commit message or a code comment loads.
A document adds the rules for documents, about 950 tokens, and the skeleton for
its type, about 200 to 400. Checking a longer text adds the patterns for its
language: about 3,400 tokens for English and 4,100 for Russian.

## Install it

```bash
claude plugin marketplace add meowshed/meowpaw
claude plugin install meow-prose@meowpaw
```

Check what you got:

```bash
claude plugin details meow-prose@meowpaw
```

## Where the rules come from

The decision is
`project/adrs/ADR-1010-the-writing-standard-ships-as-a-unit-that-reviews-itself.md`,
and the part it creates is specified in
`project/specs/SPC-1010-the-writing-standard.md`. Read the decision for the
alternatives and what would reverse it.
