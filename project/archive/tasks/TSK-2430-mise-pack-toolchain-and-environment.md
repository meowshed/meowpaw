---
id: TSK-2430
artifact: task
status: done
revised: 2026-09-27
epic: EPC-1550
closes: [REQ-2482, REQ-2490, REQ-2506]
issue: 580
projected: 3d1d09af6f67
---

# Report the pinned tools, the environment's files and idiomatic version files

`meow-mise status` names what mise carries beyond tasks: the tools a committed
file pins, the files mise loads configuration and environment from, and each
idiomatic version file mise may leave unread, as SPC-1140 states. One task,
one branch, one pull request, one review.

## Acceptance criteria

1. Given a committed `mise.toml` with `[tools]` and a committed `mise.lock`,
   when `status` runs, then each tool is named with its version and file, and
   the lock is named. Closed by: a fixture naming REQ-2482, seen failing
   first.
2. Given `[env]` with `_.file` and `_.source` and a value, when `status`
   runs, then each file and each path `mise config ls` lists is named, and
   the value isn't printed. Closed by: a fixture naming REQ-2490.
3. Given a `.python-version` and the default setting, when `status` runs,
   then the file is `possibly inert`; with the setting naming `python`, it
   isn't. Closed by: a fixture naming REQ-2506.

## What to do

Extend `status` in the `mise` module, reading committed configuration files
as TOML and printing paths and tool versions only.

## Depends on

TSK-2420, which ships the unit and `status`.

## Evidence

Closes REQ-2482, REQ-2490 and REQ-2506. The five fixtures in the `Carried`
class of `plugins/meow-mise/tests/test_mise.py` failed first against the unit
TSK-2420 shipped, and pass now, with the whole file's 26. `meow-verbs evidence
--keep format lint test` exits 0 on this change's own tree, each result kept
in `project/evidence/`, as the pull request cites.

## Left alone

Reading any value an environment file or `[env]` holds, which REQ-2490
keeps unread.
