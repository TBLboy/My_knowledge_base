#!/usr/bin/env python3
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = {
    "architecture",
    "debugging",
    "workflow",
    "config-behavior",
    "patterns",
    "anti-patterns",
    "ai-collaboration",
}
INDEX_ROOT = ROOT / "indexes"
MANIFEST_PATH = INDEX_ROOT / "manifest.json"


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "unknown"


def parse_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None
    return parts[1], parts[2]


def parse_scalar(value: str):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"\'') for item in inner.split(",") if item.strip()]
    return value.strip('"\'')


def parse_frontmatter_block(block: str):
    data = {}
    current_key = None
    list_mode = False
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, [])
            data[current_key].append(line[4:].strip().strip('"\''))
            continue
        if line.startswith("- ") and current_key and list_mode:
            data.setdefault(current_key, [])
            data[current_key].append(line[2:].strip().strip('"\''))
            continue
        if ":" not in line:
            current_key = None
            list_mode = False
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        list_mode = value == ""
        if value == "":
            data[key] = []
        else:
            data[key] = parse_scalar(value)
            list_mode = isinstance(data[key], list)
    return data


def extract_rule(body: str):
    lines = body.splitlines()
    capture = False
    collected = []
    for line in lines:
        if line.strip() == "## Rule":
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if capture and line.strip():
            collected.append(line.strip())
    return " ".join(collected)


def load_entries():
    entries = []
    for category in sorted(CATEGORIES):
        for path in sorted((ROOT / category).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            parsed = parse_frontmatter(text)
            if not parsed:
                continue
            frontmatter, body = parsed
            meta = parse_frontmatter_block(frontmatter)
            entry = {
                "path": str(path.relative_to(ROOT)),
                "category": category,
                "title": meta.get("title", path.stem),
                "id": meta.get("id"),
                "tags": meta.get("tags", []),
                "keywords": meta.get("keywords", []),
                "triggers": meta.get("triggers", []),
                "related": meta.get("related", []),
                "aliases": meta.get("aliases", []),
                "source_projects": meta.get("source_projects", []),
                "source_refs": meta.get("source_refs", []),
                "confidence": meta.get("confidence"),
                "applicability": meta.get("applicability"),
                "updated_at": meta.get("updated_at"),
                "rule": extract_rule(body),
            }
            entries.append(entry)
    return entries


def write_group_index(base_dir: Path, groups, heading_prefix: str):
    base_dir.mkdir(parents=True, exist_ok=True)
    for old in base_dir.glob("*.md"):
        if old.name != "README.md":
            old.unlink()
    for key, items in sorted(groups.items()):
        path = base_dir / f"{key}.md"
        lines = [f"# {heading_prefix}: {key}", ""]
        for item in items:
            lines.append(f"## {item['title']}")
            lines.append("")
            lines.append(f"- Path: `{item['path']}`")
            lines.append(f"- Rule: {item['rule'] or 'N/A'}")
            lines.append(f"- Tags: {', '.join(item['tags']) if item['tags'] else 'N/A'}")
            lines.append(f"- Triggers: {', '.join(item['triggers']) if item['triggers'] else 'N/A'}")
            lines.append(f"- Updated: {item['updated_at'] or 'N/A'}")
            lines.append("")
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_quick_ref(entries):
    quick_ref_dir = INDEX_ROOT / "quick-ref"
    for old in quick_ref_dir.glob("*.md"):
        if old.name != "README.md":
            old.unlink()
    groups = defaultdict(list)
    for entry in entries:
        for tag in entry["tags"]:
            groups[slugify(tag)].append(entry)
    for key, items in sorted(groups.items()):
        path = quick_ref_dir / f"{key}.md"
        lines = [f"# Quick Ref: {key}", ""]
        for item in items[:5]:
            lines.append(f"## {item['title']}")
            lines.append("")
            lines.append(f"- Rule: {item['rule'] or 'N/A'}")
            lines.append(f"- Path: `{item['path']}`")
            lines.append(f"- Applicability: {item['applicability'] or 'N/A'}")
            lines.append("")
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_manifest(entries):
    all_tags = sorted({slugify(tag) for entry in entries for tag in entry["tags"]})
    all_keywords = sorted({slugify(keyword) for entry in entries for keyword in entry["keywords"]})
    all_triggers = sorted({slugify(trigger) for entry in entries for trigger in entry["triggers"]})
    payload = {
        "generated_at": date.today().isoformat(),
        "version": 1,
        "entries": entries,
        "normalized_fields": {
            "tags": all_tags,
            "keywords": all_keywords,
            "triggers": all_triggers,
        },
    }
    MANIFEST_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    entries = load_entries()
    by_tag = defaultdict(list)
    by_category = defaultdict(list)
    by_trigger = defaultdict(list)
    for entry in entries:
        by_category[slugify(entry["category"])].append(entry)
        for tag in entry["tags"]:
            by_tag[slugify(tag)].append(entry)
        for trigger in entry["triggers"]:
            by_trigger[slugify(trigger)].append(entry)
    write_group_index(INDEX_ROOT / "by-tag", by_tag, "Tag")
    write_group_index(INDEX_ROOT / "by-category", by_category, "Category")
    write_group_index(INDEX_ROOT / "by-trigger", by_trigger, "Trigger")
    write_quick_ref(entries)
    write_manifest(entries)
    print(f"Rebuilt indexes for {len(entries)} entries")


if __name__ == "__main__":
    main()
