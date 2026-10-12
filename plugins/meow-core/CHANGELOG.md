# meow-core

## 0.10.0

- The tool gains `paw interface`, which generates the public-interface page from its own documentation.
- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.

## 0.9.1

- The Pi package's extension works in a session, and the session routes each request itself.
- A verification result is bound to the tree it ran on, so evidence names what the binary actually checked.
