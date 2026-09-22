---
id: REQ-1138
artifact: requirement
topic: prompt-format
class: functional
status: approved
revised: 2026-09-22
elaborates: RES-0270
verification: evaluation
---

# REQ-1138

A prompt the harness ships MUST NOT carry an instruction whose removal
leaves the measured result unchanged on the models the prompt serves.

Every instruction is paid for on each turn that loads it, and one the model
already follows costs tokens and buys nothing. An instruction written for an
older model's habit becomes that cost once the habit is gone, which only a
measurement shows.
