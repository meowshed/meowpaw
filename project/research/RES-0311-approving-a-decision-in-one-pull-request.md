---
id: RES-0311
artifact: research
status: approved
revised: 2026-09-30
elaborates: RES-0310
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A decision can be approved in one pull request only if the record can tell a status waiting on its merge from an approval

## Summary

Landing a decision's research, requirements, decision record, specification
changes, epic and tasks in one pull request works today only by writing each
record as approved before anyone has read it, and the program then treats
those records as approved on the unmerged branch: `paw ready implement` exits
0 and `paw status` names the task next. Records written that way also skip the
rules the layout applies to drafts alone. This note covers what the
one-pull-request path needs so that the stop moves to the pull request and
doesn't vanish. It doesn't cover how a code host enforces a merge.

## The question

How does a decision land in one pull request, approved by its merge, without
the method building on an approval nobody has given yet?

The question assumes one pull request is worth having. RES-0310 measured that
the two record changes of one earlier decision added 4,044 lines before any
code and that a pull request merges in a median of 3.5 minutes, so splitting
the records bought no review. The assumption stands, and the owner asked for
it, so the options below keep the path and differ in how they guard it.

## Method

I read the method skill and its rules M5, M6 and M20 in `meow-flow` 0.45.0,
the `ready` and `check frozen` code in `crates/meow/src/record.rs`, and the
draft rules in `plugins/meow-flow/lib/layout.toml`, all on `main` after #764.
I ran one probe on 2026-09-30: on a branch off `main`, I added an approved
task that realises an approved decision, ran `paw ready implement` and
`paw status`, and removed the task. I read the two agent reviews of the closed
pull request #765, which tried to fix this by wording alone; they are not
kept, so what I take from them is restated here as findings I checked.

## Findings

### The method skill states two rules that can't both hold

M5 says to stop after writing an artifact that needs approval. M20 says to
land a decision's research, requirements, decision record, specification
changes, epic and tasks in one pull request "where they are written together".
Neither names the other, and the step chain's gate, `paw ready`, refuses a
step whose input isn't approved, so a session following M20 has to mark each
record approved itself to go on.

### An approved status on an unmerged branch reads as an approval

With an approved task added on a branch and absent from `origin/main`,
`paw ready implement` printed `ready; TSK-3999 approved and complete` and
exited 0, and `paw status` printed `next: implement TSK-3999`. `ready` reads
the working tree and asks git nothing. A later session on that branch, which
remembers nothing, would implement before the person merged.

### Records written as approved skip the draft rules

The layout applies `draft_rules` and `draft_sections` to a record whose status
is `draft` and to no other. For research these are dated sources and no cited
requirement; for a requirement, one obligation, standing alone, a named
verifier and no negated form; for a task, one authority and declared
dependencies. A record written as approved from the start meets none of them
and `paw check` still reports 0 findings.

### The frozen check already leaves such records free until they merge

`check frozen --base <rev>` skips a file absent at the base, so a record
created on the branch, whatever its status, can be edited there until it
lands. Nothing extra is needed for a person to ask for changes on the pull
request.

### The repository declares its trunk

`.meowpaw/profile.toml` names the trunk under `[git] trunk`, and the git pack
reads it to refuse a commit there. A repository with no git, or that declares
no trunk, gives the record program nothing to compare a branch against.

### Wording alone did not close the gap

The closed pull request #765 rewrote M5, M20 and the specification twice.
After the second rewrite the path still marked a record approved with check
findings open, still let a fresh session implement before the merge, and
narrowed an approved decision's unconditional sentence with no record
authorising it.

## Options

1. **Leave the two rules as they are.** It costs nothing. A session picks
   one rule by chance, and the second finding stays.
2. **Drop the one-pull-request path.** Every gate stops, as the first rule
   says. It is the safest and the simplest to state. It returns the cost
   RES-0310 measured, and the owner asked for the path.
3. **Keep the path on request, and have the program hold the two gaps.** The
   skill writes each record as a draft, checks it, marks it approved and goes
   on, stopping once at the pull request. The program refuses to call a task
   ready to implement while its record is absent from the declared trunk. It
   is better at keeping one pull request and one stop. It needs a git read in
   `ready` and `status`, and it holds nothing where no trunk is declared.
4. **Store a separate status for "waiting on a merge".** It is better at
   being visible in the file itself. It adds a stored status that somebody
   must move after the merge, which the derived-state rule of the record
   exists to avoid, and the merge already says it.

The third fits the findings, and I lead with it.

### The case against the third option

The trunk check reads git, and the record program has read only files until
now, so a repository with a shallow clone, a renamed trunk or no remote can
get an answer it didn't expect. Where the trunk can't be read the program has
to say so and not guess, and a repository that commits records straight to
its trunk sees no difference at all, which means the check guards only the
one path that needs it.

## Conclusions

1. Where a person asks for a decision to land in one pull request, the method
   stops once, at that pull request, and at no gate before it, because the
   merge is the approval and the first finding shows two rules disagreeing on
   where to stop.
2. Without that request the method stops at every approval gate, because a
   request for one pull request is what moves the stop.
3. A record written on the one-pull-request path meets every rule a draft of
   its kind meets before it is marked approved, because the third finding
   shows an approved record skipping them.
4. A task whose record is absent from the trunk the repository declares is
   not reported ready to implement, because the second finding shows a
   status on an unmerged branch read as an approval.
5. The chain's status names such a task as waiting on the merge, and not as
   next, because a session that remembers nothing reads only the status.
6. Where no trunk is declared or it can't be read, the program says the
   approval can't be told from a pending one and doesn't refuse, because a
   guess either way is worse than the statement.

## Sources

- Read 2026-09-30: `plugins/meow-flow/skills/method/SKILL.md` in `meow-flow`
  0.45.0 - rules M5, M6 and M20.
- Read 2026-09-30: `crates/meow/src/record.rs` on `main` after #764 - `ready`,
  `check_frozen` and how a record is opened.
- Read 2026-09-30: `plugins/meow-flow/lib/layout.toml` - the draft rules of
  each kind.
- Read 2026-09-30: `.meowpaw/profile.toml` - the declared trunk.
- Read 2026-09-30: the probe on a branch off `main`, `paw ready implement` and
  `paw status` over a task absent from `origin/main`.
- Read 2026-09-30: the closed pull request #765 and RES-0310 - the earlier
  attempt and the measurements.
