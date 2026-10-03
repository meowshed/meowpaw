---
id: TSK-5125
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2565
closes: [REQ-2410, REQ-2412, REQ-2414, REQ-2432, REQ-2436, REQ-2444]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold what a pack reports it didn't check in the shared pack layer

The shared pack layer reports what a bound verb leaves unchecked, as SPC-1190
states under "What a pack reports it didn't check". One task, one branch, one
pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given a fixture pack whose bound tool covers less than the ecosystem's
   default, when it reports, then it names what is no longer checked, or its
   binding runs the rest (REQ-2410). Closed by: a crate test naming REQ-2410,
   seen failing first.
2. Given a fixture language that runs documentation examples as tests, when
   the pack binds `test`, then the command runs them, and a binding to a
   runner that leaves them out fails the layer's test (REQ-2412). Closed by:
   a crate test naming REQ-2412.
3. Given a fixture language with a defect detector, when the pack binds
   `test`, then the detector is on, and a profile turning it off is named in
   the report (REQ-2414). Closed by: a crate test naming REQ-2414.
4. Given a clean fixture run, when the pack reports it, then the report names
   the rule groups enabled and the severity level it ran at (REQ-2432,
   REQ-2444). Closed by: a crate test naming both.
5. Given a fixture supply-chain check, when the pack reports it, then it
   states whether it covers transitive dependencies and whether it reports
   presence or reachability (REQ-2436). Closed by: a crate test naming
   REQ-2436.

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

Which detector each language ships, which each pack's own document names.
