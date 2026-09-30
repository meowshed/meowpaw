---
id: TSK-3500
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-2000
closes: [REQ-0334, REQ-0338, REQ-0342, REQ-0344, REQ-0346]
issue: 648
projected: 3ce6cbc42e07
---

# Add the read-only router agent that routes a request on the repository

`meow-flow` ships `agents/router.md`, an agent that holds `Read`, `Grep` and
`Glob` and nothing else, reads a request with the repository, and replies with
a size, a shape, a reason naming what it read, whether the evidence was
ambiguous and the override words. The `route` skill that dispatches it is
TSK-3510's. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given `plugins/meow-flow/agents/router.md`, when its front matter is read,
   then `tools` names exactly `Read`, `Grep` and `Glob`; given a copy that adds
   `Write`, `Edit` or `Bash`, or drops `tools`, the same assertion fails.
   Closed by: `RouterAgent.test_tools_are_read_grep_glob` and
   `RouterAgent.test_a_writing_copy_fails` in
   `plugins/meow-flow/tests/test_route.py`.
2. Given the router's prompt, when it is read, then it names the sizes `none`,
   `reduced` and `full`, the four shapes including several changes, and the
   reply fields size, shape, reason, ambiguous and override words. Closed by:
   `RouterAgent.test_the_prompt_names_sizes_shapes_and_fields`.
3. Given Claude Code at the version `plugins/meow-flow/requires.toml` states,
   when the router is dispatched in the foreground from `claude -p` and asked
   to create a file, then it reports no tool that writes and
   `git status --porcelain` prints nothing; with `Write` added to a copy, the
   same brief creates the file. Closed by: the kept run of both dispatches,
   and `requires.toml` naming that version as the one the allowlist was last
   observed on. Judgement for whether the reply reads as a refusal, because
   the model's words vary between runs.
4. Given a request in plain words for verbs to read tasks from a task runner,
   and one calling a change to how the profile is parsed a tiny fix, when the
   router is dispatched on this repository's tree, then each reply routes
   `full` and its reason names a path or an identifier in the repository.
   Closed by: the cases `route-plain-words` and `route-a-tiny-fix` under
   `plugins/meow-flow/evals/`, scoring at least their thresholds on Sonnet 5
   and Opus 5.5 in a run by hand.
5. Given a request whose evidence points to two sizes, when the router is
   dispatched, then it replies with the larger size, `ambiguous`, and the
   evidence on each side. Closed by: the case `route-both-ways`.
6. Given a request for three unrelated changes, when the router is
   dispatched, then it replies with three entries, each with its size and
   shape. Closed by: the case `route-three-changes`.
7. Given `meow-flow`, when the `budget` check runs, then it passes with the
   agent's description counted. Closed by: `mise run budget` in the gate's
   output.

## What to do

Write `plugins/meow-flow/agents/router.md` following `meow-author:write`, with
`tools: Read, Grep, Glob`. Its prompt states the three sizes, the four shapes
and the reply fields as SPC-1090 "The route" gives them, because the skill
reads those fields and nothing its brief adds. It tells the router to read
`.meowpaw/profile.toml`, the record's indexes and specifications where the
profile declares a record, and the files the request would touch, to name at
least one of them in its reason, and to take the larger size where the
evidence points to two. The agent inherits the session's model.

Write `plugins/meow-flow/tests/test_route.py` with the class `RouterAgent`,
and see its tests fail before the agent exists.

Repeat RES-0304's dispatch and its control on the version `requires.toml`
states, keep both runs with `meow-verbs evidence --keep`, and record in
`requires.toml` the version on which the allowlist was last observed.

Add the cases `route-plain-words`, `route-a-tiny-fix`, `route-both-ways` and
`route-three-changes` under `plugins/meow-flow/evals/`, each prompt asking the
session to dispatch `meow-flow:router` on the request and report its reply,
with graders for the criterion each closes. Add each case to
`evals/thresholds.toml` before its first run (REQ-0159), and record each run's
time and cost. Every case runs with `meow-core` enabled, so the router's brief
carries the output style's block.

Raise the unit's `permanent_characters` in `budget.toml` to what the budget
check measures, and no further than 1,000. Raise `meow-flow`'s minor version
in `plugin.json`, and its README's `describes` to match.

## Depends on

Nothing: the agent stands alone, and the route skill is the one that needs it.

## Evidence

Closes REQ-0334, REQ-0338, REQ-0342, REQ-0344 and REQ-0346 as far as the
router states them; the route skill that reports the route is TSK-3510's.

Criteria 1 and 2. The cover commit added the three checks, and
the run under #669, whose output is no longer kept, held their failing run: the `test` verb
exited 1 with `FAILED (failures=3)`, all three in `RouterAgent`, because
`agents/router.md` didn't exist. With the agent in place,
`python3 -m unittest plugins/meow-flow/tests/test_route.py -v` exits 0:

```text
Ran 3 tests in 0.002s

OK
```

`python3 -m unittest discover -s plugins/meow-flow/tests` exits 0 with
`Ran 206 tests` and `OK`. `git diff 5b49fa2 -- plugins/meow-flow/tests/test_route.py`
prints nothing, so the checks are the ones the cover commit wrote.

Criterion 3. `requires.toml` states 2.1.283, which is installed beside a
2.1.280 that `claude` resolves to first, so I ran RES-0304's dispatch with the
2.1.283 binary on 2026-09-29. Each session ran
`claude -p --plugin-dir <plugin> --model sonnet --max-turns 6 --permission-mode acceptEdits --output-format stream-json --verbose`
in a scratch repository holding one committed `README.md`, and every `init`
event gave `claude_code_version` as `2.1.283`:

| Run | Agent                                                       | Agent's tool calls                  | `git status --porcelain` |
| --- | ----------------------------------------------------------- | ----------------------------------- | ------------------------ |
| 1   | RES-0304's probe, `tools: Read, Grep, Glob`                 | `Glob` `*.md`, `Grep` `wrold`       | empty                    |
| 2   | the same probe with `Write` added, the control              | `Glob`, `Grep`, `Write` `probe.txt` | `?? probe.txt`           |
| 3   | the shipped `meow-flow:router`, asked to create `probe.txt` | none                                | empty                    |

Run 1's agent replied "Write ... not attempted, no Write tool in my toolset
(only Read, Grep, Glob are available to me)", and run 2's "Write created
.../probe.txt containing `probe`", so the allowlist and not the model's
choice kept run 1 from writing. Run 3's router replied "I hold no tools that
write files or run commands - I have only Read, Grep, and Glob", which reads
as a refusal. A control on the shipped router with `Write` added didn't write
either: it declined as outside its role, so only the probe separates the
allowlist from the prompt. Each dispatch was foreground, with
`run_in_background: false`. `meow-verbs evidence --keep` keeps a verb's run
and not a model's, so the streams stayed in a scratch directory and the
events are quoted here. `requires.toml` now names 2.1.283 as the version the
allowlist was last observed on, and the foreground dispatch from `claude -p`
as the mode.

Criteria 4 to 6. The four cases are `case.yaml` cases, not `prompt.md`,
because only a `case.yaml` takes a `scaffold_script`, and each case's
`scaffold.sh` copies this repository's committed tree into the run's working
directory, which is the tree the router reads. Their thresholds of 0.66 were
committed before the first run (REQ-0159). Each ran by hand on 2026-09-29
with `claude plugin eval plugins/meow-flow --case 'route-*' -j 4 --scaffold --ablation none --model <model> --judge-model claude-opus-5-5`,
3 runs a case, Claude Code 2.1.283, with `meow-core` enabled. Opus 5.5
judged both models, so the Opus figures are a smoke check (REQ-3028).

| Model    | plain words | tiny fix | both ways | three changes | Cost     | Wall time |
| -------- | ----------- | -------- | --------- | ------------- | -------- | --------- |
| Sonnet 5 | 1.00        | 0.78     | 1.00      | 1.00          | USD 4.94 | 495 s     |
| Opus 5.5 | 1.00        | 1.00     | 1.00      | 1.00          | USD 3.08 | 162 s     |

Every case meets its threshold on both models. In all 24 runs the main
session's only tool call was one `Agent` dispatch of `meow-flow:router`, and
the router called only `Read`, `Grep` and `Glob`. The first round, before R4
named a reworded message as pointing to two sizes, scored Sonnet 5 0.33 on
`route-both-ways`: two runs resolved the reword to one size, one of them
`none`, and never said `ambiguous`. That round cost USD 4.76 on Sonnet 5 and
USD 2.95 on Opus 5.5, with every other case at 1.00. In the second round's
failing `route-a-tiny-fix` run, Sonnet 5 found that `crates/meow/src/verbs.rs`
already treats a missing `[verbs]` table as empty, and routed the request a
`reduced` defect. That reading is sound, so the case asks for behaviour the
repository already has, and a later case needs a request that is new work.

The dispatch costs more than ADR-2100's first reversal allows. That reversal
moves routing into the main session where the median dispatch on this
repository takes over 60 s or costs over USD 0.25. From the kept traces, the
router's own median time was 117.9 s on Sonnet 5 (47.0 s to 189.3 s, median
54,490 tokens) and 28.8 s on Opus 5.5 (16.5 s to 39.0 s, median 20,422
tokens). The median session cost USD 0.402 on Sonnet 5 and USD 0.258 on
Opus 5.5, and a session includes the main session's two turns, so it bounds
the dispatch from above. Sonnet 5 exceeds both figures, and Opus 5.5 is near
the cost figure. Whether the reversal applies is the owner's decision, and
this task doesn't make it.

Criterion 7. `mise run budget` prints `meow-flow: 621 of 625 characters on
every turn` with the router's description counted, and `budget.toml` now
states 625.

`meow-flow` moves to 0.38.0, above the 0.37.0 another change landed, and its
README's `describes` with it. SPC-1090 says the router ships and the route
skill doesn't yet.

## Left alone

The `route` skill, the method skill, the constitution template and
`CLAUDE.md`, which TSK-3510 changes. The body of `plugins/meow-flow/README.md`,
the root `README.md` and `llms.txt`, which the document step updates once both
tasks are done. The model the router runs on, which ADR-2100 leaves to the
session until an evaluation shows a smaller model routes as well.
