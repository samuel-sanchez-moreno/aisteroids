# MCP Server Best Practices

## Quick Reference

| Concern | Rule |
|---|---|
| Python server name | `{service}_mcp` (e.g., `slack_mcp`) |
| TypeScript server name | `{service}-mcp-server` (e.g., `slack-mcp-server`) |
| Tool names | `snake_case` with service prefix: `github_create_issue` |
| Response formats | Support both `json` and `markdown` |
| Pagination default | 20–50 items; always return `has_more`, `next_offset` |
| Transport | stdio for local; Streamable HTTP for remote/multi-client |

---

## Server Naming Conventions

**Python**: `{service}_mcp` — e.g., `slack_mcp`, `jira_mcp`, `dynatrace_mcp`
**TypeScript**: `{service}-mcp-server` — e.g., `slack-mcp-server`, `jira-mcp-server`

The name should be:
- General — not tied to specific features
- Descriptive of the service being integrated
- Without version numbers or dates

---

## Tool Naming and Design

### Naming rules
- `snake_case`: `search_users`, `create_project`, `get_channel_info`
- Always include service prefix to avoid conflicts with other MCP servers:
  - ✅ `slack_send_message` not `send_message`
  - ✅ `github_create_issue` not `create_issue`
- Action-oriented verbs: `get`, `list`, `search`, `create`, `update`, `delete`

### Tool design
- Tool descriptions must narrowly and unambiguously describe functionality
- Keep tools focused and atomic
- Always provide tool annotations (see below)

---

## Response Formats

All data-returning tools should support two formats via a `response_format` parameter:

**`json`** — Machine-readable structured data
- Include all available fields and metadata
- Consistent field names and types
- Use for programmatic processing

**`markdown`** (default) — Human-readable formatted text
- Use headers, lists, bold for clarity
- Convert timestamps to human-readable (`2024-01-15 10:30 UTC` not epoch)
- Show display names with IDs in parentheses: `John Doe (U123456)`
- Omit verbose metadata

---

## Pagination

For tools that list resources:

```python
# Always include these fields in responses
{
    "total": 150,        # Total number of matches
    "count": 20,         # Items in this response
    "offset": 0,         # Current offset
    "items": [...],      # The items
    "has_more": true,    # Whether more results exist
    "next_offset": 20    # Offset to pass for the next page
}
```

- Default limit: 20–50 items
- Always respect the `limit` parameter; never load all results into memory
- Use `offset`-based or cursor-based pagination consistently

---

## Transport Options

### stdio
- **Use for**: local integrations, command-line tools, single-user scenarios
- Runs as a subprocess of the client
- Simple setup, no network config needed
- **Do NOT log to stdout** — use stderr for logging

### Streamable HTTP
- **Use for**: remote servers, multi-client scenarios, cloud deployments
- Supports multiple simultaneous clients
- For local Streamable HTTP: bind to `127.0.0.1`, validate `Origin` header (DNS rebinding protection)

---

## Tool Annotations

Provide annotations to help clients understand tool behavior:

| Annotation | Type | Default | Meaning |
|---|---|---|---|
| `readOnlyHint` | bool | false | Does not modify environment |
| `destructiveHint` | bool | true | May perform destructive updates |
| `idempotentHint` | bool | false | Repeated calls with same args = no extra effect |
| `openWorldHint` | bool | true | Interacts with external entities |

Annotations are hints, not security guarantees.

---

## Security Best Practices

### Authentication
- Store API keys in environment variables, never in code
- Validate keys on server startup with a clear error if missing
- Use OAuth 2.1 with proper token validation when applicable

### Input Validation
- Use Pydantic (Python) or Zod (TypeScript) for all inputs — validate before use
- Sanitize file paths to prevent directory traversal
- Validate external identifiers before using in queries
- Check parameter sizes and ranges

### Command Safety
- Never use `os.system()` or `subprocess.run("...", shell=True)` with user input
- Use `subprocess.run([...], check=True)` (list form)
- Validate all inputs before using in file paths or commands

### Error Handling
- Do not expose internal errors or stack traces to clients
- Provide helpful, actionable error messages with suggested next steps
- Log security-relevant errors server-side
- Clean up resources after errors

---

## Error Message Patterns

Good error messages guide agents toward a solution:

```
Error: Resource not found. Check the ID is correct and the resource exists.
Error: Permission denied. Your token may lack the required scope: read:users.
Error: Rate limit exceeded. Wait 60 seconds before retrying.
Error: Request timed out after 30s. The service may be unavailable.
```

---

## Testing Requirements

- **Functional**: Valid and invalid inputs
- **Integration**: Real API interaction (use a test account or sandbox)
- **Security**: Auth validation, input sanitization
- **Error handling**: Confirm graceful failures, no internal leakage

---

## Documentation Requirements

Every MCP server should document:
- All tools with input/output schemas and at least 2 examples per tool
- Required environment variables and their purpose
- Authentication setup instructions
- Rate limits and performance characteristics
