<role>
The research step. It reads a question, and writes from
`paw template research`. Its artifact lands in `research/RES-NNNN-<topic>.md`
under the record root, `[record] root` in `.meowpaw/profile.toml` or
`project/` where it declares none. The step that picks it up is requirements.
</role>

<steps name="research">
1. State the question, then challenge the assumption behind it before you
   explore any alternative, because an assumption every option shares turns
   invisible once the options exist. Take the record's identifier from
   `paw new research`.
2. Dispatch the researcher — the `meow-flow:researcher` agent on Claude Code,
   the `meow-research` tool on Pi — with the question, the sources the person
   named and, on Pi, the material the call drafts from: the template
   `paw template research` prints, the record searches and the sources' text,
   because a nested call reads nothing (REQ-3526). The researcher reads the
   primary sources and returns the draft, and writes nothing.
3. Write the artifact from `paw template research`: the front matter with the
   identifier, and the body from the researcher's draft, held to the rules
   below, because the rules bind the record however it was drafted.
4. Run `paw check` and stop at the gate, as the method skill says.
</steps>

<rules name="research">
- R1. Challenge the assumption behind the question before you explore any
  alternative, because an assumption every option shares turns invisible once
  the options exist.
- R2. Read the primary source, the documentation, the code or the tool itself,
  and not a description of it, because secondary coverage lags most where a
  project has changed.
- R3. Check a claim about one tool that comes from a comparison a competing
  tool published against the tool it describes before you repeat it, because a
  rival's table is written to win.
- R4. Trace a figure from a secondary source to the source it is attributed
  to, and record it as unverified where that source doesn't contain it.
- R5. Research or drop a claim you remember and didn't read, and never record
  it as a finding, because memory is the source least likely to be current.
- R6. Support every conclusion with a finding in the same document, and report
  a conclusion no finding supports as an opinion.
- R7. Write each conclusion as what must now be true, not what was
  interesting, because a conclusion nothing can be required of is a summary.
- R8. State the case against the alternative you lead with, inside the
  document, because a separate adversarial step is one nobody runs.
- R9. Compare at least three options where the question admits them, doing
  nothing among them and evaluated rather than mentioned, each in the terms
  its advocate would use and with what it is genuinely better at.
- R10. End a comparison as decided, deferred or left to discretion: a deferral
  names what it waits on, and discretion is recorded as a result.
- R11. Let a comparison inform a decision and never record one, because the
  decision belongs to the design step and its record.
- R12. Give a fact that will change the date it was true where you state it.
- R13. Drop an option that is better at nothing rather than listing it,
  because a survey padded with weak options looks like diligence and
  manufactures consent.
- R14. Let the verdicts an assessment may reach include abandoning the idea
  entirely.
</rules>
