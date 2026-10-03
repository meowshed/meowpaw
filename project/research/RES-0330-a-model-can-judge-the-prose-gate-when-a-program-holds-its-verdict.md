---
id: RES-0330
artifact: research
status: approved
revised: 2026-10-03
elaborates: RES-0027
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A model can judge text in the prose gate when a program holds the verdict

## Summary

A model can judge the rules a program can't state, but only if a program
outside the model decides whether its finding blocks. Claude Code's own model
hooks can't be overruled: a `prompt` or `agent` hook that denies a command wins
over every other hook on that event. A command hook, though, can call
`claude -p` with hooks, plugins and instructions turned off, ask for a fixed
JSON shape, and check what comes back before it blocks.

BUG-1230's failures fall into two kinds that need two different guards. A
block quoting text the command doesn't hold is caught by a program checking
the span. A block on text that is there but breaks no rule, such as `in depth`
judged as `deep dive`, survives that check. It is caught only by asking more
than once and blocking where the answers agree, which is the reversal
condition ADR-1600 names: a model shown to settle a rule the same way twice.

This covers how the gate can call a model and what guards its verdict. It
doesn't measure how often a judge agrees with itself on this repository's
texts, because no such run was made.

## The question

Can the prose gate let a model judge text again without repeating BUG-1230,
where a Haiku prompt hook blocked four texts of four on one day for findings
they didn't hold?

ADR-1600 assumed that a gate either is a program or is a model. I challenged
that assumption first, because a program can call a model and still own the
decision, and then the question becomes which part decides.

## Method

On 2026-10-03 I read the Claude Code hooks reference, the CLI reference and
the headless guide in full, as Markdown fetched from `code.claude.com`. I
reread ADR-1600, BUG-1230 and SPC-1010 at `main` after #811, and the gate's `hooks/hooks.json` and README. I read the abstracts of two
papers on sampling a model more than once and on models as judges.

I ran no model and measured no agreement rate. Every statement about how
often a judge agrees with itself is a claim from the sources, not a result on
this repository's texts.

## Findings

### A deny from any hook wins, so a model hook can't be checked by a command hook

The hooks reference says that when several `PreToolUse` hooks return
different decisions, "precedence is `deny` > `defer` > `ask` > `allow`", and
that "All matching hooks run in parallel." A `prompt` hook beside a command
hook that confirms the quote therefore can't overrule a false block. ADR-1600
rejected that pairing for the same reason, and the reference still says it.

### Claude Code's model hooks give the hook author no hold on the verdict

A `prompt` hook returns `{"ok": true | false, "reason": "..."}`, and on
`PreToolUse` an `ok: false` denies the call. With `continueOnBlock: true` the
reason goes back to the model as the tool error. The default timeout is 30
seconds, and the model defaults to the one Claude Code uses for background
work, so Haiku, which BUG-1230 ran.

An `agent` hook spawns a subagent that "can use tools like Read, Grep, and
Glob" for up to 50 turns, with a 60-second default timeout. The reference
marks it experimental: "Behavior and configuration may change in future
releases. For production workflows, prefer command hooks."

Neither type lets a program inspect the model's reason before Claude Code acts
on it, so neither can hold the rule SPC-1010 states, that a block quotes a
span occurring verbatim in the command.

### A command hook can call a model with nothing of the session loaded

`claude -p` runs one prompt and prints the result. `--output-format json` and
`--json-schema` return validated JSON matching a schema. `--model` takes an
alias such as `sonnet`, and `--tools ""` disables every built-in tool.
`--no-session-persistence` keeps the call off disk.

`--safe-mode` loads no CLAUDE.md, skill, plugin, hook, MCP server, command or
agent, while "Authentication, model selection, built-in tools, and permissions
work normally". That matters because `--bare` "never reads OAuth credentials
or the system keychain" and needs `ANTHROPIC_API_KEY`, which a person signed
in through Claude Code doesn't have.

Two risks follow without these flags. A judge that loads plugins loads the
gate's own hook. A judge that loads CLAUDE.md reads the repository's
instructions as its own. Safe mode removes both. Managed policy hooks still
apply under it, and the reference says so.

### A span check catches one kind of false block and not the other

BUG-1230 records blocks on a bold line where there was no bold, and on
`deep dive` in a body that didn't hold it. A program checking that the quoted
span is a slice of the command drops both, because neither span is there.
ADR-1600 already runs this check on its own findings, as a last guard.

When reproduced, BUG-1230's case 2 blocked once in three runs on `in depth`,
a phrase the body holds and which is off the list. The span is there, so the
check passes it, and the block is still wrong. Only a second, independent
judgement disagreeing would drop it.

### Asking twice and keeping what agrees is the documented way to steady a model's answer

Wang and others sample "a diverse set of reasoning paths instead of only
taking the greedy one", then select "the most consistent answer by
marginalizing out the sampled reasoning paths". They report gains on every
benchmark they ran, from +3.9% on ARC-challenge to +17.9% on GSM8K. Zheng and
others find strong judges reach "over 80% agreement" with human preferences,
"the same level of agreement between humans", and name position, verbosity
and self-enhancement biases as limits.

For a gate, a block that needs two independent judgements to agree on the
same rule and the same span turns a false block that happens once in three
runs into one that needs two such runs in a row. If two runs were independent
at that rate, the chance falls from about 1 in 3 to about 1 in 9. That figure
is arithmetic on BUG-1230's one reproduced rate, not a measurement.

### A judge that can't answer must not block

The gate already lets a publish through, saying nothing was checked, when its
binary is missing, because blocking every publish on a missing part teaches
people to uninstall the gate (ADR-1600). A judge call fails in more ways: no
`claude` on the path, no sign-in, no network, a timeout, or JSON outside the
schema. Each is a judgement that didn't happen, and the constitution's rule
that unresolved isn't a pass says to report it as not checked, never as
passed. A command hook that exits 0 can say so: the hooks reference says that
to "surface a message to the user on any platform, return `systemMessage` in
JSON output".

### Two calls cost time on every publish

A `prompt` hook defaults to 30 seconds and a command hook to 600. Two judge
calls run side by side cost the time of the slower one, plus the start-up of
`claude`. I didn't measure that start-up. The gate's rules run first, and a
text the program already blocks needs no model call.

## Conclusions

1. A rule that names its defect exactly is settled by a program with no model
   call, because a program gives the same answer every time and a model adds
   only cost and doubt to it.
2. A rule that needs judgement can be held by the gate only through a model a
   program calls, because Claude Code's own model hooks deny with no way for a
   program to check the finding first.
3. A judged finding blocks only where the quoted span occurs verbatim in the
   command, confirmed by a program, because BUG-1230's blocks quoted text
   that wasn't there.
4. A judged finding blocks only where two independent judgements name the same
   rule and the same span, because a span that is there can still be judged
   wrongly, and agreement is how a model's answer is steadied.
5. The judged rules are a closed list the unit names, so what the gate can
   block on is known before it blocks.
6. The judge's call loads no hook, plugin, skill or project instruction, so it
   can't fire the gate again or take the repository's instructions as its own.
7. A judge that can't be reached, runs out of time or answers outside the
   schema is reported as not checked, and the publish goes through.
8. How often a judge agrees with itself on this repository's texts is measured
   locally by hand on BUG-1230's four shapes, never in CI, and the result is a
   smoke check, not proof.

## Sources

- [Hooks reference](https://code.claude.com/docs/en/hooks.md), read 2026-10-03 - the precedence of `deny` over the other decisions, parallel hooks, the `prompt` and `agent` hook fields, response schema, default timeouts and default model, `continueOnBlock`, agent hooks being experimental, `systemMessage`, and `--settings '{"disableAllHooks": true}'`.
- [CLI reference](https://code.claude.com/docs/en/cli-reference.md), read 2026-10-03 - `-p`, `--output-format`, `--json-schema`, `--model`, `--tools`, `--no-session-persistence`, `--max-turns`, `--safe-mode` and `--bare`.
- [Run Claude Code programmatically](https://code.claude.com/docs/en/headless.md), read 2026-10-03 - that bare mode reads no OAuth credentials or keychain and needs `ANTHROPIC_API_KEY`.
- [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171), Wang and others, read 2026-10-03 - sampling several answers and keeping the most consistent one, and the gains reported.
- [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685), Zheng and others, read 2026-10-03 - judge agreement with human preferences and the biases named.
- `project/bugs/BUG-1230-the-prose-gate-blocks-on-findings-the-text-lacks.md` and `project/adrs/ADR-1600-the-prose-gate-is-a-program-that-blocks-only-on-a-span-it-found.md` at `main` after #811, read 2026-10-03 - the four false blocks, the one reproduced rate, and the reversal condition.
