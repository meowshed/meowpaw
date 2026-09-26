# meow-prose

`meow-prose` holds everything Claude Code writes for you to one writing
standard: documents, commit messages, pull request and issue bodies, review
comments, code comments and replies. It installs on its own and needs no other
part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-prose@meowpaw
```

Check what you got:

```bash
claude plugin details meow-prose@meowpaw
```

The details list one skill, `meow-prose:writing`, and one agent,
`meow-prose:prose`, which the next two sections describe.

## Write to the standard

`meow-prose` ships a skill that loads before Claude Code writes, so the
standard shapes the first draft instead of a rewrite afterwards. It asks for
the answer first and the reason beside it, one term for one thing, sentences a
second-language reader can follow, and the skeleton each kind of document
needs. It also lists the shapes of text to rewrite on sight, such as a bold
sentence opening a paragraph or an opener announcing how many items follow,
each with a failing and a corrected example and the words that find it, in
English and in Russian.

The standard is British English unless your repository declares another
language. To declare one, add it to `.meowpaw/profile.toml`:

```toml
[prose]
language = "en-US"
```

Claude Code then writes that language across the repository. A technical term
keeps the spelling its own domain uses, and a quotation keeps its author's
wording, whatever you declare.

## Review a text

`meow-prose` also ships a reviewer, `meow-prose:prose`. Ask Claude Code to
review a text, or a change with comments in its code, and the reviewer reads it
line by line against the same standard. It reports each finding with its line,
the rule it breaks and the smallest fix, and it edits nothing and blocks
nothing, so you decide what to change. It reads a quotation without judging
it, and on a change to code it reads only the files the change touched.

## Replace the standard

To hold your repository to a standard of its own, put it in `.meowpaw/prose/`
at the repository's root, in as many Markdown files as you like. When that
directory exists, the skill and the reviewer read your files and nothing of
the shipped standard: the replacement is total, because two standards that
disagree leave an author no way to tell which one applies. `meow-prose` only
reads the directory and never writes to it.

## What it costs you

The skill's description costs 299 characters in context on every turn, so
that Claude Code knows when to load the skill, and the reviewer's description
costs 277. Claude Code loads the skill whenever it writes, rewrites, edits or
reviews prose, a one-line commit message included. In the measurement recorded
in `project/research/RES-0272-routing-a-skill-by-its-description.md`, it loaded
in every writing request on Sonnet 5 and Opus 5.5 and in none that only
changes code. On Opus 5.5 it also loads for some answers in chat.

Every token count here is for Sonnet 5. The skill file costs about 4,400
tokens and holds the rules every text needs, and a commit message or a code
comment loads only that file. A document adds the rules for documents, about
950 tokens, and the skeleton for its type, about 200 to 400. Checking a longer
text adds the patterns for its language: about 3,400 tokens for English and
4,100 for Russian.

## Where the rules come from

The decision is
`project/adrs/ADR-1010-the-writing-standard-ships-as-a-unit-that-reviews-itself.md`,
and the part it creates is specified in
`project/specs/SPC-1010-the-writing-standard.md`. Read the decision for the
alternatives and what would reverse it.
