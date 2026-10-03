---
id: ADR-2450
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-2710,
    REQ-2712,
    REQ-2714,
    REQ-2716,
    REQ-2718,
    REQ-2720,
    REQ-2722,
    REQ-2724,
    REQ-2726,
    REQ-2727,
    REQ-2728,
    REQ-2730,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2450. A shipped hook only denies, and `meow-author check` holds every hook to the rules

## Decision

A hook the harness ships answers in one of two ways: it denies with a reason,
or it says nothing. It never answers `allow`, because that skips the
permission flow the repository owns (REQ-2720). It never rewrites a tool's
input, because a rewritten call runs something nobody asked for (REQ-2718).
Where a hook needs a person, it answers `ask` and lets the platform prompt,
because a hook has no terminal (REQ-2722). The harness reads a hook's silence,
crash or timeout as abstention and never as approval (REQ-2714).

A blocking hook does a small, fixed amount of work: it reads its input, runs
one native subcommand that touches only local files, and exits. Anything
slower runs in the gate (REQ-2716). No hook reaches the network (REQ-2727) or
writes its input to a log (REQ-2724). A unit declares each hook in its
`hooks/hooks.json` and states in its README, in one sentence, what that hook
stops (REQ-2726). Five units ship hooks today: `meow-flow` on `SessionStart`,
and `meow-git`, `meow-github`, `meow-loop` and `meow-prose-gate` on
`PreToolUse`.

A rule that must hold is layered: a hook stops the call, the gate checks the
tree, and the instruction says why (REQ-2710). A design that is safe only
because a hook blocks something gets a gate check as well (REQ-2712). The
revision counter advances after a failed tool use as well as a successful
one, because a failed command can still change the tree (REQ-2728). A pending
gate reaches the model through the `SessionStart` hook's output, which the
platform adds to the context, and not through a file the model has to read
(REQ-2730). The `meow-flow` hook in `plugins/meow-flow/hooks/hooks.json`
already meets REQ-2730.

`meow-author check` reads every `hooks/hooks.json` and fails a hook that
answers `allow`, returns updated input, names a network command or carries no
one-sentence description in its unit's README.

Once this is accepted, every shipped hook is held by a program to the same
answers. What still doesn't work: the check reads the declaration and the
source it can find, so a hook that builds a network call at run time escapes
it, and review holds that case.

## Why

RES-0203 found that a hook which allows a call silently widens the
permissions a repository chose, that a hook rewriting input hides the change,
and that a slow hook stalls every call it matches. It also found that the
platform runs hooks from different units in no defined order, so a rule can't
rest on one hook alone. CLAUDE.md's gate already runs `meow-author check`, so
the new rule lands in a check that runs on every pull request.

## Alternatives

| Option                         | Better at                                 | Why it lost                                                      |
| ------------------------------ | ----------------------------------------- | ---------------------------------------------------------------- |
| Do nothing                     | No new check                              | Twelve requirements are held by review alone                     |
| Rules in the authoring skill   | No code                                   | A skill explains a rule and can't fail a pull request            |
| A hook framework in the kernel | Every hook gets the rules by construction | It adds a dependency every hook unit must load, against ADR-1270 |

## What it costs

Each unit with a hook carries a sentence in its README for it, and a hook
that needs to allow a call can't be shipped and has to become a permission
rule the repository writes.

## What would reverse it

- The platform defines the order in which hooks from different units run, and
  a rule could then rest on one hook.

## Consequences

`meow-author check` gains the hook rules. The five units with hooks state each
one in their README. The revision counter in the crate counts failed tool uses.

## How I will know it was realised

1. `meow-author check` fails a fixture hook that answers `allow`, returns
   updated input, or calls `curl` (REQ-2720, REQ-2718, REQ-2727).
2. It fails a unit whose README doesn't describe its hook (REQ-2726).
3. A fixture tool use that fails advances the revision counter (REQ-2728).
4. The `SessionStart` hook's output names a pending gate in a fixture with one
   (REQ-2730).

## What this does not settle

- Which hooks the units should have. This decision governs how a hook
  answers, not which hooks exist.
