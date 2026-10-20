---
reader: someone installing or running meow-csharp on Pi
answers: what meow-csharp provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-csharp@0.1.0]
---

# @meowshed/meow-csharp

Detects a .NET solution or project from what git tracks, compares the SDK global.json pins with the ones installed, prints a stages table that restores explicitly and keeps every build's output outside the working tree, reports Nullable, TreatWarningsAsErrors and AnalysisLevel left unset, writing no file, and carries what a reviewer of C# checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-csharp
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
