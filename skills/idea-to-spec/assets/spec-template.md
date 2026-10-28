---
status: draft      # draft | approved | obsolete. Only a person marks it approved; task-done marks it obsolete when the change is done.
issue:             # optional: tracker link or ID (e.g. TRIBBU-123)
---

# Feature name

## Goal
<!-- What we want to achieve. One or two sentences summarizing the feature and its purpose. -->

## Problem
<!-- What pain exists today. Describe the current situation and why it is unsatisfactory. Do not include the solution. -->

## Users
<!-- Who we are building this for. Define profiles with role, technical level and context of use. -->

## User stories
<!-- What each user needs and why. Format: "As a [user], I want [action] so that [benefit]". -->

## Functional requirements
<!-- What the system must do. Observable, verifiable behaviours. Format: "FR-01: The system must..." -->

## Non-functional requirements
<!-- Quality constraints: performance, security, accessibility, compatibility. Format: "NFR-01: ..." -->

## Edge cases
<!-- What happens in rare or extreme situations: empty, massive or corrupt data, concurrent actions. -->

## Acceptance criteria
<!-- How we verify it works. Format: "Given [context], when [action], then [result]". -->

## Scope
<!-- How far this spec goes. What IS included. Optional for small tasks. -->

## Out of scope
<!-- What is NOT included even if it looks related. Important for AI agents: they do not infer by omission. -->

## Entities / Data model
<!-- Main domain concepts, key attributes and relationships. Not a database design. Optional. -->

## Success metrics
<!-- How we will know it works in the real world. Measurable post-launch metrics. Optional. -->

## Dependencies
<!-- Systems, APIs or features that must exist before or during implementation. Optional. -->

## Risks
<!-- What can go wrong or complicate the implementation. Technical or business uncertainties. Optional. -->

## Assumptions
<!-- What we take for granted without having validated it, and the reversible details proposed with a default instead of asked. Making them explicit lets the person or a review change them. Optional. -->

## Open questions
<!-- What we do not know yet. Better to list them than to invent the answer. Optional. -->

## Security
<!-- Mandatory if the feature touches data, authentication or external input. Otherwise, delete it. -->
- Data handled and its sensitivity:
- Who can do what (authorization matrix):
- Untrusted inputs and how they are validated:
- Required negative tests (no auth, another user, malicious input, limits):
