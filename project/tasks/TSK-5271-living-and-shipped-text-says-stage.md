---
id: TSK-5271
artifact: task
status: done
revised: 2026-10-10
epic: EPC-2760
closes: [REQ-4200]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Living and shipped text says "stage"

Every living and shipped file says "stage" where it said "verb", introduces the
word with the statement that the five are independent, and this repository's
profile declares them under `[stages]`.

## Acceptance criteria

1. Given the living and shipped files, when `git grep -iwE 'verbs?'` runs over
   them outside the allow-list TSK-5272 names, then it prints nothing. Closed
   by: that command's exit status, 1.
2. Given the page that introduces the term (SPC-1040 and `docs/`), when a
   reader meets the word first, then the same paragraph says the five are
   independent and that `format` goes first. Rests on judgement, by the owner:
   no program can read whether a paragraph says it.
3. Given this repository's profile, when the stages resolve, then they resolve
   from `[stages]` and the report names no deprecation. Closed by: `meow-checks
status` printing no deprecation line.

## What to do

Change the text in two parts, reviewed as two commits: the mechanical part, the
word itself where the sentence stays true with it, and the editorial part, the
sentences that argued from the word (such as "a verb is a verb of the
harness"). Where a sentence says "verification verb", say "verification
stage". Leave frozen records, the Rust module names and the `mise` task names
as they are. The mirrored copies under `packages/` change with their
originals.

## Depends on

- TSK-5270 (blocking): the pages say a profile declares `[stages]`, and that
  has to work before they say it.

## Evidence

Pull request 876. A mechanical script made the word change and a short set of
hand edits made the rest, in two commits with the tests' expectations in a
third.

- Criterion 1: `git grep -niP '\bverbs?\b'` over the tracked files, outside
  the frozen record kinds, `plugins/meow-prose` and its mirror, `evals/`,
  `tests/`, `tools/test_*` and `crates/`, then outside lines naming
  `meow-verbs`, `verbs=`, the `verbs` subcommand, a `[verbs]` table, the JSON
  key `"verbs"` or `VERBS`, leaves the onboarding section name `Verbs` in two
  `layout.toml` files and two grammatical uses in `tools/`. TSK-5272 turns that
  list into the check's allow-list.
- Criterion 3: `meow-checks status` on this repository prints no deprecation
  line, because the profile declares `[stages]`.

Criterion 2 rests on the owner's judgement, because no program can read
whether a paragraph says the stages are independent: SPC-1040's section "The
term" says it in its first paragraph.

The onboarding section name `Verbs` stays, because it names a heading in an
onboarding report that repositories already carry, so changing it is a record
shape migration that needs its own task. The writing standard's grammatical
use of "verb", the evaluation cases and the Rust identifiers also stay.

`meow-checks run format lint check test` passed on every stage with this
branch's binary, after two rounds of corrections to tests and tables.

## Left alone

Frozen records, which keep "verb", the Rust module and directory names that
say "verbs", and the `mise` task names ADR-1410 left to the repository.
