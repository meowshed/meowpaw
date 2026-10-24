---
id: TSK-4985
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2540
closes: [REQ-2292, REQ-2304]
issue: 977
projected: c31f31ee3c5d
tracked: 8232bda09d2a
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Parse each Mermaid block, and fail the `check` verb on one that doesn't parse

`meow-markdown diagrams` parses each `mermaid` block in the tracked Markdown
with `mmdc`, writing its output outside the working tree, and `bind` prints
`check = "meow-markdown diagrams"` where the corpus holds one, as SPC-1195
states under "Diagrams". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository with a Markdown file holding a `mermaid` block that doesn't parse, when `meow-markdown diagrams` runs, then it prints a finding naming the file, the line and the parser's words and exits 1 (REQ-2304). Closed by: a fixture under `plugins/meow-markdown/tests/` naming REQ-2304, seen failing first.
2. Given the same repository with the block fixed, when `diagrams` runs, then it exits 0 and `git status --porcelain` prints nothing afterwards. Closed by: a fixture under `plugins/meow-markdown/tests/`.
3. Given a repository with no `[docs] diagrams` and a `mermaid` block, when `bind` runs, then it prints `check = "meow-markdown diagrams"` in place of the line saying Markdown has no types, and with no `mermaid` block it prints that line as it does today (REQ-2292). Closed by: a fixture naming REQ-2292.
4. Given a machine with no `mmdc` on `PATH`, when `diagrams` runs, then it prints `tool absent: mmdc` and exits 3. Closed by: a fixture.

## What to do

Add `diagrams` to the `markdown` feature of `crates/meow/`, classifying `mmdc`'s
results as SPC-1190 states under "A check that reaches outside the
repository". Pin `mmdc` in `mise.toml` where this repository's own `check`
verb comes to run it, and state the cost ADR-2620 names, a headless browser,
on `plugins/meow-markdown/README.md` with the version observed.

## Depends on

Nothing.

## Evidence

Criteria 1 and 2 are closed by `test_tsk_4985_criterion_1_a_block_that_does_not_parse_is_a_finding`, `test_tsk_4985_criterion_1_inputs_limit_the_files_parsed` and `test_tsk_4985_criterion_2_a_block_that_parses_exits_0_and_leaves_the_tree_alone` in `plugins/meow-markdown/tests/test_markdown.py` (REQ-2304), seen failing first. Criterion 3 is closed by `test_tsk_4985_criterion_3_a_mermaid_block_binds_check_to_diagrams` and `test_tsk_4985_criterion_3_no_mermaid_block_keeps_the_unresolved_line` (REQ-2292). Criterion 4 is closed by `test_tsk_4985_criterion_4_no_mmdc_is_tool_absent`. `unit_help` holds the new subcommand's output to the words its help states.

The fixtures run a stand-in `mmdc`, since none is installed on the machine that wrote this, so the real tool's wording and exit statuses are assumed from its documentation and not observed. The README says so and gives no version for `mmdc`. Pinning `mmdc` in `mise.toml` waits, as the task's Left alone says, until this repository's own `check` verb runs it.

Every stage passed in pull request #1078.

## Left alone

Binding this repository's own `check` verb to `diagrams`, which waits until a
record document carries a Mermaid block.
