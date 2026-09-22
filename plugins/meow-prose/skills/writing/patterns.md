# Patterns to rewrite

Each of these shapes sounds authoritative by hiding the author, the reader or
the reason. When you find one, rewrite it into the corrected form below it. The
failing example is a real habit, and the corrected one keeps every fact while
putting the missing actor or reason back.

## Bold verdict as a paragraph opener

A bold sentence at the head of a paragraph states a conclusion before the
argument, and a page of them reads as orders nobody argued for.

Failing:

> **The design rests on one split of responsibility.** The service answers
> every question about an order and applies every change to it.

Corrected:

> The design splits responsibility in one place: the order service answers
> every question about an order and applies every change, and the web client
> keeps only what it draws on the screen.

## Long sentence plus a short punchline

The punchline is usually a reason that came loose from its sentence.

Failing:

> The dashboard shows the result of the last run that completed. Sometimes no
> run completed.

Corrected:

> The dashboard shows the result of the last completed run, and during a busy
> hour there often isn't one, because each new push cancels the run in
> progress.

## Counted opener

Announcing how many items follow makes the reader count instead of read. State
the first item, and use a list when there really are three.

Failing:

> Three things make this work. The cache stores rendered pages, so the server
> skips the template step...

Corrected:

> This works because the cache stores rendered pages, so the server skips the
> template step. It also helps that...

## Judgement of worth

"Worth reading closely", "deserves a direct answer" and "the honest summary is"
promise value instead of giving it. Delete the frame and say the thing.

Failing:

> Two details of that result are worth reading closely. The retry already
> returned an error, so...

Corrected:

> The retry already returned an error, so the second write changes nothing and
> the record stays as it was.

## Definition chain

A row of X-is-Y sentences reads as doctrine. Say what happens and why.

Failing:

> A check is a pass, and it blocks nothing.

Corrected:

> The checker runs as a scheduled pass, so it can't block a save: by the time
> it reports, the edit has already landed.

## Contrastive tail

"X, and Y is not Z" hides the consequence the reader needs.

Failing:

> The validation is available, and the integration is not built.

Corrected:

> The validation rules already exist, but neither the import job nor the admin
> form calls them yet, so data entered either way skips every rule.

## Rather-than contrast

"X rather than Y", "X instead of Y" and "X, not Y" are the same contrastive
tail with a softer word. One is fine; a page of them reads as a string of
aphorisms, and the reason is usually missing after the contrast. Keep the
claim, drop the mirror, add the reason.

Failing:

> The fix is ownership rather than tooling.

Corrected:

> No tool fixes that; only an owner can, because the cost of an unowned queue
> falls on every team that reads from it and no single team feels it.

## The document as author

"This document argues", "these notes take the position" and "this change
decides" hide who decided.

Failing:

> These notes therefore say "the importer" and reserve "the loader" for the
> old tool.

Corrected:

> I'll call it the importer here and keep "the loader" for the old tool.

## Abstract "one" as the subject

"One rule decides" and "one consequence is" make an abstraction the actor.

Failing:

> One rule decides what belongs in a request.

Corrected:

> A request carries everything the server needs to validate it; the client
> keeps everything that only affects how it is displayed.

## Pointer fragment

A bare reference at the end of a paragraph makes the reader guess why to
follow it.

Failing:

> It runs on the current storage layer. Section 8.

Corrected:

> It runs on today's storage layer; section 8 lists what not to promise until
> the new one ships.

## Summary as a blockquote of bold theses

A summary made of bold claims asks to be believed; a summary made of numbers
and actions can be checked.

Failing:

> **A migration of this kind demands close reading, and it disturbs little
> code.**

Corrected:

> The migration took three days and changed 122 of the 4,141 lines it moved.
> Most of the time went into reading the old code closely enough to find the
> 23 rules it enforced.

## Absence as the subject

"Nothing refreshes it", "nobody measured" and "no check ran" describe a world
where nobody acts. Name who doesn't, and why.

Failing:

> The client caches answers, and nothing tells it when one stops being true.

Corrected:

> The client caches answers but never invalidates them, because the only event
> it receives names a table and not a row.

## "That" pointing at a whole sentence

"That allows" and "that sets the limit" make the reader guess what "that" is.
Give it a noun, or join the sentences.

Failing:

> A stub carries a name and a type, and no content. That allows one process to
> hold a whole project.

Corrected:

> A stub carries a name and a type, and no content, so one process can hold a
> whole project.

## "X matters"

A sentence that promises importance delays the important thing. Say it.

Failing:

> The scaling property matters more than the numbers. An edit costs in
> proportion to its own size.

Corrected:

> An edit costs in proportion to its own size, which is why the absolute
> numbers above matter less than the fact that they don't grow with the
> project.

## The paragraph narrating itself

"This paragraph gives the plan" and "for reasons worth naming" replace the text
with commentary about it.

Failing:

> The third gap is the most expensive, so this paragraph gives its plan. No
> test compares the new rules against the old ones.

Corrected:

> The most expensive gap is that no test compares the new rules against the old
> ones. A run over last month's data closes it: ...

## Draft archaeology

"An earlier draft said" and "that removal is withdrawn" tell the reader the
history, where they came for the current rule. Version control keeps the
history.

Failing:

> Nothing is removed for being redundant. An earlier phase cut aliases such as
> `rm-all` because another command did the same work. Those cuts are withdrawn.

Corrected:

> Redundant aliases such as `rm-all` stay, because removing them saves nothing
> and breaks the scripts that call them.

## "A person" where the reader is you

"A person makes a change" and "somebody can finish it" is the voice of a
rulebook with no author. Address the reader, or name the role.

Failing:

> A person makes a series of changes, reads the whole diff, and then decides.

Corrected:

> You make a series of changes, read the whole diff, and then decide whether to
> save.

## Pet abstraction

Shape, surface, seam, weight and blast radius, used again and again, are
category words standing in for the thing (rule D3).

Failing:

> That pair is the shape of the migration, and every migrated service repeats
> it.

Corrected:

> Every migrated service is built as this pair: a stateless front end and a
> worker that owns the queue.

## Drama in place of an argument

"The overlap is uncomfortable", "this is fatal" and "read that paragraph again"
put emotion where the reason belongs.

Failing:

> Read that paragraph against section 3 and the overlap is uncomfortable.

Corrected:

> The existing tool already has every property section 3 asks for: it is
> deterministic, sandboxed and bounded. That overlap is the strongest argument
> for adopting it instead of building one.

## Restatement or preview

A sentence that repeats its neighbour, or announces what the next paragraph
will say, costs the reader a sentence and gives them nothing.

Failing:

> The next section explains the cache. As mentioned above, the cache stores
> rendered pages.

Corrected:

> The cache stores rendered pages, so a repeat request skips the template step.

## Bold fragment as an inline heading

"Nothing extra." "What would reverse this." A bold fragment is either a heading
or an unfinished sentence. If it is a heading, make it one; if it is a
sentence, finish it.

Failing:

> **What would reverse it.** A fall in the hit rate below 60%.

Corrected:

> We would reverse this if the hit rate fell below 60%, because below that the
> cache costs more memory than it saves in database calls.
