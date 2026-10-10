---
id: SPC-1210
artifact: spec
status: live
revised: 2026-10-10
states: [REQ-2214, REQ-2216, REQ-2196, REQ-2198, REQ-2200, REQ-3035]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The repository's files on the code host

## Scope

This covers what this repository keeps under `.github/` for GitHub to read:
the files a newcomer needs before contributing, and the rules every workflow
holds. It states where each file sits, what the workflows may and may not do,
and the two checks under `tools/` that hold both.

It leaves the release's archives, its attestation and the build it runs to
SPC-1080, signing and the push guard to SPC-1060, and the rules the
repository's contributors follow to `CLAUDE.md`, which no file here repeats.
The harness writes none of these files into another repository.

ADR-2510 decides the community files, and TSK-4610 realises it. ADR-2520
decides the rules a workflow holds, and EPC-2420 realises it.

## Boundary

| Surface                            | What it is                                                |
| ---------------------------------- | --------------------------------------------------------- |
| `.github/CONTRIBUTING.md`          | How to contribute, pointing at `CLAUDE.md` for the rules  |
| `.github/SECURITY.md`              | How to report a vulnerability privately                   |
| `.github/CODE_OF_CONDUCT.md`       | The behaviour expected of everyone taking part            |
| `.github/CODEOWNERS`               | Who owns which paths, and so who reviews a change to them |
| `.github/ISSUE_TEMPLATE/`          | The template an issue opens with                          |
| `.github/pull_request_template.md` | The template a pull request opens with                    |
| `.github/workflows/*.yml`          | The workflows CI runs                                     |
| `tools/check_community.py`         | The check that the six community files are present        |
| `tools/check_workflows.py`         | The check that every workflow holds the rules below       |
| The `test` stage                   | Runs both checks, as `.meowpaw/profile.toml` binds it     |

## Behaviour

### The community files

The repository carries six files for a newcomer: how to contribute, how to
report a vulnerability, what behaviour is expected, who owns what, and a
template for an issue and one for a pull request (REQ-2214). Each sits under
`.github/`, the place GitHub reads it from for its community profile, and not
where it would read well in a directory listing (REQ-2216).

`CONTRIBUTING.md` points at `CLAUDE.md` for every rule a contributor follows
and repeats none of them, because `CLAUDE.md` is the only instruction file and
a second copy drifts. `SECURITY.md` names a private route for a report, so a
vulnerability doesn't arrive as a public issue. The pull request template asks
for what the change does, the record that authorises it, the evidence that it
works and what a reviewer reads first, in that order, as the writing standard's
rule for a pull request asks.

`tools/check_community.py` fails, naming the file, when any of the six is
missing from `.github/`. The `test` stage runs it.

### The workflows

Every workflow under `.github/workflows/` declares `permissions:` at its top
level with `contents: read` and nothing wider, and grants write access only on
the job that needs it, in that job's own `permissions:` (REQ-2196).

No workflow checks out a pull request's code under `pull_request_target`,
`workflow_run` or any other trigger that runs with a write token or the
repository's secrets (REQ-2198).

No value the workflow doesn't control reaches a `run:` line by expression: a
step passes an issue's title, a branch name, a pull request's body or any
other value of `${{ github.event.* }}`, `${{ github.head_ref }}` or
`${{ matrix.* }}` through its `env:` block, and the script reads the
environment variable (REQ-2200). A `run:` line holds no `${{` at all, so the
check has no list of trusted contexts to keep.

No workflow runs the measurement suite or names a model credential, because
every run of the suite is a real model call and the owner keeps those out of
continuous integration (REQ-3035).

`tools/check_workflows.py` reads every workflow file and fails, naming the
file and the line, on a missing top-level `permissions`, a top-level
permission other than `contents: read`, a forbidden trigger in a workflow that
also runs `actions/checkout`, `${{` inside a `run:` value, and the suite's
task or a model credential named anywhere in the file. The `test` stage runs it.

## Failure paths

| Condition                                               | What happens                                                    |
| ------------------------------------------------------- | --------------------------------------------------------------- |
| A community file is missing from `.github/`             | `check_community.py` fails, naming the file                     |
| A community file sits only at the root                  | It counts as missing, because the check reads `.github/` alone  |
| A workflow has no top-level `permissions`               | `check_workflows.py` fails, naming the file                     |
| A workflow grants write access at its top level         | `check_workflows.py` fails, naming the file and the permission  |
| `pull_request_target` or `workflow_run` with a checkout | `check_workflows.py` fails, naming the file and the trigger     |
| `${{` inside a `run:` value                             | `check_workflows.py` fails, naming the file and the line        |
| A workflow names the suite's task or a model credential | `check_workflows.py` fails, naming the file and the line        |
| A workflow file doesn't parse                           | `check_workflows.py` fails, naming the file and the parse error |
