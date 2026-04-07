# 🌟 Aisteroids

A collection of AI agent skills for software engineering workflows.

## Skills

| Skill | Description |
|-------|-------------|
| [dt-presentation-builder](skills/dt-presentation-builder/) | Transform markdown, notes, and data into polished Dynatrace-branded HTML slide decks and reports — no build step, no dependencies |
| [dt-skill-creator](skills/dt-skill-creator/) | Create, test, and iterate on Dynatrace-safe skills with built-in security guardrails and eval pipeline |
| [dt-mcp-builder](skills/dt-mcp-builder/) | Build production-quality MCP servers for internal services — Python (FastMCP) or TypeScript, with DT API/dtctl patterns |
| [dt-service-health-check](skills/dt-service-health-check/) | Kubernetes service health check via Dynatrace `dtctl` — pods, logs, problems, endpoints |
| [dt-story-refiner](skills/dt-story-refiner/) | PO story reviewer — checks drafts for completeness, DoR compliance, and quality |
| [dt-story-writer](skills/dt-story-writer/) | PO story writer — generates business, tech debt, and research stories from requirements |
| [lima-pr-reviewer](skills/lima-pr-reviewer/) | Expert code reviewer for Team LiCoCo services (entitlement-service, lima-bas-adapter, lima-tenant-config, BAS) — parallel sub-agent review with repo-specific checklists |

## Installation

### Claude Code / Copilot CLI

Add a skill to your project by copying the skill folder into `.claude/skills/` or `.github/skills/` in your repo:

```bash
# Clone the repo
git clone https://github.com/samuel-sanchez-moreno/aisteroids.git

# Copy a skill into your project
cp -r aisteroids/skills/dt-presentation-builder /path/to/your-project/.claude/skills/
# or for GitHub Copilot
cp -r aisteroids/skills/dt-presentation-builder /path/to/your-project/.github/skills/
```

Or add as a git submodule for automatic updates:

```bash
git submodule add https://github.com/samuel-sanchez-moreno/aisteroids.git .aisteroids
ln -s ../.aisteroids/skills/dt-presentation-builder .claude/skills/dt-presentation-builder
```

For OpenCode, skills live in `~/.config/opencode/skills/`:

```bash
cp -r aisteroids/skills/dt-presentation-builder ~/.config/opencode/skills/
```

## Using dt-presentation-builder

Transforms raw markdown, meeting notes, and data into self-contained Dynatrace-branded HTML
presentations — keyboard-navigable slide decks or scrollable reports — following the Strato
design system. Opens directly in any browser; no build step, no server, no dependencies beyond
Google Fonts.

### Trigger phrases

Say any of these to activate the skill:

- `"build a presentation about X"`
- `"create slides for Y"`
- `"HTML slide deck — here are my notes"`
- `"executive briefing on Z"`
- `"status update deck"`
- `"convert this report to slides"`
- `"Dynatrace presentation"`

### What to provide

| Input | Notes |
|-------|-------|
| Source content | Markdown file, pasted notes, bullet points, raw data — anything works |
| Audience | Name who's in the room: exec, engineering team, customer ops, sales |
| Mode (optional) | **Mode A** (slide deck, default) or **Mode B** (scrollable report/runbook) |
| Topic label | Used for the output filename and folder |

### Output

The skill writes a single self-contained `.html` file to `presentations/<topic>/`:

```
presentations/
  my-topic/
    2026-04-07-my-topic-slides.html   ← Mode A deck
    2026-04-07-my-topic.html          ← Mode B report
```

Open it with:

```bash
open presentations/my-topic/2026-04-07-my-topic-slides.html
```

### Output modes

**Mode A — Slide Deck (default)**

Full-viewport, keyboard-navigable deck. Arrow keys / Space to advance, progress dots,
URL hash addressing (`#0`…`#N`), touch swipe, print-to-PDF.

Best for: sprint reviews, executive briefings, customer onboarding, status updates.

**Mode B — Scrollable Page**

Scrollable single-page document with sticky header, IntersectionObserver entrance animations,
and a `prefers-reduced-motion` / no-JS fallback.

Best for: engineering reports, architecture analyses, dashboards, operational runbooks.

### Page frameworks

| Framework | Slides | Best for |
|-----------|--------|----------|
| Executive Brief | 5–8 | Leadership reviews, budget approvals |
| Technical Deep-Dive | 10–20 | Engineering teams, architecture reviews |
| Customer Onboarding | 8–12 | Platform handover to customer ops |
| Project Retro | 6–10 | Team review, lessons learned |

### strato-docs-mcp integration

When the `strato-docs-mcp` MCP server is available in your environment, the skill
automatically queries it for live Strato component props and usage examples before
generating any HTML. No configuration needed — the skill probes availability at the
start of every session and falls back to the bundled `references/design-system.md`
if the server is not reachable.

To get the most accurate Strato component output, install and configure `strato-docs-mcp`
in your agent environment.

### Example session

```
User:  Build a presentation. Audience: engineering team. Topic: our new event-bus
       architecture. Here are my notes: [paste markdown]

Agent: [calls strato_list_components — MCP available]
       [calls strato_get_component_props for Chip, Container, SingleValue, ...]
       [selects Technical Deep-Dive framework, Mode A]
       [generates presentations/event-bus/2026-04-07-event-bus-slides.html]

User:  open presentations/event-bus/2026-04-07-event-bus-slides.html
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
