#!/usr/bin/env python3
"""Validate Project X-Ray skill structure and frontmatter.

Dependency-free (stdlib only) so it runs anywhere CI puts a Python.
Exit code 0 = all checks pass, 1 = one or more failures.

Checks:
  * SKILL.md exists and has a YAML frontmatter block.
  * Frontmatter has `name` and `description`.
  * `name` uses only lowercase letters, numbers, and hyphens.
  * `description` starts with "Use when" (trigger-focused, per skill guidance).
  * Frontmatter block is <= 1024 characters.
  * Every relative link in SKILL.md (references/...) points to a real file.
  * The three reference files exist.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "project-x-ray"
SKILL_MD = SKILL_DIR / "SKILL.md"
REQUIRED_REFS = [
    "references/investigation-playbook.md",
    "references/detection-heuristics.md",
    "references/report-template.md",
]

NAME_RE = re.compile(r"^[a-z0-9-]+$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LINK_RE = re.compile(r"\]\((references/[^)]+)\)")

errors: list[str] = []
checks_run = 0


def check(condition: bool, ok_msg: str, fail_msg: str) -> bool:
    global checks_run
    checks_run += 1
    if condition:
        print(f"  [PASS] {ok_msg}")
        return True
    print(f"  [FAIL] {fail_msg}")
    errors.append(fail_msg)
    return False


def parse_frontmatter(text: str) -> dict[str, str]:
    """Minimal `key: value` frontmatter parser (no nested structures needed)."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    block = match.group(1)
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    fields["__raw__"] = match.group(0)
    return fields


def main() -> int:
    print("Validating Project X-Ray skill...\n")

    if not check(SKILL_MD.is_file(), f"found {SKILL_MD.name}", f"missing {SKILL_MD}"):
        return 1

    text = SKILL_MD.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)

    check(bool(fm), "frontmatter block present",
          "no YAML frontmatter (--- ... ---) at top of SKILL.md")
    if not fm:
        return 1

    raw = fm.get("__raw__", "")
    check(len(raw) <= 1024, f"frontmatter is {len(raw)} chars (<= 1024)",
          f"frontmatter is {len(raw)} chars (must be <= 1024)")

    name = fm.get("name", "")
    check(bool(name), "has `name`", "frontmatter missing `name`")
    if name:
        check(bool(NAME_RE.match(name)),
              f"`name` '{name}' uses only [a-z0-9-]",
              f"`name` '{name}' must use only lowercase letters, numbers, hyphens")

    desc = fm.get("description", "")
    check(bool(desc), "has `description`", "frontmatter missing `description`")
    if desc:
        check(desc.lower().startswith("use when"),
              "`description` starts with 'Use when'",
              "`description` should start with 'Use when' (trigger-focused)")

    # Reference files exist
    for ref in REQUIRED_REFS:
        path = SKILL_DIR / ref
        check(path.is_file(), f"found {ref}", f"missing required reference: {ref}")

    # Every linked reference resolves
    for link in sorted(set(LINK_RE.findall(text))):
        path = SKILL_DIR / link
        check(path.is_file(), f"link resolves: {link}",
              f"SKILL.md links to '{link}' but file does not exist")

    print()
    if errors:
        print(f"FAILED: {len(errors)} problem(s) across {checks_run} checks.")
        return 1
    print(f"OK: all {checks_run} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
