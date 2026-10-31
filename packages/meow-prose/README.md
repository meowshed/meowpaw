---
reader: someone installing or running meow-prose on Pi
answers: what meow-prose provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-prose@0.9.0]
---

# @meowshed/meow-prose

Holds everything Pi writes for you to one writing standard: the answer first, a reason for every rule, one term for one thing, and plain English for a reader who learned it as a second language. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-prose
```

The paw executable ships with `@meowshed/meow-core` alone (REQ-4612): this
package's launchers run their subcommands through it, so install the core
package beside this one for the binary-backed checks. Without it, every
check reports unrun and lets the command through.

```bash
pi install npm:@meowshed/meow-core   # carries the binary the launchers run
```

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script.

## Write to the standard

`meow-prose` ships a skill that loads before Pi writes, so the
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

Pi then writes that language across the repository. A technical term
keeps the spelling its own domain uses, and a quotation keeps its author's
wording, whatever you declare.

## Review a text

The `meow-prose-review` tool reviews a finished text against the writing
standard, and the model calls it when a review, check, proofread or critique
is asked for. Its nested call runs on glm 5.3 flash, or the model the
`MEOW_NESTED_MODEL` environment variable names, and carries the standard and
the reply shape with it, because a nested call reads no file and holds no
skill.

## Replace the standard

To hold your repository to a standard of its own, put it in `.meowpaw/prose/`
at the repository's root, in as many Markdown files as you like. When that
directory exists, the skill and the reviewer read your files and nothing of
the shipped standard: the replacement is total, because two standards that
disagree leave an author no way to tell which one applies. `meow-prose` only
reads the directory and never writes to it.

## Tools

The `prose` agent holds three tools, each for one step of its procedure:

- `Read`: the set-up step reads the standard, the patterns file for the text's language and the text.
- `Grep`: the review steps find a pattern across the text's lines.
- `Glob`: the set-up step finds the `.meowpaw/prose/` files that replace the standard.

## What it costs you

Pi loads the skill whenever it writes, rewrites, edits or reviews
prose, a one-line commit message included. Measured on 24 requests, three runs
each, it loaded in every writing request on Sonnet 5 and Opus 5.5 and in none
that only changes code. On Opus 5.5 it also loads for some answers in chat.

Every token count here is for Sonnet 5. The skill file costs about 4,400
tokens and holds the rules every text needs, and a commit message or a code
comment loads only that file. A document adds the rules for documents, about
950 tokens, and the skeleton for its type, about 200 to 400. Checking a longer
text adds the patterns for its language: about 3,400 tokens for English and
4,100 for Russian.
