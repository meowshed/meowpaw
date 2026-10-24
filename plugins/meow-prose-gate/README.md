---
reader: someone choosing or running meow-prose-gate
answers: what meow-prose-gate does, what it adds to a session and how to run it
kind: reference
describes: [meow-prose-gate@0.7.0]
description: "Stops Claude Code from publishing a commit message, pull request, issue, comment or release note that carries a writing defect any reader can point to. A program blocks a stock idiom from a fixed list, a line of bold text in place of a heading and text hidden in a file, and a model judging twice blocks other idioms, unexpanded acronyms and a bold phrase opening a paragraph only where both judgements agree on a span the text holds. It keeps nothing in context."
---

# meow-prose-gate

`meow-prose-gate` stops Claude Code from publishing a text that carries a
defect any reader can point to. It reads a commit message, a pull request or
issue body, a comment, a review and release notes before the command runs, and
it installs on its own, with no other part of the `meowpaw` harness.

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
`plugins/deep-dive/`, because that names a thing. A text given inline, in a
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

When the gate blocks, Claude Code gets one line per finding as the command's
error, such as `P1 | "low-hanging fruit" | say literally what the idiom stands for`
or `J2 | "TTL" | write time to live on first use`, and publishes again with
the text corrected.

## When the judge can't run

<!-- host-specific: claude -->

The gate lets the publish through and tells you so, in a message such as
`meow-prose-gate: the judged rules were not checked: the judge ran past 45 seconds`.
It does that when `claude` isn't on the path or can't be started, when a call
exits non-zero, when a call runs past 45 seconds, and when an answer doesn't
match the schema the unit ships. P1, P2 and P3 still apply then, because they
need no model.

## What it costs you

<!-- host-specific: claude -->

Nothing in context. The gate is a command hook that runs when Claude Code runs
a command that publishes text: `git commit`, and `gh` creating or editing a
pull request, an issue or a release, commenting on a pull request or an issue,
or reviewing a pull request. It also runs on any command that opens with
`git -C`, `git -c`, `gh -R` or `gh --repo`, because `gh -R owner/repo pr create`
publishes too, and on a command that publishes nothing it finds no text and
exits at once.

A text that breaks P1, P2 or P3 costs no model call. Any other published text
costs two Sonnet calls from your own Claude Code usage, run as
`claude -p --safe-mode --tools ""`, so the judge loads no plugin, hook, skill,
MCP server or project instruction and can't fire the gate again. On
2026-10-03 the two calls took 3 to 6 seconds together for a pull request body.
Each hook waits up to 120 seconds, so the judge's 45-second limit always fires
first.

The program is a native binary shipped inside the unit. On a machine the unit
carries no binary for, it denies each `git` and `gh` command its hook matches
and names `claude plugin install meow-core@meowpaw`, to run in a terminal
outside the session.

`MEOW_PROSE_GATE_JUDGE` names a program to run in place of `claude`. It exists
for the unit's fixtures, which set it to a stub judge so that no test calls a
model, and nothing else should set it.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://paw.retran.me/meowpaw/marketplace.json
claude plugin install meow-prose-gate@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

The gate carries its own criteria and needs no other plugin: neither
`meow-prose`, the writing standard, nor `meow-core`, the harness's kernel. With
`meow-prose` installed as well, the writing skill shapes the text before it is
written and the gate catches what the skill missed.

## Measure it

The executable in `plugins/meow-prose-gate/evals/` sends the four texts an earlier gate blocked wrongly and
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

## Hooks

<!-- host-specific: claude -->

`check` stops a publish whose text breaks a rule the gate holds: the exact rules first, then a judge model asked twice, which is the one hook allowed to reach beyond local files; the `meow-prose:writing` skill says why, and `mise run layers` runs the exact rules over the message of each commit a branch adds.

## What it needs

<!-- host-specific: claude -->

Claude Code 2.1.284 or later, the version this unit was tested on, declared in
`plugins/meow-prose-gate/requires.toml`, and `claude` on the path for the
judged rules. It relies on these platform behaviours, each documented by
Claude Code:

- `PreToolUse` command hooks filtered by an `if` rule, which block a command by exiting 2 with the reason on standard error, and a `systemMessage` on exit 0: [documentation](https://code.claude.com/docs/en/hooks.md)
- `claude -p` with `--safe-mode`, `--tools`, `--json-schema` and `--output-format json`: [documentation](https://code.claude.com/docs/en/cli-reference.md)
