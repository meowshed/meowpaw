---
id: TSK-5135
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2565
closes: [REQ-2416, REQ-2418, REQ-2450]
issue: 1004
projected: fbd794733bd1
tracked: f4732e446745
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Hold what a pack keeps in the shared pack layer

The shared pack layer keeps what a run produced, as SPC-1190 states under
"What a pack keeps". One task, one branch, one pull request, one review: the
tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture ecosystem with a machine-readable report format, when the
   pack runs a verb, then the result is collected in that format, and for
   one with none the report says the evidence is captured output
   (REQ-2416). Closed by: a crate test naming REQ-2416, seen failing first.
2. Given a fixture tool that deletes its files unless asked, when the pack
   runs it, then the files are kept and the report names where (REQ-2418).
   Closed by: a crate test naming REQ-2418.
3. Given the shared layer, when a pack's document is checked, then a pack
   whose document doesn't state which generated files are state to commit
   and which are cache to ignore fails the layer's test (REQ-2450). Closed
   by: a crate test naming REQ-2450.

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

1. `tsk_5135_criterion_1_a_result_is_collected_in_the_ecosystems_format` and
   `tsk_5135_criterion_1_with_no_format_the_evidence_is_captured_output`
   (REQ-2416), through `run_in` with a `Format`. `meow-markdown links` names
   lychee's JSON report as its evidence, which
   `test_tsk_5135_links_names_the_format_its_evidence_is_read_from` in
   `plugins/meow-markdown/tests/test_markdown.py` holds.
2. `tsk_5135_criterion_2_files_the_tool_deletes_are_kept_and_named`
   (REQ-2418), through `Invocation::keeping`.
3. `tsk_5135_criterion_3_a_document_without_the_generated_files_fails` and
   `tsk_5135_criterion_3_every_language_pack_states_its_generated_files`
   (REQ-2450), through `states_generated_files`; the second reads the page of
   every unit whose manifest carries the `language` keyword, and
   `plugins/meow-markdown/README.md` gains its `Generated files` section, as
   the Pi package's page does.

lychee deletes no file a run would keep, so `meow-markdown` asks for none.

Every stage passed in pull request #PR.

## Left alone

Each ecosystem's report format, which each pack's own document names.
