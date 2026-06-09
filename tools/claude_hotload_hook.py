#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOTLOAD_TOOL = ROOT / "tools" / "kb_hotload.py"

PROMPT_KEYS = [
    "prompt",
    "user_prompt",
    "message",
    "text",
    "input",
]


def extract_prompt(payload):
    for key in PROMPT_KEYS:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        for key in PROMPT_KEYS:
            value = tool_input.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}

    prompt = extract_prompt(payload)
    if not prompt:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit"}}, ensure_ascii=False))
        return 0

    completed = subprocess.run(
        [sys.executable, str(HOTLOAD_TOOL), prompt],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    response = {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit"}}
    additional = completed.stdout.strip()
    if completed.returncode == 0 and additional and additional != "No hot-load trigger matched.":
        response["hookSpecificOutput"]["additionalContext"] = additional
    print(json.dumps(response, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
