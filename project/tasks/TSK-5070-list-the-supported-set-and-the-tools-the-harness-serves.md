---
id: TSK-5070
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2560
closes: [REQ-2330, REQ-2358, REQ-2360, REQ-2364]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# List the supported set, and document the code host, the tracker and the worktree manager

`docs/README.md` carries the supported set, a table of every language and
tool the harness supports with its pack and its state, as SPC-1110 states,
and the pages say how `meow-github` serves GitHub and its issues and how
worktrunk is used. One task, one branch, one pull request, one review: the
tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given `docs/README.md`, when `tools/check_docs.py` runs, then it finds a
   supported set table naming Rust, TypeScript and JavaScript, Python, Go,
   C#, Lua, Neovim plugins, Godot and GDScript, Starlark, Scheme, Markdown,
   GitHub, GitHub Issues and worktrunk, each with a pack and a state of
   `shipped`, `planned` or `postponed`, and fails on a row with another state
   or no pack (REQ-2330). Closed by: a test in `tools/test_check_docs.py`
   naming REQ-2330, seen failing first.
2. Given `plugins/meow-github/README.md`, when a reader looks for the code
   host and the tracker, then the page says the unit creates, links and
   reads back the issues an epic projects onto, and projects the record as a
   mapping from each task to its issue (REQ-2358, REQ-2360). Closed by:
   judgement, because a page's claim about behaviour is read and not
   matched; the existing `project` fixtures hold the behaviour.
3. Given `plugins/meow-scm/skills/commit/SKILL.md` and its unit's page, when
   a reader looks for the worktree manager, then they say worktrunk is used
   only through operations whose result the harness reads from git
   (REQ-2364). Closed by: a test under `plugins/meow-scm/tests/` naming
   REQ-2364.

## What to do

Add the table to `docs/README.md` as SPC-1110 states under "What the
documentation covers". It sits in the index and on no other page, because
REQ-3132 keeps planned material off every page but the index, where
REQ-3134 names unbuilt parts. A planned row names a pack and no behaviour.
Teach `tools/check_docs.py` the table's states. Add the sentences on GitHub,
GitHub Issues and worktrunk to the pages named above, as SPC-1080 states
under "Projecting the record onto a tracker" and SPC-1060 under "Tools that
run operations". Version control other than git gets the row `postponed`.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

Each pack's own page, which ships with its pack, and moving a row to
`shipped`, which each pack's task does.
