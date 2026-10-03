---
id: TSK-4630
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2420
closes: [REQ-2218]
issue:
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

Not yet.

Criterion 3 rests on judgement, because the page's wording is read.

## Left alone

Running `gh attestation verify` on a real archive, which waits on the next
release the owner starts, and signing the archives, which ADR-2520 rejected.
