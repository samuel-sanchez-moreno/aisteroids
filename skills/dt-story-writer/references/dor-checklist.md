# Definition of Ready (DoR) — Soft Check

After generating a story, append this checklist as a reminder. This is NOT a gate — the story is output regardless. The checklist helps the team verify readiness during refinement.

## Checklist

Append this after every generated story:

```
---
### 📋 DoR Reminder (check during refinement)

The following items should be verified before a story enters a sprint.
This applies to all story types (business, tech debt, research).

- [ ] **Dependencies identified** — linked ticket or comment describing the dependency
- [ ] **Acceptance criteria defined** — specific, testable criteria in the ticket
- [ ] **What and Why are clear** — the problem and motivation are stated
- [ ] **Out of scope is stated** — what is explicitly NOT part of this story
```

## Usage

- Always append this checklist after the generated story output
- Do not block story generation if DoR items are missing — the story may be a draft
- If obvious gaps are visible (e.g., no "why" at all), mention it conversationally before the checklist
- The checklist serves as a reminder for sprint refinement, not a hard gate
