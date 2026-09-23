#!/usr/bin/env python3
"""Does a live OpenCode session actually delegate to a subagent through the task tool?

tests/test_opencode_surface.py proves the role files and permission.task rules are shaped
correctly, but a static shape is not delegation. This probe drives a real opencode serve in
an isolated XDG root, asks the primary agent to hand a bounded read-only review to
verification-reviewer, and checks whether OpenCode created a child session for it
(GET /session/{id}/children).

Usage:
    python3 opencode-subagent-delegation-probe.py --model opencode-go/glm-5.3-flash
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request


BASE = ""


def http(method: str, path: str, body: dict | None = None, timeout: int = 120):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
    return json.loads(raw) if raw else None


def main() -> int:
    global BASE
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="opencode-go/glm-5.3-flash")
    parser.add_argument("--seconds", type=int, default=180)
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args()

    root = Path(tempfile.mkdtemp(prefix="oc-delegation-"))
    for name in ("config/opencode", "cache", "data/opencode", "state", "sandbox"):
        (root / name).mkdir(parents=True, exist_ok=True)

    # The harness ships the real surface, so copy it the way the installer would.
    package = Path(__file__).resolve().parents[2] / "vibe-coding" / "runtime" / "opencode"
    for name in ("agents", "commands", "plugins"):
        shutil.copytree(package / name, root / "config" / "opencode" / name)

    (root / "config" / "opencode" / "opencode.json").write_text(json.dumps({
        "$schema": "https://opencode.ai/config.json",
        "plugin": ["./plugins/vibe-workflow.ts"],
        "default_agent": "vibe-main",
        "permission": {"task": {"*": "deny", "verification-reviewer": "allow"}},
    }, indent=2) + "\n", encoding="utf-8")

    credential = root / "data" / "opencode" / "auth.json"
    shutil.copyfile(Path(os.path.expanduser("~/.local/share/opencode/auth.json")), credential)
    credential.chmod(0o600)
    (root / "sandbox" / "README.md").write_text(
        "# Probe target\n\nThis file is the read-only artifact under review.\n", encoding="utf-8"
    )

    environment = {
        **os.environ,
        "XDG_CONFIG_HOME": str(root / "config"),
        "XDG_CACHE_HOME": str(root / "cache"),
        "XDG_DATA_HOME": str(root / "data"),
        "XDG_STATE_HOME": str(root / "state"),
    }
    print(f"ISOLATED_ROOT {root}", flush=True)
    log = root / "serve.log"
    server = subprocess.Popen(
        ["opencode", "serve", "--port", "0", "--log-level", "INFO"],
        cwd=str(root / "sandbox"), env=environment,
        stdout=log.open("w"), stderr=subprocess.STDOUT,
    )
    failure = 0
    try:
        # `--port 0` makes OpenCode pick a free port; read it back from the log.
        deadline = time.time() + 120
        port = None
        while time.time() < deadline and port is None:
            time.sleep(1)
            for line in log.read_text(errors="replace").splitlines():
                if "listening on" in line:
                    port = int(line.rsplit(":", 1)[1].strip())
        if port is None:
            raise SystemExit(f"server did not report a port:\n{log.read_text(errors='replace')}")
        BASE = f"http://127.0.0.1:{port}"
        print(f"PORT {port}", flush=True)

        provider, model = args.model.split("/", 1)
        session = http("POST", "/session",
                       {"agent": "vibe-main", "model": {"providerID": provider, "id": model}})
        sid = session["id"]
        print(f"SESSION {sid}", flush=True)
        http("POST", f"/session/{sid}/message", {
            "agent": "vibe-main", "model": {"providerID": provider, "modelID": model},
            "parts": [{"type": "text", "text": (
                "Delegate a bounded, read-only review of README.md in this directory to the "
                "verification-reviewer subagent using the task tool: ask it to report the "
                "exact first heading and whether the file mentions the word Probe. "
                "Then relay its answer verbatim. Do not do the review yourself."
            )}],
        })

        deadline = time.time() + args.seconds
        children: list = []
        while time.time() < deadline:
            time.sleep(5)
            children = http("GET", f"/session/{sid}/children") or []
            if children:
                break
        print(f"CHILD_SESSIONS {len(children)}", flush=True)

        tools = []
        for message in http("GET", f"/session/{sid}/message"):
            for part in message.get("parts", []):
                if part.get("type") == "tool":
                    tools.append(part.get("tool"))
        print(f"PRIMARY_TOOLS {json.dumps(tools)}", flush=True)
        print(f"DELEGATED {'task' in tools or bool(children)}", flush=True)
        for child in children:
            info = child.get("info", child) if isinstance(child, dict) else {}
            child_id = info.get("id")
            print(f"    child_id={child_id} title={info.get('title')!r}", flush=True)
            if child_id:
                print(f"    child_messages="
                      f"{len(http('GET', f'/session/{child_id}/message') or [])}", flush=True)
        if not children and "task" not in tools:
            print("RESULT no child session and no task tool call, so delegation is NOT verified")
            failure = 1
    finally:
        server.send_signal(signal.SIGTERM)
        try:
            server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.kill()
        errors = [line for line in log.read_text(errors="replace").splitlines()
                  if "level=ERROR" in line]
        if errors:
            print("SERVE_LOG_ERRORS")
            for line in errors[:5]:
                print("   ", line[:300])
        if args.keep:
            print(f"KEPT {root}")
        else:
            shutil.rmtree(root, ignore_errors=True)
    print(f"PROBE_STATUS {'ok' if failure == 0 else 'failed'}")
    return failure


if __name__ == "__main__":
    sys.exit(main())
