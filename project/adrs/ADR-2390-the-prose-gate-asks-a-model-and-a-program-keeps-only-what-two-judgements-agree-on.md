---
id: ADR-2390
artifact: adr
status: done
revised: 2026-10-03
addresses:
  [REQ-3740, REQ-3742, REQ-3744, REQ-3746, REQ-3748, REQ-3750, REQ-3752]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2390. The prose gate asks a model to judge the text, and its program blocks only on what two judgements agree on

## Decision

`meow-prose-gate check` judges the published text with a model, as well as
matching the three exact rules. The model only reports what it finds, and the
gate's program decides whether a finding blocks. This amends ADR-1600 in the
places named below, and the rest of ADR-1600 stands: the hook, the commands
it fires on, how the program reads the text from the command, P1, P2, P3 and
the launcher's rule for a missing binary.

The program runs in this order:

1. It reads the text from the command, as ADR-1600 states, and checks P1, P2
   and P3. On any finding it blocks as it does today and calls no model,
   because the text has to change anyway and an exact rule needs no judgement
   (REQ-3740).
2. With no exact finding, it asks the judge twice, in two calls started side
   by side, each with the same text and the same rules. A judgement is one
   run of `claude -p --safe-mode --tools "" --no-session-persistence
--max-turns 1 --model sonnet --output-format json --json-schema <schema>`,
   with the text passed as data inside a tag and never as instructions. The
   schema allows one shape: a list of findings, each with `rule`, one of the
   judged rules, plus `span` and `fix` (REQ-3750).
3. It keeps a finding only where the span is a slice of the text it read from
   the command, which ADR-1600's reader keeps as the command writes it, so the
   span is also a slice of the command (REQ-3746, REQ-3183).
4. It blocks only on a finding whose rule and span appear in both judgements,
   and prints `J1 | "span" | fix` for each, with the fix from the first
   judgement (REQ-3744). With none left, it exits 0 and prints nothing.

The judged rules are three, the list is closed, and a rule joins or leaves it
only by a decision of its own (REQ-3742):

- J1, an idiom, saying or culture reference that P1's list doesn't spell, such
  as `circling back` or `a perfect storm`, because the writing standard's rule
  H2 says a second-language reader looks it up or misreads it.
- J2, an acronym the text uses before it expands it, or never expands, outside
  code font, URLs, identifiers and a commit subject's type and scope, as rule
  H6 says. An acronym that is the product's name, such as `CLI` in a sentence
  naming a tool, still counts, because the reader still has to expand it.
- J3, a paragraph or a list item that opens with a bold phrase and goes on in
  the same line, such as `**Why.** Because ...`, which states a conclusion
  with its argument stripped out, as the writing standard's patterns say. P2
  holds the case where the bold phrase fills the line.

Where a judgement can't be made, the gate lets the publish through and says
so on stdout as `{"systemMessage": "meow-prose-gate: the judged rules were not
checked: <cause>"}`, with exit 0 (REQ-3748). The causes are: no `claude` on
the path, a call that exits non-zero, a call that runs past 45 seconds, and a
reply outside the schema. One failed judgement of the two is enough to report
the rules as not checked, because one judgement alone can't meet REQ-3744.
The hook's timeout rises from 30 to 120 seconds, so the 45-second judge limit
always fires before the hook's.

A hand run, never CI, measures the judged rules before a release ships them:
BUG-1230's four texts pass in three runs of three, and one text per judged
rule that breaks it blocks in three runs of three, with Opus 5.5 judging any
case whose result a fixture can't read (REQ-3752). The run is a smoke check,
and the release notes say so.

Once this is accepted, the gate holds three rules of the writing standard it
couldn't hold before, without a block that quotes text the command lacks, and
a model's single misjudgement no longer blocks on its own. What still doesn't
work:

- A misjudgement both calls make passes the agreement test and blocks. The
  person reads the reason and can dispute it, and a fixture can't catch it.
- A publish where the judge can't run is checked only against P1, P2 and P3,
  and the person is told so on every publish.
- Each publish that passes the exact rules waits for two model calls, which I
  haven't timed.
- Rules of the standard beyond J1, J2 and J3 stay with the writing skill and
  the reviewer.

## Why

The owner asked for the gate to judge text with a model and not with scripts
alone. ADR-1600 named its own reversal: a rule that can't be stated exactly
becomes one the gate must hold, and a model is shown to settle it the same way
twice. J1, J2 and J3 are rules ADR-1600 and SPC-1010 left to review because
no program states them exactly, and blocking only on what two judgements share
is the "same way twice" the condition asks for.

RES-0330 found that a `prompt` or `agent` hook can't be checked by any other
hook, because a deny from one hook wins over the rest. A command hook that
calls `claude -p` and reads the reply keeps the verdict with the program.

BUG-1230's false blocks were of two kinds. A span the command doesn't hold is
dropped by the span check, which ADR-1600's program already runs on its own
findings. A span that is there but breaks no rule, as `in depth` in case 2,
is dropped unless both judgements make the same mistake. If the two calls
were independent at the one rate BUG-1230 reproduced, one in three, that
leaves about one in nine. That figure is arithmetic and not a measurement,
which is why REQ-3752 asks for the hand run.

Sonnet judges because BUG-1230's false blocks came from Haiku, the default
for background work, and this repository designs its prompts for Sonnet 5 and
Opus 5.5. `--safe-mode` keeps the sign-in Claude Code already has, where
`--bare` would need an API key, and it loads no plugin, so the judge can't
fire the gate again (RES-0330).

## Alternatives

| Option                                                        | Better at                                                        | Why it lost                                                                                                      |
| ------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| A program calls the judge twice and keeps what agrees         | A model judges, and a program holds the verdict and the span     | Chosen                                                                                                           |
| A `prompt` hook beside the command hook                       | Uses the platform's own model hook, with no `claude` call to own | A deny from any hook wins, so nothing can drop its false blocks, which is BUG-1230 again                         |
| An `agent` hook that runs the program to confirm its findings | One hook, with tools to check its own quote                      | The model decides whether to check, the hook type is marked experimental, and its deny still wins                |
| A program calls the judge once and confirms only the span     | Half the cost and time of two calls                              | It still blocks on `in depth`, the one false block BUG-1230 reproduced, because that span is in the text         |
| The judge's finding asks the person, with `ask`, never denies | A wrong judgement costs a click, never a rewrite                 | In an unattended run nobody answers, so the call is denied anyway, and in a session it interrupts every publish  |
| Do nothing                                                    | No model call, no cost, the same answer every time               | The owner asked for a model to judge the text, and J1, J2 and J3 keep reaching the reader unchecked until review |

## What it costs

Every publish that passes the exact rules waits for two calls to `claude` and
spends two Sonnet calls of the person's usage. A text the exact rules block
costs no call. On a machine with no `claude` on the path, or no sign-in, the
person sees the not-checked message on every publish.

The unit's program gains a process call, a JSON schema and a prompt it ships,
which SPC-1030 governs as it governs every shipped prompt. Its fixtures need a
judge that isn't a model, so the program reads the judge's command from
`MEOW_PROSE_GATE_JUDGE` where that is set, which only the fixtures set.

A false block both judgements agree on now reaches the person as a block,
where under ADR-1600 it never existed. The person pays a rewrite or a dispute
for it. That is the trade the owner chose.

## What would reverse it

- The hand run shows BUG-1230's four texts blocked in any run, which would
  show that agreement between two calls doesn't steady the judge enough for
  the gate.
- A defect record shows a block both judgements agreed on for text that breaks
  none of J1, J2 and J3, a second time after the prompt was changed for the
  first.
- Claude Code gives command hooks a way to call the session's model directly,
  which would make the `claude -p` call and its start-up unnecessary.

## Consequences

- `crates/meow/` adds the judge to the `prose` feature: the two calls, the
  schema, the span check, the agreement test and the not-checked message.
- `plugins/meow-prose-gate/` ships the judge's prompt and schema, and
  `hooks/hooks.json` sets each hook's `timeout` to 120.
- `plugins/meow-prose-gate/tests/` gains fixtures with a stub judge for each
  path: agreement, disagreement, a span the text lacks, each failure cause,
  and an exact finding that calls no judge.
- `plugins/meow-prose-gate/evals/` returns, for the hand run REQ-3752 asks
  for, and no workflow runs it.
- The unit's README, its `budget.toml` reasoning and SPC-1010's section on the
  gate state the judged rules.
- REQ-3187 is withdrawn, because it allowed the program to block only on the
  three exact rules.

## How I will know it was realised

1. With a stub judge that returns `J1` on `circling back` in both calls, a
   body holding `circling back` is blocked with `J1 | "circling back" | ...`
   (REQ-3744).
2. With a stub judge that returns the finding in one call only, the same body
   passes (REQ-3744).
3. With a stub judge that returns a span the body lacks in both calls, the
   body passes (REQ-3746).
4. With a body holding `deep dive`, the gate blocks on P1 and the stub judge
   records no call (REQ-3740).
5. With the judge command missing, failing, sleeping past 45 seconds or
   printing JSON outside the schema, the gate exits 0 and prints the
   not-checked `systemMessage` naming that cause (REQ-3748).
6. The judge's command line, read from the program's source by a fixture,
   holds `--safe-mode`, `--tools ""` and `--json-schema` (REQ-3750).
7. The schema's `rule` field allows exactly `J1`, `J2` and `J3` (REQ-3742).
8. The hand run's output, in the pull request that ships the judge, shows the
   four BUG-1230 texts passing and one text per judged rule blocked, each in
   three runs of three (REQ-3752).

## What this does not settle

- Whether `gh pr merge` joins the gate, which ADR-1600 left open as well.
- Which rules join J1, J2 and J3 later. Each needs a decision, and a hand run
  showing it blocks the same way twice.
- Whether the judge's model can be chosen by the repository. It is `sonnet`
  until a decision makes it a profile key.
- How long a publish waits for the two calls. The task that ships the judge
  times them, and a wait a person finds too long is a defect against this
  decision.
- What SPC-1020's measure of a gate means for a gate with a judge. The hand
  run here is a smoke check and doesn't claim SPC-1020's thresholds.
