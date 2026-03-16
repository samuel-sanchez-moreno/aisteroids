# Aisteroids — Copilot Instructions

A collection of AI agent skills for software engineering workflows, primarily targeting the Dynatrace/SPINE ecosystem. Each skill is a self-contained `SKILL.md`-based instruction set that AI agents (Claude, Copilot CLI) load and execute.

## Build & Site Generation

```bash
# Install dependency (one-time)
pip3 install pyyaml

# Generate the GitHub Pages marketplace site from skills/*/SKILL.md
python3 scripts/generate_site.py
```

Output lands in `docs/`. The GitHub Actions workflow (`deploy.yml`) runs this on push to `main` and deploys to GitHub Pages.

## Repository Structure

```
skills/
  <skill-name>/
    SKILL.md          ← Required. YAML frontmatter + Markdown instructions
    agents/           ← Sub-agent prompt files (e.g., grader.md, analyzer.md)
    evals/            ← Test cases (evals.json)
    references/       ← Reference docs loaded into context on demand
    scripts/          ← Python scripts bundled with the skill
docs/                 ← Generated static site (do not edit manually)
scripts/
  generate_site.py    ← Site generator (reads SKILL.md frontmatter)
```

## Skill Conventions

### SKILL.md structure

Every skill **must** have YAML frontmatter with `name` and `description`:

```markdown
---
name: my-skill-name          # kebab-case
description: >
  When to trigger and what it does. Written to combat undertriggering —
  be slightly "pushy" and include example trigger phrases.
---

# Skill Title
...markdown instructions...
```

The frontmatter `description` is what AI agents use to decide whether to load the skill. Make it explicit about trigger phrases.

### Progressive disclosure

Skills use a three-level loading model:
1. **Frontmatter** (`name` + `description`) — always in context
2. **SKILL.md body** — loaded when skill triggers; keep under 500 lines
3. **Bundled resources** (`references/`, `scripts/`, `agents/`) — loaded or executed as needed; reference them explicitly from SKILL.md with guidance on when to use them

If SKILL.md approaches 500 lines, refactor into `references/` files with clear pointers from the main file.

### Naming and layout

- Skills: `kebab-case` directory names under `skills/`
- Reference files: descriptive names, include a table of contents if over 300 lines
- Domain-split skills: put per-domain guides in `references/` (e.g., `aws.md`, `gcp.md`)

## dt-skill-creator Eval Pipeline

The `dt-skill-creator` skill has its own Python tooling under `skills/dt-skill-creator/scripts/`:

```bash
# Safety audit — run after every write/revision; this is a gate
python -m scripts.quick_validate <path-to-skill>

# Aggregate benchmark results for an iteration
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>

# Description optimization loop
python -m scripts.run_loop \
  --eval-set <trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id> \
  --max-iterations 5
```

Eval results go in `<skill-name>-workspace/iteration-<N>/eval-<ID>/` as a sibling to the skill directory.

## Safety Rules (enforced for all skills)

Skills run with the user's full OS permissions. These rules are non-negotiable:

- **No external URLs** — no CDN links, no `curl`/`wget` to external hosts; use system fonts and bundled resources
- **No dangerous shell patterns** — no `rm -rf /`, no `eval()`/`exec()` with user input, no `shell=True` in subprocess calls, no `pkill`/`killall` (use specific PIDs), no base64-encoded payloads
- **No data exfiltration** — no sending local data to external services, no reverse shells
- **Safe subprocess**: always use list form — `subprocess.run(["cmd", "arg"], check=True)`
- **Safe file paths**: use `pathlib.Path`, never string concatenation

## Commit Message Format

Commits are validated on push against this pattern:

```
type(scope): description

[optional body]

Refs: NOISSUE   # or LIMA-1234, comma-separated
```

Valid types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `style`, `test`  
Scope is optional, lowercase. The `Refs:` line must be **last** — nothing after it.

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`)
2. Run `python scripts/generate_site.py` to verify it appears in the generated site
3. Add `references/`, `agents/`, `scripts/`, or `evals/` subdirectories as needed
4. If the skill bundles scripts, run the safety validator: `python -m scripts.quick_validate skills/<skill-name>`
