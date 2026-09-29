---
id: EPC-1800
artifact: epic
status: approved
revised: 2026-09-28
realises: ADR-1900
checked-at: "#624"
---

# A Markdown pack binds the verbs from the configuration, checks the settings behind them, and reports an unreachable link as unreachable

Realises exactly one authorising record, ADR-1900. The epic is complete when
`meow-markdown` ships with `status`, `bind`, `check` and `links`, a skill and
`reviewing.md`, each doing what SPC-1195 states and held by fixtures, and this
repository declares its render target and runs `meow-markdown check` in its
`lint` verb.

## Acceptance criteria

Taken from ADR-1900, from its list of how I will know it was realised, before
the tasks below were written:

1. A fixture repository with two tracked `*.md` files is detected, one with a
   lone `README.md` isn't, and one with a lone README and a
   `.markdownlint.yaml` is.
2. Fixtures show `bind` printing `lint` for a `.markdownlint-cli2.yaml`, with
   `meow-markdown check` named in a comment, `lint` as `meow-markdown check`
   where no linter is configured, `format` for a `.prettierrc`, `check` as
   unresolved with its reason, `test` for a `lychee.toml`, `build` as unbound
   naming `mkdocs.yml` where one exists, and nothing for a verb the profile
   already declares. Another shows a `mise.toml` named with a pointer to the
   runner's pack.
3. `check` exits 1 naming the missing target where the profile has no
   `[markdown] target`, and 0 on a profile declaring `github` or `forgejo`.
4. `check` exits 1 on a `lint` verb running markdownlint-cli2 with no
   configuration, on one running `markdownlint` beside a
   `.markdownlint-cli2.jsonc`, naming the file, and on a directory holding both
   configuration families. This repository's `.markdownlint-cli2.yaml` is
   listed by `status` as read by markdownlint-cli2.
5. `check` exits 1 naming `max_retries` on a `lychee.toml` without it, 0 on one
   declaring all three settings, and 0 where a verb running `lychee` directly
   passes `--offline --max-retries 0 --cache=false`.
6. A stand-in lychee printing RES-0294's JSON with a timeout and a failed
   connection makes `links` print both as `unreachable` and exit 3, as do a
   403 and a 503. A 404 or a missing relative file exits 1 as a finding, a mix
   exits 1 with the unreachable addresses listed apart, a run with only
   excluded addresses prints them as `skipped` and exits 0, and no lychee on
   `PATH` prints `tool absent` and exits 3. A stand-in exiting 3, one printing
   text that isn't JSON, and one printing RES-0294's JSON with `timeout_map`
   renamed each make `links` print `tool broken` and exit 3. A stand-in whose
   JSON holds a rejected 3xx response prints `unresolved` and exits 3. One run
   against the real lychee on a fixture with a missing relative file exits 1.
7. A test reads `reviewing.md` and finds each of RES-0111's reviewer points.
8. `git status --porcelain --ignored` reads the same before and after `status`,
   `bind` and `check`.
9. Every requirement ADR-1900 addresses lands in exactly one closed task, and
   REQ-2424 and REQ-2484 read as postponed.

Criterion 8 is held by TSK-3100 for `status` and `bind` and by TSK-3110 for
`check`. Criterion 9 is closed by `paw check coverage` and `paw show` on the
decision once the tasks close.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number, as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-3100 ship `meow-markdown` with detection, `status` and `bind`,
      in `plugins/meow-markdown` and the `markdown` feature of `crates/meow`
      closes: REQ-2352
      evidence: 13 checks seen failing at the cover commit 593222a, and
      passing unchanged in #651.

- [x] T-002 [P] TSK-3110 `check` the render target and the markdownlint
      settings, and adopt it in this repository's profile
      closes: REQ-2434, REQ-2452
      depends: TSK-3100 - the program and its detection must exist
      evidence: 14 checks seen failing at the cover commit b9acb6f, and
      passing unchanged in #665.

- [x] T-003 [P] TSK-3120 `links`, and `check` the link check's settings
      closes: REQ-2438, REQ-2454
      depends: TSK-3100 - the program and its detection must exist
      evidence: 13 checks seen failing at the cover commit 97915b4, and
      passing unchanged in #671.

- [x] T-004 [P] TSK-3130 the skill's body and `reviewing.md`
      closes: REQ-0083
      depends: TSK-3100 - the unit and its skill file must exist
      evidence: 7 checks seen failing at the cover commit 4142a15, and
      passing unchanged in #677.

## Verified

I checked this under #624 on `main` after #677, gathering the evidence there
and carrying none over from the tasks. `meow-verbs evidence --keep format lint
check test build` runs on this change's own tree, each result kept in
`project/evidence/`, as the pull request cites. The 47 fixtures in
`plugins/meow-markdown/tests/test_markdown.py` run 47, OK, with one skipped:
the `test` verb has no lychee on `PATH`, so it skips
`Links.test_criterion_5_the_real_lychee_reports_a_missing_file`. I ran that
fixture again under `mise exec lychee@0.24.2`, and it passes against lychee
0.24.2. Every criterion is met:

| Criterion                                                                                                                                                         | Evidence on `main` after #677                                                                                                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Two tracked `*.md` files are detected, a lone `README.md` isn't, and a lone README beside a `.markdownlint.yaml` is                                            | The three `Detection` fixtures pass                                                                                                                                                                                                               |
| 2. `bind` prints each verb from the configuration it finds, nothing for a declared verb, and names a `mise.toml` with a pointer                                   | The seven `Bind` fixtures and `Runner.test_criterion_3_a_mise_toml_is_named_with_the_mise_pack` pass                                                                                                                                              |
| 3. `check` exits 1 naming a missing render target, and 0 on `github` or `forgejo`                                                                                 | The three `RenderTarget` fixtures pass                                                                                                                                                                                                            |
| 4. `check` finds markdownlint settings the `lint` verb lacks, ignores or never applies, and `status` lists `.markdownlint-cli2.yaml` as read by markdownlint-cli2 | The six `MarkdownlintSettings` fixtures and `Status.test_criterion_4_a_markdownlint_cli2_file_is_read_by_cli2_alone` pass. `meow-markdown status` on this repository prints `.markdownlint-cli2.yaml: read by markdownlint-cli2 alone`, exiting 0 |
| 5. `check` names a `lychee.toml` without `max_retries`, and passes all three settings in the file or the flags                                                    | The four `LinkSettings` fixtures pass                                                                                                                                                                                                             |
| 6. `links` tells unreachable, finding, skipped, tool absent, tool broken and unresolved apart, and the real lychee exits 1 on a missing file                      | The nine `Links` fixtures pass, the real-lychee one under `mise exec lychee@0.24.2` only                                                                                                                                                          |
| 7. A test finds each of RES-0111's reviewer points in `reviewing.md`                                                                                              | `Reviewing.test_criterion_1_reviewing_carries_each_reviewer_point` passes                                                                                                                                                                         |
| 8. `git status --porcelain --ignored` reads the same before and after `status`, `bind` and `check`                                                                | `Tree.test_criterion_5_status_and_bind_leave_the_tree_as_it_was` and `CheckTree.test_criterion_6_check_leaves_the_tree_as_it_was` pass                                                                                                            |
| 9. Every requirement lands in one closed task, and REQ-2424 and REQ-2484 read as postponed                                                                        | `paw show` derives REQ-2352 as closed by TSK-3100, REQ-2434 and REQ-2452 by TSK-3110, REQ-2438 and REQ-2454 by TSK-3120 and REQ-0083 by TSK-3130, and REQ-2424 and REQ-2484 as postponed by ADR-1900. `paw check coverage` reports 0 findings     |

Each fixture above asserts the exit status and the line the program prints, so
each would fail if the program broke its requirement. I judged that by reading
the assertions and didn't break the program to watch them fail.

The real-lychee half of criterion 6 is held by a fixture the `test` verb skips
on a machine with no lychee, and this repository's `mise.toml` installs none.
The criterion is met, because the run under #624 passed, but the gate doesn't
hold it: a later change that breaks the real run passes the gate unseen.
Declaring lychee as a tool in `mise.toml` would make the gate run it.

### Documentation

`plugins/meow-markdown/README.md` describes `status`, `bind`, `check` and
`links`, each binding and each exit status, and the documentation index lists
the unit. The `test` verb checked the pages.

### Postponements

REQ-2424 stays postponed until an approved decision gives a pack a command
that writes or edits a tool's configuration file; `paw find` finds none.
REQ-2484 stays postponed until the first pack for an ecosystem whose manifest
declares scripts; `meow-markdown` is the only language pack in `plugins/`.

## Coverage

ADR-1900 addresses 6 requirements, REQ-0083, REQ-2352, REQ-2434, REQ-2438,
REQ-2452 and REQ-2454, and each lands in exactly one task above. T-002, T-003
and T-004 can run in parallel once T-001 lands, and T-002 and T-003 both touch
`check`, so the second to merge rebases onto the first.

The smallest set that tests the decision is T-001 and T-003: detection and a
`links` that tells an unreachable site from a broken link, which is the claim
RES-0294 makes and no tool's exit status can. The first thing measurable before
the epic ends is criterion 6 run against RES-0294's recorded JSON.

## Not covered

REQ-2424, which ADR-1900 postpones until an approved decision gives a pack a
command that writes or edits a tool's configuration file.

REQ-2484, which ADR-1900 postpones again until the first pack for an ecosystem
whose manifest declares scripts.

What ADR-1900 leaves unsettled stays out: spelling and its word list, Vale,
parsing fenced diagrams, binding `build`, remark-lint or textlint, reading a
runner's tasks to see which tool a verb reaches, a shared detector for every
language pack, and how `meow-verbs` reports a `test` verb whose command exited 3.
