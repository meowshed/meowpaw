<role>
A defect record is evidence that a requirement is not met, and it authorises a
fix the way a decision does.
</role>

<rules name="sections, in order">
<rule id="reproduction">The smallest reproduction, run against a named
change.</rule>
<rule id="does">What the system does.</rule>
<rule id="should">What it should do, and which requirement says so.</rule>
<rule id="triage">The triage: whether a requirement in force covers it, which
decides where the fix enters the method.</rule>
<rule id="closed">What closed it, with the check that now guards against its
return.</rule>
</rules>

<rules name="done">
<rule id="done">It is done when someone could reproduce it from the record, and
after the fix, see the reproduction pass.</rule>
</rules>
