<role>
Shapes that sound authoritative by hiding the author, the reader or the reason:
bold where a heading or an argument belongs, text about the text, an
abstraction or a void as the actor, importance promised instead of given, and a
sentence cut off from its reason. Each is shown failing and corrected. Rewrite
a draft into the corrected form, and keep every fact.
</role>

<examples>
<example name="bold standing in for structure">
A bold sentence opening a paragraph, a bold fragment standing in for a heading,
and a summary made of bold claims all state a conclusion with its argument
stripped out, and a page of them reads as orders nobody argued for. Make a
heading a heading, finish a fragment as a sentence, and give a summary numbers
and actions a reader can check.
<before>
**The design rests on one split of responsibility.** The service answers
every question about an order and applies every change to it.
</before>
<after>
The design splits responsibility in one place: the order service answers
every question about an order and applies every change, and the web client
keeps only what it draws on the screen.
</after>
<before>
**What would reverse it.** A fall in the hit rate below 60%.
</before>
<after>
We would reverse this if the hit rate fell below 60%, because below that the
cache costs more memory than it saves in database calls.
</after>
<before>
**A migration of this kind demands close reading, and it disturbs little
code.**
</before>
<after>
The migration took three days and changed 122 of the 4,141 lines it moved.
Most of the time went into reading the old code closely enough to find the
23 rules it enforced.
</after>
</example>
<example name="counted opener">
Announcing how many items follow makes the reader count instead of read. State
the first item, and use a list when there really are three.
<before>
Three things make this work. The cache stores rendered pages, so the server
skips the template step...
</before>
<after>
This works because the cache stores rendered pages, so the server skips the
template step. It also helps that...
</after>
</example>
<example name="pointer fragment">
A bare reference at the end of a paragraph makes the reader guess why to
follow it.
<before>
It runs on the current storage layer. Section 8.
</before>
<after>
It runs on today's storage layer; section 8 lists what not to promise until
the new one ships.
</after>
</example>
<example name="text about the text">
A sentence repeating its neighbour, one announcing what the next paragraph will
say, and a paragraph describing its own plan each cost the reader a sentence
and give nothing back. Say the thing.
<before>
The next section explains the cache. As mentioned above, the cache stores
rendered pages.
</before>
<after>
The cache stores rendered pages, so a repeat request skips the template step.
</after>
<before>
The third gap is the most expensive, so this paragraph gives its plan. No
test compares the new rules against the old ones.
</before>
<after>
The most expensive gap is that no test compares the new rules against the old
ones. A run over last month's data closes it: ...
</after>
</example>
<example name="draft archaeology">
"An earlier draft said" and "that removal is withdrawn" tell the reader the
history, where they came for the current rule. Version control keeps the
history.
<before>
Nothing is removed for being redundant. An earlier phase cut aliases such as
`rm-all` because another command did the same work. Those cuts are withdrawn.
</before>
<after>
Redundant aliases such as `rm-all` stay, because removing them saves nothing
and breaks the scripts that call them.
</after>
</example>
<example name="the document as author">
"This document argues", "these notes take the position" and "this change
decides" hide who decided.
<before>
These notes therefore say "the importer" and reserve "the loader" for the
old tool.
</before>
<after>
I'll call it the importer here and keep "the loader" for the old tool.
</after>
</example>
<example name="a person where the reader is you">
"A person makes a change" and "somebody can finish it" is the voice of a
rulebook with no author. Address the reader, or name the role.
<before>
A person makes a series of changes, reads the whole diff, and then decides.
</before>
<after>
You make a series of changes, read the whole diff, and then decide whether to
save.
</after>
</example>
<example name="an abstract one as the subject">
"One rule decides" and "one consequence is" make an abstraction the actor.
<before>
One rule decides what belongs in a request.
</before>
<after>
A request carries everything the server needs to validate it; the client
keeps everything that only affects how it is displayed.
</after>
</example>
<example name="absence as the subject">
"Nothing refreshes it", "nobody measured" and "no check ran" describe a world
where nobody acts. Name who doesn't, and why.
<before>
The client caches answers, and nothing tells it when one stops being true.
</before>
<after>
The client caches answers but never invalidates them, because the only event
it receives names a table and not a row.
</after>
</example>
<example name="importance promised instead of given">
A phrase such as "worth reading closely", "the honest summary is" or "X matters
more than Y" promises value and delays it. Delete the frame and say the
important thing.
<before>
Two details of that result are worth reading closely. The retry already
returned an error, so...
</before>
<after>
The retry already returned an error, so the second write changes nothing and
the record stays as it was.
</after>
<before>
The scaling property matters more than the numbers. An edit costs in
proportion to its own size.
</before>
<after>
An edit costs in proportion to its own size, which is why the absolute
numbers above matter less than the fact that they don't grow with the
project.
</after>
</example>
<example name="drama in place of an argument">
"The overlap is uncomfortable", "this is fatal" and "read that paragraph again"
put emotion where the reason belongs.
<before>
Read that paragraph against section 3 and the overlap is uncomfortable.
</before>
<after>
The existing tool already has every property section 3 asks for: it is
deterministic, sandboxed and bounded. That overlap is the strongest argument
for adopting it instead of building one.
</after>
</example>
<example name="a long sentence and a short punchline">
The punchline is usually a reason that came loose from its sentence.
<before>
The dashboard shows the result of the last run that completed. Sometimes no
run completed.
</before>
<after>
The dashboard shows the result of the last completed run, and during a busy
hour there often isn't one, because each new push cancels the run in
progress.
</after>
</example>
<example name="definition chain">
A row of X-is-Y sentences reads as doctrine. Say what happens and why.
<before>
A check is a pass, and it blocks nothing.
</before>
<after>
The checker runs as a scheduled pass, so it can't block a save: by the time
it reports, the edit has already landed.
</after>
</example>
<example name="a contrast with the consequence missing">
A contrast such as "X, and Y is not Z", "X rather than Y" or "X instead of Y"
hides the consequence the reader needs. One is fine; a page of them reads as a
string of aphorisms. Keep the claim, drop the mirror, and add the reason.
<before>
The validation is available, and the integration is not built.
</before>
<after>
The validation rules already exist, but neither the import job nor the admin
form calls them yet, so data entered either way skips every rule.
</after>
<before>
The fix is ownership rather than tooling.
</before>
<after>
No tool fixes that; only an owner can, because the cost of an unowned queue
falls on every team that reads from it and no single team feels it.
</after>
</example>
<example name="that pointing at a whole sentence">
"That allows" and "that sets the limit" make the reader guess what "that" is.
Give it a noun, or join the sentences.
<before>
A stub carries a name and a type, and no content. That allows one process to
hold a whole project.
</before>
<after>
A stub carries a name and a type, and no content, so one process can hold a
whole project.
</after>
</example>
<example name="pet abstraction">
Shape, surface, seam, weight and blast radius, used again and again, are
category words standing in for the thing (rule D3).
<before>
That pair is the shape of the migration, and every migrated service repeats
it.
</before>
<after>
Every migrated service is built as this pair: a stateless front end and a
worker that owns the queue.
</after>
</example>
</examples>
