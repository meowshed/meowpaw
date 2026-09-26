---
id: TSK-1620
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1180
closes: [REQ-0522, REQ-0523, REQ-0575, REQ-2870, REQ-2871, REQ-2872, REQ-2873]
issue: 252
---

# Generate each kind's index and check it for drift

Generate each kind's index and check it for drift, as ADR-1180 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record whose decisions index holds a generated block, when a decision is added without `--write`, then `check index` exits 1 naming the index; when `index adr --write` runs, then it exits 0. Closed by: a fixture.
2. Given a kind of more than 36 requirements, when `index requirement` runs, then it prints the rows ordered by identifier and a view grouped by topic. Closed by: a fixture.
3. Given this repository, when its requirements index is migrated, then the count of requirements it lists equals the count of files before and after. Closed by: the counts in the evidence.

## What to do

Add `index <kind> [--write]` to `meow record` as SPC-1100 states it, and teach `check index` to report a generated block that differs from what `index` prints. Migrate `project/requirements/README.md` and `project/adrs/README.md` to generated blocks, as expand, migrate and contract, recording the count of entries before and after in the evidence.

## Depends on

Nothing. ADR-1180 is approved.

## Evidence

`meow record index <kind> [--write]` generates a kind's index from the tree:
the count of artifacts by stored status, a table ordered by identifier whose
rows carry what each artifact concluded and its stored status only, the
amendments each decision names, and a view by topic once a kind with topics
holds more than 36. `--write` replaces the block between the markers and keeps
the prose around it. `check index` reports a block that differs from what
`index` prints, ignoring the padding a formatter adds to a table.

The two indexes migrated as expand, migrate and contract: the program first,
then the generated blocks in place of the tables written by hand, counted
before and after:

| Index                            | Entries before | Entries after | Files in the tree |
| -------------------------------- | -------------- | ------------- | ----------------- |
| `project/requirements/README.md` | 1080           | 1080          | 1080              |
| `project/adrs/README.md`         | 19             | 19            | 19                |

The hand-written requirements index had said "1073 obligations" where 1075
are in force, and the decisions index noted one amendment of six; the
generated blocks say 1075 approved and 5 withdrawn, and list all six
amendments. Four new fixtures cover writing, drift, padding and the view by
topic:

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 73 tests in 4.323s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=71, errors=2)
```

## Left alone

The research index and the project index, which ADR-1180 leaves as prose.
