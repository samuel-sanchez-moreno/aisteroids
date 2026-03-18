# 🌟 Aisteroids

A collection of AI agent skills for software engineering workflows.

## Skills

| Skill | Description |
|-------|-------------|
| [dt-skill-creator](skills/dt-skill-creator/) | Create, test, and iterate on Dynatrace-safe skills with built-in security guardrails and eval pipeline |
| [dt-mcp-builder](skills/dt-mcp-builder/) | Build production-quality MCP servers for internal services — Python (FastMCP) or TypeScript, with DT API/dtctl patterns |
| [dt-service-health-check](skills/dt-service-health-check/) | Kubernetes service health check via Dynatrace `dtctl` — pods, logs, problems, endpoints |
| [dt-story-refiner](skills/dt-story-refiner/) | PO story reviewer — checks drafts for completeness, DoR compliance, and quality |
| [dt-story-writer](skills/dt-story-writer/) | PO story writer — generates business, tech debt, and research stories from requirements |

## Installation

### Claude Code / Copilot CLI

Add a skill to your project by copying the skill folder into `.claude/skills/` or `.github/skills/` in your repo:

```bash
# Clone the repo
git clone https://github.com/samuel-sanchez-moreno/aisteroids.git

# Copy a skill into your project
cp -r aisteroids/skills/dt-service-health-check /path/to/your-project/.claude/skills/
# or for GitHub Copilot
cp -r aisteroids/skills/dt-service-health-check /path/to/your-project/.github/skills/
```

Or add as a git submodule for automatic updates:

```bash
git submodule add https://github.com/samuel-sanchez-moreno/aisteroids.git .aisteroids
ln -s ../.aisteroids/skills/dt-service-health-check .claude/skills/dt-service-health-check
```

## Custom Commands

Slash commands for Claude Code that can be copied into your project's `.claude/commands/` folder:

| Command | Description |
|---------|-------------|
| [/verify](commands/verify.md) | Full quality gate — lint, checkstyle, unit tests, SonarQube, and integration tests in order |

```bash
# Copy a command into your project
cp aisteroids/commands/verify.md /path/to/your-project/.claude/commands/verify.md
```

## Contributing

Have a useful skill? Open a PR! Each skill lives in its own folder under `skills/` with a `SKILL.md` file.

## License

Apache-2.0
