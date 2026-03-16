---
name: mcp-builder
description: >
  Guide for creating high-quality MCP (Model Context Protocol) servers that let AI agents interact with
  internal services through well-designed tools. Use when building MCP servers to integrate internal APIs
  or services (Dynatrace, SPINE, Lima, or any service), in Python (FastMCP) or TypeScript (MCP SDK).
  Triggers include: "build an MCP server", "create MCP tools for X", "integrate X with Claude via MCP",
  "add MCP support for the Y API", or "help me write an MCP server".
---

# MCP Server Builder

Build production-quality MCP (Model Context Protocol) servers that enable AI agents to interact with
internal services through well-designed tools.

## How to use this skill

Follow the 4-phase workflow below. Start at Phase 1 — but if the user already has a draft, pick up where they are.

Reference files (load as needed):
- [`references/mcp-best-practices.md`](references/mcp-best-practices.md) — naming, response formats, pagination, transport, annotations
- [`references/python-guide.md`](references/python-guide.md) — Python/FastMCP implementation guide + examples
- [`references/typescript-guide.md`](references/typescript-guide.md) — TypeScript SDK guide + examples
- [`references/dt-integrations.md`](references/dt-integrations.md) — DT API auth, dtctl, SPINE/Lima patterns

---

## Safety Rules

Every MCP server produced by this skill must comply with these rules.

### No secrets in code
- All API tokens, passwords, and credentials must come from environment variables
- Validate required env vars at startup and fail clearly if they're missing

### No external URL dependencies in the server code
- API base URLs come from environment variables — never hard-coded
- No CDN links, no external package fetches at runtime

### Safe subprocess usage
- Use list form: `subprocess.run(["dtctl", "get", ...], check=True)` — never `shell=True`
- Validate user-supplied values before passing to subprocess args
- Always set `timeout=` to prevent hangs

### Safe file operations
- Use `pathlib.Path` for file paths — no string concatenation
- Write to explicitly specified output directories, not arbitrary locations
- Never `rm -rf` or broad recursive deletes

### Input validation
- Use Pydantic v2 (Python) or Zod with `.strict()` (TypeScript) for all tool inputs
- Validate external identifiers before using in queries or commands

---

## Phase 1: Research and Planning

### 1.1 Understand the target API

Before writing any code, gather:
- What API endpoints exist, and what authentication do they require?
- What are the most common operations a user (or AI agent) would want to perform?
- Are there rate limits, pagination patterns, or quota constraints?
- What's the base URL pattern, and does it vary per environment?

For **DT/SPINE services**, read [`references/dt-integrations.md`](references/dt-integrations.md) for API auth patterns, dtctl usage, and environment variable conventions.

### 1.2 Choose language and transport

**Recommended: TypeScript**
- Broad ecosystem support, great IDE tooling, static typing catches bugs early
- Use for: remote servers, multi-client scenarios, services that benefit from deployment flexibility

**Python** is a solid alternative:
- Use for: local integrations, scripting-heavy workflows, teams more comfortable with Python

**Transport**:
- **stdio** — local tools, single-user, no network config (most common for developer tools)
- **Streamable HTTP** — multi-client, remote deployment. If running locally: bind to `127.0.0.1`, validate `Origin` header

Load the relevant guide:
- TypeScript: [`references/typescript-guide.md`](references/typescript-guide.md)
- Python: [`references/python-guide.md`](references/python-guide.md)

### 1.3 Plan your tools

List the API operations you'll expose. Prioritise comprehensive coverage over narrow workflow tools:
- Read operations first: list, get, search
- Write operations second: create, update, delete
- Workflow shortcuts last (convenience tools that combine multiple operations)

Name tools with service prefix + action + resource:
`{service}_{action}_{resource}` → `jira_list_issues`, `dt_get_problem`, `slack_send_message`

---

## Phase 2: Implementation

### 2.1 Project setup

**TypeScript**:
```
service-mcp-server/
├── package.json        (type: module, build: tsc, start: node dist/index.js)
├── tsconfig.json       (target ES2022, strict: true)
└── src/
    ├── index.ts        (McpServer init + transport)
    ├── constants.ts    (API_BASE_URL, CHARACTER_LIMIT)
    ├── tools/
    └── services/
```

**Python**:
```
service_mcp/
├── server.py           (FastMCP init + tool registration)
├── tools/
├── services/
└── requirements.txt
```

### 2.2 Core infrastructure first

Before tools, implement:
1. **Environment validation** — check all required env vars at startup; fail loudly if missing
2. **API client** — authenticated HTTP helper (`api_get`, `api_post`) with timeout
3. **Error handler** — translate HTTP status codes to actionable messages

See language guides for copy-paste patterns.

### 2.3 Implement tools

For each tool:

1. **Define the input schema** (Pydantic model or Zod object) with field descriptions and constraints
2. **Add annotations**: `readOnlyHint`, `destructiveHint`, `idempotentHint`
3. **Write the handler**: call API client → format response → handle errors
4. **Support both formats**: `json` (machine-readable) and `markdown` (default, human-readable)
5. **Paginate list tools**: return `total`, `count`, `offset`, `has_more`, `next_offset`

Keep tool docstrings/descriptions explicit — include what the tool does, when to use it, when NOT to use it, and return schema.

---

## Phase 3: Review and Test

### 3.1 Code quality review

- No duplicated HTTP logic — use shared API client
- Consistent error handling across all tools
- Type coverage (TypeScript strict / Pydantic models)
- Tool descriptions match actual behaviour

### 3.2 Build

**TypeScript**: `npm run build` — fix all TypeScript errors before testing.

**Python**: `python -m py_compile server.py` — catches syntax errors.

### 3.3 Test with MCP Inspector

```bash
# TypeScript
npx @modelcontextprotocol/inspector node dist/index.js

# Python
npx @modelcontextprotocol/inspector python server.py
```

Walk through each tool manually:
- Happy path with valid inputs
- Edge cases: empty results, resource not found, pagination
- Error cases: missing required field, invalid ID format

### 3.4 DT safety review

Run the checklist in [`references/dt-integrations.md`](references/dt-integrations.md) (DT Safety Checklist section).

---

## Phase 4: Create Evaluations

After the MCP server is working, create 5–10 evaluation questions to verify an AI agent can use it effectively.

### Good eval questions are:
- **Complex** — require multiple tool calls to answer
- **Read-only** — only non-destructive operations
- **Verifiable** — single clear answer (a number, a name, a status)
- **Realistic** — based on real use cases
- **Stable** — answer won't change over time (or is pinned to a snapshot)

### Format

```xml
<evaluation>
  <qa_pair>
    <question>How many open P1 problems are currently active in the production environment?</question>
    <answer>3</answer>
  </qa_pair>
  <qa_pair>
    <question>What is the average response time (p50) of the checkout service over the last 2 hours?</question>
    <answer>142ms</answer>
  </qa_pair>
</evaluation>
```

Save as `evals.xml` alongside your MCP server.

### Process
1. List your tools and understand their capabilities
2. Use read-only operations to explore available data
3. Draft 5–10 questions; verify each answer yourself by calling the tools
4. Review the set: are questions diverse? Do they exercise different tools?

---

## Finishing up

Once the server is working and evals are passing:

1. Write a `README.md` documenting all tools, required env vars, and setup steps
2. Add at least 2 usage examples per tool
3. Optionally: package as a Docker container or npm package for easy distribution

---

## Quick-start checklist

- [ ] Required env vars validated at startup
- [ ] API client with timeout and auth helper
- [ ] All inputs validated (Pydantic/Zod)
- [ ] All tools have annotations
- [ ] Both `json` and `markdown` output formats
- [ ] Pagination for all list tools
- [ ] Helpful error messages
- [ ] TypeScript builds clean / Python syntax checks pass
- [ ] Tested with MCP Inspector
- [ ] DT safety checklist passed
- [ ] Evals written and verified
