---
id: TSK-5430
artifact: task
status: done # draft, approved, then done when the authorising mark or Evidence derives completion
revised: 2026-10-11
bug: BUG-1590
closes: []
issue: # the tracker's number, where the repository uses one
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Make the npm publish step fail when npm fails

`.github/workflows/pi-release.yml`'s "Publish each package to npm" step tests
the exit status of `npm publish … | tee`, which is `tee`'s, so a publish the
registry rejected reads as passed. The step decides on npm's own status and
keeps the two replies it already special-cases: the version published moments
ago, and the output a person reads.

## Acceptance criteria

1. Given the workflow at `main`, when `python3 tools/test_check_workflows.py`
   runs, then a check that reads the publish step's shell fails while the
   pipeline stands and passes once npm's exit status decides. Closed by: the
   test seen failing before the workflow changed.
2. Given a tag whose publish the registry accepts, when the Pi Release run
   finishes, then the step ends with `+ @meowshed/<unit>@<version>`. Closed
   by: the next tag's run on `main`.

## What to do

Capture npm's output and status, print the captured log either way, and treat
the "cannot publish over the previously published" reply as the publish that
already happened. The check that holds this lives with the workflow rules in
`tools/test_check_workflows.py`, so a later pipe can't reintroduce it.

## Depends on

Nothing.

## Evidence

`test_an_npm_publish_inside_a_pipeline_fails_naming_its_line` and
`test_an_npm_whose_status_decides_passes` in `tools/test_check_workflows.py`
came first and closed criterion 1: the first failed against the workflow
while the pipe stood (`python3 tools/check_workflows.py` named
`pi-release.yml:107` and exited 1) and passes after the change, and the
second held the success path. `mise run all` passed with exit status 0 over
the branch. Criterion 2's mechanism is the same publish the step already
carried: run 38132626035 published `@meowshed/meow-code@0.3.0` and run
38132752519 published `@meowshed/meow-core@0.9.0`, each ending with
`+ @meowshed/<unit>@<version>`; the reworded shell takes the same path at the
next tag pushed to `main`.

## Left alone

The npm publish mechanism itself (trusted publishing, `--provenance`) and
every other step of the workflow; the registry-side trusted-publisher
settings, which the repository's owner configures and no workflow change
fixes.
