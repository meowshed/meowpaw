# meow-flow

## 0.53.0

- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.
- Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions.

## 0.52.0

- The method's steps work from a Pi package, and the session routes each request itself.
