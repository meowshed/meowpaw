---
id: RES-0131
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0014, RES-0005
---

# git

## Summary

Exactly one status format carries a compatibility promise, and it is not the
newer one - so the richer format is used for what only it provides and read as
best effort. Anything carrying a path is read with null termination or the
filename is wrong. Signature verification has eight outcomes, and four of them
describe a good signature with a key that should not be trusted. So a gate
tests for the good value exactly, and never for the absence of a bad one.

Research for one supported tool, and the only one the harness assumes is
present. git is what the harness reads history from, what it commits through,
what it isolates work with, and what it verifies signatures against.

It covers which of git's outputs may be parsed, and which of its commands have
side effects a harness would not expect. It also covers how signing is
verified, what worktrees guarantee, what a pack authors, and what the skill has
to contain.

It does not cover the method's rules for commits, branches and merges, which
are [RES-0014-commits.md](RES-0014-commits.md), nor the forge, which is
[RES-0133-github-and-gh.md](RES-0133-github-and-gh.md).

## The question

git's command-line output is designed for people and has been since before
anyone tried to script it. Some of it is now contractually stable and some
looks stable and is not, and the documentation states the difference, which
nobody can guess.

So the question is which outputs a harness may treat as data, and what reading
them costs.

## Method

We fetched and read the vendor documentation on 2026-09-20. The status
command's page gave the two porcelain formats and the exact wording of the
compatibility guarantee, and the environment-variable section gave the settings
that make behaviour reproducible. The pretty-format page gave the full
signature vocabulary, and the worktree page the machine-readable listing and
the same-branch restriction.

The signature values are quoted as written, and summarised nowhere, because the
distinction between them is the finding.

Nothing was run for this document. The repository's own commits were checked
for signatures separately, outside it.

## Findings

### Exactly one status format carries a compatibility promise, and it is not the newest

The documentation is precise about version 1:

> Version 1 porcelain format is similar to the short format, but is guaranteed
> not to change in a backwards-incompatible way between Git versions or based
> on user configuration. This makes it ideal for parsing by scripts.

Version 2 adds more information - a branch header with `branch.oid`,
`branch.head`, `branch.upstream` and `branch.ab` giving ahead and behind counts

- and does not carry the same stated guarantee.

That is a real trade, and no reason to avoid v2. The ahead/behind counts and
the detached-head signal are exactly what a harness needs, and they are not in
v1. The rule is to know which half of the output is promised and to treat the
rest as best effort.

`-z` is the other half of parsing correctly. It terminates entries with NUL,
implies v1 when no format is given, and carries the clause that decides
everything: _"Filenames containing special characters are not specially
formatted; no quoting or backslash-escaping is performed."_ Without it, a
filename with a quote or a newline is escaped in a way a naive parser gets
wrong, which is the classic path-handling defect and entirely avoidable.

### Reading the repository's state has a side effect, and there is a flag for it

`GIT_OPTIONAL_LOCKS=0` prevents git from performing operations that require a
lock, and the documentation gives the example directly: it stops `git status`
from refreshing the index as a side effect.

So the default behaviour of the most obviously read-only command is to take a
lock and write to the index. For a harness that is two problems: a background
inspection can contend with the user's own git process, and an inspection
changes a file in the repository.

This is the same class of finding as make's enumeration, in a much milder form
and with a clean remedy: a harness reading state sets the variable, and a
harness doing work does not.

### A predictable environment is set explicitly

The variables that make git's behaviour independent of the machine it runs on:

| Variable                      | What it settles                                 |
| ----------------------------- | ----------------------------------------------- |
| `GIT_OPTIONAL_LOCKS=0`        | No index refresh or lock while reading          |
| `GIT_TERMINAL_PROMPT=0`       | Never block waiting for credentials             |
| `GIT_PAGER=cat`               | No pager swallowing or truncating output        |
| `GIT_CONFIG_NOSYSTEM=1`       | Ignore `/etc/gitconfig`                         |
| `GIT_CONFIG_GLOBAL=/dev/null` | Ignore the user's global configuration          |
| `GIT_DIR`, `GIT_WORK_TREE`    | Operate on a known repository without discovery |
| `--no-advice`                 | No advice hints mixed into the output           |

The two configuration variables deserve a caveat, and no blanket use. Ignoring
the user's global configuration also discards their signing key, their identity
and their aliases, which is right for parsing output and wrong for making a
commit. So the harness has two environments: a reading environment that is
maximally isolated, and a working environment that is the user's.

`GIT_TERMINAL_PROMPT=0` is the one that turns a hang into a failure, which is
always the better outcome for an unattended run.

### Signature verification has eight outcomes and only one of them is good

`%G?` in a pretty format reports, quoted as written:

> show "G" for a good (valid) signature, "B" for a bad signature, "U" for a
> good signature with unknown validity, "X" for a good signature that has
> expired, "Y" for a good signature made by an expired key, "R" for a good
> signature made by a revoked key, "E" if the signature cannot be checked (e.g.
> missing key) and "N" for no signature

The companions: `%GS` the signer's name, `%GK` the key, `%GF` the key's
fingerprint, `%GP` the primary key's fingerprint where a subkey signed, `%GT`
the trust level, and `%GG` the raw verification message.

Three of those eight are the trap. `U`, `X`, `Y` and `R` all describe a _good_
signature - the cryptography checked out - while saying the key should not be
trusted: unknown validity, expired signature, expired key, revoked key. A check
that tests for "not B" passes all of them. A check that tests for `G` does not.

`E` is the ambiguous one: the signature cannot be checked, usually because the
key is missing locally. That states something about this machine and nothing
about the commit, and reporting it as an unsigned commit would be wrong.

So a gate over signing tests for `G` exactly, and reports `E` as unverifiable,
and never as failing. The allowed-signers file is what turns `E` into `G` for
SSH signing, and it is repository configuration that no personal setting
replaces.

### Worktrees are the isolation primitive, and their machine-readable form is documented

`git worktree list --porcelain` emits one attribute per line with a blank line
between entries, boolean attributes present only when true, and `-z` for NUL
termination. The attributes: `worktree`, `bare`, `HEAD`, `branch`, `detached`,
`locked` with an optional reason.

The constraint that shapes any use of worktrees for parallel work: **the same
branch cannot be checked out in two worktrees**. `add` refuses unless forced,
and the intended ways round it are `-b` for a new branch or `--detach`.

Linked worktrees share the repository's object store and refs, and have their
own `HEAD` and index in `$GIT_DIR/worktrees/<name>`. So two worktrees see each
other's commits immediately, and a branch created in one is visible in the
other. That makes them the right primitive for stacked work, and the wrong one
for pretending two agents have separate repositories.

`locked` exists to stop pruning, needs `--force` twice to override, and carries
a reason string, which makes it a usable marker for _this worktree is in use by
something_.

### What the pack authors

`.gitignore`, `.gitattributes` and `.github/allowed_signers`. Repository-level
`git config` where a setting is genuinely the repository's - signing
configuration, merge drivers - and never the user's global configuration.

`.gitattributes` is the underused one. It is where generated files are marked
so they do not dominate a diff, where merge drivers are declared for files
nothing can merge textually, and where end-of-line handling stops being a
per-machine accident.

### What a reviewer needs that no command reports

Whether the history is the history: a force-push that rewrote a reviewed commit
leaves no trace in the branch a reviewer sees.

Whether a commit's author is who the signature says, since author fields are
free text and only the signature is evidence.

Whether a merge was a merge or a rewrite, which changes what a later bisect can
find.

Whether a file that looks binary is actually text with a missing
`.gitattributes` entry.

### What the skill has to contain

In the body, in this order:

1. Two environments. The reading environment with locks, prompts, pager and
   system configuration disabled, and the working environment which is the
   user's.
2. Which outputs are data. Porcelain v1 is promised; v2 is richer and is
   not; `-z` for anything containing a path.
3. Signature verification. Test for `G`, treat `E` as unverifiable, and
   never treat "not B" as a pass.
4. Worktrees. The porcelain listing, the same-branch restriction, and that
   worktrees share refs and objects.
5. What must never happen. Parsing human-readable output. Reading paths
   without `-z`. Writing the user's global configuration. Accepting `U`, `X`,
   `Y` or `R` as a valid signature. Running a read while holding optional
   locks.

In supporting files: the environment variable table; the porcelain v2
branch header fields; the `%G?` value table; the worktree porcelain attributes;
and the dated facts with what to re-check.

## Conclusions

1. Only porcelain v1 is treated as a stable contract, because it is the only
   status format git guarantees not to change incompatibly between versions or
   with user configuration. 2. Porcelain v2 is used for what only it provides -
   the branch header with upstream and ahead-behind counts - and is read as
   best effort, because it promises nothing. 3. Any output containing a path is
   read with `-z`, since without it special characters are escaped and a naive
   parser gets the filename wrong. 4. A read sets `GIT_OPTIONAL_LOCKS=0`,
   because `git status` otherwise refreshes the index as a side effect, which
   both contends for a lock and modifies the repository. 5. The harness has two
   git environments. The reading environment disables prompts, the pager,
   advice and system configuration; the working environment is the user's,
   because it carries their identity and signing key. 6.
   `GIT_TERMINAL_PROMPT=0` is set for anything unattended, so a missing
   credential fails, and hangs nothing. 7. A signature gate tests for `G`
   exactly, since `U`, `X`, `Y` and `R` all describe a good signature with a
   key that should not be trusted and all pass a test for "not bad". 8. `E` is
   reported as unverifiable and never as unsigned, because it describes this
   machine's key material and says nothing about the commit. 9. The signer, key
   and fingerprint are recorded alongside the verdict, through `%GS`, `%GK` and
   `%GF`, so a verification can be re-checked later. 10. Worktrees are
   enumerated with `--porcelain`, whose attribute-per-line shape is documented,
   and `-z` where paths are involved. 11. The same branch is never checked out
   in two worktrees, so parallel work uses `-b` or `--detach`, and forces
   nothing. 12. Worktrees are not treated as separate repositories, since they
   share objects and refs and a branch made in one is immediately visible in
   the other. 13. A `locked` worktree with a reason is the marker for in-use,
   because it resists pruning and carries a message. 14. The pack authors
   `.gitignore`, `.gitattributes` and the allowed-signers file, and repository
   configuration, and never the user's global configuration. 15. The skill body
   carries the two environments, which outputs are data, signature
   verification, worktrees, and the prohibitions, in that order.

## Sources

All read 2026-09-20.

- [git-status](https://git-scm.com/docs/git-status) - that version 1 porcelain
  is guaranteed not to change in a backwards-incompatible way between versions
  or with user configuration and is ideal for parsing, with no equivalent
  statement for version 2; the version 2 branch header fields `branch.oid`,
  `branch.head`, `branch.upstream` and `branch.ab`; and `-z` terminating
  entries with NUL, implying v1, reversing rename field order and performing no
  quoting or escaping of filenames.
- [git environment variables](https://git-scm.com/docs/git#_environment_variables)
  - `GIT_DIR` and `GIT_WORK_TREE` turning off discovery; `GIT_CONFIG_GLOBAL`
    settable to `/dev/null` to skip the user's configuration;
    `GIT_CONFIG_NOSYSTEM` skipping `/etc/gitconfig`; `GIT_TERMINAL_PROMPT`
    preventing terminal prompts; `GIT_PAGER` disabling paging; `GIT_OPTIONAL_LOCKS`
    preventing lock-requiring operations with the stated example of `git status`
    refreshing the index; and `--no-advice`.
- [git pretty formats](https://git-scm.com/docs/pretty-formats) - the complete
  set of `%G?` values with their meanings, and `%GS`, `%GK`, `%GF`, `%GP`,
  `%GT` and `%GG`.
- [git-worktree](https://git-scm.com/docs/git-worktree) - `add`, `list`,
  `remove`, `prune`, `lock` and `unlock`; the `--porcelain` format with one
  attribute per line, blank-line-separated entries, boolean attributes present
  only when true, and `-z`; the attributes `worktree`, `bare`, `HEAD`,
  `branch`, `detached` and `locked` with a reason; the refusal to check out the
  same branch twice without `--force` and the `-b` and `--detach` alternatives;
  and that linked worktrees share refs and objects while keeping their own
  `HEAD` and index under `$GIT_DIR/worktrees/`.
