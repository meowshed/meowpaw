---
id: BUG-1210
artifact: bug
status: approved
severity: major
violates: REQ-1382
enters: implement
found: 2026-09-27
revised: 2026-09-27
issue: 508
---

# `meow-github project` writes no `issue:` into a task that lacks the field, so a replay opens a duplicate issue

## Reproduction

With `meow-github` 0.4.1 on macOS, on the trunk after #507, using the fixture
repository in `plugins/meow-github/tests/test_github.py`, whose fake `gh`
records every issue it is asked to open:

1. Remove the `issue:` line from `TSK-0001`'s front matter.
2. Run `meow-github project EPC-0001 o/r`.
3. Run it again.

```text
TSK-0001: projected to issue #3 at 35732234dd3b, read back
TSK-0002: unchanged, issue #2 at 7bf01c8b72d9
issues: 3
```

## What the system does

The first run opens issue #1 for `TSK-0001` and writes `projected:` into the
task, but no `issue:`, because the writer replaces an `issue:` line and never
adds one. The second run finds no mapping on the task and opens issue #3 for
the same task. It happened for real on TSK-2240 and TSK-2250, which were
written without the field; I added `issue: 502` and `issue: 503` by hand
before anything replayed.

## What it should do, and why

REQ-1382 records the mapping on the task itself, and REQ-1386 makes a replayed
projection no action instead of a duplicate. A task missing the optional field
is still a task the program projected, so the program writes `issue:` beside
`projected:` wherever the field is absent, as it already does for
`projected:`.

## Triage

It violates REQ-1382 and REQ-1386, so it enters at implementation and needs no
decision. Major, because a replay publishes a duplicate issue on the code
host, which nobody can take back without closing it by hand, and the template
carrying `issue:` is the only thing that has prevented it so far.

## Closed by

Not yet.

## Tasks

- [ ] T-001 TSK-2260 write `issue:` when projecting a task that lacks it, in
      `crates/meow/src/github/project.rs`
