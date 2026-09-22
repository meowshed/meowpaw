<role>
These shapes detach a sentence from its reason: a punchline, a chain of
definitions, a contrast with the consequence missing, a bare "that", and a
category word standing in for the thing. Each is shown failing and corrected.
Rewrite a draft into the corrected form, and keep every fact.
</role>

<examples>
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
