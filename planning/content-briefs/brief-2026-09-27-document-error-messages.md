# Brief: How to Document Error Messages

**Slot:** 2026-09-27 | Order 60 | **Cluster:** Developer experience and DevRel | **Experience: A**

## Keyword

`error message documentation` returned no measurable volume. Near zero, same cluster caveat as
row 59. It earns the slot on evidence.

## Reader task

Connect an exact error message to its cause, its fix, and its escalation path.

## Owns

Error messages as a documented surface: the message text itself, and the page it should lead to.

## Must not repeat

The troubleshooting format (row 47). API error documentation, owned by the live API best-practices
anchor, which covers recovery. Keep this on the message and its routing.

## Evidence — Experience A, and it is unusually direct

`rule_checker.py` emits graded error messages he wrote: `paragraph-length`, `em-dash`,
`rule-of-three`, `contrastive`, each with a line number and a suggested replacement. `build.py`
fails with a named reason. `tools/check_link_retrofit.py` prints a specific failure per rule rather
than a single boolean.

Those are real error messages he designed, and the design decisions are inspectable: why the
checker names the rule, why it prints the offending text, why it exits non-zero.

The useful pattern: a good error message makes the docs page almost unnecessary, and the ones that
need a page are the ones that could not carry their own fix.

## Internal links

Outbound:
- `/articles/api-documentation-best-practices-reference-guides-and-working-requests/` if the
  sentence is genuinely about API errors, noting the cross-cluster rule
- row 47's troubleshooting template, live by this date

**Inbound retrofit source:** row 47's troubleshooting template, whose symptom-to-recovery structure
begins with the message this page covers.
