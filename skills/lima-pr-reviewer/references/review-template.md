# PR Review — {repo} PR #{pr_id}

**Branch:** `{branch_name}`
**Ticket:** {ticket_id} — {ticket_summary | "no ticket"}
**Reviewer:** LiCoCo PR Reviewer (lima-pr-reviewer skill)
**Date:** {date}

---

## Summary

{1–3 sentences: what the PR does, scope of change, overall risk.}

**Overall verdict:** {LGTM | Needs changes | Critical issues — do not merge}
**Jira AC coverage:** {X}/{Y} criteria met  ← omit line if no ticket

---

## Critical Issues  ← omit entire section if none

- **[CRITICAL]** `{path/to/File.java:line}` — {what is wrong and why it matters. One sentence per finding.}
- **[CRITICAL]** `PR-WIDE` — {use PR-WIDE when the issue is architectural or spans all files}

---

## Non-Critical Findings  ← omit entire section if none

- **[IMPORTANT]** `{path/to/File.java:line}` — {description}
- **[MINOR]** `{path/to/File.java:line}` — {description}
- **[MINOR]** `PR-WIDE` — {description}

---

## Security Findings  ← omit entire section if Task C returned "No security issues found."

- **[{CRITICAL|HIGH|MEDIUM|LOW}]** `{path/to/File.java:line}` — {description}. OWASP: {category}

---

## Performance Findings  ← omit entire section if Task D returned "No performance issues found."

- **[{CRITICAL|IMPORTANT|MINOR}]** `{path/to/File.java:line}` — {description}. Impact: {estimated magnitude}

---

## Simplicity & Design  ← omit entire section if Task E returned "No simplicity issues found."

- **[UNIFY]** `{path/to/File.java:line}` — {question about duplicated logic, citing both locations}
- **[SIMPLIFY]** `{path/to/File.java:line}` — {question about whether code can be removed or replaced}
- **[QUESTION]** `{path/to/File.java:line}` — {challenge to an abstraction, wrapper, or architectural choice}
- **[SCOPE]** `{path/to/File.java:line}` — {naming, package placement, or PR scope discipline issue}

---

## Jira AC Gaps  ← omit entire section if all ACs met or no ticket

- ❌ AC: "{acceptance criterion text}" — not implemented because {reason}
- ⚠️ AC: "{acceptance criterion text}" — partially met: {what is missing}

---

## Commit / PR Format  ← omit entire section if no violations

- {describe the violation and the correct format}

---

<!-- FILLING INSTRUCTIONS (remove this block before publishing the review):
  - Replace every {placeholder} with actual content.
  - Use exact file paths from the diff (e.g. lpc/service/src/main/java/module-info.java:34).
  - Line numbers must come from the diff hunk headers (+/- line numbers).
  - If the diff fetch failed and line numbers are unavailable, use the class or method name
    instead: `{path/to/File.java} (method: handleEvent)`.
  - Use PR-WIDE only when a finding genuinely applies to the whole PR and has no single anchor line.
  - Omit — do not leave empty — any section with no findings.
  - Do not add extra sections beyond those defined here.
-->
