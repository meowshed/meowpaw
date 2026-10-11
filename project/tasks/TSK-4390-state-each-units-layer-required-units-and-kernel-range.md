---
id: TSK-4390
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2340
closes: [REQ-1482, REQ-2990, REQ-2998, REQ-3006]
issue: 943
projected: 3586ca81ff63
tracked: 483eddf4f11c
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

The tests were written first and seen failing in `02af6df4`, and pass after
`01f87d38`. Each criterion closes with the tests naming it:

1. REQ-1482: `author::tests::a_unit_without_requires_toml_fails` in
   `crates/meow/src/author.rs`, and
   `test_a_unit_without_requires_toml_fails` in
   `plugins/meow-author/tests/test_author.py`.
2. REQ-2990: `author::tests::a_unit_without_a_version_fails`, and
   `test_a_unit_without_a_version_fails`.
3. REQ-2998: `author::tests::a_pack_without_a_kernel_range_fails`, and
   `test_a_pack_without_a_kernel_range_fails`.
4. The `lint` stage, whose `prompts` task runs `meow-author check` over every
   unit, passed with the new rules in force.
5. REQ-3006: `author::tests::a_unit_requiring_another_says_the_platform_enables_it`.

The five stages passed at tree `f8a5c87d9119`, each bound by `meow-checks
run` and confirmed by `meow-checks evidence`, exit 0: format record
`2b209cd2636f`, check `b89e63499fbe`, lint `2b134470a25e`, test
`d862724ea621`, build `8268c2d6ae4c`. The branch is
`feat/each-unit-is-a-versioned-plugin`, carried by this epic's pull request.

Along the way the branch also cleared what left the trunk's gate red before
any change of this one: BUG-1650, by repointing BUG-1400's `violates:` off
the withdrawn REQ-4110, and BUG-1660, by aligning the record suite's
fixture; plus three residuals of the measurement removal and the stages
rename, each in a commit of its own — the held `author cost` call in
`crates/meow/tests/unit_help.rs`, the `test_loop.py` entry in `mise.toml`,
the budget assertions in `plugins/meow-github/tests/`, the verbs wording in
`plugins/meow-prose-gate/evals/hand_run.py`, and the REQ-1060 citation in
this unit's README. BUG-1640's TSK-5500, which stops the checker walking a
defect's `violates` as a provider at all, stays open.

## Left alone

A dependency field in the platform's own manifest, because the platform offers
none, which is ADR-2480's reason for `requires.toml`.
