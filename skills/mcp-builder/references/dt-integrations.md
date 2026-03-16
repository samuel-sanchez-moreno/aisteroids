# DT Ecosystem Integration Patterns for MCP Servers

This guide covers DT-specific patterns for MCP servers that integrate with Dynatrace services.

---

## Dynatrace API Authentication

### Environment Variables

Never hard-code tokens. Read them from environment variables at startup:

```python
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dynatrace_mcp")

DT_API_TOKEN = os.environ.get("DT_API_TOKEN")
DT_ENV_URL = os.environ.get("DT_ENV_URL")  # e.g., https://abc12345.live.dynatrace.com

if not DT_API_TOKEN or not DT_ENV_URL:
    raise RuntimeError(
        "DT_API_TOKEN and DT_ENV_URL environment variables are required. "
        "Set them before starting the MCP server."
    )
```

For TypeScript:
```typescript
const DT_API_TOKEN = process.env.DT_API_TOKEN;
const DT_ENV_URL = process.env.DT_ENV_URL;

if (!DT_API_TOKEN || !DT_ENV_URL) {
  throw new Error(
    "DT_API_TOKEN and DT_ENV_URL environment variables are required."
  );
}
```

### API Request Patterns

DT API uses bearer token auth:

```python
import httpx

async def dt_api_get(path: str, params: dict | None = None) -> dict:
    """Make a GET request to the Dynatrace API."""
    url = f"{DT_ENV_URL.rstrip('/')}/api/v2/{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Api-Token {DT_API_TOKEN}"},
            params=params or {},
        )
        response.raise_for_status()
        return response.json()
```

For TypeScript:
```typescript
async function dtApiGet(path: string, params?: Record<string, string>): Promise<unknown> {
  const url = new URL(`/api/v2/${path}`, DT_ENV_URL);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }
  const response = await fetch(url.toString(), {
    headers: { Authorization: `Api-Token ${DT_API_TOKEN}` }
  });
  if (!response.ok) {
    throw new Error(`DT API error ${response.status}: ${await response.text()}`);
  }
  return response.json();
}
```

### Common DT API v2 Endpoints

| Resource | Endpoint | Notes |
|---|---|---|
| Problems | `GET /api/v2/problems` | `from`, `to` (relative time: `-2h`), `problemSelector` |
| Entities | `GET /api/v2/entities` | `entitySelector`, `fields` |
| Metrics | `GET /api/v2/metrics/query` | `metricSelector`, `resolution`, `from`, `to` |
| Events | `GET /api/v2/events` | `from`, `to`, `eventSelector` |
| Settings | `GET /api/v2/settings/objects` | `schemaIds` |

Time format: ISO 8601 or relative (`-2h`, `-30m`, `now`).

---

## Using dtctl as a Data Source

`dtctl` is the kubectl-style CLI for Dynatrace. Use it with `subprocess.run` (list form only):

```python
import subprocess
import json
from pathlib import Path

def run_dtctl(args: list[str]) -> str:
    """Run a dtctl command and return stdout. Raises on failure."""
    result = subprocess.run(
        ["dtctl"] + args,
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    return result.stdout

# Example: list services in a namespace
def list_services(namespace: str) -> list[dict]:
    output = run_dtctl(["get", "services", "-n", namespace, "-o", "json"])
    return json.loads(output)
```

**Safety rules for dtctl usage:**
- Always use list form: `["dtctl", "get", ...]` — never `shell=True`
- Validate `namespace` and other user-provided args before passing to subprocess
- Never pass raw user strings directly into subprocess args without validation
- Use `timeout=60` to prevent hangs

**Validation example:**
```python
import re

def validate_namespace(ns: str) -> str:
    if not re.match(r'^[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$', ns):
        raise ValueError(f"Invalid namespace: {ns!r}")
    return ns
```

---

## SPINE / Lima Service Patterns

When building MCP servers that interact with SPINE or Lima (licensing/billing) services:

### Internal API Calls

SPINE services expose REST APIs on internal cluster URLs. Use the same bearer token pattern but with internal base URLs from environment variables:

```python
LIMA_API_URL = os.environ.get("LIMA_API_URL")  # e.g., http://lima-bas-adapter.svc:8080

async def lima_get(path: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{LIMA_API_URL}/{path}",
            headers={"Authorization": f"Bearer {os.environ['LIMA_API_TOKEN']}"},
        )
        response.raise_for_status()
        return response.json()
```

### Kafka Event Context

If your MCP server needs to reflect on Kafka event flows (read-only, for diagnostics), use `dtctl` to query the relevant service's logs rather than connecting to Kafka directly from MCP tools.

---

## Java / Spring Boot Service Awareness

Most SPINE services are Java 8+ Spring Boot apps. When building diagnostic MCP tools:

- Health endpoints are typically `/actuator/health`
- Metrics at `/actuator/metrics` or via Dynatrace
- Logs available via `dtctl logs` or the DT API events endpoint
- Java heap dumps / thread dumps should never be triggered from MCP tools (destructive)

---

## DT Safety Checklist for Generated Code

Before finalising any MCP server code for a DT environment, verify:

- [ ] No API tokens, passwords, or secrets in source code
- [ ] All credentials read from environment variables
- [ ] No external URL references (CDN, public APIs, raw.githubusercontent.com)
- [ ] `subprocess` calls use list form — never `shell=True`
- [ ] User inputs validated before use in file paths or subprocess args
- [ ] `httpx` calls use `timeout=` to prevent hangs
- [ ] No `eval()`, `exec()`, or dynamic code execution
- [ ] No `rm -rf` or broad recursive deletions
- [ ] File writes go to explicitly specified directories, not `/tmp` by default
