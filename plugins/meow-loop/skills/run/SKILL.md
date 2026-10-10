---
name: run
description: Starts a run inside this session that repeats `/meow-flow:run` until the record holds no open work or a bound is reached. A person types it with --iterations, --hours and --tokens.
disable-model-invocation: true
---

<role>
A person typed this command to start a run in this session. The
`UserPromptSubmit` hook has already written the run's files and told you its
id, its bounds and its progress file, so this skill starts nothing itself.
Only a person can start a run, because a run the model started is one nobody
chose to pay for (REQ-0894).
</role>

<steps name="work an iteration">
1. Read the progress file the run's context names, and note what the earlier
   iterations did.
2. Run `/meow-flow:run` once and carry the chain to its next stop.
3. Update the progress file with what you did and what the next iteration
   needs, before you finish.
</steps>

<rules name="run">
- R1. Never run `meow-loop` or edit a run's `run.toml`, `log.jsonl` or its
  bounds, because the run's program decides every ending from the record and
  the transcript, and the guard denies each of them.
- R2. Write only the run's `progress/progress.md` and `report.md`, because
  they are the two files an iteration may write.
- R3. Don't decide that the run is finished or that a bound is reached,
  because the record decides when the run ends and you don't.
</rules>
