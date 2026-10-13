---
id: TSK-5130
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2565
closes: [REQ-2430, REQ-2440, REQ-2442]
issue: 1003
projected: 7b3be549289a
tracked: 2ed214e5567d
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold what a pack never changes in the shared pack layer

The shared pack layer applies no unsafe fix and no modernising suggestion,
and leaves no file in the working tree, as SPC-1190 states under "What a pack
never changes". One task, one branch, one pull request, one review: the tests
first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture tool that marks one fix unsafe, when the pack runs its
   fixing verb, then that fix isn't applied and is reported (REQ-2430).
   Closed by: a crate test naming REQ-2430, seen failing first.
2. Given a fixture tool that suggests a newer language feature, when the pack
   runs a check, then the suggestion is reported and the file is unchanged
   (REQ-2440). Closed by: a crate test naming REQ-2440.
3. Given a fixture tool that writes output into the working directory by
   default, when the pack runs the verb, then `git status --porcelain` is
   empty afterwards and the output sits outside the tree (REQ-2442). Closed
   by: a crate test naming REQ-2442.

## What to do

Add the rules to a shared layer in `crates/meow/` that every language pack's
feature uses, so a pack meets them by using the layer and not by restating
them. Hold each rule with a fixture pack in the crate's tests that breaks it.
Move `meow-markdown` onto the layer wherever a rule applies to Markdown, and
leave its behaviour SPC-1195 states unchanged. Document the layer's rules on
`plugins/meow-markdown/README.md` only where they change what that pack
reports.

## Depends on

- TSK-5120 (not blocking): both add rules to the same shared layer, and
  either can land first.

## Evidence

Each criterion closes with a crate test in `crates/meow/src/pack.rs`, each
seen failing against stubbed bodies before the rule was written:

1. `tsk_5130_criterion_1_a_fix_marked_unsafe_is_reported_and_not_applied`
   (REQ-2430), through `apply` in `Mode::Fix`.
2. `tsk_5130_criterion_2_a_suggestion_is_reported_and_the_file_unchanged`
   (REQ-2440), through `apply` in `Mode::Check`.
3. `tsk_5130_criterion_3_output_goes_outside_and_the_tree_stays_clean` and
   `tsk_5130_criterion_3_a_file_left_in_the_tree_is_named` (REQ-2442),
   through `run_in`, with a fixture tool writing into the working directory
   by default. `tsk_5130_an_absent_tool_is_reported_as_absent` holds
   SPC-1190's `tool absent` line for a run.

`meow-markdown links` runs lychee through `run`, and
`test_tsk_5130_a_file_lychee_leaves_in_the_tree_is_named` in
`plugins/meow-markdown/tests/test_markdown.py` holds the line naming a file
the run left. Markdown proposes no fixes, so `apply` has no caller in
`meow-markdown`; lychee writes `.lycheecache` at the root with no flag to
move it, so `links` names it where it shows in `git status` and `check`
keeps reporting an unignored cache, as SPC-1195 states.

Every stage passed in pull request #1072.

## Left alone

Where outside the tree a pack points its tool's output, which each pack's own
document states.
