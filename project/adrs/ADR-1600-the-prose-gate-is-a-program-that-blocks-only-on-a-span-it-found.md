---
id: ADR-1600
artifact: adr
status: approved
revised: 2026-09-28
addresses: [REQ-3182, REQ-3183, REQ-3187, REQ-1756, REQ-2076]
supersedes: []
---

# 1600. The prose gate is a program, and it blocks only on a span it found in the command

## Decision

`meow-prose-gate` replaces its `PreToolUse` prompt hook with a command hook
that runs the unit's own program, `meow-prose-gate check`, a subcommand of the
native tool every unit's program already is (ADR-1110). No model reads the
text. This amends ADR-1010, whose gate named a prompt hook on Haiku; the rest
of ADR-1010 stands.

The hook fires on the same publishing commands as before: `git commit`, and
`gh` creating or editing a pull request, an issue or a release, commenting on
a pull request or an issue, and reviewing a pull request. The program reads
the shell command from the hook's input and splits it into simple commands at
`;`, `&&`, `||`, `|` and line breaks. In each `git commit` and each such `gh`
command it takes the published text from the arguments of `-m` and
`--message` for `git`, and of `-t`, `--title`, `-b`, `--body`, `-n` and
`--notes` for `gh`, each written as a separate argument, with `=` as in
`--body=...`, attached as in `-m"..."`, or last in a cluster as in `-am`.
It also takes a heredoc or a here-string that feeds that
same command, where the command reads its text from standard input with
`-F -`, `--file -`, `--body-file -` or `--notes-file -`. A heredoc feeding
any other command, such as `cat > notes.md <<'EOF'`, is never read, because
that text isn't published. The program then checks three rules and nothing
else:

- P1 blocks on a phrase from a closed list of fifteen idioms, because a
  second-language reader looks each one up or misreads it, as the writing
  standard's rule H2 says. The list is the one ADR-1010's gate carried:
  low-hanging fruit, under the hood, silver bullet, move the needle, boil the
  ocean, circle back, deep dive, game changer, at the end of the day, out of
  the box, on the same page, ballpark figure, in the weeds, rule of thumb and
  the elephant in the room. A phrase joins or leaves the list only by a
  decision of its own, because the list being closed is what makes P1 exact
  (REQ-3187). It matches case-insensitively and as whole words, because
  capitals and a word's neighbours don't change the idiom, and it accepts any
  run of spaces, line breaks or hyphens between the words, because a text
  wraps and "low-hanging" is spelt both ways. The span is the text it matched.
- P2 blocks on a line holding only bold text, such as `**Why.**` or
  `__Why__:`, optionally followed by a colon or a full stop, because it states
  a conclusion with the sentence that argues for it stripped out. The span is
  that line.
- P3 blocks on a path the text hides behind, because a text the gate can't
  read is one it can't check, as ADR-1010 decided. That is the value of `-F`,
  `--file`, `--body-file` or `--notes-file` other than `-`, a file redirected
  with `<` into a command reading `-F -`, and a `$(cat notes.md)`,
  `$(< notes.md)` or `` `cat notes.md` `` inside a text the shell expands. The
  span is the path. `-F -` with a heredoc, and `$(cat <<'EOF' ... EOF)`, are
  readable and pass.

P1 and P2 skip fenced code, code spans and URLs, as the prompt told the model
to, because they quote rather than state. P1 also skips each
whitespace-separated token holding a `/`, a `\`, an `_` or a file extension,
such as `plugins/deep-dive/` or `rule-of-thumb.md`, because that is a path or
an identifier and names a thing. The reader keeps each quoted argument as the
command writes it, escapes included, so a match is a slice of the command and
the span quoted is that slice (REQ-3183). As a last guard, the program drops a
finding whose span the command doesn't hold.

On a finding it exits 2 and prints one line per finding to standard error as
`P1 | "span" | fix`, which Claude Code hands the model as the reason, so the
model corrects the text and publishes again. On none it exits 0 and prints
nothing. Where the unit carries no binary for the machine, its launcher prints
that nothing was checked and lets the command through, as `meow-git`'s guard
does, because blocking every publish on a missing binary would teach people
to uninstall the gate.

After this decision the gate gives the same answer for the same command every
time, costs no model call and no network, and quotes only text that is there.
What still doesn't work:

- An idiom in a form the list doesn't spell, such as `circling back`, passes,
  because matching inflections would be the guess REQ-3187 forbids.
- A text built in a way the program doesn't parse, such as a variable
  expanded into `-m "$MSG"`, is checked only as the characters the command
  holds.
- A match that spans a quote boundary or an unquoted backslash, such as an
  idiom split across `"under the "'hood'`, isn't a slice of the command, so
  the last guard drops it and the text passes.
- On a machine the unit ships no binary for, nothing is checked.
- A bold fragment with text after it on the same line, such as
  `**Why.** Because ...`, passes, because it isn't a line holding only bold
  text, and the writing skill and the reviewer in `meow-prose` hold it.

## Why

BUG-1230 records the prompt hook blocking four texts of four on one day for
findings they didn't hold: a bold line where there was no bold, an idiom that
wasn't there, words off the list, and a structure no rule names. The prompt
already said that phrases off the list pass, and the model blocked on them
anyway, so a better prompt asks for the same thing again with nothing checking
the answer.

All three rules name their defect exactly, as a list, a line of Markdown
syntax or a flag's argument, so a program settles them with no judgement.
REQ-2076 prefers the cheaper kind of check wherever it can settle an
obligation, REQ-1756 asks a check to match the defect and never a word that
appears innocently, and RES-0027 concludes that the mechanical checks belong
in the gate and the judgements in review. REQ-3187 replaces REQ-3186, which
forbade any pattern over the text, with a ban on a pattern that guesses at
meaning.

## Alternatives

| Option                                                          | Better at                                                               | Why it lost                                                                                                       |
| --------------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| A program matching the three rules in a command hook            | The same verdict every time, no model call, a span that is always there | Chosen                                                                                                            |
| Keep the prompt, and require the model to quote a span verbatim | No new program, and room for rules a program can't state                | Nothing checks the quote, and BUG-1230's model ignored an instruction as explicit as that one                     |
| A prompt hook beside a command hook that confirms the quote     | Keeps a model for later rules                                           | Claude Code blocks when either hook blocks, so the command hook can't overrule a false block from the prompt hook |
| Drop the gate and leave everything to the reviewer              | No hook at all                                                          | REQ-3182 asks for a check before publishing, and the reviewer never blocks                                        |
| Do nothing                                                      | No change                                                               | The gate keeps blocking good texts, and ADR-1010 names that as its own reversal condition                         |

## What it costs

The unit now ships a binary per platform, built by `crates/meow/build-units`
and released with the other units' binaries, and whoever maintains the crate
takes on a shell-word reader for the gate. A repository gains nothing to run
and nothing written into its tree (REQ-3180).

On a machine the unit ships no binary for, every text is published
unchecked, and the reader of that text pays for what the gate would have
caught. The launcher says so on every publish, so the person sees it.

A defect the model used to catch outside the exact rules, such as an idiom
inflected past the list, now passes the gate and reaches the reviewer or the
reader, where it was before the gate existed. That trade is the point: a miss
costs what it cost without the gate, and a false block costs the gate itself.

## What would reverse it

- A rule that can't be stated exactly becomes one the gate must hold, and a
  model shown to settle it the same way twice is available to judge it.
- A defect record shows the shell-word reader misreading a form of
  publishing command, and no change to the unit's reader closes it.

## Consequences

- `plugins/meow-prose-gate/hooks/hooks.json` holds command hooks, one per
  publishing command, each running `meow-prose-gate check`.
- `plugins/meow-prose-gate/bin/` carries a launcher and the binaries, and
  `crates/meow/` gains the `prose` feature behind which the subcommand sits,
  so no other unit's binary carries it (REQ-0076).
- `plugins/meow-prose-gate/evals/` goes, because a program's verdict is a
  fixture's to check, and `tests/` holds the fixtures in its place, the four
  false blocks from BUG-1230 among them.
- SPC-1010's section on the gate, the unit's README and its version follow.

## How I will know it was realised

1. The four texts BUG-1230 records pass the gate, each as a fixture, and a
   text with an idiom, one with a bold-only line and one hiding behind
   `--body-file` are each blocked with a span found verbatim in the command.
2. `hooks/hooks.json` holds no hook of type `prompt`.
3. Every fixture runs the unit's launcher, so the gate a repository installs is
   what the fixtures check.

## What this does not settle

- Whether `gh pr merge`, whose `--subject` and `--body` write a squash
  commit's message, joins the gate. ADR-1010 never listed it, and adding a
  command widens what the gate reads, which is a decision of its own.

- Whether other rules of the writing standard join the gate. Each needs a
  statement exact enough for REQ-3187, and a decision of its own.
- How `tools/measure_gate.py` and SPC-1020's measure of a gate apply to a
  gate with no model; nothing in this unit is measured that way now.
