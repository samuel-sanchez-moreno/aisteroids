# Team Lima Bees — Domain Context

Reference document for the PO story writing agent. Use this to understand the team's services, domain terminology, and ecosystem when writing or reviewing stories.

## Team

**Team Lima Bees** (Team LiCoCo) — responsible for licensing, configuration, and connectivity services in the Dynatrace LIMA ecosystem.

## Services

| Service | Purpose | Status | Key Constraint |
|---------|---------|--------|----------------|
| **BAS** | Legacy billing & license management system | **MAINTENANCE ONLY** | No new features. Only hotfixes, deprecations, and feature flag changes allowed. |
| **lima-bas-adapter** | Event bridge between BAS and the LIMA ecosystem | Active | Anti-corruption layer. 100% test coverage required. |
| **entitlement-service** | Feature entitlements & license state engine | Active | TDD required. Java 25. Event-driven via Kafka. |
| **lima-tenant-config** | Configuration distribution for environments | Active | Config management service. |

### BAS — Maintenance-Only Rules

BAS is in maintenance mode. If a story touches BAS, it MUST be one of:
- Hotfix for a production issue
- Deprecation of legacy functionality
- Feature flag change
- Data migration or cleanup

Stories proposing new features, new endpoints, or new business logic in BAS must be rejected or redirected to entitlement-service or lima-bas-adapter.

## Domain Terminology

- **Entitlements** — The right to use specific product features, derived from the license model
- **Features** — Capabilities that can be enabled or disabled per environment
- **Subscriptions** — Billing models: DPS (Dynatrace Platform Subscription), SKU-based, Classic, Trial
- **License Model** — Determines which entitlements an environment receives
- **Environments** — Dynatrace deployment instances (equivalent to "tenants" in legacy terminology)

## Key Integrations

- **ADA** — Account Data API: source of account and environment hierarchy data
- **PMS** — Product Management Service: receives feature and entitlement data pushes
- **Kafka** — Event bus for asynchronous communication between LIMA services
- **V4 API** — External REST endpoint exposing entitlement data to consumers
- **DebugUI** — Internal Dynatrace tool for verifying enabled features per environment

## Common Verification Patterns

When writing the "Verification" section of a story, these are typical approaches:

- **Trial account check:** "Create a trial account and check enabled features in DebugUI. XYZ is enabled."
- **E2E test suite:** "E2E tests are adapted and passing for the new behavior."
- **Kafka event verification:** "Verify the expected Kafka event is produced/consumed by checking logs or event tracing."
- **V4 endpoint check:** "Call the V4 endpoint for the environment and verify the new feature appears in the response."
- **PMS push verification:** "Verify the updated entitlement data is pushed to PMS."

## Story Scope Guidance

- If a story touches **3+ services**, consider splitting it into smaller stories
- Stories should ideally be completable within **one sprint**
- Each story should have a **single clear outcome** — avoid "and also" scope creep
- If a story requires changes in BAS **and** another service, the BAS part should be a separate maintenance story
