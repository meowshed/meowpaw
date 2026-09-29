---
reader: someone whose meowpaw unit just refused, blocked or reported something they didn't expect
answers: what each message a unit prints means, why it appeared and what fixes it
kind: troubleshooting
describes:
  [
    meow-core@0.6.1,
    meow-git@0.2.3,
    meow-github@0.4.2,
    meow-flow@0.39.0,
    meow-method@0.30.0,
    meow-prose-gate@0.2.0,
    meow-scm@0.4.2,
    meow-verbs@0.7.1,
  ]
---

# Troubleshooting

Each entry starts from the message a unit prints, or from what you see, then
says why it happened and what fixes it.

## No meow binary was found for this machine

`no meow binary was found for this machine` means a unit's program couldn't
find its binary for your operating system and processor. `meow-verbs` then
reports every verb unresolved, `meow-git` checks nothing, `meow-scm` reports
the message unchecked and exits 3, `meow-github` names the machine and exits
3, and `paw` reports the record as not checked.

Each unit that runs a program ships a binary for macOS, Linux and Windows on
arm64 and x86_64. If your machine is one of those six, the unit was installed
from a copy without its binary, so reinstall it from the marketplace. Replace
`<unit>` with the unit that printed the message:

```bash
claude plugin marketplace update meowpaw
claude plugin install <unit>@meowpaw
```

If your machine is none of the six, the unit can't run its checks there, and
it keeps reporting them as unchecked, never as passed.

## A verb is unresolved

`unresolved` means `meow-verbs` ran nothing for that verb and reports nothing
as passed. The words after it say why:

- `undeclared: the profile doesn't name it`: `.meowpaw/profile.toml` has no
  command for the verb. If your repository has that check, declare it under
  `[verbs]`, such as `lint = "./scripts/lint"`. If it doesn't, unresolved is
  the right answer, and you can leave it.
- `no profile`: `.meowpaw/profile.toml` doesn't exist at the repository's
  root. Create it and declare each verb under `[verbs]`.
- `malformed declaration: the value isn't one command`: the verb's value is
  a list or a table. Write one command as a string, joining several with `&&`.
- `profile unparseable`: the file isn't valid TOML, and the words after it
  say what the parser found, such as `invalid table header`. Fix the file.

## A commit on the trunk was refused

``refused a commit on `main`, the trunk this repository declares`` means
`meow-git` stopped a commit on the branch you declared as the trunk under
`[git]`, so every change reaches it through a branch and a review. Create a
branch and commit there:

```bash
git switch --create fix/the-change
```

## A push was refused

`refused the push; 1 problem in the 1 commit it would publish` means
`meow-git` checked the branch and each commit the push would publish and
found a problem, listed under the message. The problem is one of these:

- `branch name: it carries a date` or `the author's name`: the code host already
  stores both. Rename the branch for the change, with
  `git branch -m fix/the-change`.
- `is unsigned`: the repository declares `require_signatures = true`, and a
  commit carries no signature. Sign the latest commit with
  `git commit --amend -S --no-edit`, or every unpublished commit with
  `git rebase --exec 'git commit --amend -S --no-edit' origin/main`.
- `signed by a key this repository doesn't trust`: the key isn't in the
  allowed signers file git reads. Add your public key to that file.
- `is signed, but the signature is unverifiable here`: git has no allowed
  signers file configured, so it can't check any signature. Run
  `git config gpg.ssh.allowedSignersFile <path to the repository's list>`.
- a message problem, such as a subject over the limit: the commit message
  breaks the convention `meow-scm` checks. Reword it with
  `git commit --amend`.

## A commit message has problems

`don't use this message until they are fixed` means `meow-scm` found the
message breaks the convention your profile declares under `[commits]`, or
credits a tool. Each problem names its line and what is wrong, such as
`subject length: 74 characters, over the limit of 72`. Fix each line it names
and check the message again.

If `meow-scm` exits 3, your profile declares no convention, so it checked the
ban on crediting a tool alone. Declare your convention under `[commits]` to
have it checked.

## The prose gate blocked a publish

`meow-prose-gate` blocked a commit, a pull request, an issue, a comment or a
release note, and Claude Code shows its reason as `P1 | "span" | fix`, one line
per problem. P1 is an idiom from the gate's list of fifteen, P2 a line holding
only bold text, and P3 text hidden in a file the gate can't read. The span is
copied from the command, so you can find it there. Claude Code rewrites the
text from the reason and publishes again. If you ran the command yourself, or
the retry is blocked too, apply the fix the reason names. If the span is inside
code or a path the gate should have skipped, that is a defect in the gate:
report it with the command.

If the gate prints `unrun` and `nothing was checked`, the unit carries no
binary for your machine, so it let the publish through unchecked. Reinstall
the unit.

## A step is not ready

`paw ready implement: not ready` means the step you asked for needs an
approved input, and `paw` lists what is missing below the message, such as a
task another one depends on that isn't done. Approve the input or finish the
task it names, then run the step again. If you run `/meow-flow:run` with
nothing newly approved, it says what it is waiting on.

## meow-method is now meow-flow

`meow-method is now meow-flow` means the unit you installed as `meow-method`
was renamed, and the copy under the old name is a stub with no skill and no
`paw`. Move the install:

```bash
claude plugin install meow-flow@meowpaw
claude plugin uninstall meow-method@meowpaw
```

## GitHub's client couldn't run

`gh couldn't run` means `meow-github` couldn't start GitHub's own client,
`gh`, which it reads GitHub through. Install `gh` and sign in:

```bash
gh auth login
```

`unread` means `gh` ran, but a listing failed. The report names the listing
and what GitHub said, and lists what was read before it stopped. Fix what
GitHub reported, such as a missing permission, and run it again.

## Replies don't follow the reply shape

`meow-core` sets the shape of every reply: the command or path first, a
failure as its cause, location and fix, and no preamble or recap. Claude Code
discovers the unit's style without applying it, so select it yourself, and
replies follow it from the next one:

```text
/output-style meow-core:meow
```
