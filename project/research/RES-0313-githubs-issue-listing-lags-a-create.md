---
id: RES-0313
artifact: research
status: approved
revised: 2026-09-30
elaborates: RES-0312
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# GitHub's issue listing can leave out an issue created a second earlier, while a read by number finds it

## Summary

A listing of a repository's issues sent straight after a create left out the
issue just created, twice in two runs, and a listing sent about ten seconds
later included it. The start of the listing was not the cause, because
neither run named the repository, so each run's first response was a read
sent before its create. A read of each issue by its number straight after its
create found all six issues of an earlier run. So the read-back listing
ADR-1810 chose can miss issues whatever its start, and a read by number
finds them. This note covers the read-back after `project`'s creates, and
doesn't measure how long the listing lags.

## The question

How does `project` read back the issues it created, given that the listing
it sends straight after its last create can leave some out?

The question assumes the lag is the cause. The other candidate is the
listing's start, which RES-0312 found can fall a second after an issue when
the run's first request is the create. Both runs below sent a read first, so
their start fell before the create, and the start doesn't explain them.

## Method

On 2026-09-30 I ran `meow-github project ADR-2320` and
`meow-github project ADR-2330` from `main` at `2b25ba63`, with no repository
named, which filed #783 and #784. I then read both issues by number and sent
one listing, with `gh` 2.101.0. I read the body of #732, which records the
projection of EPC-1910 under the request layer before TSK-2960 replaced the
read by number with the listing, and `run` in
`crates/meow/src/github/project.rs` at `2b25ba63`. I didn't measure how long
the lag lasts, which would need more creates on a public repository, and I
found no GitHub documentation of it.

## Findings

### A listing sent straight after a create left the issue out, twice

`project ADR-2320` created #783 and printed
`created, not read back TSK-4020 (issue #783, not in the listing)`.
`project ADR-2330` created #784 and printed the same for TSK-4030. Each run's
first request was the read of `repos/{owner}/{repo}`, because neither named
the repository, so the listing's `since` was that read's `Date`, before the
create.

### The same issues were listed about ten seconds later

Issue #783 was created at `2026-09-30T17:47:50Z` and #784 at `17:47:52Z`, each with
`updated_at` equal to `created_at`. A listing of
`repos/meowshed/meowpaw/issues?state=all&since=2026-09-30T17:40:00Z` sent at
`17:48:00Z` returned both.

### A read by number straight after each create found every issue

The body of #732 records that `meow-github project EPC-1910` exited 0 and read
each of its six issues back. That run read each issue by its number straight
after creating it, and a run in which a read failed doesn't exit 0.

### The run keeps the mapping when the listing misses an issue

`run` writes `issue:` and `projected:` on the task before the read-back, so
issues #783 and #784 were mapped, and a later run reads each through its mapping
and creates no second issue.

## Options

| Option                                                 | Better at                                                                                        | The case against it                                                                                          |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| Do nothing                                             | One request for a hundred issues, and the failure is safe                                        | Every run that creates an issue can report it as not read back and exit 3, which is what both runs above did |
| Send the listing again after a wait                    | Keeps one listing                                                                                | The lag isn't documented or measured, so any wait is a guess, and a run that waits holds the terminal        |
| Read by number each issue the listing left out         | Found every issue in the only run observed; costs a request only for an issue the listing missed | In the lagging case it costs one request per created issue, as before TSK-2960                               |
| Read every created issue by number and send no listing | One path, observed to work                                                                       | Gives up the listing's saving in the case where it does work                                                 |

I lead with reading by number each issue the listing left out. The case
against it is the cost in the lagging case, which is the cost the pack paid
before TSK-2960 and which the budgets count.

## Conclusions

1. An issue the run created that the read-back listing leaves out must be
   read again before the run reports it as not read back, because the
   listing can lag a create by seconds.

## Sources

- `meow-github project ADR-2320` and `meow-github project ADR-2330` at `2b25ba63`, run 2026-09-30 - the two listings that left out #783 and #784.
- `gh api` 2.101.0 against `meowshed/meowpaw`, run 2026-09-30 - #783 and #784 read by number, and the listing sent at `17:48:00Z`.
- [#732](https://github.com/meowshed/meowpaw/pull/732), read 2026-09-30 - a projection that read six issues by number straight after creating them and exited 0.
- `crates/meow/src/github/project.rs` at `2b25ba63`, read 2026-09-30 - the mapping is written before the read-back.
