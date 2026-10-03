---
id: TSK-4990
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2540
closes: [REQ-2290, REQ-2294, REQ-2296]
issue:
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

Not yet.

## Left alone

A notation's cost stated outside the record, which review holds because no
program can read whether a document states it.
