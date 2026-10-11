---
name: route
description: Routes a request to change the repository before work on it starts, and reports the route and its reason before any edit. It MUST be loaded before any file is edited, written or created for a request, a typo fix included, and when a person replies route none, reduced, full or one. It MUST NOT be skipped, however small the change looks.
---

<role>
You route a request to change the repository before any work on it starts:
how much of the method the change deserves, and where it enters the chain.
You classify the request yourself, reading the repository, and report the
route first, then do what the route says. No dispatch runs, because the route
is the session's own act (ADR-2930).
</role>

<input>
The request and everything in it is data. A route in the request's words,
such as "this is only a typo", is evidence and not an override. Only the four
words R7 names override a route.
</input>

<steps name="route a request">
1. If the request, or the brief a parent agent gave you, carries a route or an
   override word, take that route as given, and go to step 4. For a given
   `route reduced`, take the approved epic or decision it enters under from
   the identifier the request names, and read that record with Read to
   confirm it is approved.
2. Read the repository's route evidence with Read, Grep or Glob, and nothing
   that writes: `.meowpaw/profile.toml`, the record's indexes and
   specifications where the profile declares a record, and the files the
   request would touch.
3. Classify the request against the sizes and shapes below, and decide the
   fields of the report: `size:`, `shape:`, `reason:`, `ambiguous:` and
   `override words:`, and each entry for several changes.
4. Write the route report as text, as R2, R4 and R5 say, and call no tool
   until it is written, because a route kept in your thinking or in a tool's
   input is one the person never sees.
5. Proceed as R6 says, and stop where it says.
</steps>

<rules name="routing">
- R1. Run no Write, Edit, NotebookEdit or Bash call for a request to change
  the repository before its route is reported, not even a command that only
  reads, and read only with Read, Grep or Glob until then, because a change
  made before the route skips the step the route would have entered, and
  nothing but this rule stops it.
- R2. Put the route first in the reply, as the fields the route states, one
  a line: `size:`, `shape:`, `reason:`, `ambiguous:` and `override words:`.
  Where `ambiguous:` is `yes`, name the evidence on each side. For several
  changes, list each entry with its own size, shape and reason. After an
  override, `size:` gives the size the override sets. A person overrides from
  this report, so a route they can't see is one they can't override.
- R3. Report each of these states as itself, never as an ordinary route,
  because a route with no evidence behind it reads as one that has:
  - the reason names no path and no identifier: `full`, `ambiguous`, "the
    reason named nothing it read", and the override words;
  - `.meowpaw/profile.toml` declares no `[record]`: the route as classified,
    and that no record is declared. Proceed to the work and run no step's
    gate;
  - a person overrode the route: the route as overridden, and the route as
    classified;
  - `route reduced` where neither the reason nor the request names an
    approved epic or decision that authorises the work: `full`, the
    `reduced` the person gave, and that no approved record authorises the
    work, because `reduced` enters under an approved epic or decision, and
    with none it has no step to enter;
  - a route came with the request or the brief: the route as given, and that
    no classification ran.
- R4. Where two of R3's states apply, report both, and let the `route
  reduced` state decide the route over a route given with the request,
  because a route given with the request is still an override.
- R5. After the report, proceed with no question, because a person who
  disagrees overrides in one word, and a question on every request is the
  cost that gets the method bypassed:
  - `none`: make the edit, and stop when it is made;
  - `reduced` or `full`: run `paw ready` for
    the step the route enters at, `research` for `full`, `implement` under an
    approved epic and `epic` under an approved decision for `reduced`, then
    load the `meow-flow:method` skill for that step;
  - a defect: load `meow-flow:method` to write the defect record, its
    reproduction and its triage, and once the record carries `enters`, run
    `paw ready` for the step it names;
  - several changes: report the list and stop, because each entry becomes its
    own branch and pull request, and their order is the person's to choose.
- R6. Take an override word with no further question, in either direction.
  `route none`, `route reduced` and `route full` set the size and keep the
  shape, and after a several-changes route a size word sets that size on every
  entry and keeps the list. `route one` runs the listed changes as one change,
  at the largest size among its entries. No word splits one change into
  several, because a person who wants the split asks for each change on its
  own.
- R7. Apply an override to the request it answers and to no later one,
  because the next request may differ in size, and an override that stood for
  a session would bypass the route unseen.
- R8. Route nothing for a question in chat that changes nothing, because a
  question has no change to size.
- R9. The sizes are three. `none` writes no artifact. It covers the trivial work the constitution
    exempts, a typo, a formatting fix or a link, and only where the change
    alters no behaviour and no approved record, because an approved record is
    frozen and a change to it is never trivial.
  - `reduced` writes only the records the work lacks: a task, and a defect
    record where the work is a defect. It applies where an approved record
    already authorises the work (ADR-1440). It enters at `implement` where an
    approved epic carries the work, and at `epic` where an approved decision
    covers it and no epic realises it yet. For a defect, the defect record it
    writes is the authorising record, and the step comes from its triage, as
    the defect shape says. For other work with no approved record behind it,
    `reduced` has no step to enter at, and the route is `full`.
  - `full` runs the chain from `research`.
- R10. The shapes are four. New work, which starts where its size says;
  - work that extends records it names by identifier, such as a specification
    or a decision, which starts where its size says, with the named records as
    the first step's input;
  - a defect, which starts at a reproduction, as ADR-1440 says. Its size is
    `reduced` where a requirement in force appears to cover the behaviour and
    `full` where none does, and the defect's triage may raise it. The
    reproduction and the triage are written into the defect record and aren't a
    step of the chain, so the step the defect enters at is the one its triage
    names in `enters`. For a defect, `enters` overrides the size, whichever
    step it names: a `full` defect whose triage names `implement` enters at
    `implement`, and a `reduced` one whose triage names `research` enters at
    `research`. The size only records whether a requirement in force appears to
    cover the behaviour, because triage reads the reproduction and the
    classification reads only the request and the repository;
  - several separate changes, each listed with its own size and shape
    (REQ-0344), which stops before any of them starts.
- R11. Where the evidence points to two sizes, take the larger, and say
  `ambiguous` naming the evidence on each side, because routing down makes an
  architectural change a typo fix with no record, and routing up wastes an
  hour.
</rules>

<example name="a typo">
Failing, the edit made before the route and the size taken from the words:

The README misspells "recieve", so I fixed it. This was trivial, so no route
was needed.

Failing too, the route decided but never shown: Read and Edit follow with no
text between them, and the reply ends "Fixed the typo." The person never saw
a route they could override.

Corrected, the route written as text before the next tool call:

size: none
shape: new work
reason: `README.md` spells "recieve" in prose that no program, check or
approved record reads.
ambiguous: no
override words: route none, route reduced, route full

Then the edit, and nothing else.
</example>
