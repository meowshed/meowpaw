---
id: EPC-1720
artifact: epic
status: approved
revised: 2026-09-29
realises: ADR-1810
---

# Every GitHub request goes through one layer that reads its limits, stops at a stated wait, and writes only issues

Realises exactly one authorising record, ADR-1810. The epic is complete when
every call `meow-github` makes to GitHub goes through one request layer, a
throttled or budget-bound `project` stops with the time to retry and a
`partial` list, every run names its credential's form and its four budgets, a
refusal names the permission it wanted, and a governance change is refused by
the layer and asked about by the hook.

## Acceptance criteria

Taken from ADR-1810, from its list of how I will know it was realised, before
the tasks below were written:

1. A stand-in `gh` answering a create with 403 and `retry-after: 30` makes the
   run print `throttled`, the endpoint and the time 30 seconds after the
   response, exit 3, and send no further call. With `--wait` and an injected
   clock, the stand-in records the next call no earlier than 30 seconds after
   it. With `--wait`, a first throttle of 3,540 seconds followed by one of 120
   seconds makes the run sleep the first, start no second sleep, and stop as
   throttled (REQ-2566).
2. A unit test derives 3,207 seconds from `x-ratelimit-reset` 1790695444
   against a `Date` of 1790692237, the pair RES-0290 observed, and would get
   about 3.2 seconds, or a date in 1970, if the value were read as
   milliseconds. A `retry-after` that isn't a number of seconds gives an
   unknown wait and no further call (REQ-2578).
3. A response with no rate-limit header is reported as carrying none and the
   run goes on. A replay whose `Date` is ten minutes old isn't counted and its
   `remaining` isn't reported as current. With the injected local clock two
   minutes ahead of the stand-in's `Date`, a fresh cached response is counted
   and its `remaining` reported as current, and the run's first call carries
   no `--cache` (REQ-2566).
4. With 501 unmapped tasks, the stand-in records 500 creates and the run stops
   before the 501st, naming content creation at 500 of 500 this hour. The
   stand-in's timestamps show writes at least a second apart. The budget lines
   name each of the four counts, and with `x-ratelimit-limit: 1000` and
   `GITHUB_ACTIONS=true` the primary line names 1,000 (REQ-2568).
5. The stand-in failing the third create makes the run send the read-back
   listing for the first two, then print `partial: projected` with those two
   and `not projected` with the rest, and exit 3. With the injected local
   clock two minutes ahead of the stand-in's `Date`, the listing's `since` is
   the first response's `Date` and both issues are read back. The stand-in
   answering the third create with a secondary throttle makes the run send no
   listing, and print the first two under `created, not read back` and the
   rest under `not projected`. A created issue the listing omits goes under
   `created, not read back` (REQ-2572).
6. A 403 carrying `X-Accepted-GitHub-Permissions: issues=write` is reported
   with `POST repos/o/r/issues` and `issues=write`. One carrying only the
   OAuth scope headers names the accepted scopes and the credential's own,
   and one carrying neither quotes GitHub's message. A 404 on a mapped issue
   adds that it may be hidden from this credential (REQ-2574).
7. `GH_TOKEN` set, only `GITHUB_TOKEN` set, and neither set yield the three
   forms on the first line, and `GITHUB_ACTIONS=true` adds the workflow. A
   sentinel token value in either variable appears nowhere in the output
   (REQ-2582).
8. A unit test shows the layer refusing `PATCH repos/o/r`,
   `PUT repos/o/r/branches/main/protection`, `POST repos/o/r/rulesets`,
   `PUT repos/o/r/actions/permissions/workflow` and
   `PUT repos/o/r/contents/.github/workflows/ci.yml` without starting `gh`,
   and no allow-list entry matching the governance list. A source test finds
   every method and endpoint the crate builds on the allow list (REQ-2576).
9. Hook fixtures answer `ask` to
   `gh api -X PUT repos/o/r/branches/main/protection`,
   `gh api repos/o/r/rulesets -f name=x`,
   `gh api repos/o/r/rulesets --input rs.json`,
   `gh repo edit --visibility private`, `gh repo archive`,
   `gh api graphql -f query='mutation { x }'`,
   `GH_TOKEN=x gh api -X PUT repos/o/r/branches/main/protection`,
   `env GH_TOKEN=x gh repo delete o/r` and
   `git status && gh api -X PUT repos/o/r/rulesets/1`, and print nothing for
   `gh api repos/o/r/issues` and
   `gh api graphql -f query='{ viewer { login } }'`. The token in front of a
   refused command appears nowhere in the hook's output (REQ-2576).
10. Every requirement ADR-1810 addresses lands in exactly one closed task, and
    REQ-2580 reads as postponed.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2940 add the request layer in
      `crates/meow/src/github/request.rs`, move `history`, `project` and
      naming the repository onto it, read the limit headers, tell a replay
      from a fresh response, derive every wait from one table, stop at a
      throttle and add `--wait`
      closes: REQ-2566, REQ-2578

- [x] T-002 [P] TSK-2950 keep the four budgets, space the writes a second
      apart, stop at a ceiling, and name the credential's form in `project`'s
      report and `history`'s document
      closes: REQ-2568, REQ-2582
      evidence: the six checks in `Budgets`, `Credential` and `History` pass
      after failing first, and the five verbs pass. TSK-2950 carries the rest.
      depends: TSK-2940 (blocking) - the counts sit in the layer

- [x] T-003 [P] TSK-2960 read the created issues back in one listing after the
      last create, and print `partial:` when `project` stops before visiting
      every task
      closes: REQ-2572
      evidence: the five checks in `Partial` pass after failing first, and the
      five verbs pass. TSK-2960 carries the rest.
      depends: TSK-2940 (blocking) - the listing goes through the layer, and
      the run stops at a throttle only once the layer does

- [ ] T-004 [P] TSK-2970 report a 401, a refused 403 and a 404 on a mapped
      object with the method, the endpoint and the permission GitHub named
      closes: REQ-2574
      depends: TSK-2940 (blocking) - the layer is what reads a refused call's
      headers

- [ ] T-005 [P] TSK-2980 refuse a write off the allow list in the layer, hold
      the governance list, and ship the `governance-guard` hook
      closes: REQ-2576
      depends: TSK-2940 (blocking) - the allow list is checked in the layer

TSK-2950, TSK-2960, TSK-2970 and TSK-2980 each wait only on TSK-2940, and none
waits on another. Each raises `meow-github`'s minor version and its README's
`describes`, and TSK-2950 and TSK-2960 both change `project`'s report, so
whichever of them lands later rebases onto the other and takes the next minor
version above it. That shared file and version are a convenience, so no task
names another of the four under `## Depends on`.

## Coverage

ADR-1810 addresses seven requirements, and each lands in one task. REQ-2566
and REQ-2578 land in TSK-2940, because reading the headers, telling a replay
from a fresh response and turning a header into a wait are the layer itself,
and a throttle's stop needs the wait the table gives. REQ-2568 and REQ-2582
land in TSK-2950, because the primary budget line reports the limit the
credential's form earned, and `history` carries both as two fields. REQ-2572
lands in TSK-2960, REQ-2574 in TSK-2970 and REQ-2576 in TSK-2980.

Criteria 1 to 3 close in TSK-2940, 4 and 7 in TSK-2950, 5 in TSK-2960, 6 in
TSK-2970, and 8 and 9 in TSK-2980. Criterion 10 is the verify step's, and
`paw check coverage` shows each requirement landing now.

The smallest set that tests the decision is TSK-2940 alone: with it, a
throttled `project` stops and says when to retry, which is what REQ-2566
changes for a person running it. Before any task is finished, one thing can be
measured: against a stand-in `gh` answering the second create with 403 and
`retry-after: 30`, `project` today prints `stopped part way`, names no time to
retry and names no header, and after TSK-2940 it must print `throttled`, the
endpoint and a time 30 seconds after the response.

## Not covered

- REQ-2580, which ADR-1810 postpones until a pack or a `meow-github` command
  reads a service that bills by query cost.
- GitHub's GraphQL budget, conditional requests, budgets spent by another run
  or a person on the same account, and an issue created by a `POST` whose
  response was lost, which ADR-1810 leaves unsettled.
- Governance changed by a command other than `gh`, or by a `gh` the guard's
  split doesn't reach, and whether the person answering the hook's prompt
  holds the governance role, which ADR-1810 names as still not working.
- The user-facing pages beyond each task's README `describes` and the lines
  its own behaviour changes: the document step brings the rest of
  `plugins/meow-github/README.md` and `docs/`, the hand path's headers and
  spacing included, into line once every task is done.
