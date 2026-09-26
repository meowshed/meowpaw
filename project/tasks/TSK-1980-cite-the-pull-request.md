---
id: TSK-1980
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1320
closes: [REQ-3176]
issue: 383
projected: fe212fdcf779
---

# The record cites a pull request, never a commit hash

The record cites a pull request, never a commit hash, as ADR-1320 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record gaining a line citing a check's revision by hash, when `check frozen` runs, then it reports the line. Closed by: a fixture.
2. Given the same line citing a pull request, when it runs, then it passes. Closed by: a fixture.

## What to do

In `meow-method check frozen`, report a line added since the base, outside the front matter, citing a hash of seven to forty hexadecimal digits after "at" or "revision". Change the verification's wording to cite the pull request.

## Depends on

Nothing. ADR-1320 is approved.

## Evidence

`meow-method check frozen` now reads every record's lines added since the
base, outside the front matter, and reports one citing a hash of seven to
forty hexadecimal digits, holding a digit and a letter, after "at" or
"revision". It reads only added lines, so an approved record keeps what it
said. Two fixtures on a committed record: a task's evidence gaining "passed at
`9f3c2e1`" is reported, exit 1, and fails against a stub that returns
nothing; the same line citing the trunk after a pull request, beside a
hex-looking word, passes.

Run from a base fifteen commits back, the check reports 8 lines: the
two hash citations in each of the four verifications written since, and
nothing else. The verify step gains V12, naming the revision by the pull
request that last merged, and the verification this repository writes now
reads "on the trunk after #N".

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 119 tests in 9.148s
OK

$ MEOW_METHOD_BIN=stub python3 -m unittest plugins/meow-method/tests/test_record.py -k citing_a_hash
FAILED (failures=1)
```

## Left alone

A version control tool other than git, which ADR-1320 leaves.
