#!/usr/bin/env python3
"""Generate the Aisteroids marketplace static site from skills/*/SKILL.md."""

import os
import re
import textwrap
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
DOCS_DIR = REPO_ROOT / "docs"
REPO_URL = "https://github.com/samuel-sanchez-moreno/aisteroids"


def parse_frontmatter(skill_md: Path) -> dict:
    """Extract YAML frontmatter from a SKILL.md file."""
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def collect_skills() -> list[dict]:
    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_md.exists():
            continue
        meta = parse_frontmatter(skill_md)
        name = meta.get("name") or skill_dir.name
        description = meta.get("description") or ""
        if isinstance(description, str):
            description = " ".join(description.split())
        skills.append({"slug": skill_dir.name, "name": name, "description": description})
    return skills


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def short_description(description: str, max_chars: int = 160) -> str:
    if len(description) <= max_chars:
        return description
    return description[:max_chars].rsplit(" ", 1)[0] + "…"


PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{meta_description}" />
  <link rel="stylesheet" href="{css_path}" />
</head>
<body>
  <header class="site-header">
    <a href="{home_path}" class="site-logo">🌟 aisteroids</a>
    <a href="{repo_url}" class="header-link" target="_blank" rel="noopener">GitHub →</a>
  </header>
  <main>
{content}
  </main>
  <footer>
    <p>
      <a href="{repo_url}" target="_blank" rel="noopener">samuel-sanchez-moreno/aisteroids</a>
      · Apache-2.0
    </p>
  </footer>
  <script>
    document.querySelectorAll('.copy-btn').forEach(function(btn) {{
      btn.addEventListener('click', function() {{
        var code = btn.previousElementSibling.textContent;
        navigator.clipboard.writeText(code).then(function() {{
          btn.textContent = 'Copied!';
          setTimeout(function() {{ btn.textContent = 'Copy'; }}, 1500);
        }});
      }});
    }});
  </script>
</body>
</html>
"""


def render_home(skills: list[dict]) -> str:
    cards = ""
    for skill in skills:
        slug = html_escape(skill["slug"])
        name = html_escape(skill["name"])
        desc = html_escape(short_description(skill["description"]))
        cards += textwrap.dedent(f"""\
            <article class="skill-card">
              <h2><a href="skills/{slug}/">{name}</a></h2>
              <p>{desc}</p>
              <a class="card-link" href="skills/{slug}/">View skill →</a>
            </article>
        """)

    content = textwrap.dedent(f"""\
        <section class="hero">
          <h1>Aisteroids</h1>
          <p class="tagline">A collection of AI agent skills for software engineering workflows.</p>
        </section>
        <section class="skills-grid">
{textwrap.indent(cards.rstrip(), "          ")}
        </section>
    """)

    return PAGE_TEMPLATE.format(
        title="Aisteroids — AI Agent Skills",
        meta_description="A marketplace of AI agent skills for software engineering workflows.",
        css_path="style.css",
        home_path="./",
        repo_url=REPO_URL,
        content=content,
    )


def install_block(slug: str) -> str:
    escaped = html_escape(slug)
    cp_cmd = (
        f"# Copy directly into your project\n"
        f"git clone {REPO_URL}.git .aisteroids\n"
        f"cp -r .aisteroids/skills/{escaped} .github/skills/"
    )
    submodule_cmd = (
        f"# Or use a git submodule for automatic updates\n"
        f"git submodule add {REPO_URL}.git .aisteroids\n"
        f"ln -s ../.aisteroids/skills/{escaped} .github/skills/{escaped}"
    )
    return textwrap.dedent(f"""\
        <section class="install-section">
          <h2>Install</h2>
          <div class="code-block">
            <pre><code>{html_escape(cp_cmd)}</code></pre>
            <button class="copy-btn" aria-label="Copy command">Copy</button>
          </div>
          <div class="code-block">
            <pre><code>{html_escape(submodule_cmd)}</code></pre>
            <button class="copy-btn" aria-label="Copy command">Copy</button>
          </div>
        </section>
    """)


def render_skill(skill: dict) -> str:
    slug = html_escape(skill["slug"])
    name = html_escape(skill["name"])
    desc = html_escape(skill["description"])

    content = textwrap.dedent(f"""\
        <div class="skill-detail">
          <nav class="breadcrumb"><a href="../../">← All skills</a></nav>
          <h1>{name}</h1>
          <p class="skill-description">{desc}</p>
          {install_block(slug)}
        </div>
    """)

    return PAGE_TEMPLATE.format(
        title=f"{skill['name']} — Aisteroids",
        meta_description=short_description(skill["description"]),
        css_path="../../style.css",
        home_path="../../",
        repo_url=REPO_URL,
        content=content,
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


def main() -> None:
    print("Collecting skills…")
    skills = collect_skills()
    print(f"  found {len(skills)} skill(s): {[s['slug'] for s in skills]}")

    print("Generating site…")
    write(DOCS_DIR / "index.html", render_home(skills))
    for skill in skills:
        write(DOCS_DIR / "skills" / skill["slug"] / "index.html", render_skill(skill))

    print(f"Done — {len(skills) + 1} file(s) written to docs/")


if __name__ == "__main__":
    main()
