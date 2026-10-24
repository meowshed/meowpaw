<role>
What a reviewer of a Markdown document checks that no command reports. Read
it when you review a Markdown document, after the render target is known. A
clean lint says the structure holds, and each point here asks whether the
structure serves the reader. The writing standard stays with `meow-prose`.
</role>

<rules name="reviewing Markdown">
- R1. Read the heading outline alone and check that it is the document's
  argument, because the linter checks that heading levels increment and
  can't tell whether the outline says what the document argues.
- R2. Use a table where the reader compares items across two dimensions, and
  a list where the items are parallel with one dimension, because a table
  of one column is a list with a border, and a list of attributes hides the
  comparison.
- R3. Check that each fence carries the right language tag for its content,
  because the linter accepts any tag, and a `bash` tag on a TOML block
  highlights it wrongly and misleads a reader who copies it.
- R4. Use reference links for a source cited more than twice, because
  repeated inline addresses make the source form unreadable, and one
  definition changes in one place.
- R5. Write a relative link to a file in a style that survives a move of the
  document or its target, and check each link a moved file carries, because
  whether a link survives a move is a property of the link's style, not of
  its target.
- R6. Check that the prose beside a diagram states everything the diagram
  asserts, and that the diagram claims nothing the prose doesn't say, because
  a parser checks only that the diagram parses, a reader of the raw file gets
  the source and not the picture, and only a reader sees an arrow or a box
  that the text never states.
- R7. Check that a diagram carries no obligation and no reason, because an
  obligation belongs in a requirement and a reason in a decision, where each
  is found by its identifier, and a diagram that holds one hides it from the
  record.
</rules>

<example>
A failing outline: "Introduction", "Details", "More details", "Conclusion".
Each heading names a place in the document and says nothing it argues.

The corrected outline: "Links fail for two reasons", "A site that is down is
no defect", "A missing file is one", "Report them apart". Read alone, it is
the argument.
</example>
