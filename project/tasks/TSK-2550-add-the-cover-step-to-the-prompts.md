---
id: TSK-2550
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1580
closes: [REQ-3200, REQ-3203]
issue:
---

# Add the cover step's prompt, name ten steps in the method skill, and name where each step's artifact lands

`meow-flow` ships `steps/cover.md`, its method skill names the ten steps in
order, the task and bug templates carry the cover step's part, and each step
file's role names the committed file its artifact lands in, review excepted.
So the prompts hold REQ-3200 and REQ-3203 as the program already holds the
gate. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given `plugins/meow-flow/skills/method/SKILL.md`, when it is read, then its
   body names research, requirements, design, spec, epic, cover, implement,
   document, verify and review in that order, its description names the same
   ten in order, and `steps/` holds one file for each name and no other.
   Closed by: `MethodSkill.test_the_skill_names_ten_steps_in_order` and
   `MethodSkill.test_each_step_has_one_file` in
   `plugins/meow-flow/tests/test_record.py`.
2. Given `meow-flow`, when the `budget` check runs, then it passes with the
   longer description. Closed by: `mise run budget` in the gate's output.
3. Given each file under `steps/`, when its `<role>` is read, then it names
   the committed file ADR-1620's table gives for that step, and review's role
   says it writes nothing into the repository. Closed by:
   `MethodSkill.test_each_role_names_where_its_artifact_lands`.
4. Given `steps/cover.md`, when it is read, then it tells the model to write
   checks and no implementation code, run them and see them fail, keep the
   failing run with `meow-verbs evidence --keep`, land the checks, and fill
   `## Cover` in the four lines, and its role names `implement` as the step
   that picks it up. Closed by: `MethodSkill.test_cover_writes_checks_only`,
   which asserts each of those instructions is present, and the `prompts`
   check in the gate, which holds its tags.
5. Given `steps/epic.md`, then its role names cover as the step that picks it
   up; given `steps/implement.md`, then its third step runs the checks the
   cover step wrote and sees them pass, and no longer writes the task's
   checks. Closed by: `MethodSkill.test_epic_hands_over_to_cover` and
   `MethodSkill.test_implement_runs_the_cover_checks`.
6. Given `paw template task`, then it prints a `## Cover` section reading
   `Not yet.` and naming the four lines; given `paw template bug`, then its
   `enters` comment names cover. Closed by:
   `Chain.test_the_task_template_carries_a_cover` and
   `Chain.test_the_bug_template_names_cover`.
7. Given `CLAUDE.md`'s `own_method_first` chain and `project/vision.md`'s
   chain, when they are read, then each names ten steps with cover between
   epic and implement. Closed by:
   `MethodSkill.test_the_living_documents_name_ten_steps`.
8. Given this change's tree, when `meow-verbs run format lint test` runs,
   then each passes. Closed by: the kept evidence of that run.

## What to do

Write `plugins/meow-flow/skills/method/steps/cover.md` in the shape of the
other step files, following `meow-author:write`. It carries the step's shape
only: which task it reads, `paw ready cover`, writing the task's checks and
never implementation code, running them and seeing them fail, keeping that
run, landing the checks, and filling `## Cover` in the four lines SPC-1090
gives, with each criterion no program can check named under `Judgement` with
its reason. The content rules that REQ-3204, REQ-3206, REQ-3208, REQ-3210,
REQ-3211 and REQ-3213 state stay out, because ADR-1620 leaves them to the
decision that addresses them.

`method/SKILL.md` names ten steps in its body and its description, and the
description stays within `budget.toml`'s 500 characters. `plugin.json`'s
description names ten steps. `steps/epic.md` hands over to cover.
`steps/implement.md` step 3 runs the cover step's checks and sees them pass.
Each step file's role names where its artifact lands, by the kind's name and
not a path, as ADR-1620's table gives, because the profile decides where a
repository's record lives.

`templates/task.md` gains `## Cover` after `## Depends on`, reading `Not yet.`
and naming the four lines. `templates/bug.md`'s `enters` comment names cover.
`CLAUDE.md`'s `own_method_first` chain and `project/vision.md`'s chain, in its
two places, name ten steps.

Raise `meow-flow`'s minor version in `plugin.json` and its README's
`describes`. Write the checks first, in a commit of their own, and see them
fail.

## Depends on

TSK-2530, because the prompts tell the model to run `paw ready cover`, which
exits 2 until that task lands.

## Cover

Not yet.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

The run skill, which TSK-2540 changes. The body of
`plugins/meow-flow/README.md`, the root `README.md` and `llms.txt`, which the document step updates once
every task is done. The cover step's content rules, which a later decision
adds.
