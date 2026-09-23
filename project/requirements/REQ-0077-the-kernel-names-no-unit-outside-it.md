---
id: REQ-0077
artifact: requirement
topic: universality
class: non-functional
status: approved
revised: 2026-09-23
elaborates: RES-0004
verification: static
---

# REQ-0077

A kernel unit MUST NOT name, point to or load a unit outside the kernel.

The kernel has to behave the same whether or not an optional unit is
installed. A kernel prompt that names one behaves differently when the unit is
there, and it asks the model about something that may not exist when it isn't.
REQ-0076 stops a unit from requiring another, and a yield for the missing case
satisfies it, so it doesn't catch this.
