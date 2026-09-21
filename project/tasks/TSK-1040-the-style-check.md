---
id: TSK-1040
artifact: task
status: approved
revised: 2026-09-21
unit: U-0001
epic: EPC-1000
closes: [REQ-0931]
issue: 8
---

# Check the style mechanically

One task, one branch, one pull request, one review.

## What to do

Write a check that reads every style `meow-core` ships and fails, naming the
file and the field, when either holds:

- `keep-coding-instructions` is false or absent. The platform's default is
  false, so a careless style silently deletes the engineering guidance, and the
  failure leaves no trace without this check.
- A rule ships with no condition under which it yields (REQ-0931). A rule with
  no stated exception is switched off entirely the first time it costs an
  answer.

Run the check in the repository's gate. The check is seen to fail first
(REQ-2072): write a style with `keep-coding-instructions: false`, watch it
fail, and only then point it at the shipped style.

A check that cannot fail is rewritten and never supplemented (REQ-2078).

## Depends on

TSK-1020, because the check has nothing to read before the style exists.

## Evidence

Closed by this task's own change, at `a689e20`:

```text
$ python3 tools/check_style.py          # keep-coding-instructions: false
plugins/probe/output-styles/probe.md: keep-coding-instructions is false, so the
platform's engineering instructions are deleted            exit 1

$ python3 tools/check_style.py          # a rule with no stated exception
plugins/probe/output-styles/probe.md: the rule 'A rule' states no condition
under which it yields                                      exit 1

$ mise run style                        # the shipped style
1 output style, 0 failures                                 exit 0
```

The check is in the gate: `mise.toml` declares `style` and `all` depends on it,
and CI runs `mise run all`.

## Left alone

The check reads the style's front matter and its rule table. It does not judge
the prose, which is what the writing standard governs and what no program
settles.
