---
reader: someone choosing or running meow-code
answers: what meow-code does, what it adds to a session and how to use it
kind: reference
describes: [meow-code@0.1.0]
---

# meow-code

`meow-code` holds how Claude Code changes code and how it writes a check, in
any language and whether or not you keep a record of decisions. It installs on
its own, with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-code@meowpaw
```

## What it adds to a session

Before Claude Code changes code or writes a check, it loads the
`meow-code:change` skill, which has it:

- make the smallest change that is correct, and never reformat while it
  changes behaviour;
- read a file before writing to it, and batch reads and edits that don't
  depend on each other;
- ask a language server about a symbol where the session offers one, and say
  what a text search can't cover where it offers none;
- prefer a semantic edit for a symbol, a structural one for a mechanical
  rewrite and a textual one only for a literal;
- read a file's diagnostics after editing it, and take its evidence from your
  verification verbs, never from the diagnostics;
- document every declaration another module or a user can reach, preferring
  an example the language runs as a check;
- check what it can statically before behaviourally, and behaviourally before
  by evaluation, and see a check fail before the work that makes it pass;
- report a check that couldn't fail as a defect, and rewrite it instead of
  adding a second one;
- run mutation testing through the tool you or a pack names, when you ask
  whether the checks would catch a change.

You don't invoke the skill yourself: Claude Code loads it from its
description whenever it's about to change code.

## What it costs you

The skill's description costs 233 characters in context on every turn, and
the skill's body loads each time Claude Code changes code. The unit ships no
program.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared in
`plugins/meow-code/requires.toml`.
