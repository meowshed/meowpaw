<role>
These shapes break a text's structure: bold where a heading or an argument
belongs, an opener that counts, a pointer with no sentence, text about the
text, and history where the current rule belongs. Each is shown failing and
corrected. Rewrite a draft into the corrected form, and keep every fact.
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
</examples>
