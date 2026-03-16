#!/usr/bin/env python3
"""
Quick validation script for skills - DT-safe version

Validates structural correctness AND security safety:
- Standard checks: SKILL.md exists, valid frontmatter, required fields
- Safety checks: no external URLs, no dangerous shell patterns, no data exfiltration
"""

import re
import sys
from pathlib import Path


# Patterns that indicate external URL usage
EXTERNAL_URL_PATTERNS = [
    r'https?://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)',
    r'href\s*=\s*["\']https?://',
    r'src\s*=\s*["\']https?://',
    r'url\s*\(\s*["\']?https?://',
    r'@import\s+["\']https?://',
]

# Patterns that indicate dangerous commands/code
DANGEROUS_PATTERNS = [
    (r'\brm\s+-rf\s+/', 'Recursive delete from root'),
    (r'\beval\s*\(', 'Use of eval()'),
    (r'\bexec\s*\(', 'Use of exec()'),
    (r'os\.system\s*\(', 'Use of os.system() — use subprocess with list args instead'),
    (r'shell\s*=\s*True', 'subprocess with shell=True — use list args instead'),
    (r'chmod\s+777', 'Overly permissive file permissions'),
    (r'chmod\s+666', 'World-writable file permissions'),
    (r'\bpkill\b', 'Process killing by name — use specific PIDs'),
    (r'\bkillall\b', 'Process killing by name — use specific PIDs'),
    (r'\.ssh/', 'Accessing SSH credentials'),
    (r'\.aws/', 'Accessing AWS credentials'),
    (r'\.kube/config', 'Accessing kube config'),
    (r'base64\s+--decode.*\|\s*(sh|bash)', 'Base64-encoded shell execution'),
    (r'\bnc\s+-[el]', 'Netcat listener (potential reverse shell)'),
    (r'\bsocat\b.*TCP', 'Socat TCP connection (potential tunnel)'),
]

# File extensions to scan for safety
SCANNABLE_EXTENSIONS = {
    '.py', '.sh', '.bash', '.js', '.ts', '.md', '.html', '.css',
    '.yaml', '.yml', '.toml', '.cfg', '.conf', '.ini',
}


def _parse_simple_yaml(text: str) -> dict | None:
    """Parse simple key: value YAML frontmatter without external dependencies.

    Handles single-line values (plain and quoted), and YAML block scalars
    (>, |, >-, |-) with indented continuation lines. Does not handle nested
    mappings, sequences, or anchors — those aren't used in skill frontmatter.
    """
    result = {}
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        # Skip blank lines and comments
        if not line.strip() or line.strip().startswith('#'):
            i += 1
            continue
        # Match key: value
        m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_-]*)\s*:\s*(.*)', line)
        if not m:
            i += 1
            continue
        key = m.group(1)
        value = m.group(2).strip()
        # Handle block scalar indicators
        if value in ('>', '|', '>-', '|-'):
            continuation: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith('  ') or lines[i].startswith('\t')):
                continuation.append(lines[i].strip())
                i += 1
            result[key] = ' '.join(continuation)
            continue
        # Strip surrounding quotes
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        result[key] = value
        i += 1
    return result if result else None


def validate_skill(skill_path):
    """Validate a skill for structural correctness and safety."""
    skill_path = Path(skill_path)

    # --- Structural Validation ---

    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse frontmatter using stdlib only (no PyYAML dependency)
    frontmatter = _parse_simple_yaml(frontmatter_text)
    if frontmatter is None:
        return False, "Could not parse YAML frontmatter"

    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = str(frontmatter.get('name', '')).strip()
    if name:
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    description = str(frontmatter.get('description', '')).strip()
    if description:
        if '<' in description or '>' in description:
            return False, "Description cannot contain angle brackets (< or >)"
        if len(description) > 1024:
            return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    compatibility = str(frontmatter.get('compatibility', '')).strip()
    if compatibility:
        if len(compatibility) > 500:
            return False, f"Compatibility is too long ({len(compatibility)} characters). Maximum is 500 characters."

    # --- Safety Validation ---

    safety_issues = []

    # Scan all files in the skill directory
    for file_path in skill_path.rglob('*'):
        if not file_path.is_file():
            continue
        if file_path.suffix not in SCANNABLE_EXTENSIONS:
            continue
        # Skip __pycache__ and similar
        if '__pycache__' in str(file_path) or 'node_modules' in str(file_path):
            continue

        try:
            file_content = file_path.read_text(errors='replace')
        except Exception:
            continue

        rel_path = file_path.relative_to(skill_path)

        # Track fenced code blocks in markdown to skip documentation examples
        in_code_block = False
        for line_no, line in enumerate(file_content.splitlines(), 1):
            stripped = line.strip()

            # Toggle code block state for markdown files
            if file_path.suffix == '.md' and stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # Skip comment lines
            if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('*'):
                continue

            # Skip Python regex pattern definitions (tuples with regex strings)
            if file_path.suffix == '.py' and re.match(r"""^\s*\(?\s*r?['\"]""", stripped):
                continue

            # For markdown files, strip inline backtick content and quoted strings before scanning
            scan_line = line
            if file_path.suffix == '.md':
                scan_line = re.sub(r'`[^`]+`', '', scan_line)
                scan_line = re.sub(r'"[^"]*"', '', scan_line)
                scan_line = re.sub(r"'[^']*'", '', scan_line)

            # Check for external URLs
            for pattern in EXTERNAL_URL_PATTERNS:
                if re.search(pattern, scan_line):
                    safety_issues.append(
                        f"[EXTERNAL_URL] {rel_path}:{line_no} — External URL detected: {stripped[:80]}"
                    )

            # Check for dangerous patterns
            for pattern, description_text in DANGEROUS_PATTERNS:
                if re.search(pattern, scan_line):
                    safety_issues.append(
                        f"[DANGEROUS] {rel_path}:{line_no} — {description_text}: {stripped[:80]}"
                    )

    if safety_issues:
        issues_text = "\n".join(f"  - {issue}" for issue in safety_issues)
        return False, f"Safety validation failed ({len(safety_issues)} issue(s)):\n{issues_text}"

    return True, "Skill is valid and safe! ✅"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
