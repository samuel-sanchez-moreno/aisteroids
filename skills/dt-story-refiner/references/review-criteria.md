# Story Review Criteria

Reference document for the PO story refiner agent. Use these criteria when reviewing existing story drafts for completeness, quality, and DoR compliance.

## Template Compliance

Check that the story has all required sections for its type. Flag missing sections with ❌.

| Section | Business Story | Tech Debt Story | Research Story |
|---------|:-:|:-:|:-:|
| Description / User Story | Required | — | — |
| Why? | Implied in story | Required | Required |
| What? | Implied in ACs | Required | Required (as steps) |
| How? / Solution Proposal | Required | Required | — |
| Acceptance Criteria | Required | — | — |
| Examples / Business Scenarios | Required | — | — |
| Verification | Required | Required | — |
| Expected Outcome | — | — | Required |

## DoR Compliance

Check these items. Flag missing ones with ⚠️ (soft check, not blocking):

- [ ] **Dependencies identified** — linked ticket or comment
- [ ] **Acceptance criteria / steps defined** — specific and testable
- [ ] **What and Why are clear** — problem and motivation stated
- [ ] **Out of scope stated** — what is explicitly NOT included

## Quality Rules

Apply these quality checks. Use ⚠️ for weak items, ❌ for clearly inadequate ones:

### "Why" Quality
- ✅ Good: States customer pain OR technical risk with specifics
- ⚠️ Weak: Generic justification ("we should improve this", "it would be nice")
- ❌ Bad: Missing entirely or just restates the "what"

### Acceptance Criteria Quality
- ✅ Good: Each criterion is independently testable with a clear pass/fail condition
- ⚠️ Weak: Compound criteria ("X and Y and Z work"), vague criteria ("system works correctly")
- ❌ Bad: Missing or just one generic criterion

### Verification Quality
- ✅ Good: Names specific tools, accounts, endpoints, and expected observations
- ⚠️ Weak: Generic ("test it" or "check that it works")
- ❌ Bad: Missing entirely

### Scope Quality
- ✅ Good: Single clear outcome, completable in one sprint
- ⚠️ Broad: Touches 3+ services or has "and also" scope creep
- ❌ Overloaded: Multiple independent outcomes, clearly multi-sprint

### BAS Constraint
- If the story touches BAS, verify it is ONLY one of: hotfix, deprecation, feature flag change, data migration
- Flag any story proposing new features, new endpoints, or new business logic in BAS

## Output Format

Structure the review as follows:

```text
## Story Review

**Story type detected:** [Business / Tech Debt / Research]

### Template Compliance
- [Section name]: ✅ Present / ⚠️ Needs improvement / ❌ Missing
  - [Specific feedback if not ✅]

### DoR Compliance
- [Item]: ✅ / ⚠️ / ❌
  - [Specific feedback if not ✅]

### Quality Assessment
- **Why:** ✅ / ⚠️ / ❌ — [brief note]
- **Acceptance Criteria:** ✅ / ⚠️ / ❌ — [brief note]
- **Verification:** ✅ / ⚠️ / ❌ — [brief note]
- **Scope:** ✅ / ⚠️ / ❌ — [brief note]

### Suggestions
- [Specific, actionable improvement suggestions]
```
