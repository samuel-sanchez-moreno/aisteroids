---
name: dt-service-health-check
description: >-
  Check the health status of a SPINE/Lima microservice in a Dynatrace-monitored Kubernetes environment using dtctl.
  Produces a structured report with pod status, pod restarts, error and warning logs, active problems, HTTP endpoint
  response time medians, and 5xx error counts. Use this skill whenever the user asks about service status, health,
  pod state, error logs, response times, or availability of any service in dev, sprint, or prod — even if they don't
  use the word "health check". Triggers include phrases like "how is X doing in dev", "check X in prod",
  "is X healthy", "show me errors for X", "status of X", "any problems with X", "pods for X", or
  "response times of X". Also use when the user asks to monitor, diagnose, or triage a service.
---

# Service Health Check

Produce a quick health report for a Kubernetes-deployed microservice monitored by Dynatrace.

## Prerequisites

This skill requires the `dtctl` CLI. Before running any commands, verify it's available with `which dtctl`. If it's not installed, ask the user to install it.

The dtctl skill (if loaded) handles authentication and context details. If you hit an `invalid_grant` / token refresh error, re-login:

```bash
dtctl auth login --context <ctx> --environment <env-url>
```

## Inputs

Parse these from the user's request:

| Parameter | How to extract | Default |
|-----------|---------------|---------|
| **Service name** | Whatever the user calls the service (e.g., "entitlement-service", "lima-bas-adapter"). This may not match the exact k8s deployment name — you'll fuzzy-match it. | *(required)* |
| **Environment** | "dev", "sprint", or "prod". Infer from context if not explicit. | Current dtctl context |
| **Timeframe** | How far back to look. | `2h` |

## Workflow

### 1. Set the dtctl context

If the user specified an environment, switch to it:

```bash
dtctl config use-context <env>
dtctl config current-context --plain
```

### 2. Find the service entities

The user's name for a service often doesn't match the Kubernetes deployment name exactly. For instance, someone might say "entitlement-service" when the actual deployment is called "lima-entitlement". Use a broad `contains()` search to find matching entities, then narrow down.

```dql
fetch dt.entity.cloud_application
| filter contains(entity.name, "<search-term>")
| fields id, entity.name, lifetime, cloudApplicationLabels
```

Pick the main application entity (not mockservers, db-migrators, or test helpers) and note its ID.

Then find the service-level entities for span/endpoint queries:

```dql
fetch dt.entity.service
| filter contains(entity.name, "<search-term>")
| fields id, entity.name
```

### 3. Get pod status, restarts, and deployment health

Query cloud application instances to find ALL running pods — not just healthy ones. A pod is "running" if its `lifetime.end` is within the last ~2 minutes of now (Dynatrace updates this continuously for live entities). Include pods that recently terminated too (within the timeframe), since they tell the deployment story.

```dql
fetch dt.entity.cloud_application_instance
| filter contains(entity.name, "<deployment-name>")
| fields id, entity.name, lifetime
| sort lifetime.start desc
```

**Detect deployment state:** Pod names typically include the ReplicaSet hash (e.g., `lima-entitlement-764c6f747b-gbck5`). If you see pods from *multiple* ReplicaSet hashes that are all currently running, this indicates a rolling deployment that may be incomplete or stuck. This is important to flag — an incomplete deployment means not all pods are running the same version, which can cause inconsistent behavior and needs team awareness.

Look for:
- Multiple distinct ReplicaSet hashes among running pods → **deployment in progress or stuck**
- Recently terminated pods from different ReplicaSets → **rollout occurred recently**
- A single pod on a different RS than the majority → **possible stuck/failed pod from old or new version**

For restart counts, query Kubernetes events:

```dql
fetch events, from:now()-<timeframe>
| filter event.type == "K8S_EVENT"
  and contains(entity_name, "<deployment-name>")
  and contains(event.name, "restart")
| fields timestamp, event.name, entity_name
| sort timestamp desc
| limit 20
```

Also check for deployment spec change events — these confirm a deployment was triggered:

```dql
fetch events, from:now()-<timeframe>
| filter contains(entity_name, "<deployment-name>")
  and contains(event.name, "Deployment spec change")
| fields timestamp, event.name, entity_name
| sort timestamp desc
| limit 10
```

### 4. Get error and warning logs

First get counts by severity, then sample recent messages for each level.

```dql
fetch logs, from:now()-<timeframe>
| filter contains(k8s.deployment.name, "<deployment-name>")
  and not contains(k8s.deployment.name, "mockserver")
  and not contains(k8s.deployment.name, "migrator")
| filter in(loglevel, array("ERROR", "WARN", "SEVERE"))
| summarize cnt = count(), by:{loglevel}
| sort cnt desc
```

Then get recent samples (latest 10 per level) to show the user what the errors actually are. **Include the pod name** so errors can be correlated to specific pods — this matters especially during deployments when one pod may have issues the others don't:

```dql
fetch logs, from:now()-<timeframe>
| filter contains(k8s.deployment.name, "<deployment-name>")
  and not contains(k8s.deployment.name, "mockserver")
  and not contains(k8s.deployment.name, "migrator")
| filter loglevel == "ERROR"
| fields timestamp, content, k8s.pod.name
| sort timestamp desc
| limit 15
```

Look for patterns: Are errors concentrated on one specific pod (suggesting a pod-level issue like bad config or missing sidecar)? Are they uniform across all pods? This distinction is crucial for triage.

### 5. Check for active problems

Search for Dynatrace-detected problems affecting this service's entities:

```dql
fetch events, from:now()-<timeframe>
| filter contains(entity_name, "<service-name>")
  or contains(entity_name, "<deployment-name>")
| filter event.kind == "DAVIS_PROBLEM"
| fields timestamp, event.kind, event.name, event.type, entity_name
| sort timestamp desc
| limit 20
```

If that returns empty, also try searching by entity ID:

```dql
fetch events, from:now()-<timeframe>
| filter matchesValue(affected_entity_ids, "*<cloud-app-entity-id>*")
| fields timestamp, event.kind, event.name, event.type
| sort timestamp desc
| limit 20
```

### 6. Get HTTP endpoint response medians and 5xx errors

Because OneAgent-detected services don't always carry k8s labels in spans, first discover which spans match the service by searching for the service name in span names:

```dql
fetch spans, from:now()-<timeframe>
| filter contains(span.name, "<search-term>")
| filter startsWith(span.name, "GET") or startsWith(span.name, "POST")
  or startsWith(span.name, "PUT") or startsWith(span.name, "DELETE")
  or startsWith(span.name, "PATCH")
| summarize
  median_ms = median(duration) / 1000000.0,
  p95_ms = percentile(duration, 95) / 1000000.0,
  cnt = count(),
  errors_5xx = countIf(http.response.status_code >= 500),
  by:{span.name}
| sort cnt desc
| limit 20
```

If the search term doesn't directly appear in HTTP span names (common when the service name differs from the URL path), also try looking up spans by the service entity IDs discovered in step 2:

```dql
fetch spans, from:now()-<timeframe>
| filter in(dt.entity.service, array("<svc-id-1>", "<svc-id-2>"))
| filter span.kind == "SERVER"
| summarize
  median_ms = median(duration) / 1000000.0,
  p95_ms = percentile(duration, 95) / 1000000.0,
  cnt = count(),
  errors_5xx = countIf(http.response.status_code >= 500),
  by:{span.name}
| sort cnt desc
| limit 20
```

## Important: Avoid token race conditions

dtctl uses OAuth tokens that break when refreshed concurrently. **Run DQL queries sequentially, not in parallel.** If you launch multiple `dtctl query` commands at once, the concurrent token refresh will invalidate the session and all queries will fail with `invalid_grant`.

## Output format

Present a structured markdown report with these sections:

### Overall status indicator

Use a single emoji+color header that summarizes health at a glance:
- 🟢 **Healthy** — no problems, no 5xx errors, pods stable, single ReplicaSet
- 🟡 **Degraded** — warnings present, elevated error rates, recent restarts, or deployment in progress but service is functional
- 🔴 **Unhealthy** — active problems, high 5xx rate, pods crashing, or stuck deployment with failing pods

An incomplete deployment (multiple active ReplicaSets) should bump the status to at least 🟡 Degraded since it indicates version inconsistency across pods.

### Sections

1. **Pods** — table with pod name, status (✅ Running / ❌ Down / 🔄 Restarting), ReplicaSet hash, age/uptime, restart count. If pods are on different ReplicaSets, highlight this with a ⚠️ note about deployment state.
2. **Deployment State** *(only if noteworthy)* — If a rolling deployment is in progress or appears stuck (multiple ReplicaSets active), call this out explicitly. Mention which RS is old vs new, how many pods are on each, and whether the deployment appears healthy or stuck.
3. **Error & Warning Logs** — count table by severity, then a brief summary of what the errors are (group repeated messages, don't dump raw logs). Note which pods the errors come from — if errors are concentrated on a single pod, flag it.
4. **Problems** — list of active Dynatrace problems, or ✅ "No active problems" if clean
5. **HTTP Endpoints** — table with endpoint, median response time, P95, request count, 5xx error count
6. **Action Items** — Concrete things the team should investigate or act on. Examples: "Investigate metrics exporter failure on pod X", "Rolling deployment appears stuck — pod Y on old ReplicaSet is still running", "5xx errors on endpoint Z need attention". If everything is clean, say "No action needed." This section turns the report from informational into actionable.
7. **Summary** — 1-2 sentence plain-English assessment of service health

### Style notes

- Use tables for structured data
- Use emoji status indicators (✅ ❌ 🟢 🟡 🔴 🔄) for quick scanning
- Round response times to whole milliseconds
- Format large request counts with commas (e.g., 1,293)
- If an entire section returns no data, say so briefly rather than omitting it
- If errors are all the same repeated message, say "all N errors are: <message>" rather than listing each one
