---
id: REQ-3700
artifact: requirement
topic: long-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0320, RES-0074
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3700

A run MUST start, repeat and end inside the Claude Code session where a person starts it, with no command run outside that session.

The owner chose this on 2026-10-03, so a person who works in one session can run the chain there without a second terminal. A command Stop hook makes it possible, because a program decides whether the session's next turn starts (RES-0320, conclusion 1).
