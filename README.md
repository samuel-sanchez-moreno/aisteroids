# 🌟 Aisteroids

A collection of AI agent skills for software engineering workflows.

## Skills

| Skill | Description |
|-------|-------------|
| [dt-skill-creator](skills/dt-skill-creator/) | Create, test, and iterate on Dynatrace-safe skills with built-in security guardrails and eval pipeline |
| [service-health-check](skills/service-health-check/) | Kubernetes service health check via Dynatrace `dtctl` — pods, logs, problems, endpoints |

## Installation

### Claude Code / Copilot CLI

Add a skill to your project by copying the skill folder into `.claude/skills/` or `.github/skills/` in your repo:

```bash
# Clone the repo
git clone https://github.com/samuel-sanchez-moreno/aisteroids.git

# Copy a skill into your project
cp -r aisteroids/skills/service-health-check /path/to/your-project/.claude/skills/
# or for GitHub Copilot
cp -r aisteroids/skills/service-health-check /path/to/your-project/.github/skills/
```

Or add as a git submodule for automatic updates:

```bash
git submodule add https://github.com/samuel-sanchez-moreno/aisteroids.git .aisteroids
ln -s ../.aisteroids/skills/service-health-check .claude/skills/service-health-check
```

## Contributing

Have a useful skill? Open a PR! Each skill lives in its own folder under `skills/` with a `SKILL.md` file.

## License

Apache-2.0
