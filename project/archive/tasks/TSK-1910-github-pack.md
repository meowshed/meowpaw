---
id: TSK-1910
artifact: task
status: done
revised: 2026-09-26
epic: EPC-1290
closes: [REQ-2556, REQ-2558, REQ-2560, REQ-2564, REQ-2826, REQ-2832, REQ-2906]
issue: 359
---

# The GitHub pack reads a repository's history

The GitHub pack reads a repository's history, as ADR-1290 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a stand-in `gh` serving two pages of issues and pull requests, a pull request listing and both comment listings, when `meow-github history` runs, then it prints every item, `merged` for each pull request, and every comment, and passes `--paginate`, `--slurp` and `--cache`. Closed by: a fixture.
2. Given a response missing a field the pack prints, when it runs, then it fails naming the field. Closed by: a fixture.
3. Given a `gh` that refuses a listing, when it runs, then it reports the history as unread, names the listing, and prints no document. Closed by: a fixture.
4. Given the repository, when `check_standalone.py` runs, then it passes with the new unit. Closed by: its output.

## What to do

Add the feature `github` to the native tool, with `history` reading the four listings through `gh api` as ADR-1290 says. Add `plugins/meow-github/` with its manifest, `requires.toml`, `budget.toml`, launcher and fixtures, a pair in `build-units`, an entry in the marketplace, a page in `docs/`, and a row in the docs index.

## Depends on

Nothing. ADR-1290 is approved.

## Evidence

`meow-github history` reads four listings through `gh api`, every page with
`--paginate --slurp` and through `--cache 1h`, and prints one JSON document.
Four fixtures run it against a stand-in `gh` on the `PATH`:

- Two pages of issues and pull requests, a pull request listing and both
  comment listings print as issue 1, pull request 2 merged and pull request 3
  not merged, with labels and both kinds of comment. Every one of the four
  calls ends in `--paginate --slurp --cache 1h`.
- A response lacking `title` exits 3 with "lacks the field `title`" and no
  document.
- A refused comment listing exits 3, names the listing and the endpoint with
  GitHub's `HTTP 403`, lists the two listings read before it stopped, and
  prints no document.
- The launcher alone, with no binary, reports the history as unread, names
  the machine, and says to reinstall the unit.

The first three fail against a stub that returns nothing; the fourth tests
the launcher script, which the stub doesn't replace.

Read against this repository, `history` printed 360 issues and pull requests,
188 of them pull requests, 187 merged and 1 closed without merging, and 16
conversation comments, and exited 0. The unit is in the marketplace, built by
`build-units`, documented in `docs/meow-github.md`, and run by the `test`
verb.

```text
$ python3 -m unittest discover -s plugins/meow-github/tests
Ran 4 tests in 0.397s
OK

$ MEOW_GITHUB_BIN=stub python3 -m unittest discover -s plugins/meow-github/tests
FAILED (failures=2, errors=1)

$ python3 tools/check_standalone.py
88 unit files, 0 paths leaving their unit
```

## Left alone

Onboarding reading the history, which a later decision takes.
