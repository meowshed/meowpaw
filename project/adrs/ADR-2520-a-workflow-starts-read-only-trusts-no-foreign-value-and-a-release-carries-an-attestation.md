---
id: ADR-2520
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-2194, REQ-2196, REQ-2198, REQ-2200, REQ-2218]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2520. A workflow starts read-only, trusts no foreign value, and a release carries an attestation

## Decision

Every workflow under `.github/workflows/` declares `permissions: contents:
read` at the top and grants write access only on the job that needs it
(REQ-2196). `release.yml` already does both. No workflow checks out a pull
request's code under `pull_request_target` or any other trigger that runs
with write access (REQ-2198). No value the workflow doesn't control, such as
an issue title, a branch name or a pull request body, reaches a `run:` line
by expression. A step passes it through an environment variable instead
(REQ-2200).

The release job produces a build provenance attestation for each archive,
with GitHub's `actions/attest-build-provenance`, so a consumer can check what
an archive was built from with `gh attestation verify` and without trusting
the publisher (REQ-2218).

`meow-github` gains a read-only report of the trunk's branch protections:
which of required reviews, required checks, signed commits, linear history
and blocked force-pushes are in force and which are absent (REQ-2194). It
reads them through the request layer ADR-1810 decided and writes nothing.

`tools/` gains a check, run by the `test` verb, that reads every workflow
file and fails on a missing top-level `permissions`, a forbidden trigger with
a checkout, or an expression inside a `run:` line.

Once this is accepted, the workflows this repository writes are held to the
rules by a check, and a consumer can verify a release. What still doesn't
work: the check covers this repository's workflows, and the harness writes
none into another repository yet.

## Why

RES-0066 concluded that a workflow's token is read-only at the top and write
per job, that no workflow checks out untrusted code under a trigger holding
write access or lets an untrusted value reach something executable, and that
a consumer needs provenance as well as a signature. It also gave the
protections an order of value, force pushes and deletion blocked first, which
is the order the report lists them in.

## Alternatives

| Option                      | Better at                        | Why it lost                                                         |
| --------------------------- | -------------------------------- | ------------------------------------------------------------------- |
| Do nothing                  | No new check                     | One edit to a workflow can widen its token and nothing fails        |
| An external workflow linter | More rules, maintained by others | It adds a tool the gate must install for three rules                |
| Sign the archives instead   | A familiar way to vouch          | A signature says who published, not what the archive was built from |

## What it costs

The release job needs the `id-token: write` and `attestations: write`
permissions, which widen what that one job can do. A workflow author has to
pass foreign values through the environment.

## What would reverse it

- GitHub drops artifact attestations, or the check finds no workflow change
  in a year, which would make it cost more than it saves.

## Consequences

The release job gains the attestation step. The `tools/` check joins the
`test` verb. `meow-github` gains the protection report.

## How I will know it was realised

1. The check fails a fixture workflow with no top-level `permissions`, with
   `pull_request_target` and a checkout, or with `${{ github.event.issue.title }}`
   in a `run:` line (REQ-2196, REQ-2198, REQ-2200).
2. `gh attestation verify` succeeds for an archive from the next release
   (REQ-2218).
3. The protection report names each protection as in force or absent for
   this repository (REQ-2194).

## What this does not settle

- Which protections the trunk should have. The report states them and
  changes none.
