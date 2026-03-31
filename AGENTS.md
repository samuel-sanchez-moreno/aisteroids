# Aisteroids — Agent Context

A collection of AI agent skills for software engineering workflows, primarily targeting the
Dynatrace/SPINE ecosystem. Each skill is a self-contained `SKILL.md`-based instruction set
that AI agents (Claude, Copilot CLI) load and execute.

## Build & Site Generation

```bash
# Install dependency (one-time)
pip3 install pyyaml

# Generate the GitHub Pages marketplace site from skills/*/SKILL.md
python3 scripts/generate_site.py
```

Output lands in `docs/`. The GitHub Actions workflow (`.github/workflows/deploy.yml`) runs
this on every push to `main` and deploys to GitHub Pages. **Never edit `docs/` manually.**

## Validation & "Testing"

There is no traditional test framework. Quality gates are:

```bash
# Structural safety audit — run after every write/revision of a skill; treat as a gate
# Must be run from the repo root (uses Python module syntax)
python -m scripts.quick_validate skills/<skill-name>

# Run description-trigger optimization loop (functional eval)
python -m scripts.run_loop \
  --eval-set skills/dt-skill-creator/evals/evals.json \
  --skill-path skills/<skill-name> \
  --model <model-id> \
  --max-iterations 5

# Aggregate benchmark results for one iteration
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

To validate a single skill structurally (closest to a "single unit test"):
```bash
python -m scripts.quick_validate skills/<skill-name>
```

Eval results land in `<skill-name>-workspace/iteration-<N>/eval-<ID>/` as a sibling to the
`skills/` directory.

## Repository Structure

```
skills/
  <skill-name>/
    SKILL.md          ← Required. YAML frontmatter + Markdown instructions
    agents/           ← Sub-agent prompt files (e.g., grader.md, analyzer.md)
    evals/            ← Test cases (evals.json)
    references/       ← Reference docs loaded into context on demand
    scripts/          ← Python scripts bundled with the skill
commands/
  <command-name>.md   ← Slash commands available to agents
docs/                 ← Generated static site (do not edit manually)
scripts/
  generate_site.py    ← Site generator (reads SKILL.md frontmatter)
.github/
  copilot-instructions.md  ← Copilot-specific agent instructions (kept in sync with this file)
  workflows/
    deploy.yml        ← CI: generate site + deploy to Pages
```

## README Policy

The `README.md` must stay current. Whenever you add, remove, or rename a skill, agent
sub-prompt, slash command (`commands/`), plugin, or bundled script, **update `README.md`** to
reflect the change. The README is the human-facing index; keep it accurate.

## Skill Conventions

### SKILL.md structure

Every skill **must** have YAML frontmatter with `name` and `description`:

```markdown
---
name: my-skill-name          # kebab-case, matches directory name
description: >
  When to trigger and what it does. Written to combat undertriggering —
  be slightly "pushy" and include example trigger phrases.
---

# Skill Title
...markdown instructions...
```

The frontmatter `description` is the routing key: agents decide whether to load the skill
based on it. Be explicit about trigger phrases. Explain the *why* behind instructions —
agents respond better to understanding than to rigid MUSTs.

### Progressive disclosure (three-level loading)

1. **Frontmatter** (`name` + `description`) — always in context; keep under ~100 words
2. **SKILL.md body** — loaded when skill triggers; keep **under 500 lines**
3. **Bundled resources** (`references/`, `scripts/`, `agents/`) — loaded or executed only
   when the body explicitly directs the agent to use them

If `SKILL.md` approaches 500 lines, extract content into `references/` files and add a
pointer from the main file saying when to load each one.

### Naming and layout

- Skill directories: `kebab-case` (enforced by `quick_validate.py` regex `^[a-z0-9-]+$`)
- Reference files: descriptive names; add a table of contents if over 300 lines
- Domain-split skills: isolate per-domain knowledge in `references/` (e.g., `repo-bas.md`)
- Sub-agent prompts: `agents/<role>.md` (e.g., `grader.md`, `comparator.md`, `analyzer.md`)

## Python Code Style (scripts/)

All Python in this repo targets **Python 3.10+**. Follow these conventions:

**Naming**
- Functions and variables: `snake_case`
- Constants: `SCREAMING_SNAKE_CASE`
- No class hierarchies unless genuinely needed; prefer module-level functions

**Types**
- Use modern union syntax: `str | None`, `dict | None` (not `Optional[str]`)
- Use built-in generics: `list[dict]`, `tuple[str, str]` (not `List`, `Tuple` from `typing`)
- Annotate all public function signatures (parameters and return types)

**Imports**
- Standard library first (alphabetical), then third-party (`anthropic`, `yaml`), then local
- No wildcard imports

**Error handling**
- Prefer returning `(bool, str)` tuples for validation results over raising exceptions
- Catch specific exceptions (`json.JSONDecodeError`, `OSError`); avoid bare `except:`
- Use `sys.exit(1)` for CLI failure exits
- Pass `errors='replace'` to `read_text()` to handle encoding edge cases

**File I/O**
- Use `pathlib.Path` exclusively — never `os.path` string concatenation
- Write files with explicit encoding: `path.write_text(content, encoding="utf-8")`
- Anchor to repo root with `Path(__file__).parent.parent`

**Subprocess**
- Always use list form: `subprocess.run(["cmd", "arg"], check=True)`
- Never use `shell=True`

## Safety Rules (non-negotiable for all skills)

Skills execute with the user's full OS permissions. Any agent writing or reviewing skill
content must enforce these:

- **No external URLs** — no CDN links, no `curl`/`wget` to external hosts; use system fonts
  and bundled resources only
- **No dangerous shell patterns** — no `rm -rf /`, no `eval()`/`exec()` with user input,
  no `shell=True`, no `pkill`/`killall` (use specific PIDs), no base64-encoded payloads
- **No data exfiltration** — no sending local data to external services, no reverse shells
- Run `python -m scripts.quick_validate` after every skill write; do not skip this step

## Commit Message Format

Commits are validated on push. Every message **must** match:

```
type(scope): description

[optional body]

Refs: NOISSUE
```

- Valid types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `style`, `test`
- Scope is optional and must be lowercase
- `Refs:` line must be **last** — nothing after it (no `Co-authored-by`, no blank lines)
- Use `Refs: LIMA-1234` for issue references; `Refs: NOISSUE` otherwise

## Adding a New Skill — Checklist

1. Create `skills/<skill-name>/SKILL.md` with `name` and `description` frontmatter
2. Run `python3 scripts/generate_site.py` — verify the skill appears in generated output
3. Add `references/`, `agents/`, `scripts/`, or `evals/` subdirectories as needed
4. If bundling scripts, run the safety validator: `python -m scripts.quick_validate skills/<skill-name>`
5. Update `README.md` to list the new skill with a one-line description
