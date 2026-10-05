---
id: REQ-4116
artifact: requirement
topic: pi-packages
class: functional
status: withdrawn
revised: 2026-10-04
elaborates: RES-0340
verification: behavioural
---

# REQ-4116

**Withdrawn by ADR-2790. Replaced by REQ-4106.**

It read: the prose gate's Pi `user_bash` handler makes the two-judge model
call itself, with `ctx.modelRegistry.streamSimple()`, blocking only where
both judgements agree.

Reading the gate's program (`crates/meow/src/prose.rs`, RES-0330) showed
the binary holds the judge itself: it spawns the judge twice with a bounded
deadline, keeps only what both judgements agree on, and exits 2 with the
agreed findings, exactly as it does for the Claude Code hook. An extension
re-implementing the judge would duplicate a program that already holds its
own verdict. REQ-4106 already states what holds: the handler shells out to
the binary and interprets its exit code.
