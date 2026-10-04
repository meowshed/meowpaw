---
reader: someone installing or running the meowpaw kernel on Pi
answers: what meow-core provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-core@0.1.0]
---

# @meowshed/meow-core

The meowpaw kernel for Pi: the reply shape, the writing standard and the prose
gate. It shapes every reply, holds all prose to one writing standard, and
blocks a publish whose text breaks a rule any reader can point to.

## Install it

```bash
pi install npm:@meowshed/meow-core
```

The npm tarball carries the meow binary for every platform, so the install
makes no request and needs no checkout. Installing from this repository's
checkout is the development install: it loads the package in place, runs no
lifecycle script, and the person installing it runs `node install-meow.mjs`
by hand to fetch the binary for their machine.

```bash
pi install packages/meow-core   # development install, from the checkout
```

## What it does

### The reply shape

On every model call, the extension injects the reply shape from
`plugins/meow-core/output-styles/meow.md` into the system prompt guidelines.
This replaces Claude Code's `force-for-plugin: true` and ensures every reply
leads with the answer, reports failures as cause-location-fix, and carries no
preamble or recap.

Where the extension or a tool makes a nested model call, it includes the
reply shape in the nested call's messages, so a dispatched agent receives the
same shape.

### The writing standard

The `writing` skill is the same `SKILL.md` that `meow-prose` ships, loaded by
Pi's skill discovery. It holds every text to one writing standard: the answer
first, a reason for every rule, one term for one thing, and plain English for
a reader who learned it as a second language.

### The prose gate

The extension intercepts `git commit`, `gh pr create`, `gh issue create` and
other publish commands. It shells out to the `meow-prose-gate` binary, which
checks the text for stock idioms, bold-open paragraphs and hidden text. Where
the binary finds spans that might be idioms, acronyms or bold-open, the
extension runs the two-judge model call and blocks only where both judgements
agree on a span.

## Binaries

The package carries `meow-prose-gate` as a platform-specific native binary.
The shell wrapper in `bin/meow-prose-gate` resolves the correct binary for
the current machine, or reports the check as unrun where none exists.
