---
id: TSK-1600
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1170
closes: [REQ-0392, REQ-0394, REQ-0402]
issue: 243
---

# Report what waits for approval when a session starts

Report what waits for approval when a session starts, as ADR-1170 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a record with a draft decision, when `status --waiting` runs, then it prints the decision with "at the design gate". Closed by: a fixture.
2. Given a record with nothing waiting, or a repository with no record, when `status --waiting` runs, then it prints nothing and exits 0. Closed by: fixtures.
3. Given a fresh session in a repository with a draft waiting, when it starts, then its first reply names the draft. Closed by: a session run with `claude -p`, its output recorded.

## What to do

Add `--waiting` to `meow record status`, printing only the waiting lines, each naming the gate: a draft research record at the research gate, a requirement at the requirements gate, a decision at the design gate, an epic or task at the epic gate, a defect at triage. Print nothing, and exit 0, when nothing waits or the record's root doesn't exist, and make the launcher's fallback silent for `status --waiting`. Add a `SessionStart` hook to `meow-method` that runs it.

## Depends on

Nothing. ADR-1170 is approved.

## Evidence

`meow record status --waiting` prints only the drafts, each with the gate it
waits at, and nothing at all when none waits or the repository has no record.
The full `status` now names each draft's gate too. The launcher's fallback
stays silent for `status --waiting`, and `plugins/meow-method/hooks/hooks.json`
runs it at `SessionStart`.

Three new fixtures, and the five frozen fixtures #246 left passing against a
program that returns nothing now assert its output, so every fixture fails
against one:

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 69 tests
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=67, errors=2)
```

A fresh `claude -p` session, with this unit loaded by `--plugin-dir` in a
scratch repository whose decision is a draft, asked only "What's the state of
things here?", opened with:

```text
ADR-0001 is waiting for your approval at the design gate, and it's the only
thing blocking the next step.
```

On this repository, with nothing waiting, `status --waiting` prints nothing
and exits 0.

## Left alone

Running the frozen check in continuous integration, which ADR-1170 leaves.
