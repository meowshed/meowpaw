---
id: TSK-2470
artifact: task
status: approved
revised: 2026-09-28
bug: BUG-1230
closes: [REQ-1756, REQ-3183, REQ-3187]
issue: 597
---

# `meow-prose-gate` checks a publish with a program that quotes only what it found

The gate's prompt hook becomes a command hook running `meow-prose-gate check`,
which blocks only on a span it found verbatim in the command, as ADR-1600
states. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given each of the four texts BUG-1230 records, a body of plain paragraphs
   with no bold, one without the phrase `deep dive`, one holding `look` and
   `gate passes`, and one of plain paragraphs each opening with a full
   sentence and no emphasis, when the gate reads a `gh pr create --body "..."`
   carrying it, then it exits 0 and prints nothing. Closed by: four fixtures
   naming REQ-1756, seen failing first.
2. Given a commit message holding `low-hanging fruit`, an issue body with a
   line holding only `**Why.**`, and `gh pr create --body-file body.md`, when
   the gate reads each, then it exits 2 and prints to standard error one line
   `RULE | "span" | fix` naming P1, P2 or P3 and quoting `low-hanging fruit`,
   `**Why.**` or `body.md`, and each quoted span occurs verbatim in the
   command. Closed by: three fixtures naming REQ-3183, seen failing first.
3. Given `git commit -F -` with a heredoc, and `git commit -m` with the
   message in `$(cat <<'EOF' ... EOF)`, when the gate reads each, then it
   exits 0 and prints nothing. Closed by: two fixtures naming REQ-1756.
4. Given an idiom only inside a code span, fenced code, a URL or a path such
   as `plugins/deep-dive/`, when the gate reads it, then it exits 0 and prints
   nothing. Closed by: two fixtures naming REQ-1756.
5. Given the unit, when `hooks/hooks.json` is read, then it holds no hook of
   type `prompt`. Closed by: one fixture naming ADR-1600.
6. Given a launcher with no binary beside it, when it runs `check` on a text
   holding an idiom, then it exits 0 and prints to standard output that
   nothing was checked.
   Closed by: one fixture naming ADR-1600.
7. Given the program's source, when a reviewer reads its rules, then it
   matches only the fifteen idioms ADR-1600 lists, a line holding only bold
   text and a path argument or substitution. Closed by: the pull request's
   review, because REQ-3187 is verified by judgement.
8. Given any fixture under `plugins/meow-prose-gate/tests/`, when it runs,
   then it runs `plugins/meow-prose-gate/bin/meow-prose-gate`, so the gate a
   repository installs is what the fixtures check. Closed by: the pull
   request's review, naming ADR-1600.

## What to do

ADR-1600 chose a program over a model with a stricter prompt, and REQ-3187
limits it to the three exact rules; this task records that choice as the
defect's fix.

Add a `prose` feature and subcommand to `crates/meow`, a launcher
`plugins/meow-prose-gate/bin/meow-prose-gate` in the form the other units'
launchers take, and the unit to `crates/meow/build-units`. Replace each prompt
hook with a command hook on the same `if`. Move the eval cases into fixtures
under `plugins/meow-prose-gate/tests/`, run by the `test` verb, and delete
`evals/`. Keep the unit's README, SPC-1010 and the documentation pages true,
and move the unit to its next minor version, since its hook changes kind.

The fixtures come first, in a commit of their own, run against the launcher
before the program exists, and are seen failing, because a blocking fixture
never seen failing may pass against a program that does nothing. The passing
fixtures fail then only because the program is absent, so they count as
evidence only beside the blocking ones.

## Depends on

Nothing. BUG-1230, REQ-3183, REQ-3187 and ADR-1600 are approved.

## Evidence

Closes REQ-1756, REQ-3183 and REQ-3187. `meow-verbs evidence --keep format lint
test` exits 0 on this change's own tree, each result kept in
`project/evidence/`, as the pull request cites.

The fixtures went in first, in a commit of their own, and against the unit
without its program `python3 -m unittest discover -s
plugins/meow-prose-gate/tests` ran 19, with 18 errors, each the launcher
missing, and 1 failure, `test_no_hook_is_a_prompt`, against the prompt hooks.
After the change it runs 19, OK. The crate's `prose` tests run 11, OK, and
cover the parts the fixtures don't: a clustered `-am`, `-n` read as git's own
flag, a heredoc feeding another command, a heredoc after `&&`, a file on
standard input, a single-quoted substitution and `--body-file=`.

For criterion 7, the rules in `crates/meow/src/prose.rs` are the fifteen
idioms in `IDIOMS`, the bold-only line in `rule_p2`, and the path arguments
and substitutions in `publishing` and `substitutions`, and nothing else. The
fixtures all run `plugins/meow-prose-gate/bin/meow-prose-gate`, the launcher a
repository installs, for criterion 8. `meow-prose-gate` moves to 0.2.0.

## Left alone

`tools/measure_gate.py` and SPC-1020's section on measuring a gate, which no
unit uses once this lands; retiring them is a change of its own. The writing
skill and the reviewer in `meow-prose`, which this doesn't touch.
