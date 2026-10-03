---
id: EPC-2615
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2720
---

# Generate the interface reference

Realises ADR-2720 in TSK-5170.

## Acceptance criteria

1. The generated page covers every declared interface and drifts on neither a subcommand nor a profile key.
2. REQ-2992 lands in the closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

## Tasks

- [ ] T-001 TSK-5170 generate and check the interface reference
      closes: REQ-2992

## Coverage

TSK-5170 owns the generator, page and drift check together.

## Not covered

Narrative documentation outside the interface reference.
