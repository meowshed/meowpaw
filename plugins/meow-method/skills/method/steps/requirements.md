<role>
The requirements step. It reads approved research, named by its identifiers, and writes from `meow-method template requirement`. The step that picks
it up is design.
</role>

<steps name="requirements">
1. Build requirements from the research's conclusions, not its body.
2. Write one obligation per file, as `REQ-NNNN`, in the identifier block of
   its topic, with the gap its neighbours leave.
3. State what must be true, never how: a requirement that names a mechanism
   has decided what the design hasn't.
4. Give each one its verification: static, behavioural, judgement or
   evaluation, naming who judges where it is judgement.
5. Name the research it elaborates in its front matter, and an outside source
   such as a person's instruction where one imposed it.
</steps>

<rules name="requirements">
- Q1. Write one obligation per requirement, because a requirement carrying two
  can't be closed when only one is met.
- Q2. State what must be true, never how to achieve it, because a requirement
  naming a mechanism has decided what the design hasn't.
- Q3. Describe observable behaviour, not a product, so work that isn't code
  passes through the same chain.
- Q4. Write the obligation itself, never a user story standing in for it,
  because a story says who wants something and not what must hold.
- Q5. Trace a requirement resting on a claim to the research that recorded the
  claim, in its `elaborates`.
- Q6. Record what imposed a requirement from outside, such as a standard or a
  person's instruction, separately from the research that noticed it.
- Q7. Write a constraint that always holds as prose with its modal keyword,
  and conditional behaviour in a trigger-and-response form: when this happens,
  the system does that.
- Q8. Choose a default for every question you didn't ask, and record each as a
  choice that was made, because an unrecorded default can't be told from a gap
  nobody noticed.
- Q9. Give a requirement its reason where the obligation would otherwise look
  arbitrary, and none where the sentence already carries it.
</rules>
