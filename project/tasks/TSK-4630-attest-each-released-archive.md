---
id: TSK-4630
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2420
closes: [REQ-2218]
issue: 948
projected: 71aebcce2e43
tracked: c32c08d627f9
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Attest each released archive with its build provenance

The release workflow's publishing job attests every archive it publishes, so
a consumer checks what an archive was built from with `gh attestation verify`,
as SPC-1080 states under "A release". One task, one branch, one pull request,
one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given `.github/workflows/release.yml`, when a test reads it as YAML, then
   the publishing job has a step using `actions/attest-build-provenance`
   whose subject covers every archive the job publishes, and the step runs
   only when the run publishes (REQ-2218). Closed by: a test under `tools/`
   naming REQ-2218, seen failing first.
2. Given the same file, when the test reads each job's permissions, then only
   the publishing job holds `id-token: write` and `attestations: write`, and
   the top level still holds `contents: read` alone. Closed by: the same test.
3. Given the unit pages that tell a person how to install a release, when a
   reader looks for how to check an archive, then `docs/README.md` gives the
   `gh attestation verify` command. Closed by: judgement in the pull request's
   review.

## What to do

Add the attestation step to the job that publishes, after the archives exist
and before they are uploaded, pinned to a released major version of the
action. Widen that job's `permissions` by the two entries, and no other job's.
Add the verify command to `docs/README.md` where it tells a person how the
release is published.

## Depends on

- TSK-4620 (not blocking): both edit `release.yml`, and whichever lands second rebases on the first.

## Evidence

The release workflow the task names, `release.yml`, no longer exists:
ADR-2810's build split replaced it with three workflows, and each publishes
archives. `claude-release.yml` publishes each unit's Claude Code zip,
`pi-release.yml` each Pi package's zip and `rust-tool.yml` the meow-full zip,
so the change attests in the publishing job of all three, and the tests read
all three. Each closes REQ-2218 for the archives it publishes.

1. `Attestation.test_the_publishing_job_attests_every_archive_it_publishes_and_only_when_it_publishes`,
   in `tools/test_check_workflows.py`, reads each workflow as YAML with the
   check's own reader. In every job that runs `gh release create`, it finds one
   `actions/attest-build-provenance@v3` step before the first publishing step,
   running under the publishing step's condition. Its subject is either the
   checksum file the packing step appends beside each archive it lists for
   publishing, or the archive path the publishing step uploads. It failed
   first on all three workflows, with no attesting step.
2. `Attestation.test_only_the_publishing_job_holds_the_attestation_permissions`
   holds the top level at `contents: read` alone, the publishing job at
   `id-token: write` and `attestations: write`, and every other job at
   neither. It failed first on all three publishing jobs.
3. Criterion 3 rests on judgement, because the page's wording is read:
   after the paragraph on how a release reaches you, `docs/README.md` gives
   the command `gh attestation verify` with `--repo meowshed/meowpaw`. The
   example wasn't run, because no archive carries an attestation until the
   next release.

`claude-release.yml` attests only the archives the run built, and not one it
downloaded from an earlier release, because that archive's provenance belongs
to the run that built it. Its attesting step and `pi-release.yml`'s skip a
run that built no new archive, through `hashFiles` on the checksum file, so a
run that publishes nothing new doesn't fail on an empty subject.
`rust-tool.yml`'s publishing job runs only when the run publishes, so its
attesting step needs no condition of its own, and the step that packed and
published the archive is now two steps, with the attestation between them.

Only a real release run shows that the action accepts the subjects, that the
repository's settings allow the attestation and that `gh attestation verify`
succeeds on a published archive. ADR-2520's second criterion waits on that
run, which the owner starts.

Every stage passed in pull request #PR.

## Left alone

Running `gh attestation verify` on a real archive, which waits on the next
release the owner starts, and signing the archives, which ADR-2520 rejected.
