---
name: lima-pr-reviewer
description: >
  Expert code reviewer for Team LiCoCo services: lima-entitlement (entitlement-service),
  lima-tenant-config, lima-bas-adapter, and BAS. Use this skill whenever the user asks to
  review a PR, diff, branch, or commit in any of these repositories — including "review this
  PR", "look at these changes", "check this diff", or "review what I committed". Triggers:
  Bitbucket PR URL containing entitlement-service, lima-bas-adapter, lima-tenant-config or
  bas; branch names matching LIMA-* or fix/*; any review request without a repo qualifier
  while cwd is one of these repos.
---

# LiCoCo PR Reviewer

You are reviewing code on behalf of Team LiCoCo. Surface issues that genuinely matter —
bugs, correctness problems, spec deviations, architectural regressions. Zero noise on style
unless it violates enforced rules (Checkstyle, forbiddenApis).

---

## Step 1 — Identify the repo and get the diff

Detect the repo from the PR URL, cwd, or context:

| Repo | Stack | Bitbucket project | Cluster |
|------|-------|------------------|---------|
| `entitlement-service` | Java 25, Gradle, MyBatis, Kafka, JPMS | `SPINE` | CSC |
| `lima-bas-adapter` | Java, Gradle, Kafka, SPINE, SQL Server (direct BAS DB access) | `SPINE` | CSC |
| `lima-tenant-config` | Java, Gradle, Kafka, SPINE | `SPINE` | SPINE |
| `bas` | Java 8, Hibernate, Spring JdbcTemplate, Quartz, JAX-RS | `SPINE` | SPINE |

### Getting the diff (Bitbucket)

Use `bkt` with the `dt-bitbucket` skill to fetch the PR diff:

```bash
# Confirm bkt context
bkt context list

# PR metadata (safe fields only)
bkt api '/rest/api/1.0/projects/SPINE/repos/<repo>/pull-requests/<id>' --json \
  | jq '{id, title, state, description, toRef: .toRef.displayId, fromRef: .fromRef.displayId}'

# Full diff (save to file — diffs are large)
bkt api '/rest/api/1.0/projects/SPINE/repos/<repo>/pull-requests/<id>/diff?contextLines=5' \
  --json > /tmp/pr-<id>-diff.json

# Extract file list
cat /tmp/pr-<id>-diff.json | jq '[.diffs[] | {
  file: (.destination.toString // .source.toString),
  type: (if .source.toString == null then "ADDED" elif .destination.toString == null then "DELETED" else "MODIFIED" end)
}]'

# Extract specific file diff (use for reading hunks)
cat /tmp/pr-<id>-diff.json | jq -r '
  .diffs[] | select(.destination.toString == "<file-path>")
  | .hunks[] | .segments[] | "\(.type) | \(.lines[] | "\(.line): \(.text)")"
'
```

### Getting the diff (local git)

```bash
git --no-pager diff origin/master...HEAD   # branch vs master
git --no-pager show <sha>                  # specific commit
git --no-pager diff --cached               # staged changes
```

**Read all changed files before forming any opinions.**

---

## Step 2 — Check the Jira ticket

If the PR title or branch contains a LIMA-* ticket reference:

1. Search Juno for the ticket: use `juno_semantic_search` with the ticket ID + keywords
2. Extract acceptance criteria and solution proposal
3. During review, **validate that the implementation satisfies every AC** — this is as important as code correctness

If no Jira MCP is available and Juno returns nothing useful, ask the user:
> "I couldn't find LIMA-XXXX in Juno. Please paste the ticket's acceptance criteria and solution proposal."

---

## Step 3 — Run four parallel review sub-agents

Dispatch all four sub-agents **in a single message** using the Task tool. Do not run them
sequentially — launch A, B, C, and D simultaneously and wait for all four to return before
synthesising. Each sub-agent receives the diff path and any AC text you collected in Steps 1–2.

```
// Launch all four in one message:

Task A — Spec & Correctness:
  Role: Verify every Jira AC is met and flag correctness bugs (wrong logic, race conditions,
        null-safety, idempotency gaps, missing transaction boundaries).
  Input: diff at /tmp/pr-<id>-diff.json (or paste diff), Jira ACs.
  For each AC: ✅ Met / ❌ Not met / ⚠️ Partial — cite file:line.
  For each bug: severity [CRITICAL/IMPORTANT/MINOR], file:line or PR-WIDE, one-sentence impact.
  IMPORTANT for lima-bas-adapter: LBA has NO BAS HTTP client. Any ADR or design doc that
    mentions a BAS endpoint path (e.g. /private/account/changeAccountStatus/) means a direct
    DB DAO call — never an HTTP call. Do NOT recommend calling BAS REST APIs. If you see such
    a path in a design doc, interpret it as the DAO method name, not an HTTP endpoint.
  Return: raw bullet list only.

Task B — Code Quality & Conventions:
  Role: Apply the repo-specific checklist from references/repo-<repo>.md.
        Flag only real violations — not style preferences unless enforced by Checkstyle/forbiddenApis.
  Input: diff at /tmp/pr-<id>-diff.json (or paste diff), repo name.
  For each finding: severity [CRITICAL/IMPORTANT/MINOR], file:line or PR-WIDE, one-sentence explanation.
  Return: raw bullet list only.

Task C — Security:
  Role: OWASP Top 10 scan, secrets/PII detection, injection risks, authorization depth.
  Input: diff at /tmp/pr-<id>-diff.json (or paste diff), repo name.
  Scan focus areas:
    - Hardcoded secrets, tokens, passwords (grep for patterns: apiKey, password=, secret, token)
    - SQL injection risk (LBA uses raw SQL via JdbcTemplate / MyBatis — check parameter binding)
    - OAuth2 / client credential misuse (wrong client IDs, wrong scopes)
    - Sensitive data logged or exposed in error responses
    - Missing auth checks on new endpoints (BAS JAX-RS resources)
    - Input validation & sanitization: new REST endpoints or Kafka event handlers that accept
      external input without @Valid, @NotNull, or explicit null/blank/length checks. Unvalidated
      input written to DB or forwarded to downstream services is an injection/corruption risk.
    - Authorization depth: new endpoints must enforce RBAC (role or scope checks), not just
      authentication. Flag endpoints reachable without a role restriction.
    - Encryption at rest: new DB columns holding PII, credentials, email addresses, or billing
      data stored in plaintext. Flag missing encryption or masking.
    - Audit logging for sensitive operations: tenant deletion, license modification, account
      status changes, and entitlement grants must produce a log entry with actor + entity ID.
      Flag handlers for these operations that produce no audit trail.
  IMPORTANT for lima-bas-adapter: LBA has NO BAS HTTP client — do NOT flag absence of HTTP auth
    headers as a security issue. Focus on DB-level access control, SQL injection risks, and
    audit logging for DB mutations (account/tenant/license state changes).
  For each finding: severity [CRITICAL/HIGH/MEDIUM/LOW], file:line, OWASP category.
  Return: raw bullet list only. If nothing found, return "No security issues found."

Task D — Performance:
  Role: Identify performance regressions, inefficient DB access, missing caching, and
        resource-heavy patterns introduced or worsened by the PR.
  Input: diff at /tmp/pr-<id>-diff.json (or paste diff), repo name.
  Scan focus areas:
    - N+1 query patterns: loops calling DAO or repository methods per element instead of a
      batch query or join fetch. Each DB round-trip adds latency.
    - Missing DB indexes: new WHERE / ORDER BY / JOIN columns in queries that have no
      corresponding index. Flag if the table is known to be large.
    - Unbounded queries: SELECT without LIMIT or pagination on tables that can grow without
      bound. Flag new list endpoints that return all rows.
    - Connection pool pressure: new DataSource/Connection acquisition outside the pool (e.g.
      DriverManager.getConnection()), or Connection/Statement/ResultSet opened inside a tight
      loop without pooling.
    - Missing caching: repeated identical reads within the same request or event cycle that
      could be memoised or cached (e.g. same ADA hierarchy fetch called multiple times, same
      config key read from DB on every call).
    - Kafka consumer throughput: blocking I/O (synchronous HTTP, large DB queries) executed
      directly in consumer thread — delays offset commit and reduces throughput.
    - Expensive operations in hot paths: regex compilation, reflection, or JSON serialisation
      inside per-request or per-message code paths.
  IMPORTANT for entitlement-service: ADA API calls cost ~50ms each. Flag any call inside a
    loop or redundant ConsumerResolver.resolve() invocations in the same event processing cycle.
  IMPORTANT for BAS: Quartz jobs run on 20-second intervals. Any job that can exceed its
    interval without @DisallowConcurrentExecution is both a performance and correctness risk.
  For each finding: severity [CRITICAL/IMPORTANT/MINOR], file:line or PR-WIDE, one-sentence
    impact with estimated magnitude where possible (e.g. "50 calls × ~50ms = ~2.5s per batch").
  Return: raw bullet list only. If nothing found, return "No performance issues found."
```

Wait for all four to finish. Deduplicate overlapping findings (keep the higher severity).

---

## Step 4 — Fill in the review template

**Before writing a single line of the review, build a master finding list:**

1. Collect every bullet from Task A, B, C, and D outputs into a flat list
2. For each bullet: assign severity, file:line anchor (or PR-WIDE), and source (A/B/C/D)
3. Deduplicate: if A and B flag the same issue, keep the higher severity and one entry
4. Verify the list is complete — if the list has N items, the review must contain exactly N findings
   (or N-deduped items). **Do not drop findings silently during template assembly.**

Then read `references/review-template.md` and fill every placeholder using the verified master
list. Do not invent a different structure — the template is the output format. Omit optional
sections only when they contain no findings (the template marks which are optional).

**One finding = one action.** No speculative warnings. If uncertain, verify before flagging.

---

## Repo-specific checklists and templates

See `references/` directory:
- `references/review-template.md` — **output template — always fill this in for Step 4**
- `references/repo-entitlement-service.md` — entitlement-service + LPC pipeline rules
- `references/repo-bas.md` — BAS maintenance-only rules
- `references/repo-lima-bas-adapter.md` — lima-bas-adapter Kafka + direct DB rules
- `references/repo-lima-tenant-config.md` — lima-tenant-config Kafka + config correctness rules

---

## Commit message format (all repos)

Pre-receive hook enforces:
```
^(build|chore|ci|docs|feat|fix|perf|refactor|style|test)(\([a-z ]+\))?:([ \n].+)([ \n].*)*[ \n][Rr]efs?: (NOISSUE|[A-Z]+-[0-9]+)(, (NOISSUE|[A-Z]+-[0-9]+))*$
```

- `Refs:` (or `refs:`, `Ref:`, `ref:`) must be the **last line** — nothing after it
- No `Co-authored-by` after `Refs:` — put it before
- `LIMA-0` / `NOISSUE` when no ticket
- The regex is `[Rr]efs?:` — all four variants (`Refs:`, `refs:`, `Ref:`, `ref:`) match
