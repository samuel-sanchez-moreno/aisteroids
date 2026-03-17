# /verify — Full Quality Gate

Run all quality checks for the current project: lint, checkstyle, static analysis (SonarQube if available), unit tests, and integration tests.

## Instructions

Run each step in order. Report results clearly after each phase. If a phase fails, show the relevant error output and stop — do not proceed to the next phase.

### Step 1 — Detect build system

```bash
if [ -f "./gradlew" ]; then
  echo "BUILD_SYSTEM=gradle"
elif [ -f "pom.xml" ]; then
  echo "BUILD_SYSTEM=maven"
elif [ -f "package.json" ]; then
  echo "BUILD_SYSTEM=npm"
else
  echo "BUILD_SYSTEM=unknown"
fi
```

### Step 2 — Lint & static checks (Checkstyle, ForbiddenApis, ESLint, etc.)

**Gradle:**
```bash
./gradlew checkstyleMain checkstyleTest forbiddenApis
```

**Maven:**
```bash
mvn checkstyle:check
```

**npm:**
```bash
npm run lint
```

### Step 3 — Unit tests

**Gradle:**
```bash
./gradlew test
```

**Maven:**
```bash
mvn test
```

**npm:**
```bash
npm test -- --watchAll=false
```

### Step 4 — SonarQube (only if configured)

Check whether SonarQube is configured in the project:

```bash
# Gradle: look for sonarqube plugin or sonar-project.properties
grep -r "sonarqube\|id.*sonar" build.gradle buildSrc/ --include="*.gradle" --include="*.kts" -l 2>/dev/null | head -3
ls sonar-project.properties 2>/dev/null
```

If sonar is configured, run:

**Gradle:**
```bash
./gradlew sonar
```
or
```bash
./gradlew sonarqube
```

**Maven:**
```bash
mvn sonar:sonar
```

If SonarQube is **not configured locally**, skip this step and note it in the summary.

### Step 5 — Integration tests

**Gradle:**
```bash
./gradlew integrationTest
```

**Maven:**
```bash
mvn verify -P integration-tests
```

**npm:**
```bash
npm run test:integration
```

> ℹ️ Integration tests may require Docker (databases, WireMock). If they fail due to missing infrastructure, report the error and mark this step as skipped.

---

## Summary

After all steps, output a summary table:

| Phase              | Status  | Notes |
|--------------------|---------|-------|
| Lint & Checkstyle  | ✅/❌   |       |
| Unit tests         | ✅/❌   |       |
| SonarQube          | ✅/❌/⏭ |       |
| Integration tests  | ✅/❌/⏭ |       |

Use ⏭ (skipped) when a step was skipped due to missing config or infrastructure.
