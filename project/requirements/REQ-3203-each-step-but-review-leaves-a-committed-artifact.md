---
id: REQ-3203
artifact: requirement
topic: the-method
class: functional
status: approved
revised: 2026-09-28
elaborates: RES-0001
verification: static
---

# REQ-3203

The instructions for each step of the method except review MUST name where the
step's artifact lands in the repository, as a location or a path pattern under
the record root `.meowpaw/profile.toml` resolves, or under the template's
default where the profile declares none. Implement names the files its task
changes, its kept runs and its task file's Evidence. Verify names the epic's
file and the kept evidence its verification cites.

A step whose output lives only in a session can't be approved, cited or
checked by the step after it, which RES-0001 records under "What nobody
needs" as the state that "loses to the first compaction". The obligation is
on the instructions, and not on the commit, on purpose: a static check can
read what a step's instructions name, and it can't observe that a step
committed anything. Review is the exception because REQ-0544 forbids it an
artifact in the repository.
