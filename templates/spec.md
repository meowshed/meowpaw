---
id: SPC-NNNN
artifact: spec
status: live
revised: YYYY-MM-DD
checked-at: rN
states: [REQ-NNNN] # the requirements documents it projects
---

# <Component or system>

## Scope

What this covers and what it does not, in a few sentences. A reader who stops
here knows whether their question belongs in this document ([R-H-250]).

## Boundary

What is observable from outside: the interface, the files written, the events
emitted, the errors and exit codes produced. What follows constrains this and
nothing behind it.

## Behaviour

Prose describing what the system does now, with the requirements it states
cited by identifier. **No history**: no tombstones, no superseded wording, no
account of what was once intended ([R-H-305]). Every statement traces to a
requirement in force ([R-H-035c]).

## Failure paths

What happens when things go wrong, specified as precisely as the success path.
This is where defects accumulate when it is skipped.
