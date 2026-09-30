---
id: TSK-2575
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1265
closes: []
issue: 711
---

# Show the prose gate holding a text in every command it reads

Add fixtures to `plugins/meow-prose-gate/tests/test_gate.py` so each of the
ten commands `hooks/hooks.json` routes to `meow-prose-gate check`, and each
argument the program reads a text from, has one fixture where the gate holds
the text back. Then a change that stops checking one of them fails a check,
which REQ-3182 needs. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a hook event for `gh pr edit`, `gh pr comment`, `gh pr review`,
   `gh issue edit`, `gh issue comment`, `gh release create` and
   `gh release edit`, each with a listed idiom in `--body` or `--notes`, when
   the launcher runs `check`, then it exits 2 and quotes a span found verbatim
   in the command. Closed by: a new fixture class in `test_gate.py`, one test
   per command.
2. Given `gh release create` with `--notes-file`, when the launcher runs
   `check`, then it exits 2 with a P3 finding quoting the path. Closed by: a
   fixture in the same class.
3. Given the ten `if` patterns in `hooks/hooks.json`, when the fixtures run,
   then each pattern's command appears in at least one fixture that expects a
   block. Closed by: a fixture that reads `hooks.json` and compares its
   patterns with the commands the blocking fixtures run.

## What to do

Run every fixture through the unit's launcher, as the existing ones do. Add
no behaviour to the program: it holds each form today, so each new fixture
passes against the current binary. Write the fixture for criterion 3 first,
in a commit of its own, and keep its run as the failing run: it fails while
seven patterns have no blocking fixture. Change no file the unit ships to a
repository, so `meow-prose-gate` keeps its version.

## Depends on

Nothing. BUG-1265 is approved.

## Evidence

The class `EveryGatedCommand` in
`plugins/meow-prose-gate/tests/test_gate.py` holds one test per command
`hooks/hooks.json` routes, each run through the unit's launcher and each
asserting exit 2 and a span found verbatim in the command. The text reaches
the program through `-m`, `--body`, `-b`, `--notes` and `-n`, and
`test_release_notes_hidden_in_a_file` holds `--notes-file notes.md` as P3.
The table `GATED` keys each blocking command by the command its pattern
names, and `TheHook.test_each_routed_command_has_a_blocking_fixture` asserts
that the set of `if` patterns equals the set `GATED` gives. So a pattern with
no fixture fails, and so does a fixture whose pattern was deleted.

That check failed first, in the commit that held it alone:
`meow-verbs run test` exited 1 with `FAILED (failures=1)`, naming the seven
patterns from `gh pr edit` to `gh release edit`, seen in
the run under #713, whose output is no longer kept. It passes now:

```text
$ python3 -m unittest test_gate    # in plugins/meow-prose-gate/tests
Ran 31 tests
OK                                 # exit 0
```

`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

The squash message `gh pr merge` writes, which ADR-1600 leaves unread and
leaves open; a fixture for it would assert a behaviour nobody decided.
