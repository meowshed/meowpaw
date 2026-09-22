<role>
These shapes hide who acts: the document or an abstraction as the author, a
void as the subject, importance promised instead of given, and drama where the
reason belongs. Each is shown failing and corrected. Rewrite a draft into the
corrected form, and keep every fact.
</role>

<examples>
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
</examples>
