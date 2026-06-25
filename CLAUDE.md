# CLAUDE.md — Project X-Ray

Guidance for AI agents (and humans) working **on this repository**. This is a Claude Code skill that performs repository onboarding.

## What this repo is

A single distributable skill, `skills/project-x-ray/`, plus examples, CI, and docs. The skill is the product; everything else supports it.

## Where things live

- `skills/project-x-ray/SKILL.md` — the skill entry point. Keep it lean: the investigation workflow and pointers, not the full template.
- `skills/project-x-ray/references/` — heavy reference, loaded on demand:
  - `investigation-playbook.md` — concrete probing commands per language/phase.
  - `detection-heuristics.md` — classification + scoring rules.
  - `report-template.md` — the 15-section output.
- `examples/` — full sample reports. Keep them realistic and consistent with the template.
- `scripts/validate_skill.py` — structural linter run by CI.

## Editing rules

- **Keep `SKILL.md` lean.** It loads into context whenever the skill triggers. Move anything long into `references/` and link to it by relative path. Don't use `@`-links (they force-load and burn context).
- **The frontmatter `description` must stay trigger-focused** — start with "Use when…", third person, and do **not** summarize the workflow (that causes Claude to skip the body). See `superpowers:writing-skills` for the rationale.
- **Evidence-first is the core invariant.** Any change must preserve the rule that every report claim cites observed evidence (path, manifest line, import count, git stat) or is marked Unknown. Don't add steps that invite guessing.
- **Keep the three references mutually consistent.** The phases in `investigation-playbook.md`, the scoring in `detection-heuristics.md`, and the sections in `report-template.md` must line up.
- Run `python scripts/validate_skill.py` before committing.

## What NOT to do

- Don't turn `SKILL.md` into the full template — that's `report-template.md`'s job.
- Don't add framework/tool names to detection heuristics without a detectable signal for them.
- Don't add example reports that aren't grounded in a plausible real codebase.

## Validating

```bash
python scripts/validate_skill.py
```

CI runs the same check on every push and PR (`.github/workflows/validate-skill.yml`).
