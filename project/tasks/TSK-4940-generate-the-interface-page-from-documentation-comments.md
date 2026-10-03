---
id: TSK-4940
artifact: task
status: approved
revised: 2026-10-03
realises: ADR-2490
closes: [REQ-2992]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Generate the interface page from documentation comments, and check it against the tool

`meow interface` prints `docs/interface.md` from the documentation comments on
what the tool parses and reads, and a crate test regenerates the page and
fails where the committed one differs, as SPC-1080 states under "The public
interface" and SPC-1110 states for the page. It realises ADR-2490 as ADR-2720
amends it. One task, one branch, one pull request, one review: the tests
first, then the change, its documentation and its marks.

## Acceptance criteria

Taken from ADR-2490's and ADR-2720's lists of how each will be known
realised:

1. Given this repository, when `meow interface` runs, then its output is
   `docs/interface.md` byte for byte, and the page names each of the six
   parts REQ-2992 lists: the verbs and their outcomes, the artifact kinds and
   their front matter, the record's paths and identifier formats, the
   profile's keys, every subcommand and the form of a piece of evidence
   (REQ-2992). Closed by: a crate test naming REQ-2992, seen failing first.
2. Given a fixture subcommand added with a documentation comment and the page
   not regenerated, when the crate's tests run, then the page test fails
   naming the subcommand. Closed by: a crate test.
3. Given a fixture profile key added to the table of keys with no
   documentation comment, when the crate's tests run, then they fail naming
   the key. Closed by: a crate test.
4. Given the generated page, when `tools/check_docs.py` runs, then it passes,
   because the page carries the four front matter fields SPC-1110 states with
   `kind: reference`. Closed by: the gate's `test` verb.

## What to do

Add the generator to `crates/meow/` as `meow interface`, reading the items it
already parses and reads: the subcommands, each verb's outcomes, the kinds
and their fields in `lib/layout.toml`, the layout's paths and identifier
formats, the table of keys in `crates/meow/src/profile.rs` and the ledger's
record. Each entry's text is its item's documentation comment, so write or
rewrite each comment as the reason a reader needs. Commit the first
generated page. State on `plugins/meow-flow/README.md` and `docs/README.md`
that the page is generated and how to regenerate it. ADR-2490 named the
retired document step as the page's writer; this task writes it in its
place.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The skills' wording, which isn't part of the interface, and when the harness
leaves major version zero, which ADR-2490 leaves open.
