<role>
How a document is shaped, whatever its type. Pick the type first and read its
skeleton in `types/` as well, because a document missing a part its type
requires is incomplete however good its sentences are.
</role>

<rules name="templates">
<rule id="template-first">Follow a template where the repository or an
installed unit ships one for the kind of document you are writing: a
repository's own in `.meowpaw/templates/` first, then the owning unit's. The
template wins over the skeleton here, because two skeletons for one kind drift
apart and the repository chose its template on purpose.</rule>
</rules>

<rules name="before you draft">
<rule id="reader">Decide who reads the document and state the level at the top
of a draft, because the same fact is written differently for each and a
reviewer can check the level only if it is written down. A reader who is
learning needs the prerequisites linked and why before how. A reader who is
integrating knows the platform and needs only what is specific to this system.
A reader who is evaluating needs the decision, the trade-offs and the limits
first. Where the request names no reader, ask one question before you
draft.</rule>
</rules>

<rules name="shape the document">
<rule id="C4">Give each paragraph one idea, topic sentence first, in three to
five sentences, so a reader skimming first sentences still gets the
argument.</rule>
<rule id="E1">Define a term before its first use, or gloss it in the same
sentence, because a reader meeting an unknown name stops reading.</rule>
<rule id="E2">Open with the reader's problem in the reader's words, and bring in
your own vocabulary once the problem is on the table.</rule>
<rule id="E3">Open each section with two to four sentences on what it covers, so
a reader who stops after any section has a coherent picture.</rule>
<rule id="E5">Give each section one question: a section answering two is two
sections, and two answering one are one.</rule>
<rule id="E6">Give sibling sections the same shape, so the reader learns it
once.</rule>
<rule id="E7">Keep the main path for what a first-time reader needs, and move
numbers, edge cases, long tables and derivations to a section they can
skip.</rule>
<rule id="E8">Refer back on the main path, never forward: "section 9 explains
why" means the sections are in the wrong order.</rule>
<rule id="E9">Refer to another section in a full sentence, never in a bare
"Section 8." fragment.</rule>
<rule id="E10">Add a glossary near the top when a document introduces more
than five terms, so the reader has one place to look a term up.</rule>
<rule id="E12">Write an executive summary as five to eight sentences of prose:
the problem, what was done, its cost, what was not measured, and the next step,
because a manager forwards it as it stands.</rule>
<rule id="E13">Add a note on how to read the document only past about 3,000
words, because a shorter one shows its own order.</rule>
<rule id="E11">Put a table or figure beside the paragraph that uses it and say
what the reader should take from it.</rule>
<rule id="E14">Test the order with a cold read: wherever a reader holding only
the earlier sections meets a name they cannot place, the structure has
failed.</rule>
</rules>

<rules name="format for scanning">
<rule id="F1">Make the headings tell the story on their own, three levels at
most, in sentence case with no end punctuation: a verb for a task, a noun
phrase for a concept. A skimmer reads only the headings.</rule>
<rule id="F2">Use numbers for ordered steps, bullets for parallel items, a table
for a comparison across two dimensions, and prose for everything else,
including every argument, because a list strips out the "because" that joins
its items.</rule>
<rule id="F3">Bold an interface element; put what the reader types or the
machine reads in code font.</rule>
<rule id="F4">Bold at most one phrase per section and open paragraphs in plain
text, because a page of bold openers reads as orders nobody argued
for.</rule>
<rule id="F5">Write ASCII outside quoted code, because some readers' tools
mangle anything else.</rule>
<rule id="F6">Use the serial comma, and leave an identifier or a protocol token
in its own spelling.</rule>
</rules>
