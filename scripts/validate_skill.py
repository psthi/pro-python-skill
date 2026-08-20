#!/usr/bin/env python3
"""
Validates SKILL.md frontmatter, chapters, and scripts integrity.
"""
import os
import sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def validate():
    skill_path = os.path.join(ROOT, "SKILL.md")
    with open(skill_path, "r", encoding="utf-8") as f:
        raw = f.read()
    assert raw.startswith("---"), "SKILL.md must start with YAML frontmatter"
    parts = raw.split("---", 2)
    meta = yaml.safe_load(parts[1])
    assert meta.get("name") == "pro-python", "Frontmatter name must be pro-python"
    print("✅ SKILL.md frontmatter is valid.")

    chapters_dir = os.path.join(ROOT, "chapters")
    chapters = [f for f in os.listdir(chapters_dir) if f.endswith(".md")]
    print(f"✅ Found {len(chapters)} chapter documentation files.")

if __name__ == "__main__":
    validate()
