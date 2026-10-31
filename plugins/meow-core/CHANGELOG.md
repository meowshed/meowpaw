# meow-core

## 0.11.0

- Its launcher runs the shared executable, which now reads the record ADR-3090 describes; the unit itself is unchanged. This release retires epics and tasks. Before using it, run `paw upgrade` to preview and `paw upgrade --write` on a branch: `paw` refuses a record holding `tasks/` or `epics/` until then.

## 0.10.2

- A second session-start hook, `reply-shape`, hands the model the reply shape, so a Claude Code session holds it whether or not the output style is selected.

## 0.10.1

- The shared executable carries `serde_json` 1.0.154 and `sha2` 0.11.1, two patch releases of its dependencies.

## 0.10.0

- The tool gains `paw interface`, which generates the public-interface page from its own documentation.
- The tool gains the shared layer every language pack builds on: it binds the tool the repository configured, reports what a stage leaves unchecked, applies no unsafe fix, points a tool's output outside the working tree and names the evidence a run keeps.
- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.

## 0.9.1

- The Pi package's extension works in a session, and the session routes each request itself.
- A verification result is bound to the tree it ran on, so evidence names what the binary actually checked.
