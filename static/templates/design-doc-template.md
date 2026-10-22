# {{Title: the change, stated as an outcome}}

<!--
Design doc template. Replace every {{placeholder}}. Keep each section, and write
"None" where a section has nothing to say rather than deleting it.
check_design_doc.py checks this structure; run it with --filled before review.
-->

Status: {{Draft | In review | Accepted | Rejected | Superseded by <link>}}
Author: {{name}}
Reviewers: {{names}}
Date: {{YYYY-MM-DD}}

## Problem

{{What is broken or missing, for whom, and the evidence: a metric, an incident, a support ticket.}}

## Goals

- {{An outcome someone could check after the change ships.}}

## Non-goals

- {{Something a reviewer might expect this change to do that it will not.}}

## Proposal

{{The design: components, data, interfaces and the order of the work.}}

## Alternatives considered

### Do nothing

What happens: {{the cost of leaving things as they are}}
Rejected because: {{why that cost is not acceptable}}

### {{Another option}}

What happens: {{how it would work}}
Rejected because: {{the reason, in one or two sentences}}

## Risks and rollout

- Risk: {{what could go wrong}}. Mitigation: {{what reduces it}}
- Rollout: {{the order of release}}
- Rollback: {{how to undo the change, and when undoing stops being possible}}

## Open questions

- {{A question that must be answered before the doc is accepted, or "None"}}

## Decision

<!-- Write None in each field while the status is Draft or In review. -->
Decided by: {{names}}
Decided on: {{YYYY-MM-DD}}
Outcome: {{what was decided, and any conditions}}
