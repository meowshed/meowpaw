<role>
A defect record is evidence that a requirement is not met, and it authorises a
fix the way a decision does.
</role>

<rules name="sections, in order">
1. Reproduction: The smallest reproduction, run against a named change.
2. What it does: What the system does.
3. What it should do: What it should do, and which requirement says so.
4. Triage: The triage: whether a requirement in force covers it, which decides
   where the fix enters the method.
5. Closed by: What closed it, with the check that now guards against its return.
</rules>

<rules name="done">
It is done when someone could reproduce it from the record, and after the fix,
see the reproduction pass.
</rules>
