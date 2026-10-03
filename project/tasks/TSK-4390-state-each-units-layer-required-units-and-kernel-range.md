---
id: TSK-4390
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2340
closes: [REQ-1482, REQ-2990, REQ-2998, REQ-3006]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# State each unit's layer, required units and kernel range, and fail a unit missing one

Each unit's `requires.toml` gains `layer` and `units`, each pack gains a
`kernel` range, and `meow-author check` fails a unit with no version, no
`requires.toml` or a missing key, as SPC-1080 states under "Each unit is a
plugin". One task, one branch, one pull request, one review: the tests first,
then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture unit with no `requires.toml`, when `meow-author check`
   reads it, then it fails naming the unit and the file (REQ-1482). Closed by:
   a crate test naming REQ-1482, seen failing first.
2. Given a fixture unit whose `plugin.json` carries no `version`, when
   `meow-author check` reads it, then it fails naming the unit (REQ-2990).
   Closed by: a crate test naming REQ-2990.
3. Given a fixture unit with `layer = "pack"` and no `kernel`, when
   `meow-author check` reads it, then it fails naming the key (REQ-2998).
   Closed by: a crate test naming REQ-2998.
4. Given this repository, when `meow-author check` runs in the `lint` verb,
   then every unit under `plugins/` passes the new rules. Closed by: the
   `lint` verb's run.
5. Given a unit whose `units` names another, when a test reads its README,
   then the README says the platform enables the required unit and keeps it
   enabled while this one is on (REQ-3006). Closed by: a crate test naming
   REQ-3006.

## What to do

Add `layer`, `units` and, for each pack, `kernel` to every
`plugins/<unit>/requires.toml`. Decide each unit's layer from what it ships
and name it in the pull request, because the catalogue isn't decided and
CLAUDE.md asks that no list of units be stated as fact elsewhere. Read each
`units` list from what the unit runs, such as `meow-git` finding `meow-scm`.

Add the rules to `meow-author check` in the `author` feature, and state them
in `plugins/meow-author/README.md`. Where a unit needs another, say so in its
README where it recommends the install.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

A dependency field in the platform's own manifest, because the platform offers
none, which is ADR-2480's reason for `requires.toml`.
