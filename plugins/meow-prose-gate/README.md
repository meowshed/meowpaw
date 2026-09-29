---
reader: someone choosing or running meow-prose-gate
answers: what meow-prose-gate does, what it adds to a session and how to run it
kind: reference
describes: [meow-prose-gate@0.2.1]
---

# meow-prose-gate

`meow-prose-gate` stops Claude Code from publishing a text that carries a
defect any reader can point to. It reads a commit message, a pull request or
issue body, a comment, a review and release notes before the command runs, and
it installs on its own, with no other part of the `meowpaw` harness.

## What it blocks

The gate blocks three defects and nothing else, because a block another reader
would dispute teaches you to route around it. A program checks each one by
exact match, so the same command gets the same answer every time, and a block
quotes a span you can find in the command:

- P1, an idiom from a fixed list of fifteen: low-hanging fruit, under the
  hood, silver bullet, move the needle, boil the ocean, circle back, deep dive,
  game changer, at the end of the day, out of the box, on the same page,
  ballpark figure, in the weeds, rule of thumb and the elephant in the room.
  Case, line breaks and hyphens between the words don't matter, and any other
  phrase passes, however figurative it is.
- P2, a line holding only bold text, such as `**Why.**`, standing in for a
  heading.
- P3, a text hidden behind a file, such as `git commit -F notes.txt`,
  `--body-file body.md` or `$(cat notes.md)`, which the gate can't read.

Fenced code, code spans and URLs are never checked, and P1 skips any word
holding a `/`, a `\`, an `_` or a file extension, such as
`plugins/deep-dive/`, because that names a thing. A text given inline, in a
heredoc read with `-F -`, `-F /dev/stdin` or `-F /dev/fd/0`, or in
`$(cat <<'EOF' ... EOF)` is readable and passes P3.

Unexplained acronyms, American spellings and a bold phrase opening a
paragraph are left to the writing skill and the reviewer in `meow-prose`,
because none of them can be matched exactly.

When the gate blocks, Claude Code gets one line per finding as the command's
error, such as `P1 | "low-hanging fruit" | say literally what the idiom stands for`,
and publishes again with the text corrected.

## What it costs you

Nothing in context, and no model call. The gate is a command hook that runs
only when Claude Code runs a command that publishes text: `git commit`, and
`gh` creating or editing a pull request, an issue or a release, commenting on
a pull request or an issue, or reviewing a pull request. The program is a
native binary shipped inside the unit, so it needs nothing installed on the
machine. On a machine the unit carries no binary for, it says it checked
nothing and blocks nothing.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-prose-gate@meowpaw
```

The gate carries its own criteria and needs no other plugin: neither
`meow-prose`, the writing standard, nor `meow-core`, the harness's kernel. With
`meow-prose` installed as well, the writing skill shapes the text before it is
written and the gate catches what the skill missed.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared in
`plugins/meow-prose-gate/requires.toml`. It relies on these platform
behaviours, each documented by Claude Code:

- `PreToolUse` command hooks filtered by an `if` rule, which block a command by exiting 2 with the reason on standard error: [documentation](https://code.claude.com/docs/en/hooks.md)
