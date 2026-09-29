---
id: ADR-1550
artifact: adr
status: superseded
revised: 2026-09-29
addresses: [REQ-2956]
supersedes: []
---

# 1550. Evidence is kept beside the record by default, and a kept file git ignores is reported

**Superseded by ADR-2300.**

## Decision

This decision amends ADR-1530 in three places, and the rest of ADR-1530
holds.

The evidence directory defaults to the record's root with `evidence` under it,
which is `project/evidence` unless the profile moves the record with `root`
under `[record]`. A profile with no `[record]` section gets `project/evidence`
too, because `project` is the record's own default root, so the two defaults
agree. `evidence_dir` under `[verbs]` still overrides it. The
default follows the record because the owner asked on 2026-09-27 for evidence
to sit in the project folder, beside the record that cites it, and a
repository that keeps its record elsewhere wants its evidence there too.

A kept file is named `<record>.txt`, not `<record>.log`, because the common
`*.log` rule in a user's global git ignore, present in this repository
owner's own, leaves a `.log` file out of the commit with no word to anyone,
and evidence left out of the commit is evidence nobody else can check.

`meow-verbs evidence --keep` asks git whether each file it wrote is ignored,
and where one is, it names the file and the rule, leaves the file where it
is, and exits 1, as for a failed keep, because the evidence isn't kept until
someone changes the rule, and the file is then ready to commit without
keeping it again (REQ-2956). Where git can't answer, outside a git work tree
or when `git check-ignore` itself fails, `--keep` says it couldn't check,
leaves the file, and exits 3, because an unchecked file is unresolved and
never reads as kept.

After this decision a repository keeps its evidence beside its record
without declaring anything, and no ignore rule drops a kept file unnoticed.
What still doesn't work: a repository ignoring `*.txt`, or the evidence
directory itself, is told so and has to change the rule or the directory.

## Why

REQ-2956 keeps evidence in the repository, and RES-0262 found that evidence
living on one machine is an assertion. A file git ignores lives on one machine
as surely as the ledger does, which TSK-2340 found on this machine: a kept
`.log` file stayed out of `git add -A`, matched by `*.log` in
`~/.config/git/ignore`. The owner's request sets the default place, and the
record's root is where this method keeps everything a second person needs.

The strongest objection: `.txt` can be ignored too. It can, and the check
after writing catches that case and any other, where the extension only
avoids the one rule this repository's owner was found to have.

## Alternatives

| Option                                               | Better at                             | Why it lost                                                                                                               |
| ---------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Keep `.meowpaw/evidence` as the default              | Separates evidence from the record    | The owner asked for evidence beside the record                                                                            |
| Default to `project/evidence` literally              | Needs no reading of the record's root | A repository that moves its record would keep evidence in a `project/` it doesn't otherwise have                          |
| Keep `.log` and only warn when ignored               | Keeps the familiar extension          | Every machine with the common rule would warn on every keep, which people learn to ignore                                 |
| Force-add kept files past the ignore rule            | Commits them whatever the rules say   | Overrides a rule the repository or its user chose, which the harness has no standing to do                                |
| Write a `!*` ignore file into the evidence directory | Beats every user rule, and is visible | Changes what git ignores in the repository, which is the repository's own configuration to decide, as its permissions are |

## What it costs

`meow-verbs` reads `[record] root` from the profile, a section `meow-flow`
also reads; the profile is a file, so `meow-verbs` reads it whether
`meow-flow` is installed or not, and a repository that moves its record moves
its evidence with it. No file was kept under ADR-1530's default name or place,
because `meow-verbs` 0.6.0, which first keeps files, hasn't been released, so
nothing needs moving. A repository that changes `root` after keeping evidence
moves its evidence directory with it, so every kept record goes stale until
it is kept again, as ADR-1530 says of moving the directory; the person who
moves the record pays for that, and `evidence_dir` pins the directory for
anyone who wants to avoid it. `meow-verbs` holds its own copy of `project`,
`meow-flow`'s default root, because neither unit may depend on the other;
whoever changes that default in `meow-flow` has to change it in `meow-verbs`
in the same change. A CI step reading exit 1 from `--keep` can't tell an
ignored file from a stale record; whoever maintains it reads the printed line.

## What would reverse it

I would return to a directory of the harness's own if keeping evidence in the
record's root made `paw check`, its indexes or a check under `tools/` treat
evidence files as documents, shown by a finding on a kept file. The `.txt`
name and the ignore check follow from REQ-2956 and change only with it.

## Consequences

- ADR-1530 carries a line naming this amendment.
- `meow-verbs` defaults the evidence directory to the record's root, names
  kept files `.txt`, and reports a kept file git ignores.
- SPC-1040 states the default, the name and the check, and
  `meow-verbs`' page states them in place of `.meowpaw/evidence/` and
  `<record>.log`.
- This repository's `evidence_dir = "project/evidence"` goes from its
  profile, because it now repeats the default.

## How I will know it was realised

1. Fixtures show `--keep` writing `project/evidence/<record>.txt` with no
   declaration, following a moved `[record] root`, and still obeying
   `evidence_dir`.
2. Fixtures show `--keep` exiting 1 and naming the rule when git ignores the
   kept file, and exiting 3 when git can't answer.
3. `paw check` passes with a kept file under `project/evidence`.
4. REQ-2956 lands in a closed task of this decision's epic.

## What this does not settle

- Moving files kept before this decision.
