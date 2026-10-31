<role>
The design step. It reads approved requirements, named by their identifiers,
and writes from `paw template adr`. Its artifact lands in
`adrs/ADR-NNNN-<slug>.md` under the record root, `[record] root` in
`.meowpaw/profile.toml` or `project/` where it declares none. The decision
carries its own `## Plan`. The step that picks it up is spec.
</role>

<steps name="design">
1. Write one decision record per decision, as the identifier `paw new decision`
   prints, addressing the requirements it settles by identifier. A decision that
   addresses none is refused.
2. Compare at least three alternatives, doing nothing among them, each with
   what it is genuinely better at and why it lost.
3. Record what it costs, what would reverse it as a condition, what it does
   not settle, and how anyone will know it was realised, written now.
4. Argue against it before you finish, and state the strongest objection.
5. Say what works once it is accepted and what still doesn't, so a reader can
   tell an increment from a promise.
6. Name each concern the decision raises, such as performance, security or
   upgrade, in the decision's `concerns:` front matter.
7. Write the decision's `## Plan` as D29 to D33 say, and land every requirement
   it addresses in a step of the plan or move it to `postpones:` with the
   reason, then run `paw check coverage` to prove it.
</steps>

<rules name="design">
- D1. Write one decision record per decision, each naming by identifier the
  requirements it satisfies; a decision may settle several requirements, and a
  requirement may be settled by several decisions.
- D2. Ask first whether a program could settle the rule, and make a rule that
  must hold every time a check or a hook rather than a paragraph.
- D3. Title the decision with the decision itself, so a list of decisions
  reads as a list of positions.
- D4. State the non-goals under What this does not settle.
- D5. Where a draft can't say what the system does after it that it didn't
  before, merge it with its neighbours or split it by capability, not by
  component.
- D6. Argue against the decision before you record it, and state the strongest
  objection rather than summarising it away.
- D7. Critique the draft for what it doesn't say: repetition, concurrency, a
  failure after a failure, empty and enormous input, unnamed failure states,
  assumed ordering, and the assumption the operator won't notice.
- D8. Close with a premortem: what went wrong, written as though it already
  had.
- D9. Where elicitation runs out of ideas, fall back on these questions: who
  is the reader, what do they do today instead, what fails first, what is the
  smallest version that works, and what would make this decision wrong.
- D10. Where the system has an interface, you may write its contract and its
  rationale as separate artifacts, because different people read them.
- D11. State the ergonomic cost: who does more work, what queue it creates,
  what it interrupts, and what happens if nobody attends to it for a month.
- D12. Leave the system working after each decision: everything decided up to
  it works without anything not yet decided, order the decisions as increments
  on a working whole with the smallest usable system first, and record two
  choices that only work together as one decision.
- D13. Say what works once the decision is accepted and what doesn't work yet,
  and keep the system working when a capability the decision adds is absent,
  so the increment can be removed by the step that added it.
- D14. Give anything that accumulates a ceiling that reports once when
  exceeded, and an automatic drain where draining is safe, because a pile that
  needs a person grows until nobody reads it.
- D15. Where the design interrupts people, state its interruption budget, fire
  a notification once per condition and never again without new information,
  and create no alert that can't be acted on.
- D16. Name every failure state the system can reach, each with its next step
  and exactly one audience, with names shared across the whole system; say so
  where two are deliberately indistinguishable.
- D17. Word a failure message as what the system couldn't do, never as what
  the person did wrong, and make a confirmation echo what the system inferred
  rather than what the person supplied.
- D18. Keep non-functional baselines, such as latency, cost and size, in one
  place per repository, each number with its reason; a design may be stricter
  when it says so and justifies being looser, and exceeding a baseline is
  recorded as a finding, not adopted.
- D19. Express a budget with slack, never at perfection, covering the paths
  where a person waits, and distinguish a budget you chose from a limit
  imposed on you, because they behave differently when exceeded.
- D20. Where the design has a security-relevant boundary, state what is
  protected and who it is defended against, ordered by the likelihood of
  damage, and update the threat model the repository's specification keeps,
  ranking the new threats among those it lists, or say in the decision that
  the specification keeps none, because threats recorded one decision at a
  time never meet in one ranking, and a missing model nobody names reads as
  one that holds.
- D21. Make every surface the design adds answer one question someone actually
  asked, name the data behind it before choosing its shape, report a surface
  named after an entity rather than a question as a finding, and report a
  number the data can't produce as unavailable rather than promise it.
- D22. Identify the person the work bottlenecks on and never require them in
  real time; show the system survives two weeks without them, losing no data
  and leaving no queue that can't be recovered, and create no backlog whose
  likely end is being approved unread.
- D23. Give a recommendation the condition that would reverse it, or mark it
  as a preference.
- D24. Run the adversarial pass over the draft before implementation, and
  write its findings against the draft rather than rewriting it.
- D25. For each decision that adds a rule to the constitution, ask whether
  the rule pulls against one already there, and write two that do as one rule
  with its exception stated, in the same decision, because two rules that
  pull against each other leave the reader to guess which wins.
- D26. For a decision that changes the vision, ask whether a requirement makes
  each claim it adds falsifiable, and remove a claim with no requirement,
  because a claim nothing can fail settles no argument.
- D27. Where a decision contradicts the vision, report that one of the two is
  stale, ask which, and stop: the step writes no decision while both stand,
  because a record that holds both leaves the contradiction for the next
  reader to resolve.
- D28. Name a concern as one word a specification heading can carry, because
  `paw check` matches it against the headings, and a concern phrased as a
  sentence is one no heading names.
- D29. Give every decision that addresses a requirement a `## Plan` of ordered
  steps, because the plan is what its pull request works through, and
  `paw ready implement` refuses a decision that has none.
- D30. Keep a decision to what one issue, one branch and one pull request can
  carry, and split one that wouldn't be one reviewable change before its work
  starts, because review turns into approval past a size. Write two parallel
  streams as two decisions, because a plan is one ordered list.
- D31. Write each plan step as a vertical slice someone can observe, naming the
  requirements it closes and what it touches, so an implementer with none of
  the conversation can follow it. Leave how it is done to the implementer,
  beyond the constraints that bind the result.
- D32. Let a step close several requirements and several steps close one,
  because a requirement often needs a program change and a prompt change, and
  write no work that no record authorises: a decision for new behaviour, a
  defect for a departure from what is already required.
- D33. Carry no estimates, because an estimate in a record is read as a
  promise, and authorise recurring work once, in the record that establishes
  it, because a new record each time it recurs adds a record and no decision.
- D34. Write each outcome under How I will know it was realised as something
  the project itself can bring about and this pull request's own work decides.
  Where a third party controls the behaviour, state what the project ships and
  record the dependency, because an outcome that waits on other work can't be
  met when it is checked. Where the work predicts a measurable outcome, state
  the number now, because a prediction written after the result fits it.
- D35. Record an unknown as an open question classified by what it blocks, and
  let it stop a step only when it blocks that step.
</rules>
