---
id: ADR-1420
artifact: adr
status: done
revised: 2026-09-27
addresses:
  [
    REQ-0090,
    REQ-0092,
    REQ-0094,
    REQ-0096,
    REQ-0098,
    REQ-1010,
    REQ-1015,
    REQ-2010,
    REQ-2012,
    REQ-2014,
    REQ-2016,
    REQ-2018,
    REQ-2070,
    REQ-2072,
    REQ-2074,
    REQ-2076,
    REQ-2078,
  ]
supersedes: []
---

# 1420. A coding unit holds how code is changed and how a check is written

## Decision

A new unit in the practice layer, `meow-code`, ships one skill,
`meow-code:change`, which loads before the model changes code. It carries
two groups of labelled rules and names no language, tool or file extension.

How code is changed:

- make the smallest change that is correct, and never reformat while
  changing behaviour (REQ-0090, REQ-0098);
- read a file before writing to it (REQ-0092);
- answer a question about a symbol through a language server where one is
  available, and where an answer comes from a text search, state what the
  search can't cover (REQ-0094, REQ-0096);
- prefer a semantic edit for a symbol, a structural edit for a mechanical
  rewrite and a textual edit only for a literal, and make a change
  expressible as one structural edit as one (REQ-2010, REQ-2012);
- batch reads and edits that don't depend on each other (REQ-2014);
- read a file's diagnostics after editing it and before claiming anything
  about it, and take evidence from the verification verbs, never from the
  diagnostics (REQ-2016, REQ-2018);
- document every publicly reachable declaration, and prefer an example the
  language runs as a check where it runs them (REQ-1010, REQ-1015).

How a check is written:

- check an obligation statically where it can be, behaviourally where it
  can't, and by evaluation only where neither can (REQ-2076);
- see a check fail before the work that makes it pass, where the language
  and the pack support it (REQ-2072);
- report a weak or tautological assertion as a defect in the check, and
  rewrite a check that wouldn't fail if its requirement were violated rather
  than adding a second one (REQ-2070, REQ-2078);
- where the ecosystem provides mutation testing, run it through the tool the
  repository or a pack names when asked whether the checks would catch a
  change, and report the survivors; where nothing names a tool, say how to
  declare one and run nothing in its place (REQ-2074).

After this decision a repository that installs `meow-code` gets these rules in
front of the model whenever the model changes code, in or out of the method's
chain. What still doesn't work: no program checks that a change was the
smallest or that a check was seen failing, so the rules rest on the model and
on review, and only a measurement will show how reliably they hold.

## Why

The rules come from RES-0021 on editing, from RES-0032 and RES-0066 on
checks, and from RES-0013 and RES-0020 on documentation. They govern every
change to code, so they can't live in the method's implement step alone:
installing the harness never obliges a repository to keep the record
(REQ-0028), and a repository that keeps none still changes code. The unit is
`meow-code` and not the `meow-editing` RES-0021 suggests, because it holds how
a check is written as well as how code is edited.

A skill loaded by a description stating the obligation is how ADR-1050 put the
writing standard in front of the model before it writes, and changing code has
the same shape: an activity whose rules must be present when it starts. The
rules name no language, because which tool edits a symbol or runs a mutation
test is a pack's knowledge (REQ-0072), and whether a language lets a check be
seen failing first is the pack's to say, as RES-0032 concludes; the rule to try
applies to every check, so this unit states it. The model knows the tools of
the session in front of it, such as a language server tool where the platform
offers one.

The strongest objection: most of these rules can't be checked by a program, and
a skill the model loads is weaker than a hook that blocks. A hook can't tell a
smallest change from a larger one either (REQ-0147), so the choice is a rule
the model reads or no rule, and review holds what the model misses.

## Alternatives

| Option                                    | Better at                                  | Why it lost                                                                                  |
| ----------------------------------------- | ------------------------------------------ | -------------------------------------------------------------------------------------------- |
| Do nothing                                | No unit to ship                            | The model edits and tests as it would anyway, and nothing holds these obligations            |
| Rules in the implement step only          | No new unit                                | A repository changing code outside the method's chain never loads them                       |
| Rules in `meow-core`'s output style       | Present on every turn with no routing      | The style shapes replies, and every turn would pay for rules only an edit needs              |
| Hooks blocking an edit that breaks a rule | A rule that holds without the model's help | No program can judge "smallest" or "tautological", so a hook would guess and be switched off |

## What it costs

Each repository that installs the unit pays for the skill's description, a few
hundred characters in context on every turn, and the skill's body each time
code changes. A repository that wants mutation testing run names the tool where
no pack does.

## What would reverse it

I would reverse this if a measurement of changes made with the skill and
without it, on Sonnet 5 and Opus 5.5, scored the same, because that would show
the rules change nothing.

## Consequences

- `plugins/meow-code/` ships the skill, a page and a budget, and joins the
  catalogue.
- SPC-1130 states the unit.

## How I will know it was realised

1. Each requirement ADR-1420 addresses is carried by a labelled rule in the
   skill, traced in the task's evidence, and no rule names a requirement, a
   language, a tool or a file extension.
2. The prompt check and the budget check pass on the unit.
3. A Claude Code session on Sonnet 5 and one on Opus 5.5, each with only the
   unit installed and asked to change code, load the skill before the first
   edit, since ADR-1050 found the two models route differently.
4. Every requirement ADR-1420 addresses lands in exactly one closed task.

## What this does not settle

- Which language server, structural editor or mutation tester serves which
  language, which belongs to packs.
- A measurement of how reliably the rules hold, which comes with the
  evaluation cases for the unit.
