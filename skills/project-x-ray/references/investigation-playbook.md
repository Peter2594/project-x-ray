# Investigation Playbook

Concrete commands and search patterns for each phase. Adapt the file globs to the repo's language. Prefer fast structural tools (ripgrep, `git`, manifest parsing) over reading every file. Read the README and top-level docs early — they're the cheapest context you'll get.

> Throughout: collect **evidence** (paths, counts, manifest lines) as you go. The report cites this evidence.

---

## Phase 1 — Inventory & Stack Detection

Read dependency manifests and config first. They tell you the stack with near-certainty.

| Ecosystem | Look for | Tells you |
|---|---|---|
| Node / TS | `package.json`, `pnpm-lock.yaml`, `tsconfig.json` | Frameworks, scripts, runtime |
| Python | `pyproject.toml`, `requirements*.txt`, `setup.cfg`, `Pipfile` | Frameworks, Python version |
| Java | `pom.xml`, `build.gradle(.kts)`, `settings.gradle` | Spring/Jakarta, modules |
| Go | `go.mod`, `go.sum` | Module path, deps |
| Rust | `Cargo.toml`, `Cargo.lock` | Crates |
| Ruby | `Gemfile`, `Gemfile.lock` | Rails/Sinatra |
| .NET | `*.csproj`, `*.sln` | Target framework |
| Infra | `Dockerfile`, `docker-compose.yml`, `*.tf`, `k8s/*.yaml`, `Procfile` | Runtime topology |
| CI | `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile` | Build/test/deploy steps |
| Services | env files, SDK imports (`stripe`, `boto3`, `sendgrid`, `@aws-sdk`, `redis`, `pg`) | External dependencies |

Quick scans:

```bash
# What manifests exist?
ls -1 | rg -i 'package.json|pyproject|requirements|pom.xml|build.gradle|go.mod|Cargo.toml|Gemfile|Dockerfile|compose'

# External services hinted by code/imports
rg -i -o 'stripe|sendgrid|twilio|boto3|aws-sdk|redis|kafka|rabbitmq|elasticsearch|postgres|mysql|mongodb' -g '!**/node_modules/**' | sort | uniq -c | sort -rn
```

Output: a Tech Stack table (Languages / Frameworks / Infrastructure / External Services), each row backed by the file that proves it.

---

## Phase 2 — Map the Tree

Get the shape before the detail.

```bash
# Directory skeleton, ignoring noise
git ls-files | rg -v 'node_modules|dist|build|vendor|\.min\.' | awk -F/ '{print $1"/"$2}' | sort | uniq -c | sort -rn | head -40
```

Identify:
- Top-level modules / bounded contexts.
- Candidate **layers** by folder name: `controllers|handlers|routes`, `services|usecases|domain`, `repositories|dao|models`, `entities`, `config`, `infra`.
- Test layout (`tests/`, `__tests__`, `*_test.go`, `*.spec.ts`) — coverage breadth is a health signal.

---

## Phase 3 — Entry Points

```bash
rg -l -i 'def main|if __name__ == .__main__.|func main\(|public static void main|app\.listen|uvicorn\.run|createServer|FastAPI\(|express\(\)|SpringApplication\.run' -g '!**/node_modules/**'
```

Common entry files: `main.py`, `app.py`, `manage.py`, `server.js`, `index.ts`, `cmd/*/main.go`, `Application.java`, `Program.cs`.

Reconstruct the **startup sequence** by reading the entry file top-to-bottom: config load → DI/container → DB/cache init → route/handler registration → server start. Render it as a vertical arrow chain in the report.

---

## Phase 4 — Dependency Graph

Approximate an import graph with ripgrep; you don't need a perfect AST parse.

```bash
# Python: count how often each internal module is imported
rg -o 'from (\w[\w.]*) import|import (\w[\w.]*)' -r '$1$2' -g '*.py' | sort | uniq -c | sort -rn | head -30

# JS/TS: most-imported local modules
rg -o "from ['\"](\.[^'\"]+)['\"]" -r '$1' -g '*.{ts,tsx,js,jsx}' | sort | uniq -c | sort -rn | head -30

# Java: most-imported internal packages
rg -o 'import (com\.[\w.]+);' -r '$1' -g '*.java' | sort | uniq -c | sort -rn | head -30
```

Derive:
- **Most-referenced modules** → likely critical (high fan-in).
- **High-coupling hotspots** → modules with high fan-in *and* high fan-out (they both depend on a lot and are depended on a lot). These are change-risk centers.
- **Circular dependencies** → look for mutual imports between two modules; flag them.

---

## Phase 5 — Capabilities & Critical Flows

**Capabilities** — infer from route definitions and service/controller names:

```bash
# Routes (framework-agnostic-ish)
rg -i -n '@(app|router)\.(get|post|put|delete|patch)|@RequestMapping|@(Get|Post|Put|Delete)Mapping|router\.(get|post|put|delete)|path\(' -g '!**/node_modules/**' | head -60
```

Group endpoints/services into business capabilities (Authentication, Billing, Order Processing, Reporting, …). Mark the one or two that are the system's reason to exist as **Core**.

**Critical flows** — pick 2–3 important capabilities and trace each end to end, naming the real files:

```
HTTP entry (route)  →  controller/handler  →  service/use-case  →  repository/DAO  →  datastore/external API
```

Cite `path:line` at each hop so a reader can follow it.

---

## Phase 6 — Risk Analysis

**Technical debt** — see detection-heuristics.md for the smell catalogue. Quick probes:

```bash
# God objects / long files
git ls-files | rg '\.(py|ts|js|java|go|rb)$' | xargs wc -l 2>/dev/null | sort -rn | head -20

# Debt markers
rg -n -i 'TODO|FIXME|HACK|XXX|deprecated' -g '!**/node_modules/**' | wc -l

# Error handling / logging gaps (sample)
rg -n 'except:\s*$|catch\s*\(\s*\)|catch\s*\(.*\)\s*\{\s*\}' -g '!**/node_modules/**' | head
```

**Blast radius** — for each candidate critical file, list the capabilities/flows that transitively depend on it (use the Phase 4 graph). More dependents + more flows touched = larger blast radius.

**Bus factor** — knowledge concentration, from git:

```bash
# Authors overall
git shortlog -sne --all | head -20

# Who owns the riskiest file?
git log --format='%an' -- path/to/hotspot.py | sort | uniq -c | sort -rn

# Churn: most-changed files (instability)
git log --pretty=format: --name-only | rg -v '^$' | sort | uniq -c | sort -rn | head -20
```

A file that is large, undocumented, heavily depended on, and authored by one person = bus factor 1, high risk.

If there's no git history (shallow clone / zip), say so and mark bus factor **Unknown**.

---

## Phase 7 — Synthesize

Now — and only now — fill in `report-template.md`. Every section should trace back to evidence you gathered above. Where evidence is thin, attach a confidence level or mark **Unknown** rather than inventing detail.
