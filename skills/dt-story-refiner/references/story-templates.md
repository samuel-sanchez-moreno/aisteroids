# Story Templates

Reference templates for the three story types used by Team Lima Bees. Each template has a specific structure. Use the matching template based on the story type identified during conversation.

---

## Business Story Template

Use for user stories in the classic sense — new functionality, behavior changes, or feature additions.

### Template

```
## Description

User story: As a [persona], I want [capability] so that [benefit].

[One paragraph of context — what is changing and why. Keep it concise.]

## Acceptance Criteria

- [ ] [Specific, testable criterion — each one must have a clear pass/fail condition]
- [ ] [e.g., "Lima entitlement handles new features (A and Z) as expected"]
- [ ] [e.g., "New features are exposed on the V4 endpoint"]
- [ ] [e.g., "New features are pushed to PMS"]
- [ ] [e.g., "E2E tests are adapted to handle new features"]

## Solution Proposal

[High-level guidance — which services are affected and the general direction. This is NOT an implementation plan or design doc.]

## Examples / Business Scenarios

[Up to 3 concrete scenarios that guide testing.]

## Verification

[Up to 4 concrete verification steps.]
```

### Fill Guidance for Business Stories

- **Description:** 2 paragraphs maximum — the user story sentence plus one context paragraph. Do not write a detailed narrative.
- **Acceptance criteria:** Each AC should be independently testable. Avoid compound criteria ("X and Y work"). Prefer one criterion per behavior.
- **Solution proposal:** High-level guidance only — state which services are affected and the general approach direction. Do NOT write implementation details, code-level steps, or design documents. The team figures out the "how" during development.
- **Examples:** Maximum 3 business scenarios. Focus on the most important cases — think about edge cases like trial accounts, Classic subscriptions, or DPS environments.
- **Verification:** Maximum 4 steps. Must be concrete — name the tool (DebugUI, V4 endpoint, E2E tests) and the expected observation.

---

## Tech Debt Story Template

Use for technical stories aimed at improving system resilience, removing legacy features, improving code quality, or addressing technical risk.

### Template

```
## Why?

[Business or technical justification — what risk, cost, or fragility does this address? Be specific about the impact of NOT doing this.]

## What?

[What exactly needs to change — scope and boundaries. Be explicit about what is in scope and what is not.]

## How?

[Technical approach — affected components, code changes, migration steps, rollback strategy if applicable]

## Verification

[Explain how to verify the implementation, e.g., "Create a trial account and check the enabled features in DebugUI. XYZ is enabled."]
```

### Fill Guidance for Tech Debt Stories

- **Why:** Must justify the effort. "Code is messy" is not enough. Explain the risk: "This race condition causes X in production" or "This legacy code blocks migration to Y."
- **What:** Be precise about boundaries. What files/services/components are touched? What is explicitly out of scope?
- **How:** Include rollback considerations for risky changes. Mention feature flags if the change can be toggled.
- **Verification:** Even for internal improvements, define how to verify. "All existing tests pass" is a minimum. Add specific checks for the changed behavior.

---

## Research Story Template

Use for stories that investigate systems, explore implementation approaches, or gather knowledge needed for future stories.

### Template

```
## Why?

[What knowledge gap or decision needs research? Why can't we proceed without this research?]

## What?

[Specify what to do in the scope of the research. This is like the acceptance criteria of a business story — concrete steps, not vague exploration.]

- Step A: [specific investigation or analysis]
- Step B: [specific investigation or analysis]

## Expected Outcome

[Specify the desired result of the study:]

- [ ] Confluence page with [specified structure — list the sections]
- [ ] Presentation to the team
- [ ] Decisions based on the results of Steps A and B
```

### Fill Guidance for Research Stories

- **Why:** Research must have a clear purpose. "Learn about X" is not enough. "We need to decide between X and Y to proceed with [future story]" is better.
- **What steps:** Each step should be a concrete investigation, not open-ended exploration. "Analyze the ADA API response for account hierarchies" is better than "Look into ADA."
- **Expected outcome:** At least one tangible deliverable (Confluence page, decision, presentation). Avoid "we'll know more" as an outcome.
