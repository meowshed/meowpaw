---
id: BUG-1030
artifact: bug
status: approved
severity: minor
violates: REQ-0690
found: 2026-09-21
revised: 2026-09-21
issue: 24
---

# The eval results were committed, because the ignore pattern matched nothing

## Reproduction

At `926b55d`:

```bash
git ls-files plugins/meow-core/evals/results/ | wc -l    # 4
grep -n "evals/results" .gitignore                        # evals/results/
```

## What the system does

`.gitignore` carries `evals/results/`. A pattern with a slash anywhere but at
its end is anchored to the directory holding the `.gitignore`, so it matches
`evals/results/` at the repository root, and the runner writes to
`plugins/meow-core/evals/results/`.

Four files reached `main`: two `report.html`, at 80K and 132K, and two
`aggregate-result.json`.

## What it should do, and why

A run's output is generated, machine-written and regenerated on the next run,
and the runner's own documentation says to ignore it. Committing it puts a
132K generated artifact in every clone, and it dates: the file on `main` would
describe a run nobody can reproduce from that tree, which is the kind of stale
state REQ-0690 exists to prevent.

The numbers that matter are in TSK-1050, written by hand from the run, where a
reader of the record finds them.

## Triage

Implementation. The pattern is wrong and the files are generated, so nothing
upstream changes.

## Closed by

`.gitignore` matching `plugins/*/evals/results/`, and the four files removed
from the tree.

The removal also deleted the local HTML reports, which held each grader's
verdict and the excerpt the judge read. The per-run scores and every judge vote
survive in the run's terminal output, and the tables survive in TSK-1050, so
what is lost is the rendering. It comes back only by running the suite again.
