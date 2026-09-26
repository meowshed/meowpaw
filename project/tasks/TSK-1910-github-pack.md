---
id: TSK-1910
artifact: task
status: approved
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

Not yet.

## Left alone

Onboarding reading the history, which a later decision takes.
