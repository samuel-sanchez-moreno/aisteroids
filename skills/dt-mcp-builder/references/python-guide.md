# Python MCP Server Implementation Guide

## Quick Reference

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from enum import Enum
import httpx
import json
import os
```

**Server init**: `mcp = FastMCP("service_mcp")`  
**Tool registration**: `@mcp.tool(name="tool_name", annotations={...})`  
**Run**: `mcp.run()` (stdio) or `mcp.run(transport="streamable-http", port=8080)`

---

## Installation

```bash
pip install mcp httpx pydantic
```

---

## Server Naming

Format: `{service}_mcp` — e.g., `github_mcp`, `jira_mcp`, `dynatrace_mcp`

---

## Project Structure

```
service_mcp/
├── server.py          # Main entry — FastMCP init + tool registration
├── tools/             # One file per domain (users.py, projects.py, etc.)
├── services/          # API client utilities
└── requirements.txt
```

---

## Tool Structure with FastMCP

```python
from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("example_mcp")

class SearchInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    query: str = Field(..., description="Search string", min_length=1, max_length=200)
    limit: Optional[int] = Field(default=20, description="Max results (1–100)", ge=1, le=100)
    offset: Optional[int] = Field(default=0, description="Pagination offset", ge=0)
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="'markdown' for human-readable, 'json' for machine-readable"
    )

@mcp.tool(
    name="example_search_items",
    annotations={
        "title": "Search Items",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def example_search_items(params: SearchInput) -> str:
    """Search for items matching a query string.

    Args:
        params: Validated input with query, limit, offset, response_format.

    Returns:
        JSON or Markdown string with matching items and pagination info.
    """
    try:
        data = await api_get("items/search", {"q": params.query, "limit": params.limit, "offset": params.offset})
        items = data.get("items", [])
        total = data.get("total", 0)

        if not items:
            return f"No items found matching '{params.query}'"

        result = {
            "total": total, "count": len(items), "offset": params.offset,
            "items": items,
            "has_more": total > params.offset + len(items),
        }
        if result["has_more"]:
            result["next_offset"] = params.offset + len(items)

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(result, indent=2)

        lines = [f"# Search: '{params.query}'", f"Found {total} items", ""]
        for item in items:
            lines.append(f"## {item.get('name', item.get('id'))}")
            lines.append(f"- ID: `{item['id']}`")
        return "\n".join(lines)

    except Exception as e:
        return _handle_error(e)
```

---

## Pydantic v2 Key Patterns

```python
from pydantic import BaseModel, Field, field_validator, ConfigDict

class CreateUserInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$', description="Email address")

    @field_validator('email')
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()
```

- Use `model_config` (not nested `Config` class)
- Use `field_validator` (not deprecated `validator`)
- Use `model_dump()` (not deprecated `.dict()`)
- `extra='forbid'` prevents unexpected fields

---

## Response Format Pattern

```python
from enum import Enum

class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
```

---

## Pagination Pattern

```python
async def list_items(limit: int = 20, offset: int = 0) -> str:
    data = await api_get("items", {"limit": limit, "offset": offset})
    total = data["total"]
    items = data["items"]
    result = {
        "total": total,
        "count": len(items),
        "offset": offset,
        "items": items,
        "has_more": total > offset + len(items),
    }
    if result["has_more"]:
        result["next_offset"] = offset + len(items)
    return json.dumps(result, indent=2)
```

---

## API Client Pattern

```python
API_BASE_URL = os.environ.get("API_BASE_URL", "")
API_TOKEN = os.environ.get("API_TOKEN", "")

async def api_get(path: str, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{API_BASE_URL}/{path}",
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            params=params or {},
        )
        response.raise_for_status()
        return response.json()

async def api_post(path: str, body: dict) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/{path}",
            headers={"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"},
            json=body,
        )
        response.raise_for_status()
        return response.json()
```

---

## Error Handling

```python
def _handle_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        code = e.response.status_code
        if code == 404:
            return "Error: Resource not found. Check the ID is correct."
        if code == 403:
            return "Error: Permission denied. Your token may lack required scope."
        if code == 429:
            return "Error: Rate limit exceeded. Wait before retrying."
        return f"Error: API request failed with status {code}."
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. The service may be unavailable."
    return f"Error: {type(e).__name__}: {e}"
```

---

## Startup Validation

```python
import os

def _require_env(*names: str) -> None:
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

# Call at module level before mcp.run()
_require_env("API_BASE_URL", "API_TOKEN")
```

---

## Async Best Practices

```python
# Good: async with httpx
async def fetch(url: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()

# Bad: synchronous requests (blocks event loop)
# import requests
# def fetch(url): return requests.get(url).json()  ← don't do this
```

---

## Running the Server

```python
if __name__ == "__main__":
    mcp.run()  # stdio (default)
    # or for Streamable HTTP:
    # mcp.run(transport="streamable-http", host="127.0.0.1", port=8080)
```

---

## Quality Checklist

- [ ] All inputs validated with Pydantic models
- [ ] All tools have `annotations` with `readOnlyHint`/`destructiveHint`
- [ ] All async network calls use `httpx.AsyncClient` with `timeout=`
- [ ] No `requests` (sync) — only `httpx` (async)
- [ ] No secrets in code — all credentials from `os.environ`
- [ ] Error handler returns helpful messages without internal details
- [ ] Pagination metadata in all list responses
- [ ] Both `json` and `markdown` response formats supported
