---
id: TSK-4650
artifact: task
status: approved
revised: 2026-10-03
realises: ADR-2530
closes: [REQ-2206, REQ-2208, REQ-2210, REQ-2212]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Check the sign-off route, the trailers that name a person and the breaking mark

`meow-scm check-message` gains the three rules SPC-1050 states, the profile
gains `[commits] may_name`, and a test holds that every commit reaches the
trunk through the gate, as SPC-1060 states. One task, one branch, one pull
request, one review: the tests first, then the change, its documentation and
its marks.

## Acceptance criteria

1. Given a message whose first `Signed-off-by` names someone other than the
   author git reports, when `check-message` runs, then it exits 1 naming the
   sign-off route, and given one whose first names the author and whose
   second names someone else, it passes that rule (REQ-2206). Closed by: a
   crate test naming REQ-2206, seen failing first.
2. Given a message with `Co-authored-by: Ada Lovelace <ada@example.org>`, when
   `check-message` runs with a profile whose `may_name` lacks her, then it
   exits 1 naming the trailer, and with her listed it passes; `Fixes` and
   `Cherry-picked-from` pass with no list (REQ-2208). Closed by: a crate test
   naming REQ-2208.
3. Given a subject `feat!: drop the old flag` and no `BREAKING CHANGE:`
   trailer, when `check-message` runs, then it exits 1 naming the breaking
   mark, and the same for a type the profile maps to `major` (REQ-2212).
   Closed by: a crate test naming REQ-2212.
4. Given `.github/workflows/ci.yml`, when a test reads it, then a job
   triggered by `pull_request` and by a push to the trunk runs `mise run all`
   (REQ-2210). Closed by: a test under `tools/` naming REQ-2210.
5. Given a profile with `[commits] may_name`, when any command reads it, then
   the key isn't reported as unknown. Closed by: the profile's test of its
   table of keys.

## What to do

Change the sign-off rule in `crates/meow/src/scm.rs` from "every sign-off
names the author" to "the first names the author", keeping the line that
reports the rule as not compared where git reports no author. Add the named
person and breaking mark rules, reading `may_name` and the type's meaning from
`[commits]`. Add `commits.may_name` to the table of keys in
`crates/meow/src/profile.rs` with its reason. `convention` prints the list.

In `plugins/meow-scm/skills/commit/SKILL.md`, name the three exempt trailers
beside the rule that a trailer naming a person needs that person's agreement,
and hold the change to SPC-1030 and the unit's `budget.toml`. Document the
key and the rules on `plugins/meow-scm/README.md`.

## Depends on

Nothing.

## Evidence

`check-message` in `crates/meow/src/scm.rs` compares the first
`Signed-off-by` alone with the author, as the `sign-off route`. It fails a
trailer whose value is `Name <address>` as a `named person` unless
`[commits] may_name` lists that person, exempting `Fixes`,
`Cherry-picked-from`, the first sign-off and any sign-off naming the author.
It fails a subject carrying `!`, or a type meaning `major`, with no
`BREAKING CHANGE:` trailer as a `breaking mark`. `convention` prints the
`may_name` list.

Each criterion is closed by the checks it names:

1. `scm::tests::the_first_sign_off_names_the_author`,
   `a_lower_case_sign_off_is_still_a_sign_off` and
   `a_sign_off_in_the_body_is_not_the_first` (REQ-2206)
2. `scm::tests::a_trailer_naming_a_person_needs_them_listed`,
   `a_later_sign_off_names_a_person`, `the_provenance_trailers_need_no_list`,
   `a_body_line_names_nobody` and `a_malformed_list_names_nobody`, with
   `test_a_co_author_nobody_listed_is_refused` and
   `test_convention_lists_who_may_be_named` in
   `plugins/meow-scm/tests/test_scm.py` (REQ-2208)
3. `scm::tests::a_break_says_what_breaks` (REQ-2212)
4. `TrunkGate` in `tools/test_trunk_gate.py` (REQ-2210)
5. `scm::tests::may_name_is_a_key_the_unit_reads`

No criterion rests on judgement. Every crate check but
`the_provenance_trailers_need_no_list` failed first, in the commit that holds
the checks alone, as did both new fixtures. That one passed there because no
rule named a person yet. The `TrunkGate` checks passed from the start,
because CI's `gate` job already ran `mise run all` on every pull request and
every push to `main`.

Two rounds of agent review found that a lower-case `signed-off-by:` and a
sign-off in the body escaped the person rules, and that a body line could fail
as a trailer. The sign-off route and the person rule now read one trailer
block, the last paragraph, as git does. Two later commits, holding checks
alone, strengthened the checks that would have passed against a wrong
implementation: the provenance check now carries an unlisted reviewer, and
`TrunkGate` refuses a condition, a forgiven failure, a `needs`, a `types`
filter, an inline trigger and a filter leaving out the trunk. The three new
crate checks failed in those commits, before the fixes.

Criterion 5 names the profile's table of keys, which isn't on `main` yet:
TSK-4300 adds it. Until it lands, `meow-scm` is the only reader of
`[commits]`, so its own list of keys holds `may_name`, and TSK-4300's table
gains `commits.may_name` when the two meet.

Two fixtures asserted what SPC-1050 no longer states, a bare `!` passing and
the rule named `sign-off`, and a commit of their own corrected them. `format`,
`lint`, `check`, `test` and `build` each pass on the change's tree, as the
pull request cites. `meow-scm` goes to 0.5.0.

The profile template in `meow-flow` doesn't show `may_name`, because this
task names only `meow-scm`'s pages.

## Left alone

How a release reads the breaking mark, which ADR-1570 decides and
`tools/check_release.py` already holds, and this repository's own `may_name`,
which stays undeclared because no commit here names a co-author.
