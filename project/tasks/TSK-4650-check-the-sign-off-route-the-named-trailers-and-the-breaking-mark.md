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

Not yet.

## Left alone

How a release reads the breaking mark, which ADR-1570 decides and
`tools/check_release.py` already holds, and this repository's own `may_name`,
which stays undeclared because no commit here names a co-author.
