---
id: EPC-2000
artifact: epic
status: done
revised: 2026-09-28
realises: ADR-2100
---

# A read-only router routes each request before work starts, and the route skill reports it before any edit

Realises exactly one authorising record, ADR-2100. The epic is complete when
`meow-flow` ships the `router` agent and the `route` skill, a request to change
a repository with `meow-flow` installed starts with a stated route and its
reason, and every requirement ADR-2100 addresses lands in a closed task.

## Acceptance criteria

Taken from ADR-2100, from its list of how I will know it was realised, before
the tasks below were written. The evaluation cases run by hand on Sonnet 5 and
Opus 5.5, never on a schedule or in CI, because each run calls a model, so a
criterion closed by a case is closed by a kept run and not by the gate.

1. The static test passes on the shipped agent and skill, and fails on a copy
   of the agent that names Write, Edit or Bash or drops `tools`. Closed by:
   `RouterAgent` and `RouteSkill` in `plugins/meow-flow/tests/test_route.py`,
   in the gate's output.
2. A case asking to fix a typo routes `none`, reports the route and its reason
   before any tool that writes, and the router is the first agent the session
   dispatches. Closed by: the case `route-a-typo`.
3. A case asking in plain words for verbs to read tasks from a task runner, a
   change ADR-1070 governs, and one calling a change to how the profile is
   parsed a tiny fix, each route `full`, and each reason names a path or an
   identifier in the repository. Closed by: the cases `route-plain-words` and
   `route-a-tiny-fix`.
4. A case whose evidence points both ways routes to the larger size and says
   `ambiguous` with the evidence on each side. Closed by: the case
   `route-both-ways` for the router's reply, and `route-reported-ambiguous`
   for the skill's report.
5. A case asking for three unrelated changes reports three entries, each with
   its size and shape, and stops. Closed by: the case `route-three-changes`.
6. A request carrying `route none` dispatches no router and reports the route
   as given. A `route none` given after a `full` route, and a `route full`
   after a `none`, each change the route with no further question. A
   `route reduced` for new work that no approved record authorises reports
   `full`, the `reduced` given, and that no approved record authorises the
   work. A `route full` after a several-changes route keeps the list with
   every entry `full`, and a `route one` after it reports one change at the
   largest size among the entries. Closed by: the cases `route-given`,
   `route-overridden`, `route-reduced-unauthorised` and `route-list-overridden`.
7. In every run of every case, the stream shows no Write, Edit, NotebookEdit
   or Bash call before the route is reported, and each run starts in a scratch
   repository where `git status --porcelain` prints nothing. Closed by: a
   grader shared by every route case, in each case's graders.
8. A question in chat that changes nothing dispatches no router. Closed by:
   the case `route-a-question`.
9. Every requirement ADR-2100 addresses, REQ-0330, REQ-0332, REQ-0334,
   REQ-0336, REQ-0338, REQ-0340, REQ-0342, REQ-0344 and REQ-0346, lands in
   exactly one closed task. Closed by: `paw check coverage` and the marks
   below, at the verify step.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-3500 add `plugins/meow-flow/agents/router.md` with
      `tools: Read, Grep, Glob`, its reply fields and its routing rules, the
      static test, the allowlist re-observed on the version `requires.toml`
      states, and the cases for how the router routes
      closes: REQ-0334, REQ-0338, REQ-0342, REQ-0344, REQ-0346

- [x] T-002 TSK-3510 add `plugins/meow-flow/skills/route/SKILL.md`, which
      dispatches the router, reports the route before any write, takes the
      four override words and reports the seven states as themselves; name it
      in the method skill and `CLAUDE.md`; raise
      the budget and the minor version
      closes: REQ-0330, REQ-0332, REQ-0336, REQ-0340
      depends: TSK-3500 (blocking) - the skill dispatches the router and
      reads the reply fields the router's definition states, and every skill
      case runs the router
      evidence: 9 checks seen failing first and passing, 227 `meow-flow`
      fixtures passing, the cases run by hand on both models, in #722;
      criteria 5 to 7 fall short on Opus 5.5 and 7 on Sonnet 5, BUG-1360

No task runs in parallel: TSK-3510 reads the reply TSK-3500 defines. Both
raise `meow-flow`'s minor version, so TSK-3510 takes the next minor version
above the one TSK-3500 lands.

## Coverage

ADR-2100 addresses nine requirements, and each lands in one task. REQ-0334 and
REQ-0346 land in TSK-3500, because the three sizes and the allowlist are
properties of the router's definition a static test reads. REQ-0338, REQ-0342
and REQ-0344 land in TSK-3500 too, because the larger size on ambiguous
evidence, reading the repository and the several-changes shape are what the
router decides; its cases show them. REQ-0330, REQ-0332, REQ-0336 and REQ-0340
land in TSK-3510, because routing before work, reporting the route and its
reason, taking an override and saying `ambiguous` are what the skill does with
the router's reply.

The smallest set that tests the decision is both tasks: without the skill
nothing dispatches the router, and without the router the skill has nothing
to report. Before either task is finished, criterion 1 can be measured: the
static test fails today, because neither file exists.

Criterion 9 rests on both tasks being closed, so no task closes it. The
verify step checks it.

## Not covered

- Recording the route in the record, or checking afterwards that work took
  the route it was given, which ADR-2100 leaves unsettled.
- A hook that refuses a write before the route is reported, which ADR-2100
  rejects until a hook reads the conversation as it stands (RES-0203).
- Unattended approval as a declared route, REQ-2370, which a later decision on
  unattended runs settles.
- Whether the allowlist holds in an interactive session, which ADR-2100 names
  as unmeasured. TSK-3500 re-observes it only from `claude -p`, as RES-0304
  did.
- The median cost of a routing dispatch against the first reversal ADR-2100
  names, 60 s or USD 0.25. The cases record each run's time and cost, and the
  verify step compares the median with that figure.
- The user-facing pages beyond `plugins/meow-flow/README.md`'s `describes`:
  its body, the root `README.md` and `llms.txt`. The document step updates
  them once both tasks are done.
