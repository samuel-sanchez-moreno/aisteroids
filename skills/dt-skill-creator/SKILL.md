---
name: dt-skill-creator
description: >
  Create, modify, and evaluate Dynatrace-safe skills with built-in security guardrails. Use this skill whenever
  someone wants to create a new skill for the Dynatrace/SPINE ecosystem, improve an existing skill, run evals to
  test skill quality, benchmark skill performance, or optimize a skill's description for better triggering. This
  skill enforces safety rules — no external URLs, no dangerous shell commands, no data exfiltration patterns — so
  every skill it produces is safe for internal Dynatrace environments. Also use when reviewing skills for security
  compliance, or when the user mentions "dt skill", "safe skill", "Dynatrace skill", or wants to package a skill
  for distribution within the team.
---

# DT Skill Creator

A Dynatrace-safe skill creator for building, testing, and iterating on skills within the Dynatrace/SPINE ecosystem. This is a security-hardened fork of the general-purpose skill-creator, with built-in guardrails that ensure every skill produced is safe for internal use.

## Core Workflow

The process of creating a skill:

1. Decide what the skill should do and roughly how it should do it
2. Write a draft of the skill
3. **Run a safety audit** on the draft (this is a DT-specific step — see Safety Rules below)
4. Create test prompts and run claude-with-access-to-the-skill on them
5. Help the user evaluate the results (qualitative + quantitative)
   - While runs happen in the background, draft quantitative evals if there aren't any
   - Use the `eval-viewer/generate_review.py` script to show the user the results
   - Let them also look at the quantitative metrics
6. Rewrite the skill based on feedback
7. **Re-run safety audit** after each revision
8. Repeat until satisfied
9. Expand the test set and try again at larger scale

Your job is to figure out where the user is in this process and help them progress. Maybe they want to create something new, or maybe they already have a draft. Be flexible — if the user says "just vibe with me", skip the formal eval pipeline.

After the skill is done, offer to run the description optimizer and package the skill.

## Safety Rules

These rules are non-negotiable. Every skill produced by dt-skill-creator must comply:

### No External URLs
Skills must not reference, fetch, or depend on external URLs. This means:
- No CDN links (fonts, CSS libraries, JS libraries)
- No external API endpoints (except the Anthropic API, which is required for Claude-based workflows)
- No image/resource hotlinks
- No `curl`/`wget`/`fetch` to external hosts
- Use system fonts, inline styles, and bundled resources instead

The reason: skills run in internal environments where external network access may be restricted, and external dependencies create supply-chain risk.

### No Dangerous Commands
Scripts bundled with skills must not contain:
- `rm -rf /` or any broad recursive delete patterns
- `eval()` or `exec()` with user-provided input
- Shell command construction from string interpolation (`os.system(f"...")`)
- `chmod 777` or overly permissive file permissions
- Credential harvesting patterns (reading `~/.ssh/`, `~/.aws/`, env vars for tokens)
- Process killing by name (`pkill`, `killall`) — use specific PIDs only
- Network listeners on privileged ports
- Base64-encoded payloads or obfuscated code

The reason: skills run with the user's permissions, and unsafe patterns could cause data loss or security incidents.

### No Data Exfiltration
Skills must not:
- Send local data to external services
- Encode and transmit file contents
- Create reverse shells or tunnels
- Write sensitive data to world-readable locations

### Safety Audit Step
After writing or modifying a skill, run the safety validator:
```bash
python -m scripts.quick_validate <path-to-skill>
```
This checks for external URLs, dangerous patterns, and structural correctness. Fix all findings before proceeding to eval.

## Dynatrace Ecosystem Awareness

When creating skills for the Dynatrace/SPINE ecosystem, be aware of these tools and conventions:

### Available Tools
- **dtctl** — kubectl-style CLI for Dynatrace. Skills that interact with DT environments should use dtctl commands.
- **Dynatrace API** — REST API for DT tenants (metrics, entities, problems, settings). Skills should reference the internal API, not external SaaS endpoints.
- **Kafka/EventBus** — SPINE microservices communicate via Kafka events. Skills dealing with event flows should understand this.
- **Java/Spring Boot** — Most SPINE services are Java 8+ Spring Boot apps. Skills for debugging/testing should know this.
- **Lima/BAS** — Licensing and billing pipeline services. Skills touching tenant data should be aware of these.

### Conventions
- Commit messages follow: `type(scope): description` + `Refs: ISSUE-123` (see project's git hooks)
- Skills should use kebab-case naming
- Configuration lives in `.claude/` directories
- Team uses IntelliJ, iTerm2, macOS

## Communicating with the user

Pay attention to context cues about the user's technical level. Default to explaining terms briefly if in doubt. "Evaluation" and "benchmark" are fine; for "JSON" and "assertion", see if the user seems comfortable with them before using without explanation.

---

## Creating a skill

### Capture Intent

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? Skills with objectively verifiable outputs benefit from tests. Skills with subjective outputs often don't need them. Suggest the appropriate default.

### Interview and Research

Ask about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until this is ironed out.

Check available MCPs — if useful for research, do so. Come prepared with context.

### Write the SKILL.md

Fill in these components:

- **name**: Skill identifier (kebab-case)
- **description**: When to trigger, what it does. Make it slightly "pushy" to combat undertriggering.
- **compatibility**: Required tools, dependencies (optional)
- **the rest of the skill**

### Skill Writing Guide

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) — Always in context (~100 words)
2. **SKILL.md body** — In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** — As needed (unlimited, scripts can execute without loading)

**Key patterns:**
- Keep SKILL.md under 500 lines; if approaching this, add hierarchy with clear pointers
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>300 lines), include a table of contents

**Domain organization**: When a skill supports multiple domains/frameworks:
```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

#### Safety-First Writing

When writing skills for the DT ecosystem, the safety rules above aren't just checkboxes — they reflect the reality that skills run in production-adjacent environments with real credentials and real data. Every script you bundle will run with the user's full permissions. Write them as if a junior engineer will copy-paste them without reading the code.

Concretely:
- Use `subprocess.run([...], check=True)` (list form) instead of `os.system()` or `subprocess.run("...", shell=True)`
- Validate inputs before using them in file paths or commands
- Use `pathlib.Path` instead of string concatenation for paths
- Write to temp directories or explicitly specified output directories, never to arbitrary locations
- Include error handling that fails gracefully rather than silently

#### Writing Patterns

Prefer the imperative form. Explain the **why** behind instructions — LLMs respond better to understanding than to rigid MUSTs.

**Defining output formats:**
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern:**
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Writing Style

Explain why things are important rather than relying on heavy-handed directives. Start with a draft, then review with fresh eyes and improve. Make the skill general, not overly narrow to specific examples.

### Safety Audit

After writing the skill draft, **always run the safety validator before proceeding to test cases**:

```bash
python -m scripts.quick_validate <path-to-skill>
```

Review the output. Fix any findings. This is a gate — don't skip it.

### Test Cases

After writing and validating the skill draft, come up with 2-3 realistic test prompts. Share them with the user for review. Then run them.

Save test cases to `evals/evals.json`:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema (including assertions).

## Running and evaluating test cases

This section is one continuous sequence. Do NOT use `/skill-test` or any other testing skill.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory (`eval-0/`, `eval-1/`, etc.).

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents — one with the skill, one without. Launch everything at once.

**With-skill run:**
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about>
```

**Baseline run** (same prompt, no skill/old version). Save to `without_skill/outputs/` or `old_skill/outputs/`.

Write `eval_metadata.json` for each test case. Give each eval a descriptive name.

### Step 2: While runs are in progress, draft assertions

Don't wait — draft quantitative assertions and explain them to the user. Good assertions are objectively verifiable and have descriptive names.

**DT-specific assertions to consider:**
- "No external URLs in generated files"
- "No dangerous shell patterns in scripts"
- "Uses pathlib for file operations"
- "Subprocess calls use list form, not shell=True"

Update `eval_metadata.json` and `evals/evals.json` with assertions.

### Step 3: Capture timing data

When each subagent completes, save `timing.json`:
```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

### Step 4: Grade, aggregate, and launch the viewer

1. **Grade each run** — read `agents/grader.md` and evaluate. Save `grading.json`. Use fields: `text`, `passed`, `evidence`. For programmatic checks, write scripts.

2. **Aggregate** — run:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```

3. **Analyst pass** — read `agents/analyzer.md` for what to look for.

4. **Launch viewer**:
   ```bash
   nohup python <dt-skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+, pass `--previous-workspace <workspace>/iteration-<N-1>`.

   **Headless environments:** Use `--static <output_path>` for standalone HTML.

5. **Tell the user** to review in their browser.

### Step 5: Read the feedback

Read `feedback.json`, focus improvements on test cases with specific complaints. Kill the viewer server when done.

---

## Improving the skill

### How to think about improvements

1. **Generalize from feedback.** Don't overfit to test examples. If a change is fiddly, try a different approach.

2. **Keep the prompt lean.** Remove things not pulling their weight. Read transcripts — if the skill wastes time on unproductive steps, trim them.

3. **Explain the why.** Frame reasoning so the model understands importance. Avoid excessive ALWAYS/NEVER in caps.

4. **Look for repeated work.** If all test runs independently wrote similar helper scripts, bundle that script in `scripts/`.

5. **Re-run safety audit.** After every revision, run `python -m scripts.quick_validate <path>` again.

### The iteration loop

1. Apply improvements
2. Run safety audit
3. Rerun all test cases into new `iteration-<N+1>/`
4. Launch reviewer with `--previous-workspace`
5. Wait for user review
6. Read feedback, improve, repeat

Keep going until the user is happy, feedback is all empty, or you're not making progress.

---

## Advanced: Blind comparison

For rigorous A/B comparison between skill versions, read `agents/comparator.md` and `agents/analyzer.md`. This is optional — the human review loop is usually sufficient.

---

## Description Optimization

After the skill is finalized, offer to optimize the description for triggering accuracy.

### Step 1: Generate trigger eval queries

Create 20 eval queries — mix of should-trigger and should-not-trigger. Save as JSON. Make queries realistic and detailed (not generic). Include edge cases.

### Step 2: Review with user

Present the eval set for review. Let them edit, then export.

### Step 3: Run the optimization loop

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id> \
  --max-iterations 5 \
  --verbose
```

### Step 4: Apply the result

Update SKILL.md frontmatter with `best_description`. Show before/after and report scores.

---

## Reference files

- `agents/grader.md` — How to evaluate assertions against outputs
- `agents/comparator.md` — How to do blind A/B comparison
- `agents/analyzer.md` — How to analyze why one version beat another
- `references/schemas.md` — JSON structures for evals.json, grading.json, etc.

---

## Cowork-Specific Instructions

- Subagents work normally. If timeouts occur, run tests in series.
- No browser — use `--static <output_path>` for the viewer.
- GENERATE THE EVAL VIEWER *BEFORE* evaluating outputs yourself.
- Feedback works via file download — read from Downloads.
- Packaging and description optimization work normally.

---

## Claude.ai-specific instructions

- No subagents — run test cases yourself, one at a time. Skip baselines.
- No browser viewer — present results in conversation. Save files for user to download.
- Skip quantitative benchmarking. Focus on qualitative feedback.
- Description optimization requires `claude` CLI — skip on Claude.ai.

---

Core loop reminder:
1. Figure out what the skill is about
2. Draft or edit the skill
3. **Run safety audit**
4. Run claude-with-access-to-the-skill on test prompts
5. Create benchmark.json and run `eval-viewer/generate_review.py` for user review
6. Run quantitative evals
7. Repeat until satisfied
8. Package the final skill
