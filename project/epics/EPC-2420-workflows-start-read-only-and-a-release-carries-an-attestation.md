---
id: EPC-2420
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2520
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Workflows start read-only and trust no foreign value, a release carries an attestation and the trunk's protections are reported

Realises exactly one authorising record, ADR-2520. The epic is complete when a
check holds every workflow to the rules SPC-1210 states under "The
workflows", the release attests each archive as SPC-1080 states under "A
release", and `meow-github protections` reports the trunk's protections as
SPC-1080 states under "Reporting the trunk's protections".

## Acceptance criteria

Taken from ADR-2520's list of how it will be known realised:

1. The check fails a fixture workflow with no top-level `permissions`, one
   with `pull_request_target` and a checkout, and one with
   `${{ github.event.issue.title }}` in a `run:` line (REQ-2196, REQ-2198,
   REQ-2200).
2. The release workflow's publishing job runs
   `actions/attest-build-provenance` on every archive it publishes, and only
   that job holds `id-token: write` and `attestations: write` (REQ-2218).
3. The protection report names each of the six protections as in force or
   absent for a fixture answer, and names an unread one as unread (REQ-2194).
4. Every requirement ADR-2520 addresses is named by a closed task.

ADR-2520's second criterion, `gh attestation verify` succeeding on an archive
from the next release, waits on a release the owner starts, so criterion 2
states what this epic ships, and the first release after it is where a person
runs the verify.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 [P] TSK-4620 hold every workflow to a read-only top, no untrusted checkout and no expression in a `run:` line, in `tools/check_workflows.py` and `.github/workflows/`
      closes: REQ-2196, REQ-2198, REQ-2200

- [ ] T-002 [P] TSK-4630 attest each released archive in `.github/workflows/release.yml`
      closes: REQ-2218
      depends: TSK-4620 (not blocking) - both edit `release.yml`, and the second rebases on the first

- [ ] T-003 [P] TSK-4640 report the trunk's protections with `meow-github protections`, in the `github` feature of `crates/meow/`
      closes: REQ-2194

## Coverage

Each of the five requirements ADR-2520 addresses lands in exactly one task.
TSK-4620 alone tests the decision's main claim, that a check holds the
workflows, because it fails on today's `build.yml` and `ci.yml` before their
fix. The three tasks run in parallel.

## Not covered

Which protections the trunk should have, which ADR-2520 leaves unsettled: the
report states them and changes none. Workflows the harness writes into another
repository, because it writes none yet.
