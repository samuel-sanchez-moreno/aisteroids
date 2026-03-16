# TypeScript MCP Server Implementation Guide

## Quick Reference

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
```

**Server init**: `new McpServer({ name: "service-mcp-server", version: "1.0.0" })`  
**Register tool**: `server.registerTool("tool_name", { title, description, inputSchema }, handler)`  
**IMPORTANT**: Use `registerTool` — do NOT use old `server.tool()` or `setRequestHandler`

---

## Installation

```bash
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node ts-node
```

---

## Server Naming

Format: `{service}-mcp-server` — e.g., `github-mcp-server`, `dynatrace-mcp-server`

---

## Project Structure

```
service-mcp-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts          # McpServer init + transport
│   ├── constants.ts      # API_URL, CHARACTER_LIMIT, etc.
│   ├── tools/            # One file per domain
│   ├── services/         # API clients
│   └── schemas/          # Shared Zod schemas
└── dist/                 # Build output
```

**tsconfig.json** (minimum):
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "node",
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src"]
}
```

**package.json** scripts:
```json
{
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "type": "module"
}
```

---

## Tool Registration Pattern

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({ name: "example-mcp-server", version: "1.0.0" });

const SearchInputSchema = z.object({
  query: z.string().min(1).max(200).describe("Search string"),
  limit: z.number().int().min(1).max(100).default(20).describe("Max results"),
  offset: z.number().int().min(0).default(0).describe("Pagination offset"),
  response_format: z.enum(["markdown", "json"]).default("markdown")
    .describe("Output format")
}).strict();

server.registerTool(
  "example_search_items",
  {
    title: "Search Items",
    description: `Search for items matching a query string.

Args:
  - query: Search string (1–200 chars)
  - limit: Max results to return (1–100, default 20)
  - offset: Pagination offset (default 0)
  - response_format: 'markdown' or 'json' (default 'markdown')

Returns:
  Matching items with pagination metadata.

Examples:
  - "find items named foo" → query="foo"
  - "get next page of results" → offset=20`,
    inputSchema: SearchInputSchema,
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false
    }
  },
  async (params) => {
    try {
      const data = await apiGet("items/search", { q: params.query, limit: String(params.limit), offset: String(params.offset) });
      const items = (data as any).items ?? [];
      const total = (data as any).total ?? 0;

      if (!items.length) {
        return { content: [{ type: "text", text: `No items found matching '${params.query}'` }] };
      }

      const output = {
        total, count: items.length, offset: params.offset, items,
        has_more: total > params.offset + items.length,
        ...(total > params.offset + items.length ? { next_offset: params.offset + items.length } : {})
      };

      const text = params.response_format === "json"
        ? JSON.stringify(output, null, 2)
        : formatMarkdown(params.query, items, total);

      return { content: [{ type: "text", text }], structuredContent: output };
    } catch (e) {
      return { content: [{ type: "text", text: handleApiError(e) }] };
    }
  }
);
```

---

## Zod Schema Patterns

```typescript
import { z } from "zod";

// Basic schema
const CreateUserSchema = z.object({
  name: z.string().min(1).max(100).describe("User's full name"),
  email: z.string().email().describe("Email address"),
  age: z.number().int().min(0).max(150).describe("Age")
}).strict();  // .strict() forbids extra fields

// Enum
const FormatSchema = z.object({
  response_format: z.enum(["markdown", "json"]).default("markdown")
});

// Pagination
const PaginationSchema = z.object({
  limit: z.number().int().min(1).max(100).default(20),
  offset: z.number().int().min(0).default(0)
});

// Derive TypeScript type from schema
type CreateUserInput = z.infer<typeof CreateUserSchema>;
```

---

## API Client Pattern

```typescript
const API_BASE_URL = process.env.API_BASE_URL ?? "";
const API_TOKEN = process.env.API_TOKEN ?? "";
const CHARACTER_LIMIT = 25_000;

async function apiGet(path: string, params?: Record<string, string>): Promise<unknown> {
  const url = new URL(`${API_BASE_URL}/${path}`);
  if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  const res = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${API_TOKEN}` },
    signal: AbortSignal.timeout(30_000)
  });
  if (!res.ok) throw new ApiError(res.status, await res.text());
  return res.json();
}

async function apiPost(path: string, body: unknown): Promise<unknown> {
  const res = await fetch(`${API_BASE_URL}/${path}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${API_TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(30_000)
  });
  if (!res.ok) throw new ApiError(res.status, await res.text());
  return res.json();
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}
```

---

## Error Handling

```typescript
function handleApiError(e: unknown): string {
  if (e instanceof ApiError) {
    if (e.status === 404) return "Error: Resource not found. Check the ID is correct.";
    if (e.status === 403) return "Error: Permission denied. Your token may lack required scope.";
    if (e.status === 429) return "Error: Rate limit exceeded. Wait before retrying.";
    return `Error: API request failed with status ${e.status}.`;
  }
  if (e instanceof Error && e.name === "TimeoutError") {
    return "Error: Request timed out. The service may be unavailable.";
  }
  return `Error: ${e instanceof Error ? e.message : String(e)}`;
}
```

---

## Startup Validation

```typescript
function requireEnv(...names: string[]): void {
  const missing = names.filter(n => !process.env[n]);
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(", ")}`);
  }
}

requireEnv("API_BASE_URL", "API_TOKEN");
```

---

## Server Entry Point (stdio)

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new McpServer({ name: "example-mcp-server", version: "1.0.0" });

// Register tools here...

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // Use process.stderr for logging — never process.stdout in stdio mode
  process.stderr.write("example-mcp-server running\n");
}

main().catch(e => {
  process.stderr.write(`Fatal error: ${e}\n`);
  process.exit(1);
});
```

---

## Character Limit / Truncation

```typescript
import { CHARACTER_LIMIT } from "./constants.js";

function truncate(text: string): string {
  if (text.length <= CHARACTER_LIMIT) return text;
  return text.slice(0, CHARACTER_LIMIT) + "\n\n[Response truncated]";
}
```

---

## Quality Checklist

- [ ] All inputs validated with Zod `.strict()` schemas
- [ ] `server.registerTool()` used — not deprecated `server.tool()`
- [ ] All tools have `annotations` including `readOnlyHint`/`destructiveHint`
- [ ] `AbortSignal.timeout(30_000)` on all fetch calls
- [ ] No secrets in code — all credentials from `process.env`
- [ ] `requireEnv()` called at startup
- [ ] Error handler returns helpful messages without stack traces
- [ ] Pagination metadata in all list responses
- [ ] Both `json` and `markdown` response formats supported
- [ ] TypeScript strict mode enabled
- [ ] `process.stdout` not used for logging in stdio mode (use `process.stderr`)
