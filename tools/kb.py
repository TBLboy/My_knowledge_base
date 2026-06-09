#!/usr/bin/env python3
"""Personal knowledge base query tool with improved ranking.

Tokenization splits camelCase/snake_case so error strings like
"setOperateMode automatic failed" can match entries whose keywords
include "operate", "mode", or "ros2 action".
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "indexes" / "manifest.json"

WEIGHTS = {
    "trigger_exact": 10,
    "title": 8,
    "alias": 7,
    "keyword": 5,
    "tag": 4,
    "trigger_partial": 4,
    "category": 2,
    "related": 1,
    "multi_token_bonus": 2,
}

NOISE_WORDS = {
    "failed", "error", "not", "the", "a", "an", "is", "was",
    "has", "does", "will", "can", "cannot", "no", "found",
}


def load_manifest():
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"manifest not found: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def normalize(text: str):
    return " ".join(text.lower().strip().split())


def split_camelcase(token: str):
    """Split camelCase/PascalCase tokens into sub-tokens.

    >>> split_camelcase("setOperateMode")
    ['set', 'operate', 'mode']
    """
    parts = re.findall(r"[a-z0-9]+|[A-Z][a-z0-9]*", token)
    return [p.lower() for p in parts if p]


def tokenize(text: str):
    """Tokenize query text with camelCase/snake_case awareness.

    CamelCase splitting happens on the original-case text before
    lowercasing, so setOperateMode yields set/operate/mode plus
    the full lowercased token.
    """
    # Split on common separators first, keeping original case
    flat = text.replace("/", " ").replace("-", " ").replace("_", " ")
    raw_tokens = [t for t in flat.split() if t]

    tokens = []
    extra = []
    for token in raw_tokens:
        lowered = token.lower()
        if lowered not in NOISE_WORDS:
            tokens.append(lowered)
        if re.search(r"[a-z][A-Z]", token):
            extra.extend(split_camelcase(token))

    seen = set()
    result = []
    for t in tokens + extra:
        if t not in seen and t not in NOISE_WORDS:
            seen.add(t)
            result.append(t)
    return result


def generate_bigrams(tokens):
    """Generate adjacent token pairs as higher-precision match signals."""
    return [" ".join(tokens[i : i + 2]) for i in range(len(tokens) - 1)]


def _submatch(a: str, b: str):
    """True if a contains b or b contains a."""
    return a in b or b in a


def score_entry(entry, query_text: str, query_tokens):
    score = 0
    reasons = []
    title = normalize(entry.get("title", ""))
    category = normalize(entry.get("category", ""))
    tags = [normalize(t) for t in entry.get("tags", [])]
    keywords = [normalize(k) for k in entry.get("keywords", [])]
    triggers = [normalize(t) for t in entry.get("triggers", [])]
    related = [normalize(r) for r in entry.get("related", [])]
    aliases = [normalize(a) for a in entry.get("aliases", [])]

    matched_fields = set()

    # --- full-query level ---
    if query_text:
        for trigger in triggers:
            if _submatch(query_text, trigger):
                score += WEIGHTS["trigger_exact"]
                reasons.append(f"trigger:{trigger}")
                matched_fields.add("trigger")
                break

    if query_text and _submatch(query_text, title):
        score += WEIGHTS["title"]
        reasons.append("title")
        matched_fields.add("title")

    if query_text:
        for alias in aliases:
            if _submatch(query_text, alias):
                score += WEIGHTS["alias"]
                reasons.append(f"alias:{alias}")
                matched_fields.add("alias")
                break

    if query_text:
        for kw in keywords:
            if _submatch(query_text, kw):
                score += WEIGHTS["keyword"]
                reasons.append(f"keyword_full:{kw}")
                matched_fields.add("keyword")
                break

    if query_text:
        for tag in tags:
            if _submatch(query_text, tag):
                score += WEIGHTS["tag"]
                reasons.append(f"tag_full:{tag}")
                matched_fields.add("tag")
                break

    # --- token-level ---
    for token in query_tokens:
        if len(token) < 2:
            continue

        if not any("title:" in r for r in reasons):
            title_words = title.split()
            if any(_submatch(token, tw) for tw in title_words):
                score += WEIGHTS["title"]
                reasons.append(f"title:{token}")
                matched_fields.add("title")

        for kw in keywords:
            if _submatch(token, kw):
                score += WEIGHTS["keyword"]
                reasons.append(f"keyword:{token}")
                matched_fields.add("keyword")
                break

        for tag in tags:
            if _submatch(token, tag):
                score += WEIGHTS["tag"]
                reasons.append(f"tag:{token}")
                matched_fields.add("tag")
                break

        for trigger in triggers:
            if _submatch(token, trigger):
                score += WEIGHTS["trigger_partial"]
                reasons.append(f"trigger_token:{token}")
                matched_fields.add("trigger")
                break

        for alias in aliases:
            if _submatch(token, alias):
                score += WEIGHTS["alias"]
                reasons.append(f"alias_token:{token}")
                matched_fields.add("alias")
                break

        if token == category or _submatch(token, category):
            score += WEIGHTS["category"]
            reasons.append(f"category:{token}")
            matched_fields.add("category")

        for item in related:
            if token in item:
                score += WEIGHTS["related"]
                reasons.append(f"related:{token}")
                matched_fields.add("related")
                break

    # --- bigram matching (higher precision) ---
    bigrams = generate_bigrams(query_tokens)
    for bigram in bigrams:
        bigram_compact = bigram.replace(" ", "")
        for trigger in triggers:
            if bigram in trigger or bigram_compact in trigger:
                score += WEIGHTS["trigger_exact"]
                reasons.append(f"bigram_trigger:{bigram}")
                matched_fields.add("bigram")
                break

    # --- multi-field bonus ---
    if len(matched_fields) >= 2:
        bonus = WEIGHTS["multi_token_bonus"] * min(len(matched_fields), 5)
        score += bonus
        reasons.append(f"multi_field:{len(matched_fields)}")

    return score, reasons


def rank_entries(entries, query: str):
    query_text = normalize(query)
    query_tokens = tokenize(query)
    ranked = []
    for entry in entries:
        score, reasons = score_entry(entry, query_text, query_tokens)
        if score > 0:
            ranked.append((score, reasons, entry))
    ranked.sort(key=lambda item: (-item[0], item[2].get("title", "")))
    return ranked


def cmd_find(args):
    manifest = load_manifest()
    ranked = rank_entries(manifest.get("entries", []), args.query)
    if not ranked:
        print("No matching knowledge entries found.")
        return 1
    for score, reasons, entry in ranked[: args.limit]:
        print(f"[{score}] {entry['title']}")
        print(f"Path: {entry['path']}")
        print(f"Rule: {entry.get('rule') or 'N/A'}")
        print(f"Tags: {', '.join(entry.get('tags', [])) or 'N/A'}")
        print(f"Triggers: {', '.join(entry.get('triggers', [])) or 'N/A'}")
        print(f"Why matched: {', '.join(reasons)}")
        print()
    return 0


def cmd_related(args):
    return cmd_find(args)


def cmd_quick_ref(args):
    key = args.key.strip().lower().replace(" ", "-")
    path = ROOT / "indexes" / "quick-ref" / f"{key}.md"
    if not path.exists():
        print(f"Quick ref not found for: {args.key}")
        return 1
    print(path.read_text(encoding="utf-8").rstrip())
    return 0


def main():
    parser = argparse.ArgumentParser(prog="kb")
    subparsers = parser.add_subparsers(dest="command", required=True)

    find_parser = subparsers.add_parser("find")
    find_parser.add_argument("query")
    find_parser.add_argument("--limit", type=int, default=5)
    find_parser.set_defaults(func=cmd_find)

    related_parser = subparsers.add_parser("related")
    related_parser.add_argument("query")
    related_parser.add_argument("--limit", type=int, default=5)
    related_parser.set_defaults(func=cmd_related)

    quick_ref_parser = subparsers.add_parser("quick-ref")
    quick_ref_parser.add_argument("key")
    quick_ref_parser.set_defaults(func=cmd_quick_ref)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
