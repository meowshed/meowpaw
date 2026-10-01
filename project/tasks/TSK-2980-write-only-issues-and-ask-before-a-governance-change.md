---
id: TSK-2980
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1720
closes: [REQ-2576]
issue: 709
projected: 8487dbae3b7c
---

# Write only issues, and ask before a `gh` command changes governance

The request layer sends a write only to an endpoint on its allow list, which
holds the issue create and the issue update, and `meow-github` ships a
`PreToolUse` hook that answers `ask` before a Bash command's `gh` changes
repository settings, branch protection, rulesets, Actions permissions,
secrets or a workflow file. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given the layer, when it is asked to send `PATCH repos/o/r`,
   `PUT repos/o/r/branches/main/protection`, `POST repos/o/r/rulesets`,
   `PUT repos/o/r/actions/permissions/workflow` or
   `PUT repos/o/r/contents/.github/workflows/ci.yml`, then it refuses each
   with `refused by meow-github:` and starts no `gh`. Closed by: the unit test
   `a_write_off_the_allow_list_starts_no_gh` in
   `crates/meow/src/github/request.rs`.
2. Given the allow list and the governance list, when a test matches one
   against the other, then no allow-list entry matches. Closed by: the unit
   test `no_allowed_write_is_governance` in
   `crates/meow/src/github/request.rs`.
3. Given the crate's source, when a test collects every method and endpoint
   it builds, then each is a `GET` or on the allow list. Closed by: the unit
   test `every_built_write_is_allowed` in `crates/meow/src/github/request.rs`.
4. Given each of `gh api -X PUT repos/o/r/branches/main/protection`,
   `gh api repos/o/r/rulesets -f name=x`,
   `gh api repos/o/r/rulesets --input rs.json`,
   `gh repo edit --visibility private`, `gh repo archive`,
   `gh api graphql -f query='mutation { x }'`,
   `GH_TOKEN=x gh api -X PUT repos/o/r/branches/main/protection`,
   `env GH_TOKEN=x gh repo delete o/r` and
   `git status && gh api -X PUT repos/o/r/rulesets/1` as a Bash tool call,
   when `meow-github governance-guard` reads it, then it answers `ask` with a
   reason naming the method and the endpoint. Closed by:
   `Guard.test_a_governance_change_is_asked` in
   `plugins/meow-github/tests/test_github.py`.
5. Given `gh api repos/o/r/issues` and
   `gh api graphql -f query='{ viewer { login } }'`, when the guard reads
   each, then it prints nothing and exits 0. Closed by:
   `Guard.test_a_read_passes_in_silence` in
   `plugins/meow-github/tests/test_github.py`.
6. Given a token in front of a command the guard asks about, when it answers,
   then the token appears nowhere in its output. Closed by:
   `Guard.test_the_token_is_never_echoed` in
   `plugins/meow-github/tests/test_github.py`.
7. Given `plugins/meow-github/hooks/hooks.json`, when a test reads it, then it
   declares one `PreToolUse` command hook matching Bash that runs
   `meow-github governance-guard`, and `budget.toml` still states 0
   characters. Closed by: `Guard.test_the_hook_runs_the_guard_on_bash` in
   `plugins/meow-github/tests/test_github.py`.
8. Given a Claude Code session with the unit installed, when the model runs a
   Bash command naming `gh`, then Claude Code runs the hook. Judgement:
   seeing the platform run a hook needs a model session, which this
   repository runs by hand and never in CI, so the criterion rests on
   `hooks.json` matching the hook schema Claude Code documents.

## What to do

Add the allow list, `POST repos/{r}/issues` and `PATCH repos/{r}/issues/{n}`,
and the governance list to the layer, and refuse any method other than `GET`
to a path off the allow list before `gh` starts, as SPC-1080's section "The
GitHub request layer" states. A later decision that adds a write adds its
endpoint in the same change.

Add a `governance-guard` subcommand to the `github` feature and ship
`plugins/meow-github/hooks/hooks.json`, which runs it on a Bash command
containing `gh` as a word. The guard reads the hook's input on standard
input, splits the command at `&&`, `||`, `;`, `|` and each new line, skips a
part's leading assignments and a leading `env` with its assignments, and
answers `ask` for the five kinds of part SPC-1080 lists. Its reason names the
method and the endpoint and never the command, because a command can carry a
token. It leaves Edit and Write alone.

Raise `meow-github`'s minor version above the one `main` carries when this
lands, match its README's `describes:`, and name the hook, its cost and the
platform behaviour it relies on, with where Claude Code documents it, in the
README's section "What it needs".

## Depends on

- TSK-2940 (blocking): the allow list is checked in the layer it adds.

## Evidence

`admits` in `crates/meow/src/github/request.rs` holds the allow list, and
`exchange` refuses any other write before `gh` starts. The only writes the
crate builds go through `Layer::create_issue` and `Layer::update_issue`,
whose endpoints come from `create_issue_endpoint` and `update_issue_endpoint`,
and `write` is private to the layer. `governance` holds the governance list.
`governance-guard`, in `crates/meow/src/github/guard.rs`, reads the hook's
input and answers `ask` for the five kinds of part SPC-1080 lists, and
`plugins/meow-github/hooks/hooks.json` runs it on every Bash command.

Criteria 1 to 7 are closed by the checks they name:

1. `a_write_off_the_allow_list_starts_no_gh` in `request.rs`
2. `no_allowed_write_is_governance` in `request.rs`
3. `every_built_write_is_allowed` in `request.rs`
4. `Guard.test_a_governance_change_is_asked` in
   `plugins/meow-github/tests/test_github.py`
5. `Guard.test_a_read_passes_in_silence`
6. `Guard.test_the_token_is_never_echoed`
7. `Guard.test_the_hook_runs_the_guard_on_bash`

Criterion 8 rests on judgement, as the task says: no session ran the hook,
and `hooks.json` follows the schema Claude Code documents for a `PreToolUse`
command hook, as `meow-git`'s does.

The checks failed first, in the commit that holds them alone: the crate's
tests didn't build, and the guard's checks failed against the tool as it was.
`format`, `lint`, `check`, `test` and `build` each pass on the change's
tree, as the pull request cites.

I made three choices the task leaves open. The hook runs on every Bash
command, with no `if` rule, because "`gh` as a word" can sit anywhere in a
command and an `if` rule matches only how one starts; the guard returns at
once where no part runs `gh`. `&` separates parts as `&&` does, because a
command sent to the background still runs. A `-X` flag with its method
joined, as in `-XPUT`, is read as a method.

`meow-github` goes to 0.13.0. Its README gains the section "What it writes,
and what it asks about", names the hook and its cost under "What it needs",
and its manifest's description no longer says it writes nothing to GitHub.

## Left alone

Governance changed through a command other than `gh`, a `gh` inside a
subshell, `eval`, `xargs`, a script, a function, a variable or an alias, and a
bare unattended run, which skips plugin hooks: ADR-1810 names each as still
not caught. Whether the person answering the prompt holds the governance
role, which the hook can't tell.
