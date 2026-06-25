# Project X-Ray 🩻

> AI-powered repository onboarding and architecture discovery — as a [Claude Code Skill](https://docs.claude.com/en/docs/claude-code/skills).

Most AI tools explain individual files. **Project X-Ray builds a mental model of the entire codebase**, then turns it into a structured onboarding report.

## Why this exists

When you inherit an unfamiliar repository, you ask the same questions every time:

- What does this system do?
- Where should I start reading?
- What are the most important files?
- What could break if I change this?
- Where is the business logic?
- What technical debt exists?

Project X-Ray answers all of them in one pass — with **evidence**, not guesses.

## What you get

A 15-section onboarding report covering: executive summary, system overview, tech stack, architecture pattern (with a confidence score), entry-point startup sequence, dependency graph, business-capability map, critical user flows, ranked critical files, technical-debt assessment, blast-radius and bus-factor analysis, a first-hour/day/week learning roadmap, questions worth asking the team, and a final health verdict.

> **Guiding principle:** Don't explain files. Explain the system.

## Showcase: a real run on Spring PetClinic

X-Ray was run against [`spring-projects/spring-petclinic`](https://github.com/spring-projects/spring-petclinic) (commit `b3ee2c5`). Every figure below is derived from the actual repo — no guessing:

- **Architecture:** Layered MVC, package-by-feature — *confidence 90%*.
- **Evidence-first catch:** there is **no service layer** (`grep @Service` → nothing); controllers inject Spring Data repositories directly. Flagged as an intentional design fact a newcomer will trip on, not a defect.
- **Bus factor:** High — **169 distinct contributors** across 1,034 commits (`git shortlog`).
- **Debt:** 0 TODO/FIXME markers, 0 empty catch blocks, no file over ~185 LOC.
- **Health score:** **92 / 100** (Maintainability: Excellent, Onboarding: Easy, Refactoring risk: Low).

📄 **Read the full report → [examples/spring-petclinic.md](examples/spring-petclinic.md)**

## Install

Project X-Ray is a standard Claude Code skill — a folder with a `SKILL.md`.

**Personal install (all your projects):**

```bash
git clone https://github.com/Peter2594/project-x-ray.git
cp -r project-x-ray/skills/project-x-ray ~/.claude/skills/
```

**Per-project install (commit it with your repo):**

```bash
cp -r project-x-ray/skills/project-x-ray /path/to/your/repo/.claude/skills/
```

On Windows PowerShell, swap `cp -r` for `Copy-Item -Recurse`.

Restart Claude Code (or start a new session) so the skill is discovered.

## Use

In Claude Code, point it at a repository and ask for an X-Ray:

```
> X-ray this repository
> Onboard me onto this codebase — run Project X-Ray
> I just inherited this service. What does it do and where do I start?
```

Claude detects the `project-x-ray` skill, runs the six-phase investigation, and produces the report. See [`examples/`](examples/) for sample outputs:

- ⭐ [**Spring PetClinic**](examples/spring-petclinic.md) — a **real run** on a live open-source repo (see Showcase above).
- [React SPA](examples/react-spa.md) — illustrative.
- [FastAPI service](examples/fastapi-service.md) — illustrative.
- [Spring Boot service](examples/spring-boot-service.md) — illustrative.

## How it works

The skill runs a disciplined, evidence-first investigation before writing a single line of the report:

| Phase | Produces |
|---|---|
| 1. Inventory & stack | Tech-stack table from manifests |
| 2. Map the tree | Module list + candidate layers |
| 3. Entry points | Startup sequence |
| 4. Dependency graph | Most-referenced modules + coupling hotspots |
| 5. Capabilities & flows | Capability map + traced critical flows |
| 6. Risk analysis | Debt, blast radius, bus factor (from git) |
| 7. Synthesize | The 15-section report |

The detection rules (architecture patterns, coupling thresholds, debt smells, health scoring) live in [`skills/project-x-ray/references/`](skills/project-x-ray/references/).

## Repository layout

```
project-x-ray/
├── skills/project-x-ray/
│   ├── SKILL.md                      # the skill entry point
│   └── references/
│       ├── investigation-playbook.md # how to probe a repo (commands per language)
│       ├── detection-heuristics.md   # classification + scoring rules
│       └── report-template.md        # the 15-section output template
├── examples/                         # sample reports on real stacks
├── .github/workflows/validate-skill.yml
└── scripts/validate_skill.py         # frontmatter + structure linter
```

## Contributing

Issues and PRs welcome. The CI workflow validates skill frontmatter and structure on every push — run `python scripts/validate_skill.py` locally before opening a PR.

## License

[MIT](LICENSE)
