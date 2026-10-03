---
id: TSK-4610
artifact: task
status: approved
revised: 2026-10-03
realises: ADR-2510
closes: [REQ-2214, REQ-2216]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Carry the six community files under `.github/`, held by a check

The repository carries how to contribute, how to report a vulnerability, the
expected behaviour, the code owners and the issue and pull request templates
under `.github/`, and `tools/check_community.py` fails when one is missing, as
SPC-1210 states under "The community files". One task, one branch, one pull
request, one review: the tests first, then the change, its documentation and
its marks.

## Acceptance criteria

1. Given a fixture tree holding all six files under `.github/`, when
   `tools/check_community.py` runs on it, then it exits 0, and given the same
   tree with any one file removed, it exits 1 naming that file (REQ-2214,
   REQ-2216). Closed by: a test per file under `tools/`, seen failing first.
2. Given a fixture tree with `CONTRIBUTING.md` at the root and none under
   `.github/`, when the check runs, then it names `.github/CONTRIBUTING.md` as
   missing (REQ-2216). Closed by: a test naming REQ-2216.
3. Given this repository, when the `test` verb runs, then the check runs and
   passes. Closed by: the `test` verb's output in the pull request.
4. Given `.github/CONTRIBUTING.md`, when a reviewer reads it, then it points
   at `CLAUDE.md` for every rule and restates none of them. Closed by:
   judgement in the pull request's review, because no pattern tells a pointer
   from a paraphrase.

## What to do

Write `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CODEOWNERS`, an
issue template under `ISSUE_TEMPLATE/` and `pull_request_template.md`, each
under `.github/`. The pull request template asks, as paragraphs, for what the
change does with the record that authorises it, the evidence that it works and
what a reviewer reads first.

Three defaults are my choices, recorded here for the owner to change in
review: `CODEOWNERS` assigns `*` to `@retran`; `SECURITY.md` routes a report to
GitHub's private vulnerability reporting and to `me@retran.me`, the address
the licence headers already publish, and promises no response time, which
ADR-2510 leaves unsettled; `CODE_OF_CONDUCT.md` adopts the Contributor
Covenant 2.1 by reference, linking its text rather than copying it.

Add the check to the `test` verb in `.meowpaw/profile.toml`. In `CLAUDE.md`,
the layout table's row for `.github/` says it holds CI and the community
files, and the gate's list of checks in `tools/` gains this one.

## Depends on

- TSK-4620 (not blocking): both add a check under `tools/` to the `test` verb and to `CLAUDE.md`'s list of checks, and whichever lands second rebases its line.

## Evidence

`.github/` carries `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`,
`CODEOWNERS`, `ISSUE_TEMPLATE/defect.md` and `pull_request_template.md`, and
`tools/check_community.py` fails, naming each one missing, closing REQ-2214
and REQ-2216. Each criterion is closed by the check it names, in
`tools/test_check_community.py`:

1. `Community.test_all_six_files_pass` and
   `Community.test_each_missing_file_fails_naming_it`, which removes each of
   the six in turn and compares the line naming it exactly.
2. `Community.test_a_file_at_the_root_counts_as_missing`.
3. The `test` verb runs `tools/test_check_community.py` and
   `python3 tools/check_community.py`, which prints
   `6 community files, 0 missing from .github/` on this repository.

The checks failed first, in the commit that holds them alone, where the module
they import didn't exist yet. The review asked for the tests to compare the
whole output and to refuse a lone `config.yml`, and that rewrite also landed
in a commit of its own, where the `config.yml` test failed. Criterion 4 rests
on judgement, for the reason it gives, and the review in the pull request
judged it. `format`, `lint`, `check` and `test` each pass on the change's
tree, and `mise run all` and `paw check` exit 0, as the pull request cites.

I made one choice the task leaves open. An issue template counts as present
when `.github/ISSUE_TEMPLATE/` holds a Markdown or YAML file other than
`config.yml`, because GitHub reads any template in that directory and reads
`config.yml` as the chooser's settings.
`Community.test_an_empty_issue_template_directory_counts_as_missing` and
`Community.test_a_chooser_configuration_alone_is_no_issue_template` hold it.
The three defaults stay as the task records them: `gh api` lists `retran` as
an admin of `meowshed/meowpaw`, so `@retran` can own the code. ADR-2510's
second sign, GitHub's community profile, can be read only after the merge.

## Left alone

Writing these files into another repository, which ADR-2510 leaves to a later
decision, and turning on private vulnerability reporting in the repository's
settings, which is the owner's act and a change to governance.
