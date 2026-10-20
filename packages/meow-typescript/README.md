---
reader: someone installing or running meow-typescript on Pi
answers: what meow-typescript provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-typescript@0.1.0]
---

# @meowshed/meow-typescript

Detects a TypeScript and JavaScript package from the package.json git tracks, reads the package manager it declares, prints a stages table bound from the tools it configured and run through that manager, reports a stage that runs a tool outside the manager or leaves a linter or compiler setting without effect, and carries what a reviewer of TypeScript checks that no command reports, writing no file. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-typescript
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

## Generated files

Commit the lockfile your package manager writes (`package-lock.json`,
`pnpm-lock.yaml`, `yarn.lock` or `bun.lock`), because it is the resolved
dependency tree every collaborator and every CI run installs from. Ignore
`node_modules/`, a build's output directory, `coverage/`, `*.tsbuildinfo` and
`.eslintcache`, because the next run regenerates each.
