---
reader: someone installing or running meow-markdown on Pi
answers: what meow-markdown provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-markdown@0.6.0]
---

# @meowshed/meow-markdown

The meowpaw Markdown pack for Pi: detects a Markdown corpus from what git
tracks, lists the tools a repository configured for it, prints a verbs
table bound from that configuration, reports a missing render target,
markdownlint settings the lint verb lacks and a link check whose network
behaviour is undeclared, and carries what a reviewer of a Markdown document
checks that no command reports.

## Install it

```bash
pi install npm:@meowshed/meow-markdown
```

The npm tarball carries the meow binary for every platform, so the install
makes no request and needs no checkout. Installing from this repository's
checkout is the development install: it loads the package in place, runs no
lifecycle script, and the person installing it runs `node install-meow.mjs`
by hand to fetch the binary for their machine.

```bash
pi install packages/meow-markdown   # development install, from the checkout
```

## What it does

### The markdown skill

The `markdown` skill holds what the session reports about a repository's
Markdown corpus and what a reviewer of a Markdown document checks that no
command reports.

### The binary

The `meow-markdown` wrapper resolves the platform meow binary and runs
`meow markdown`, which reports the corpus, the verb bindings and the gaps.
It runs lychee to report a link it couldn't reach as unreachable, never as
a finding, and writes no file.
