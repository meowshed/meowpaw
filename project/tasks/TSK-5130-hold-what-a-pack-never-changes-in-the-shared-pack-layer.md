---
id: TSK-5130
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2565
closes: [REQ-2430, REQ-2440, REQ-2442]
issue:
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

Not yet.

## Left alone

Where outside the tree a pack points its tool's output, which each pack's own
document states.
