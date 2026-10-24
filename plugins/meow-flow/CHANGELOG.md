# meow-flow

## 0.53.0

- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.
- Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions.
- The method runs each push, merge, release, issue write and governance change as its own command, so the platform asks for each one, and never asks for an approval that covers the next.

## 0.52.0

- The method's steps work from a Pi package, and the session routes each request itself.
