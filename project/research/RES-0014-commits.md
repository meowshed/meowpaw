---
id: RES-0014
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Commits, branches and merges

## Summary

The published standards and the six internal repositories agree on the grammar
and disagree about the subject limit, so the limit is stated and overridable,
and nobody assumes it. A body is written only where the reason is not evident
from the diff, because a ceremonial body teaches readers that bodies are noise.
One task lands as one branch and one squashed commit, so the history reads as
what the project gained, and never as how it got there.

Research for the `conventional-commits`, `branching` and `pull-requests` skills
in `meow-scm`. What the standards actually say, what the six internal
repositories do, where they disagree, and what a skill has to decide.

## Method

The published conventions were fetched and read directly on 2026-09-20: the
commit-message specification for the grammar, and the length conventions, which
disagree with each other, and we cite the disagreement itself.

The six internal repositories were read from their working trees for what they
actually enforce, which is where the divergence between stated and practised
limits was found.

Nothing was measured. No history was sampled to check how often the conventions
are followed, which would have made the claim about ceremonial bodies stronger
than it is.

## What the standards say

Conventional Commits 1.0.0 defines the header only: a type, an optional
scope in parentheses, an optional `!` for a breaking change, a colon, a single
space, and a description. Then an optional body and optional footers. It says
nothing about length, and it explicitly tells implementors not to treat
messages as case-sensitive.

The 50/72 rule is not part of that spec. It comes from Tim Pope's 2008 post,
and an analysis of the Linux kernel supports it, showing 50 characters as the
most common subject length. 72 comes from 80 minus the four characters of
padding `git log` adds. It is nonetheless universally expected, which makes it
a convention the harness follows and cites, having invented none of it.

commitlint is stricter than the specification it implements.
`@commitlint/config-conventional` defaults the header limit to **100**
characters, forces lower-case types, and rejects sentence-case subjects - the
last of which the spec deliberately permits. A skill that says "follow
Conventional Commits" and a repository that runs commitlint can therefore
disagree while both are correct.

### The trade-off this creates

| Limit | Argument for                                                                                                  | Argument against                                                                                     |
| ----- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 50    | Fits every `git log --oneline` and GitHub list view without truncation; forces the subject to name one change | Too tight for `type(scope):` plus a meaningful description - the prefix alone can cost 20 characters |
| 72    | Room for a prefix and a real description; still readable in a terminal                                        | Truncated in some GitHub views                                                                       |
| 100   | commitlint's default, so no conflict with the common tool                                                     | Long enough that subjects start carrying two ideas                                                   |

The position taken: **the harness states a limit and the repository may change
it**. None of the three is right everywhere, and a skill hard-coding 50 gets
overridden on its first collision with a real commitlint config. What is not
negotiable is that a subject names one change - the length rule is a proxy for
that, and the real obligation is the thing being proxied.

## What the internal repositories do

All six agree on conventional subjects, imperative mood, lower case, no
trailing full stop. They differ on three things.

Length. `meowctl` says under 72. `meowhub` says "short enough to read in a
log" without a number. Nobody says 50.

Body. `meowhub` requires the body to explain _why_, to name the real bugs
found and what proved the work, and to wrap at 72. `meowctl` leaves the body
optional. This is a real disagreement, and the resolution matters: a mandatory
body produces ceremonial paragraphs on trivial commits, which trains readers to
skip bodies entirely.

Granularity. `meowhub` is explicit that one slice lands as **one commit**,
squashed, because "the history should read as a list of what the household
gained, not as a transcript of how it was built". `meowctl` says squash merge
and one branch per issue, which is the same rule said differently.

That convergence is the strongest signal in the set: two repositories with
nothing else in common independently decided that intermediate commits are for
review and do not survive the merge.

## How others do it

Angular, the origin of the format, uses a 100-character header limit and
requires a body for anything but a trivial change.

The Linux kernel has no type prefix at all. It uses `subsystem: summary` by
convention, which no specification defines, and it demands a body explaining
the motivation for nearly everything.

Semantic-release and friends are the reason the machine-readable type exists:
version calculation, changelog entries and release notes are all derived from
the type and the breaking-change marker, with no human authorship at release
time. The skill states this, because it explains why `fix` against `feat` is a
decision with consequences that no label carries.

Conventional Comments applies the same idea to review comments, where this
specification covers commits, and is covered in
[RES-0030-review.md](RES-0030-review.md).

## Squash, merge or rebase

The three options, and what each does to the history the method depends on.

| Strategy     | History                                                  | Cost                                                                                 |
| ------------ | -------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Squash       | One commit per unit of work; the branch's steps are gone | Bisecting lands on large commits; a long-running branch produces one enormous change |
| Merge commit | Every intermediate commit survives, plus a merge node    | The log becomes a transcript; `git log --oneline main` is unreadable                 |
| Rebase       | Intermediate commits survive, linearly                   | Requires the author to have curated every commit, which in practice nobody does      |

The harness takes squash, following both internal repositories that decided it,
and the reasoning is specific, with no aesthetics in it: **the method already
produces the detailed record**. The plan carries each task with its evidence,
the artifacts carry the decisions, and the review carries the verdict. A commit
history that repeats all of that is a second, worse copy of it. What the
history is uniquely good at is answering "what did this project gain, and
when", and one commit per unit of work is the shape that answers it.

This also resolves a tension the harness would otherwise have. The rule that
status moves in the change that moves the work requires a task to be marked
complete _in the commit that completes it_, and on a squashed branch the plan's
final state lands with the squash. The intermediate marks exist during the work
and collapse with everything else, which is correct. The question "was this
ever ticked prematurely" belongs to the branch review, and the history answers
nothing about it.

## The attribution ban

Two of the six state it as an explicit override of default tooling behaviour,
and one asks for existing trailers to be removed from history. The mechanism to
copy is `meowctl`'s: a `grep` that matches the _attribution patterns_ and never
the bare word, because a check that trips on a path like `.claude/commands/`
gets disabled within a week.

```bash
git log -1 --format=%B |
  grep -iE 'co-authored-by.*(claude|anthropic|copilot)|generated with|noreply@anthropic'
```

The word naming the product is allowed where it names the product - a model id
in a configuration file states a technical fact and bylines nobody.

## Conclusions

1. A stated subject limit, overridable in the profile. Default 72: long
   enough for `type(scope):` plus a real description, short enough to fail the
   two-ideas subject.
2. A body only where the reason is not evident from the diff. Not mandatory,
   not forbidden. The failure to avoid is the ceremonial body, which teaches
   readers that bodies are noise.
3. Never a transcript. "Ran the tests, fixed the lint, updated the plan" is
   the shape of a body that should not exist.
4. One task, one branch, one squashed commit, with the scope naming the
   epic where there is one.
5. The type's consequence stated, so `fix` versus `feat` is understood as a
   release decision.
6. The attribution check as a pattern match, run before committing.

## Sources

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/),
  read 2026-09-20 - the header grammar, the optional body and footers, and the
  instruction not to treat messages as case-sensitive.
- [The 50/72 rule](https://deviq.com/practices/50-72-rule/) and
  [Git commit messages: why keep the 50-character convention](https://blog.thirstybear.co.uk/2025/05/git-commit-messages-why-keep-50.html),
  read 2026-09-20 - Tim Pope's 2008 post as the origin, the Linux-kernel
  analysis behind 50, and 72 as 80 minus `git log`'s four-character padding.
- [What is the Conventional Commits standard in commitlint](https://commitlint.com/2026/05/14/commitlint-3/),
  read 2026-09-20 - `@commitlint/config-conventional`'s 100-character header
  default and its subject-case rule, which is stricter than the specification it
  implements.
- [Conventional Commits cheat sheet (2026)](https://s2p.dev/blog/conventional-commits-cheat-sheet),
  read 2026-09-20 - the release-automation consequence of the machine-readable
  type.
- `~/workspace/meowctl/.claude/skills/scm/SKILL.md` and
  `~/workspace/meowhub/CLAUDE.md`, read 2026-09-20 - the two internal
  conventions, their disagreement about bodies, their agreement about squashing,
  and the attribution ban with its pattern-matching check.
