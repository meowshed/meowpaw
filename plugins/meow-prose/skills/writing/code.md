<role>
Comments in code and code examples in prose. A comment is prose, so the rules
in `SKILL.md` hold for it as well.
</role>

<rules name="code">
<rule id="comments">Write a comment only where the code cannot explain itself,
and improve the name first, unless the name is an interface others depend on.
Keep it short and plain, one line where one line will do, saying why the code
does what it does, because the reader already has the code and needs the reason
it doesn't show. Write nothing that restates the line below, because it goes
wrong the first time that line changes. Delete commented-out code, since version
control keeps it, and give every marker for later work an issue or a task,
because a bare marker is a promise nobody owns.</rule>
<rule id="G">Make an example runnable as pasted, with its prerequisites stated
before it, keep only what the prose around it explains, comment a line that is
not obvious, say so where you could not check it, introduce it with a sentence
ending in a colon, tag its fence, and follow it with prose. A reader copies an
example before reading the text around it, so it has to be right on its
own.</rule>
</rules>
