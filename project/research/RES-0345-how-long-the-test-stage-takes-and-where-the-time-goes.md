---
id: RES-0345
artifact: research
status: approved
revised: 2026-10-10
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The test stage takes five to sixteen minutes, and a quarter of that is one suite

## Summary

On the owner's machine the `test` stage took between 320 and 962 seconds in six
runs on 2026-10-09 and 2026-10-10, and the `gate` job in continuous integration
(CI) took between 5 minutes 47 seconds and 8 minutes. The unit suites run one
after another in a single `&&` chain, so the stage lasts as long as their sum,
about 540 seconds, and the slowest single suite, `meow-flow`, takes 162 seconds.
Running the suites at the same time would bound the stage by that suite, not
by the sum.

The document covers the duration and where it goes. It doesn't profile single
tests, and it doesn't measure the build, which the `build` stage owns.

## The question

How long does the `test` stage take, what is the time spent on, and what bound
is reachable without changing what a suite checks?

The assumption behind the question is that the time is worth reducing. A slow
stage costs a person a wait on every change and costs a run that is cut short
by the limit of a tool call, as it did twice in this session. The cost of
parallel suites is that they stop sharing state by accident, which this
document didn't test for.

## Method

I read the output of `meow-checks run test` from six runs, which prints each
suite's `Ran N tests in S` line, and the `gate` job times from `gh pr checks`
for seven pull requests. I read `[tasks.test]` in `mise.toml` and
`crates/meow/build-units`. I ran the 14 unit suites at eight at a time once,
with `xargs -P 8`. I couldn't obtain a per-test profile, and I couldn't
explain why that parallel run, whose slowest suite took 166 seconds, took
longer than 600 seconds as a whole, because my wrapper hit its limit first.

## Findings

### The stage takes 320 to 962 seconds

Six runs of `mise run test` through `meow-checks` on Darwin arm64: 962.5, 704.6,
354.3, 345.5, 330.7 and 319.6 seconds. The two longest ran while another build
was running on the same machine, which I didn't separate from the rest. The
`gate` job on seven pull requests took 5:47, 6:07, 6:19, 6:54, 7:15, 7:28 and
8:00, with the build inside it.

### The suites run one after another and their sum is about 540 seconds

`[tasks.test]` is one `run` of `mise run crate && python3 -m unittest discover
... && ...` over the units. In one run the suites took: `meow-flow` 162 s (281
tests), `meow-loop` 107 s (103), `meow-prose-gate` 96 s (58), `meow-github` 71 s
(58), `meow-checks` 23 s (52), `tools/` 11 s (142), `meow-mise` 17 s, `meow-markdown`
16 s, `meow-licence` and the other six under 10 s each. The crate's own tests
took 0.34 s and 2.4 s.

### The longest suite alone is 162 seconds

Run at eight at a time, the slowest suite took 166 seconds, so concurrency
didn't lengthen it much. The suites with the longest times start real
processes: they create temporary git repositories and run the units' own
binaries. I read the suites' sizes and names for this and not the tests.

### Every worktree rebuilds the binaries

`crates/meow/build-units` builds 12 feature sets into `target/<feature>` under
the checkout's root, and a new worktree has none. The first build in a new
worktree took 91 seconds on 2026-10-10, and `test` depends on `build`.

### The gate check reads the chain and must follow a change to it

`tools/check_gate_covers_verbs.py` splits each stage's command on `&&` and holds
`[tasks.all]` to it (BUG-1510). A split of `[tasks.test]` into tasks that run
at the same time changes what that check reads, so the two have to change
together.

## Conclusions

1. The `test` stage must finish within five minutes on the owner's machine
   with the units' binaries already built, so a change is verified in the time
   it takes to read a review comment (Findings: the stage takes 320 to 962
   seconds; the longest suite is 162 seconds). The bound is a choice I made: it
   sits above the slowest suite and below every duration measured.
2. The check that holds `[tasks.all]` to the stage commands must keep reading a
   stage that is split into tasks, so the gate doesn't pass a tree whose stage
   no longer runs a suite (Findings: the gate check reads the chain).
3. Every suite the stage ran must still run, which a check can count against
   the directories that hold tests (Findings: the suites run one after another).

## Sources

- `mise.toml`, `[tasks.test]` and `[tasks.build]`, as of pull request 877, read 2026-10-10 - the chain and its dependency.
- `crates/meow/build-units`, as of pull request 877, read 2026-10-10 - the 12 build directories.
- `tools/check_gate_covers_verbs.py`, as of pull request 877, read 2026-10-10 - how the gate holds `[tasks.all]` to the stages.
- Output of `meow-checks run test` on 2026-10-09 and 2026-10-10, six runs, and `gh pr checks` for pull requests 868 to 877, read 2026-10-10 - the durations.
