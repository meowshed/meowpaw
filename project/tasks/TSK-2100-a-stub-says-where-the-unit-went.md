---
id: TSK-2100
artifact: task
status: done
revised: 2026-09-27
epic: EPC-1370
closes: [REQ-3004]
issue: 437
projected: 79d35b02611c
---

# `meow-method` 0.30.0 is a stub that says where the unit went

The catalogue keeps `meow-method` for one release as a stub whose
`SessionStart` hook tells the session the unit is now `meow-flow`, with the
two commands that move an install, and whose page names the release that
removes it. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the stub, when its `SessionStart` hook runs, then it prints that
   `meow-method` is now `meow-flow`, with `claude plugin install
meow-flow@meowpaw` and `claude plugin uninstall meow-method@meowpaw`, and
   exits 0. Closed by: a fixture naming REQ-3004, seen failing first.
2. Given the stub's page, when a reader opens it, then it says the unit was
   renamed, what to run, and which release removes the stub. Closed by: the
   page, which `tools/check_docs.py` holds.

## What to do

Create `plugins/meow-method/` holding a manifest at 0.30.0, a page, a budget
of no context on every turn, and a `SessionStart` hook printing the notice.
It ships no skill and no program. Keep its catalogue entry. Describe it in
SPC-1070 with REQ-3004.

## Depends on

TSK-2090, because the stub names the unit it creates and takes over the
directory it empties.

## Evidence

`plugins/meow-method/` holds the stub at 0.30.0: a manifest whose description
says it was renamed and costs nothing on every turn, a page, a budget of 0
characters, and a `SessionStart` hook running `hooks/notice`, which prints
that `meow-method` is now `meow-flow`, the two commands that move an install,
and that the release after `meow-flow` 0.31.0 removes the stub, in 243
characters. It ships no skill and no program. Its catalogue entry is back, and
`claude plugin validate` passes on the catalogue and on the stub.

The fixture naming REQ-3004 failed against a notice printing nothing and
passes against this one:

```text
$ MEOW_METHOD_NOTICE=/usr/bin/true python3 -m unittest discover -s plugins/meow-method/tests
FAIL: test_the_notice_says_where_the_unit_went
FAILED (failures=1)
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 3 tests
OK
$ meow-verbs run fmt lint test
summary: fmt passed, lint passed, test passed
```

The stub's page links `meow-flow`'s page by its address, because an installed
stub has no sibling directory to link. `tools/check_standalone.py` read that
address as a path into another unit, which is a false positive, so it now
skips addresses, and a fixture that failed before the change holds it. The
gate caught the defect and this change closes it, so it carries no record of
its own. The troubleshooting page has an entry for the notice, and SPC-1070
names the notice in its boundary.

## Left alone

Removing the stub, which is a task of the release after 0.31.0.
