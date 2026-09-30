---
id: TSK-3310
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1900
closes: [REQ-2392]
issue: 655
projected: fe418aa78fc2
---

# Make `meow-unattended plan` load each unit by name, and refuse what would load by discovery

`plan` accepts a `units` entry only where it is a directory holding
`.claude-plugin/plugin.json`, refuses a URL and a folder of units, refuses a
repository whose `.claude` settings carry an `env` block, and names each unit
with its version in its output and in the snapshot. With `--bare`, the run
then loads exactly the units named and nothing by discovery, which is what
REQ-2392 asks. One task, one branch, one pull request, one review.

## Acceptance criteria

Every check below lives in `plugins/meow-unattended/tests/test_unattended.py`
and counts what it matched, failing on a count of zero where one was expected
(EPC-1900 criterion 9).

1. Given a `units` entry that is an `https://` URL, and one that is a folder
   holding two units but no `.claude-plugin/plugin.json` of its own, when
   `plan` runs on each, then it prints `unresolved` naming the entry and
   exits 3, and writes no snapshot. Closed by:
   `Units.test_url_and_folder_refused`.
2. Given three declared units, when `plan` runs, then the command line holds
   `--bare` and exactly three `--plugin-dir` arguments, one for each unit in
   the declared order, and the output and the snapshot name each unit with
   the `name` and `version` its `plugin.json` holds. Closed by:
   `Units.test_one_plugin_dir_for_each_unit`.
3. Given a fixture repository with a server in `.mcp.json` and a hook in
   `.claude/settings.json`, when `plan` runs, then neither the command line
   nor the snapshot names the server or the hook. Closed by:
   `Units.test_repository_hooks_and_servers_not_named`.
4. Given an `env` block with two keys in `.claude/settings.json`, and in
   another fixture in `.claude/settings.local.json`, when `plan` runs, then
   it prints `unresolved` naming the file and both keys and exits 3. Closed
   by: `Refusals.test_env_block_refused`.
5. Given this change's tree, when `meow-verbs run format lint check test
build` runs, then each passes. Closed by: the kept evidence of that run.

## What to do

Extend the program TSK-3300 adds, as SPC-1200's sections "The command line",
"The snapshot" and "Failure paths" state. A unit entry resolves against the
work tree's root. `plan` reports every refusal it finds before it exits.
Read each unit's `name` and `version` from its `plugin.json`, and add them to
the snapshot and to the output after the resolved table.

Raise `meow-unattended`'s minor version in `plugin.json`, and its README's
`describes:` with it, because `plan` gains refusals and output. Update the
README where it describes what `plan` accepts in `units`.

Write the checks first, in a commit of their own, and see them fail.

## Depends on

TSK-3300, because this task extends the program, the table reader and the
snapshot that task adds.

## Evidence

`crates/meow/src/unattended.rs` now reads each `units` entry against the work
tree's root. It refuses an entry holding `://` as a URL, and one with no
`.claude-plugin/plugin.json` as not a unit's own directory, which covers a
folder of units. It reads the unit's `name` and `version` from that file,
prints them after the resolved table, and stores them in the snapshot under
`meowpaw.units`. It refuses an `env` block with at least one key in
`.claude/settings.json` or `.claude/settings.local.json` on one line naming
every key, and reports these refusals together with the table's own before it
exits. `meow-unattended` is 0.2.0, and its README states what `units` accepts
and the new refusals.

The four checks failed first: `meow-verbs run test` exited 1 with
`FAILED (failures=11)` for the unit's file, counting the subtests, kept as
`project/evidence/4acbe0e3935f.txt` in the cover commit fa22b5f, which became
eac3884 when the branch was rebased onto `origin/main`. They pass now,
unchanged, since
`git diff fa22b5f42020bca44a9e09ac48e2b0bee18bce63 -- plugins/meow-unattended/tests/test_unattended.py`
prints nothing:

```text
$ python3 -m unittest -v test_unattended.Units.test_url_and_folder_refused \
    test_unattended.Units.test_one_plugin_dir_for_each_unit \
    test_unattended.Units.test_repository_hooks_and_servers_not_named \
    test_unattended.Refusals.test_env_block_refused    # in plugins/meow-unattended/tests
Ran 4 tests
OK                                                    # exit 0
$ python3 -m unittest plugins/meow-unattended/tests/test_unattended.py
Ran 17 tests
OK                                                    # exit 0
```

Criterion 3's check fails first only on its control, as the Cover's Judgement
says, so what it shows is that the snapshot names each unit with its version
and still names no server or hook. Criterion 5: `meow-verbs run format lint
check test build` passes on this change's tree, and
`meow-verbs evidence --keep` keeps each result in `project/evidence/`, as the
pull request cites.

SPC-1200 didn't state what `plan` does with a `plugin.json` that lacks a
`name` or a `version`, so I chose to refuse it as
`unresolved: unit <entry> has a plugin.json that states no name and version`,
because the plan would otherwise name a unit it can't identify, and SPC-1200
now states it. A settings file that isn't valid JSON is read as holding no
`env` block, because Claude Code refuses that file on its own.

## Left alone

Checking at start that the run loaded the units the snapshot names, and
repeating the `env` refusal at start, which ADR-2000 gives to the decision
that starts a run. A unit loaded from a URL with a checksum, which ADR-2000
names as what would reverse it. `docs/README.md` and the root `README.md`,
which the document step updates.
