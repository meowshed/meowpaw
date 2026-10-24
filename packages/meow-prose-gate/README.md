---
reader: someone installing or running meow-prose-gate on Pi
answers: what meow-prose-gate provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-prose-gate@0.7.1]
---

# @meowshed/meow-prose-gate

Stops Pi from publishing a commit message, pull request, issue, comment or release note that carries a writing defect any reader can point to. A program blocks a stock idiom from a fixed list, a line of bold text in place of a heading and text hidden in a file, and a model judging twice blocks other idioms, unexpanded acronyms and a bold phrase opening a paragraph only where both judgements agree on a span the text holds. It keeps nothing in context. Distributed as a Pi package.

## What it blocks

The gate blocks six defects and nothing else, because a block another reader
would dispute teaches you to route around it. Every block quotes a span you
can find in the command.

A program checks three of them by exact match, so the same command gets the
same answer every time:

- P1, an idiom from a fixed list of fifteen: low-hanging fruit, under the
  hood, silver bullet, move the needle, boil the ocean, circle back, deep dive,
  game changer, at the end of the day, out of the box, on the same page,
  ballpark figure, in the weeds, rule of thumb and the elephant in the room.
  Case, line breaks and hyphens between the words don't matter.
- P2, a line holding only bold text, such as `**Why.**`, standing in for a
  heading.
- P3, a text hidden behind a file, such as `git commit -F notes.txt`,
  `--body-file body.md` or `$(cat notes.md)`, which the gate can't read.

Fenced code, code spans and URLs are never checked, and P1 skips any word
holding a `/`, a `\`, an `_` or a file extension, such as
`packages/deep-dive/`, because that names a thing. A text given inline, in a
heredoc read with `-F -`, `-F /dev/stdin` or `-F /dev/fd/0`, or in
`$(cat <<'EOF' ... EOF)` is readable and passes P3.

A model judges the other three, and only where no exact rule fired:

- J1, an idiom, saying or culture reference off P1's list, such as
  `circling back` or `a perfect storm`.
- J2, an acronym the text uses before it expands it, or never expands, such as
  `TTL`, outside code font, URLs, identifiers and a commit subject's type and
  scope.
- J3, a paragraph or a list item that opens with a bold phrase and goes on in
  the same line, such as `**Why.** The server rendered every page twice`.

The program asks the judge twice, side by side, and blocks only on a finding
both judgements report with the same rule and the same span, and only where
that span is in the command. One judgement's mistake therefore never blocks on
its own. American spellings and the rest of the writing standard stay with the
writing skill and the reviewer in `meow-prose`.

When the gate blocks, Pi gets one line per finding as the command's
error, such as `P1 | "low-hanging fruit" | say literally what the idiom stands for`
or `J2 | "TTL" | write time to live on first use`, and publishes again with
the text corrected.

## Install it

```bash
pi install npm:@meowshed/meow-prose-gate
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

## Measure it

The executable in `packages/meow-prose-gate/evals/` sends the four texts an earlier gate blocked wrongly and
one text breaking each judged rule through the unit's gate, three times each,
and prints each exit status, the gate's output and the wait. It ends with a
tally and exits 1 if any run blocked a text it should pass, passed a text it
should block, or couldn't judge. Every run
calls a model, so you run it by hand, and no gate or workflow runs it. It is a
smoke check: three runs show a false block that happens often, never one that
happens rarely. Run it with the repeat count as its only argument, `3` for the
runs above.

## Read a subcommand's help

`meow-prose-gate --help` lists the subcommands, and `meow-prose-gate <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.
