---
reader: someone installing or running meow-core on Pi
answers: what meow-core provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-core@0.6.1]
---

# @meowshed/meow-core

Shapes every reply Claude Code makes to you: the action first, a failure as cause, location and fix, and no preamble, recap or offer of further help. It replaces your own output style while it is enabled, and keeps up to 4,200 characters in context on every turn. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-core
```

The npm tarball carries the all-features meow binary for every platform
(REQ-4144), so the install makes no request and needs no checkout. Every
other meowpaw package's launcher falls back to this binary, so the core
package is the one install every layer sits beside. A git-source install
downloads the binary in its `postinstall` instead.

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script; the person
installing it runs `node install-meow.mjs` by hand to fill the platform
directory the checkout ignores.
