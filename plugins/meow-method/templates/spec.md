---
id: SPC-NNNN
artifact: spec
status: live # a living document; it describes the present and carries no history
revised: YYYY-MM-DD
checked-at: # the verification that last read it, such as "#123"
states: [REQ-NNNN] # every requirement this document states
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# <The part, named in a phrase>

## Scope

What this covers and what it doesn't, so a reader who stops here knows whether
their question belongs in this document.

## Boundary

What is observable from outside: the interface, the files written, the errors
and exit codes.

## Behaviour

What the part does now, each statement citing the requirement it states. No
history and no reasons, which live in the decisions.

## Failure paths

What happens when things go wrong, as precisely as the success path, because
this is where defects gather when it's skipped.
