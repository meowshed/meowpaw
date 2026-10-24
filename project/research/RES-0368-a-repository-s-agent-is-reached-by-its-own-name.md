---
id: RES-0368
artifact: research
status: approved
revised: 2026-10-24
elaborates: RES-0263
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A repository's agent is reached by its own name, beside the unit's agent of the same name

## Summary

A hand-run case found that the platform keeps a unit's agent and a repository's
agent of the same name apart. A dispatch of `meow-flow:researcher` was answered
by the unit's definition, and a dispatch of `researcher` by the repository's.
ADR-2560 and the requirement it addresses assumed the repository's
definition would take the place of the unit's, and it doesn't. The finding rests on one run on one model,
so it settles what the harness may promise and measures nothing.

The document covers which definition answers a dispatch. It doesn't cover what
a bare name reaches where the repository defines no agent of that name, or
which Claude Code version the run used, which nobody recorded.

## The question

ADR-2560 states that a repository can replace any agent the harness ships by
defining one of the same name in its own `.claude/agents/`, which the platform
loads in place of the plugin's. The assumption behind it is that the
platform resolves one name to one definition. A harness that promises
replacement on that assumption promises a behaviour it doesn't control.

## Method

An agent ran a case by hand on `sonnet` on 2026-10-13, while implementing
TSK-4955. The repository defined an agent `researcher` beside the unit's
`meow-flow:researcher`, and the case dispatched each name once and read which
definition answered. The case is kept nowhere, because ADR-2980 removed the
harness's case sets, and I didn't repeat it. I couldn't obtain the same run on
Opus 5.5, a run where the repository defines no agent, or the platform's own
statement of its resolution order.

## Findings

### A dispatch of the namespaced name reaches the unit's definition

The dispatch of `meow-flow:researcher` was answered by the unit's definition,
with a repository agent of the same bare name defined. The source is the case
above, run once.

### A dispatch of the bare name reaches the repository's definition

The dispatch of `researcher` was answered by the repository's definition. The
case scored 1 of 2 against the claim that the repository's definition answers
both dispatches. The source is the same run.

## Conclusions

1. A repository's agent of the same name doesn't take the place of a unit's
   agent, because the platform keeps both definitions, so the harness can't
   promise replacement on the strength of a same name.
2. A unit's agent is reached by `<unit>:<agent>` and a repository's by its bare
   name, on the model of the run and a platform version nobody recorded.
3. A page that ships an agent has to say which name reaches which definition,
   because a reader who defines a same-name agent expecting replacement still
   gets the unit's.

## Sources

- The hand-run case on `sonnet`, run 2026-10-13 and read 2026-10-24 from the
  report of the agent that ran it for TSK-4955. The case is kept nowhere.
- `ADR-2560` at revision 9f061170, read 2026-10-24: the sentence on replacing
  an agent, in `project/adrs/`.
