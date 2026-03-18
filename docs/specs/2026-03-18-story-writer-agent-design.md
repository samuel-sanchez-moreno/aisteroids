# Design: PO Story Writer & Refiner Agent Skills

**Date:** 2026-03-18
**Status:** Approved
**Scope:** Two Copilot CLI / Claude Code skills for Team Lima Bees story writing

---

## Problem Statement

Team Lima Bees needs a consistent, team-wide way to write well-formed JIRA stories. Today, story quality varies depending on who writes them and how familiar they are with the templates, DoR, and domain context. The team wants an AI agent that acts as a Product Owner — guiding anyone on the team through writing complete stories via conversation.

## Proposed Approach

Create two complementary skills deployed to aisteroids (source of truth), Claude Code global settings, and Copilot CLI global settings:

1. **dt-story-writer** — Conversational story creation agent with PO persona
2. **dt-story-refiner** — Story quality reviewer for existing drafts

Both skills use the SKILL.md + references/ progressive disclosure pattern established in the aisteroids project.

---

## Skill 1: dt-story-writer

### Structure

```
aisteroids/skills/dt-story-writer/
├── SKILL.md                              # PO persona, conversation engine, routing
├── references/
│   ├── story-templates.md                # 3 story type templates with fill guidance
│   ├── domain-context.md                 # services, integrations, domain terms
│   └── dor-checklist.md                  # soft DoR reminder items
```

### SKILL.md Design

**Frontmatter:**
```yaml
name: dt-story-writer
description: >
  PO story writer for Team Lima Bees. Use when anyone needs to write a
  business story, tech debt story, or research story. Triggers: "write a story",
  "new story", "business story", "tech debt", "research story", "story template",
  "help me write a ticket".
```

**Persona:**
- Acts as the team's Product Owner
- Responsibilities: backlog quality, story completeness, challenging "what" and "why"
- Knows the team's 4 services and their constraints (BAS = maintenance only)
- Understands the DoR and reminds about it
- Tone: collaborative, constructive, direct — not bureaucratic

**Conversation Flow:**

1. **Identify story type** — Ask what kind of work this is (business / tech debt / research), or infer from context
2. **Understand the need** — Ask conversational questions one at a time:
   - *What* is the problem or need?
   - *Why* does it matter? (customer pain, technical risk, knowledge gap)
   - *Which service(s)* are involved?
   - Type-specific questions (ACs for business, what/how for tech debt, research steps)
3. **Challenge & refine** — Push back if:
   - The "why" is weak or missing
   - Scope is too broad for a single story
   - Acceptance criteria are vague or untestable
   - Verification is not concrete
4. **Generate story** — Output the complete story using the matching template, formatted in markdown for JIRA copy-paste
5. **DoR soft check** — Append a reminder checklist (not a gate)

**Key behaviors:**
- One question at a time — never overwhelm with multiple questions
- Challenge requirements like a real PO: understand the customer pain, not just the technical solution
- If a story touches BAS, remind that BAS is maintenance-only (no new features)
- If scope is too broad, suggest splitting into multiple stories
- Output is plain markdown in chat — user copies to JIRA

### references/story-templates.md

Three templates with fill guidance for each section:

**Business Story:**
```markdown
## Description

User story: As a [persona], I want [capability] so that [benefit].

[Story draft — detailed description of the change]

## Acceptance Criteria

- [ ] [Specific, testable criterion]
- [ ] [e.g., "Lima entitlement handles new features X and Y as expected"]
- [ ] [e.g., "New features are exposed on the V4 endpoint"]
- [ ] [e.g., "New features are pushed to PMS"]
- [ ] [e.g., "E2E tests are adapted to handle new features"]

## Solution Proposal

[How to cover the ACs — technical approach, affected services, migration if needed]

## Examples / Business Scenarios

[Concrete examples and business scenarios. Good guidance for testing.]

## Verification

[How to verify the implementation, e.g., "Create a trial account and check
enabled features in DebugUI. XYZ is enabled."]
```

**Tech Debt Story:**
```markdown
## Why?

[Business or technical justification — what risk, cost, or fragility does this address?]

## What?

[What exactly needs to change — scope and boundaries]

## How?

[Technical approach, affected components, migration steps if any]

## Verification

[How to verify the implementation, e.g., "Create a trial account and check
enabled features in DebugUI. XYZ is enabled."]
```

**Research Story:**
```markdown
## Why?

[What knowledge gap or decision needs research?]

## What?

[Steps to perform in the scope of the research — like acceptance criteria for a business story]

- Step A: [specific investigation]
- Step B: [specific investigation]

## Expected Outcome

[Desired result of the study:]

- [ ] Confluence page with [specified structure]
- [ ] Presentation to the team
- [ ] Decisions based on results of Steps A and B
```

### references/domain-context.md

**Team:** Lima Bees (Team LiCoCo)

**Services:**

| Service | Purpose | Status | Key Constraint |
|---------|---------|--------|----------------|
| BAS | Legacy billing & license management | MAINTENANCE ONLY | No new features — only hotfixes, deprecations, feature flags |
| lima-bas-adapter | Event bridge: BAS ↔ LIMA ecosystem | Active | Anti-corruption layer, 100% test coverage required |
| entitlement-service | Feature entitlements & license state engine | Active | TDD required, Java 25, event-driven (Kafka) |
| lima-tenant-config | Configuration distribution for environments | Active | Config management |

**Domain terminology:**
- **Entitlements** — The right to use specific product features, derived from the license model
- **Features** — Capabilities that can be enabled or disabled per environment
- **Subscriptions** — Billing models: DPS (Dynatrace Platform Subscription), SKU-based, Classic, Trial
- **License Model** — Determines which entitlements an environment receives
- **Environments** — Dynatrace deployment instances (equivalent to tenants in legacy terminology)

**Key integrations:**
- **ADA** — Account Data API: source of account/environment hierarchy data
- **PMS** — Product Management Service: receives feature/entitlement data
- **Kafka** — Event bus for async communication between services
- **V4 API** — External REST endpoint for entitlement data exposure
- **DebugUI** — Internal tool for verifying enabled features per environment

**Verification patterns:**
- "Create a trial account and check enabled features in DebugUI"
- Run E2E test suites
- Verify Kafka event production/consumption
- Check V4 endpoint response

### references/dor-checklist.md

```markdown
### 📋 DoR Reminder (check during refinement)

The following items should be verified before a story is considered "ready"
for the sprint. This applies to all story types (business, tech debt, research).

- [ ] **Dependencies identified** — linked ticket or comment describing the dependency
- [ ] **Acceptance criteria defined** — specific, testable criteria in the ticket
- [ ] **What and Why are clear** — the problem and motivation are stated
- [ ] **Out of scope is stated** — what is explicitly NOT part of this story
```

---

## Skill 2: dt-story-refiner

### Structure

```
aisteroids/skills/dt-story-refiner/
├── SKILL.md                              # PO reviewer persona, gap analysis engine
├── references/
│   ├── review-criteria.md                # DoR checks, template compliance, quality rules
│   └── domain-context.md                 # same domain knowledge (copy from dt-story-writer)
```

### SKILL.md Design

**Frontmatter:**
```yaml
name: dt-story-refiner
description: >
  PO story reviewer for Team Lima Bees. Reviews existing story drafts for
  completeness, DoR compliance, and quality. Triggers: "review this story",
  "refine this ticket", "check this story", "is this story ready?",
  "review my draft", "DoR check".
```

**Persona:**
- Same PO persona as dt-story-writer, but in "reviewer" mode
- Constructive and specific — never vague feedback
- Focuses on what's missing or weak, not what's fine

**Review Flow:**

1. User pastes a story draft (or points to a file/ticket description)
2. Agent identifies the story type (business / tech debt / research)
3. **Template compliance check** — flags missing or empty sections per the matching template
4. **DoR compliance check** — dependencies, ACs, what/why, out-of-scope
5. **Quality check:**
   - Is the "why" compelling and specific?
   - Are acceptance criteria testable and concrete?
   - Is the verification section actionable?
   - Is the scope appropriate (not too broad, not trivial)?
   - For BAS stories: does it respect maintenance-only constraints?
6. **Output structured review:**
   - Per-item status: ✅ Good / ⚠️ Needs improvement / ❌ Missing
   - Specific suggestions for each flagged item
   - Optional: rewritten sections if user asks

### references/review-criteria.md

**Template Compliance (per story type):**

| Section | Business | Tech Debt | Research |
|---------|----------|-----------|----------|
| Description / User Story | Required | — | — |
| Why? | Implied in story | Required | Required |
| What? | Implied in ACs | Required | Required (steps) |
| How? | Solution Proposal | Required | — |
| Acceptance Criteria | Required | — | — |
| Examples / Scenarios | Required | — | — |
| Verification | Required | Required | — |
| Expected Outcome | — | — | Required |

**Quality Rules:**
- "Why" must state customer pain OR technical risk — not just "we should do this"
- Acceptance criteria must be testable — each one should have a clear pass/fail condition
- Verification must be concrete — name specific tools, accounts, or checks
- Scope: if a story touches 3+ services, consider splitting
- BAS constraint: any story touching BAS must be hotfix, deprecation, or feature flag only

### references/domain-context.md

Identical copy from dt-story-writer. Maintains the same domain knowledge.

---

## Deployment

All skills deployed to 3 locations:

| Location | Purpose |
|----------|---------|
| `aisteroids/skills/dt-story-writer/` | Source of truth, committed to repo |
| `aisteroids/skills/dt-story-refiner/` | Source of truth, committed to repo |
| `~/.claude/skills/dt-story-writer/` | Claude Code global access |
| `~/.claude/skills/dt-story-refiner/` | Claude Code global access |
| `~/.copilot/skills/dt-story-writer/` | Copilot CLI global access |
| `~/.copilot/skills/dt-story-refiner/` | Copilot CLI global access |

Same SKILL.md format works for both Claude Code and Copilot CLI.

---

## Out of Scope

- JIRA API integration (stories are plain markdown, user copies to JIRA)
- Bug report or RFA templates (can be added later)
- Epic breakdown skill (can be added later)
- Automatic DoR enforcement (soft check only)

---

## Success Criteria

- Any team member can invoke dt-story-writer and produce a complete, well-formed story through guided conversation
- Stories generated follow the team's established templates exactly
- The agent challenges weak "why" statements and vague acceptance criteria
- dt-story-refiner catches missing sections, DoR gaps, and quality issues in existing drafts
- Both skills work identically in Claude Code and Copilot CLI
