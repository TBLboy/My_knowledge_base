#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB_TOOL = ROOT / "tools" / "kb.py"
RULES_PATH = ROOT / "config" / "session-rules.yaml"


def parse_scalar(value: str):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"\'') for item in inner.split(",") if item.strip()]
    return value.strip('"\'')


def load_simple_yaml(path: Path):
    data = {}
    current_key = None
    current_map = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(" ") and line.endswith(":"):
            key = line[:-1].strip()
            current_key = key
            current_map = None
            data[key] = []
            continue
        if raw_line.startswith("  ") and not raw_line.startswith("    ") and line.endswith(":"):
            if current_key is None:
                continue
            nested_key = line[:-1].strip()
            if not isinstance(data.get(current_key), dict):
                data[current_key] = {}
            data[current_key][nested_key] = []
            current_map = nested_key
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            item = stripped[2:].strip().strip('"\'')
            if current_key is None:
                continue
            if isinstance(data.get(current_key), dict) and current_map is not None:
                data[current_key][current_map].append(item)
            else:
                data.setdefault(current_key, [])
                data[current_key].append(item)
            continue
        if raw_line.startswith("  ") and not raw_line.startswith("    ") and ":" in line and not line.endswith(":"):
            if current_key is None:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            if isinstance(data.get(current_key), dict):
                data[current_key][key] = parse_scalar(value)
            else:
                data[current_key] = {key: parse_scalar(value)}
            continue
        if ":" in line and not raw_line.startswith(" "):
            key, value = line.split(":", 1)
            data[key.strip()] = parse_scalar(value)
            current_key = None
            current_map = None
    return data


def normalize(text: str):
    return " ".join(text.lower().strip().split())


def match_any(text: str, patterns):
    haystack = normalize(text)
    for pattern in patterns or []:
        pattern_norm = normalize(pattern)
        if pattern_norm and pattern_norm in haystack:
            return pattern
    return None


def collect_context_tags(text: str, mapping):
    haystack = normalize(text)
    hits = []
    for cluster, tags in (mapping or {}).items():
        cluster_norm = normalize(cluster)
        if cluster_norm and cluster_norm in haystack:
            hits.extend(tags)
            continue
        for tag in tags:
            tag_norm = normalize(tag)
            if tag_norm and tag_norm in haystack:
                hits.extend(tags)
                break
    deduped = []
    seen = set()
    for tag in hits:
        if tag not in seen:
            seen.add(tag)
            deduped.append(tag)
    return deduped


def run_kb(args):
    completed = subprocess.run(
        [sys.executable, str(KB_TOOL), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def build_hint_block(query: str, body: str):
    sections = [chunk.strip() for chunk in body.split("\n\n") if chunk.strip()]
    if not sections:
        return ""
    lines = ["## Relevant KB Hints", ""]
    for idx, section in enumerate(sections, start=1):
        section_lines = section.splitlines()
        title = section_lines[0].strip()
        path = ""
        rule = ""
        why = ""
        for line in section_lines[1:]:
            if line.startswith("Path: "):
                path = line.removeprefix("Path: ").strip()
            elif line.startswith("Rule: "):
                rule = line.removeprefix("Rule: ").strip()
            elif line.startswith("Why matched: "):
                why = line.removeprefix("Why matched: ").strip()
        entry_title = title.split("] ", 1)[-1] if title.startswith("[") else title
        lines.append(f"{idx}. {entry_title}")
        if path:
            lines.append(f"- Path: {path}")
        if rule:
            lines.append(f"- Rule: {rule}")
        if why:
            lines.append(f"- Why relevant now: query '{query}' matched {why}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main():
    parser = argparse.ArgumentParser(prog="kb-hotload")
    parser.add_argument("context", help="Current task description, error string, or session prompt")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    rules = load_simple_yaml(RULES_PATH)
    context = args.context.strip()
    limit = args.limit or int(rules.get("max_injected_entries", 3) or 3)

    explicit_hit = match_any(context, rules.get("explicit_request_patterns", []))
    error_hit = match_any(context, rules.get("error_trigger_patterns", []))
    context_tags = collect_context_tags(context, rules.get("task_context_tags", {}))

    query = None
    mode = None
    if explicit_hit:
        query = context
        mode = "related"
    elif error_hit:
        phrase_map = rules.get("error_phrase_map", {})
        query = phrase_map.get(error_hit, context)
        mode = "related"
    elif context_tags:
        query = " ".join(context_tags)
        mode = "find"

    if not query or not mode:
        print("No hot-load trigger matched.")
        return 1

    code, stdout, stderr = run_kb([mode, query, "--limit", str(limit)])
    if code != 0 or not stdout or stdout == "No matching knowledge entries found.":
        print("No matching knowledge entries found.")
        if stderr:
            print(stderr, file=sys.stderr)
        return 1

    print(build_hint_block(query, stdout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
