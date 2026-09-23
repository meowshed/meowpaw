<role>
Shapes that sound authoritative by hiding the author, the reader or the reason:
bold where a heading or an argument belongs, text about the text, an
abstraction or a void as the actor, importance promised instead of given, and a
sentence cut off from its reason. Each is shown failing and corrected, and each
lists the markers that find it. Use this file on any text: rewrite your own
draft into the corrected form, and for a text somebody else wrote, report each
finding as `SKILL.md` says under "review a text". Keep every fact either way.

A marker finds a candidate, and a hit is a problem only when the sentence
matches the failing form: "That overlap is the strongest argument" names its
noun and is fine. Some patterns have no reliable marker; find those on a
read-through.

`ru.md` holds the same patterns in the same order for Russian text. When you
add or change a pattern here, change it there too, so the two files stay
parallel.
</role>

<example name="bold standing in for structure">
A bold sentence opening a paragraph, a bold fragment standing in for a heading,
and a summary made of bold claims all state a conclusion with its argument
stripped out, and a page of them reads as orders nobody argued for. Make a
heading a heading, finish a fragment as a sentence, and give a summary numbers
and actions a reader can check.

Markers: `**` at the start of a paragraph or a list item.

Failing:

**The design rests on one split of responsibility.** The service answers
every question about an order and applies every change to it.

Corrected:

The design splits responsibility in one place: the order service answers
every question about an order and applies every change, and the web client
keeps only what it draws on the screen.

Failing:

**What would reverse it.** A fall in the hit rate below 60%.

Corrected:

We would reverse this if the hit rate fell below 60%, because below that the
cache costs more memory than it saves in database calls.

Failing:

**A migration of this kind demands close reading, and it disturbs little
code.**

Corrected:

The migration took three days and changed 122 of the 4,141 lines it moved.
Most of the time went into reading the old code closely enough to find the
23 rules it enforced.
</example>
<example name="counted opener">
Announcing how many items follow makes the reader count instead of read. State
the first item, and use a list when there really are three.

Markers: a sentence opening with a number word and a category noun, such as
"Three things", "Two reasons" or "Four ways".

Failing:

Three things make this work. The cache stores rendered pages, so the server
skips the template step...

Corrected:

This works because the cache stores rendered pages, so the server skips the
template step. It also helps that...
</example>
<example name="pointer fragment">
A bare reference at the end of a paragraph makes the reader guess why to
follow it.

Markers: a paragraph ending in "Section 8.", "See X." or a bare link.

Failing:

It runs on the current storage layer. Section 8.

Corrected:

It runs on today's storage layer; section 8 lists what not to promise until
the new one ships.
</example>
<example name="text about the text">
A sentence repeating its neighbour, one announcing what the next paragraph will
say, and a paragraph describing its own plan each cost the reader a sentence
and give nothing back. Say the thing.

Markers: "as mentioned", "as noted", "above", "below", "the next section",
"this section", "this paragraph".

Failing:

The next section explains the cache. As mentioned above, the cache stores
rendered pages.

Corrected:

The cache stores rendered pages, so a repeat request skips the template step.

Failing:

The third gap is the most expensive, so this paragraph gives its plan. No
test compares the new rules against the old ones.

Corrected:

The most expensive gap is that no test compares the new rules against the old
ones. A run over last month's data closes it: ...
</example>
<example name="draft archaeology">
"An earlier draft said" and "that removal is withdrawn" tell the reader the
history, where they came for the current rule. Version control keeps the
history.

Markers: "earlier draft", "earlier version", "previously", "withdrawn", "no
longer".

Failing:

Nothing is removed for being redundant. An earlier phase cut aliases such as
`rm-all` because another command did the same work. Those cuts are withdrawn.

Corrected:

Redundant aliases such as `rm-all` stay, because removing them saves nothing
and breaks the scripts that call them.
</example>
<example name="the document as author">
"This document argues", "these notes take the position" and "this change
decides" hide who decided.

Markers: "This document", "These notes", "This proposal", "this change
decides".

Failing:

These notes therefore say "the importer" and reserve "the loader" for the
old tool.

Corrected:

I'll call it the importer here and keep "the loader" for the old tool.
</example>
<example name="a person where the reader is you">
"A person makes a change" and "somebody can finish it" is the voice of a
rulebook with no author. Address the reader, or name the role.

Markers: "a person", "somebody", "someone".

Failing:

A person makes a series of changes, reads the whole diff, and then decides.

Corrected:

You make a series of changes, read the whole diff, and then decide whether to
save.
</example>
<example name="an abstract one as the subject">
"One rule decides" and "one consequence is" make an abstraction the actor.

Markers: a sentence opening "One ".

Failing:

One rule decides what belongs in a request.

Corrected:

A request carries everything the server needs to validate it; the client
keeps everything that only affects how it is displayed.
</example>
<example name="absence as the subject">
"Nothing refreshes it", "nobody measured" and "no check ran" describe a world
where nobody acts. Name who doesn't, and why.

Markers: a sentence or clause opening "Nothing ", "Nobody ", "None ", "No ".

Failing:

The client caches answers, and nothing tells it when one stops being true.

Corrected:

The client caches answers but never invalidates them, because the only event
it receives names a table and not a row.
</example>
<example name="importance promised instead of given">
A phrase such as "worth reading closely", "the honest summary is" or "X matters
more than Y" promises value and delays it. Delete the frame and say the
important thing.

Markers: worth, matters, honest, important, key.

Failing:

Two details of that result are worth reading closely. The retry already
returned an error, so...

Corrected:

The retry already returned an error, so the second write changes nothing and
the record stays as it was.

Failing:

The scaling property matters more than the numbers. An edit costs in
proportion to its own size.

Corrected:

An edit costs in proportion to its own size, so the numbers above stay the
same as the project grows, and that tells you more than their absolute values.
</example>
<example name="drama in place of an argument">
"The overlap is uncomfortable", "this is fatal" and "read that paragraph again"
put emotion where the reason belongs.

Markers: fatal, uncomfortable, striking, alarming, "read that again".

Failing:

Read that paragraph against section 3 and the overlap is uncomfortable.

Corrected:

The existing tool already has every property section 3 asks for: it is
deterministic, sandboxed and bounded. That overlap is the strongest argument
for adopting it instead of building one.
</example>
<example name="a long sentence and a short punchline">
The punchline is usually a reason that came loose from its sentence.

Markers: none reliable. On a read-through, look for a sentence under about
eight words that follows a long one.

Failing:

The dashboard shows the result of the last run that completed. Sometimes no
run completed.

Corrected:

The dashboard shows the result of the last completed run, and during a busy
hour there often isn't one, because each new push cancels the run in
progress.
</example>
<example name="definition chain">
A row of X-is-Y sentences reads as doctrine. Say what happens and why.

Markers: none reliable. On a read-through, look for two or more sentences in a
row built as "X is a Y".

Failing:

A check is a pass, and it blocks nothing.

Corrected:

The checker runs as a scheduled pass, so it can't block a save: by the time
it reports, the edit has already landed.
</example>
<example name="a contrast with the consequence missing">
A contrast such as "X, and Y is not Z", "X rather than Y" or "X instead of Y"
hides the consequence the reader needs. One is fine; a page of them reads as a
string of aphorisms. Keep the claim, drop the mirror, and add the reason.

Markers: "rather than", "instead of", ", not", "and ... is not".

Failing:

The validation is available, and the integration is not built.

Corrected:

The validation rules already exist, but neither the import job nor the admin
form calls them yet, so data entered either way skips every rule.

Failing:

The fix is ownership rather than tooling.

Corrected:

No tool fixes that; only an owner can, because the cost of an unowned queue
falls on every team that reads from it and no single team feels it.
</example>
<example name="that pointing at a whole sentence">
"That allows" and "that sets the limit" make the reader guess what "that" is.
Give it a noun, or join the sentences.

Markers: a sentence opening "That " or "This " followed by a verb.

Failing:

A stub carries a name and a type, and no content. That allows one process to
hold a whole project.

Corrected:

A stub carries a name and a type, and no content, so one process can hold a
whole project.
</example>
<example name="pet abstraction">
Shape, surface, seam, weight and blast radius, used again and again, are
category words standing in for the thing (rule D2).

Markers: shape, surface, seam, weight, "blast radius", things.

Failing:

That pair is the shape of the migration, and every migrated service repeats
it.

Corrected:

Every migrated service is built as this pair: a stateless front end and a
worker that owns the queue.
</example>
