---
id: TSK-4990
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2540
closes: [REQ-2290, REQ-2294, REQ-2296]
issue: 978
projected: 2a1180f411d9
tracked: fff8ef111b82
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Refuse an embedded image and a notation with a build step in the record

`meow-markdown diagrams` prints a finding for an image link to a `.png` or
`.svg` file in a document under the record's root, and `check` reads
`[docs] diagrams` and refuses a notation that needs a build step for the
record, as SPC-1195 states under "Diagrams". One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture record document holding an image link to `flow.png`, when `meow-markdown diagrams` runs, then it prints a finding naming the file and the line and exits 1, and the same link in a document outside the record's root prints nothing (REQ-2290). Closed by: a fixture naming REQ-2290, seen failing first.
2. Given a profile with `[docs] diagrams = "plantuml"`, when `meow-markdown check` runs, then it prints `[docs] diagrams = plantuml needs a build step; the record can't use it` and exits 1 (REQ-2294). Closed by: a fixture naming REQ-2294.
3. Given a profile with `[docs] diagrams = "mermaid"`, or none, when any command reads it, then nothing is reported and `docs.diagrams` isn't an unknown key (REQ-2296). Closed by: a fixture naming REQ-2296 and the profile's test of its table of keys.

## What to do

Add the image rule to `diagrams` and the notation rule to `check` in the
`markdown` feature of `crates/meow/`, reading the record's root as SPC-1070
states. Add `docs.diagrams` to the table of keys in `crates/meow/src/profile.rs`
with its reason, as SPC-1080 states under "The profile". Document the key on
`plugins/meow-markdown/README.md`.

## Depends on

- TSK-4985 (not blocking): the image finding prints from `diagrams`, and either task can add the command's skeleton.

## Evidence

Criterion 1 is closed by `test_tsk_4990_criterion_1_an_image_in_a_record_document_is_a_finding`, `test_tsk_4990_criterion_1_an_svg_image_in_a_record_document_is_a_finding`, `test_tsk_4990_criterion_1_the_same_link_outside_the_record_prints_nothing` and `test_tsk_4990_criterion_1_the_declared_record_root_decides` in `plugins/meow-markdown/tests/test_markdown.py` (REQ-2290), seen failing first. Criterion 2 is closed by `test_tsk_4990_criterion_2_a_notation_with_a_build_step_is_refused_for_the_record` (REQ-2294). Criterion 3 is closed by `test_tsk_4990_criterion_3_mermaid_or_no_notation_is_no_finding_and_no_unknown_key` and the crate test `every_key_in_the_table_carries_a_reason`, which reads `docs.diagrams` in the table of keys (REQ-2296).

The notations refused for the record are a list in `crates/meow/src/markdown.rs` (`plantuml`, `graphviz`, `dot`, `d2`, `structurizr`, `tikz`, `latex`, `drawio`), my choice, because the task names `plantuml` alone; any other string is accepted.

Every stage passed in pull request #1078.

## Left alone

A notation's cost stated outside the record, which review holds because no
program can read whether a document states it.
