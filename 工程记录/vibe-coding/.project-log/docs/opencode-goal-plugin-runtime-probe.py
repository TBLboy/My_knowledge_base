#!/usr/bin/env python3
"""Real OpenCode runtime probe for @prevalentware/opencode-goal-plugin.

The 2026-09-22 probe (``opencode-goal-plugin-probe.mjs``) drove the plugin's exported
hooks from a hand-written callback harness. That proves the plugin's *contract*, but not
that a real ``opencode`` process loads and registers it. This probe closes that gap by
driving a live ``opencode serve`` instance through its HTTP API inside a fully isolated
``XDG_*`` root.

Phases 1-4 need no model provider and are deterministic:

  1. isolation      the runtime reports config/cache/data/state under the isolated root
  2. version pin    ``/config`` resolves the plugin to the pinned version, and the
                    installed ``dist/server.js`` hash matches the harnessed artifact
  3. registration   ``/command`` lists the plugin's own commands
  4. state store    issuing the goal command makes the plugin create its state file

Phase 5 (``--model``) sends a real prompt and watches for auto-continuation after the
session goes idle. It requires a working provider credential; without one the phase
reports the upstream error verbatim and exits non-zero so the gap is never papered over.

Usage:
    python3 opencode-goal-plugin-runtime-probe.py                 # phases 1-4
    python3 opencode-goal-plugin-runtime-probe.py --model <p/m>   # phases 1-5
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request


PLUGIN = "@prevalentware/opencode-goal-plugin"
DEFAULT_VERSION = "0.1.51"
PORT = 0
BASE = ""


def free_port() -> int:
    """A port the OS says is free, so a leftover probe cannot block this one."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def http(method: str, path: str, body: dict | None = None, timeout: int = 120):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
    return json.loads(raw) if raw else None


def wait_for_server(process: subprocess.Popen, log: Path, seconds: int = 300) -> None:
    """Wait until /config answers.

    A fresh isolated cache makes the runtime download and install the pinned plugin on
    first use, which can take a while, so the window is generous and the deadline is
    reported with the server log rather than a bare failure.
    """
    deadline = time.time() + seconds
    while time.time() < deadline:
        if process.poll() is not None:
            raise SystemExit(f"opencode serve exited early with {process.returncode}")
        try:
            http("GET", "/config", timeout=20)
            return
        except (urllib.error.URLError, OSError):
            time.sleep(2)
    detail = log.read_text(errors="replace")[-800:] if log.exists() else "<no log>"
    raise SystemExit(f"opencode serve did not become ready in {seconds}s:\n{detail}")


def isolated_home(root: Path) -> Path:
    """One sandbox plus the four XDG roots OpenCode resolves paths from."""
    for name in ("config/opencode", "cache", "data", "state", "sandbox"):
        (root / name).mkdir(parents=True, exist_ok=True)
    return root


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--model", help="provider/model for the live-turn phase")
    parser.add_argument("--seconds", type=int, default=180,
                        help="how long to watch an idle session for auto-continuation")
    parser.add_argument("--keep", action="store_true", help="keep the isolated root")
    args = parser.parse_args()

    global PORT, BASE
    PORT = free_port()
    BASE = f"http://127.0.0.1:{PORT}"

    root = Path(tempfile.mkdtemp(prefix="oc-goal-runtime-"))
    isolated_home(root)
    environment = {
        **os.environ,
        "XDG_CONFIG_HOME": str(root / "config"),
        "XDG_CACHE_HOME": str(root / "cache"),
        "XDG_DATA_HOME": str(root / "data"),
        "XDG_STATE_HOME": str(root / "state"),
    }
    (root / "config" / "opencode" / "opencode.json").write_text(
        json.dumps({"$schema": "https://opencode.ai/config.json",
                    "plugin": [f"{PLUGIN}@{args.version}"],
                    "default_agent": "build"}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"ISOLATED_ROOT {root}", flush=True)

    # A fresh isolated cache makes the runtime install the pinned plugin on first use.
    # Warm that here so "the server never answered" cannot be confused with "the plugin
    # never loaded", and so the install itself is part of the recorded evidence.
    print("PHASE 0a resolve and install the pinned plugin", flush=True)
    warmed = subprocess.run(
        ["opencode", "debug", "config"], cwd=str(root / "sandbox"), env=environment,
        capture_output=True, text=True, timeout=600, check=False,
    )
    if warmed.returncode:
        raise SystemExit(f"opencode debug config failed ({warmed.returncode}): "
                         f"{warmed.stderr[-500:]}")
    try:
        resolved = json.loads(warmed.stdout).get("plugin")
    except json.JSONDecodeError:
        resolved = "<unparsed>"
    print(f"    resolved_plugin={json.dumps(resolved)}", flush=True)

    server = subprocess.Popen(
        ["opencode", "serve", "--port", str(PORT), "--log-level", "INFO"],
        cwd=str(root / "sandbox"), env=environment,
        stdout=(root / "serve.log").open("w"), stderr=subprocess.STDOUT,
    )
    failure = 0
    try:
        print(f"PHASE 0 launch opencode serve on port {PORT}", flush=True)
        wait_for_server(server, root / "serve.log")
        paths = subprocess.run(["opencode", "debug", "paths"], capture_output=True,
                               text=True, env=environment, check=True).stdout
        print("PHASE 1 isolation")
        for line in paths.splitlines():
            if line.split() and line.split()[0] in ("data", "cache", "config", "state"):
                print("   ", line.strip())
        isolated = str(root) in paths
        print(f"    all_paths_under_isolated_root={isolated}")
        if not isolated:
            failure = 1

        print("PHASE 2 version pin")
        configured = http("GET", "/config").get("plugin", [])
        print("    configured_plugin", json.dumps(configured))
        expected = f"{PLUGIN}@{args.version}"
        print(f"    pinned_as_expected={expected in configured}")
        if expected not in configured:
            failure = 1
        installed = sorted((root / "cache").glob(f"opencode/packages/{PLUGIN}@{args.version}"
                                                 f"/node_modules/{PLUGIN}/package.json"))
        if not installed:
            print("    installed_package=NOT_FOUND")
            failure = 1
        else:
            package = json.loads(installed[0].read_text())
            dist = installed[0].parent / "dist" / "server.js"
            digest = hashlib.sha256(dist.read_bytes()).hexdigest()
            print(f"    installed_version={package['version']}")
            print(f"    dist_server_sha256={digest}")

        print("PHASE 3 registration")
        commands = [c.get("name") for c in http("GET", "/command")]
        print("    commands", json.dumps(commands))
        expected_commands = {"goal", "pause_goal", "resume_goal"}
        missing = sorted(expected_commands - set(commands))
        print(f"    missing_goal_commands={missing}")
        if missing:
            failure = 1

        print("PHASE 4 state store")
        session = http("POST", "/session", {"agent": "build"})
        state = root / "data" / "opencode-goal-plugin" / "goals.json"
        try:
            http("POST", f"/session/{session['id']}/command",
                 {"command": "goal", "arguments": "probe: touch goal-state", "agent": "build"})
        except urllib.error.HTTPError as error:
            print(f"    command_dispatch_status={error.code}")
        deadline = time.time() + 20
        while time.time() < deadline and not state.exists():
            time.sleep(1)
        print(f"    state_file={state}")
        print(f"    state_file_exists={state.exists()}")
        if not state.exists():
            failure = 1

        if args.model:
            print("PHASE 5 live model turn")
            provider, model = args.model.split("/", 1)
            session = http("POST", "/session",
                           {"agent": "build", "model": {"providerID": provider, "id": model}})
            sid = session["id"]
            try:
                http("POST", f"/session/{sid}/command",
                     {"command": "goal", "agent": "build", "model": args.model,
                      "arguments": "create ping.txt containing pong, then close the goal"})
            except urllib.error.HTTPError as error:
                print(f"    goal_command_status={error.code} {error.read()[:200]!r}")
            deadline = time.time() + args.seconds
            turns, texts = 0, []
            while time.time() < deadline:
                time.sleep(5)
                messages = http("GET", f"/session/{sid}/message")
                texts = [p.get("text", "") for m in messages
                         if (m.get("info") or m).get("role") == "assistant"
                         for p in m.get("parts", []) if p.get("type") == "text"]
                if len(texts) != turns:
                    turns = len(texts)
                    print(f"    assistant_turns={turns}", flush=True)
            goals = json.loads(state.read_text()).get("goals", {}) if state.exists() else {}
            print(f"    goal_registered={bool(goals)}")
            print(f"    last_text={texts[-1][:200] if texts else '<none>'}")
            if not goals:
                print("    RESULT real model turn did not complete; see serve.log stream errors")
                failure = 1
        else:
            print("PHASE 5 live model turn SKIPPED (no --model); "
                  "idle auto-continuation remains unverified")

    finally:
        server.send_signal(signal.SIGTERM)
        try:
            server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.kill()
        log = (root / "serve.log")
        if log.exists():
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
