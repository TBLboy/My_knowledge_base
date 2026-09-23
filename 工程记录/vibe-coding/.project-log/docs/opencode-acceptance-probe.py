#!/usr/bin/env python3
"""TASK-075 real OpenCode end-to-end acceptance.

Every earlier OpenCode probe answered one question in isolation. This one installs the
shipped surface the way a user would, then drives a live `opencode serve` through the
scenarios TASK-075 has to sign off:

  S1 lifecycle   the agent reads real .project-log state and a write task grows the ledger
  S2 goal        /goal auto-continues, /pause_goal stops it, /resume_goal restarts it
  S3 compaction  an active goal survives session compaction
  S4 permission  delegation to a role outside permission.task is refused
  S5 read-only   a verification-reviewer session cannot edit files
  S6 degradation the fallback path when the task tool is unavailable

Everything runs inside one temporary XDG root; the user's ~/.config/opencode is never
touched. Results are printed as `CHECK <name> <PASS|FAIL|SKIP> <detail>` so a reader can
see exactly which claim each line supports.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request


BASE = ""
CHECKS: list[tuple[str, str, str]] = []


def check(name: str, ok: bool | None, detail: str) -> None:
    verdict = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
    CHECKS.append((name, verdict, detail))
    print(f"CHECK {name} {verdict} {detail}", flush=True)


def http(method: str, path: str, body: dict | None = None, timeout: int = 180,
         tolerant: bool = False):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")[:600]
        raise RuntimeError(f"{method} {path} -> HTTP {error.code}: {detail}") from error
    except (TimeoutError, socket.timeout) as error:
        # Some endpoints (notably `/session/<id>/command` with an active goal) keep
        # the request open for as long as the agent keeps working. The side effect is
        # already dispatched server-side, so callers that only need the side effect
        # can tolerate the timeout and observe the result by polling instead.
        if tolerant:
            print(f"    note: {method} {path} did not return within {timeout}s "
                  "(side effect already dispatched)", flush=True)
            return None
        raise RuntimeError(f"{method} {path} timed out after {timeout}s") from error
    except urllib.error.URLError as error:
        reason = getattr(error, "reason", error)
        if tolerant and isinstance(reason, (TimeoutError, socket.timeout)):
            print(f"    note: {method} {path} did not return within {timeout}s "
                  "(side effect already dispatched)", flush=True)
            return None
        raise RuntimeError(f"{method} {path} failed: {error}") from error
    return json.loads(raw) if raw else None


def command(session: str, name: str, model: str, arguments: str = "",
            timeout: int = 90) -> None:
    """Dispatch a slash command without waiting for the agent to stop working."""
    http("POST", f"/session/{session}/command",
         {"command": name, "agent": "vibe-main", "model": model, "arguments": arguments},
         timeout=timeout, tolerant=True)


def messages(session: str) -> list:
    return http("GET", f"/session/{session}/message") or []


def census(session: str) -> tuple[int, int]:
    msgs = messages(session)
    users = sum(1 for m in msgs if (m.get("info") or m).get("role") == "user")
    assistants = sum(1 for m in msgs if (m.get("info") or m).get("role") == "assistant")
    return users, assistants


def goal_entry(state_path: Path, session: str) -> dict:
    if not state_path.is_file():
        return {}
    goals = json.loads(state_path.read_text()).get("goals", {})
    return goals.get(session) or next(iter(goals.values()), {}) if goals else {}


def wait_for_turns(session: str, minimum: int, seconds: int) -> int:
    deadline = time.time() + seconds
    seen = 0
    while time.time() < deadline:
        time.sleep(5)
        users, assistants = census(session)
        if assistants != seen:
            seen = assistants
            print(f"    turns user={users} assistant={assistants}", flush=True)
        if assistants >= minimum:
            return assistants
    return seen


def ledger_lines(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(1 for line in path.read_text(errors="replace").splitlines() if line.strip())


def wait_for_ledger_growth(path: Path, before: int, seconds: int) -> int:
    deadline = time.time() + seconds
    current = ledger_lines(path)
    while time.time() < deadline and current <= before:
        time.sleep(5)
        current = ledger_lines(path)
    return current


def response_text(session: str) -> str:
    return "\n".join(p.get("text", "") for m in messages(session)
                     for p in m.get("parts", []) if p.get("type") == "text")


def prepare_root(root: Path, repo: Path) -> tuple[Path, dict]:
    """Install the shipped surface into `root`; return (project dir, child env)."""
    config = root / "config" / "opencode"
    project = root / "work"
    project.mkdir(parents=True, exist_ok=True)
    install = subprocess.run(
        [sys.executable, str(repo / "scripts" / "opencode_installer.py"), "install",
         "--opencode-home", str(config), "--skip-preflight", "--skip-plugin-install"],
        capture_output=True, text=True, check=False,
    )
    if install.returncode:
        print(install.stdout[-2000:], install.stderr[-2000:])
        raise SystemExit("installer failed")
    print("SURFACE installed via opencode_installer.py", flush=True)

    environment = {
        **os.environ,
        "XDG_CONFIG_HOME": str(root / "config"),
        "XDG_CACHE_HOME": str(root / "cache"),
        "XDG_DATA_HOME": str(root / "data"),
        "XDG_STATE_HOME": str(root / "state"),
    }
    credential = root / "data" / "opencode" / "auth.json"
    credential.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(os.path.expanduser("~/.local/share/opencode/auth.json")), credential)
    credential.chmod(0o600)
    return project, environment


def boot_server(project: Path, environment: dict, root: Path):
    """Start `opencode serve`, wait for its port, and point BASE at it."""
    global BASE
    log = root / "serve.log"
    server = subprocess.Popen(
        ["opencode", "serve", "--port", "0", "--log-level", "INFO"],
        cwd=str(project), env=environment,
        stdout=log.open("w"), stderr=subprocess.STDOUT,
    )
    deadline = time.time() + 180
    port = None
    while time.time() < deadline and port is None:
        time.sleep(1)
        for line in log.read_text(errors="replace").splitlines():
            if "listening on" in line:
                port = int(line.rsplit(":", 1)[1].strip())
    if port is None:
        server.send_signal(signal.SIGTERM)
        raise SystemExit(f"server did not start:\n{log.read_text(errors='replace')[-1500:]}")
    BASE = f"http://127.0.0.1:{port}"
    print(f"PORT {port}", flush=True)
    return server, log


def stop_server(server, log: Path, keep: bool, root: Path) -> None:
    server.send_signal(signal.SIGTERM)
    try:
        server.wait(timeout=15)
    except subprocess.TimeoutExpired:
        server.kill()
    errors = [line for line in log.read_text(errors="replace").splitlines()
              if "level=ERROR" in line]
    if errors:
        print("SERVE_LOG_ERRORS")
        for line in errors[:6]:
            print("   ", line[:300])
    if keep:
            print(f"KEPT {root}")
    else:
        shutil.rmtree(root, ignore_errors=True)


def collapse_task_permission(agent_path: Path) -> None:
    """Rewrite the agent frontmatter so `task` keeps only a bare `"*": deny`.

    The installer copies a per-role task allowlist into every agent's frontmatter,
    and agent-level permissions merge on top of the global config. Collapsing the
    allowlist here is what actually removes delegation from the Task tool
    description, i.e. what makes the task tool unavailable to the agent.
    """
    lines = agent_path.read_text().splitlines()
    out: list[str] = []
    in_task = False
    for line in lines:
        if line.strip() == "task:":
            out.append(line)
            out.append('    "*": deny')
            in_task = True
            continue
        if in_task:
            if line.startswith(" ") or line.startswith("\t"):
                continue
            in_task = False
        out.append(line)
    agent_path.write_text("\n".join(out) + "\n")


def main() -> int:
    global BASE
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="opencode-go/glm-5.3-flash")
    parser.add_argument("--seconds", type=int, default=180)
    parser.add_argument("--phases", default="s1,s2,s3,s4,s5,s6",
                        help="comma separated subset of s1,s2,s3,s4,s5,s6")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args()
    phases = {item.strip() for item in args.phases.split(",") if item.strip()}

    repo = Path(__file__).resolve().parents[2] / "vibe-coding"
    root = Path(tempfile.mkdtemp(prefix="oc-acceptance-"))
    print(f"ISOLATED_ROOT {root}", flush=True)

    # Install the shipped surface exactly the way a user would.
    project, environment = prepare_root(root, repo)
    config = root / "config" / "opencode"

    # A real project log the agent must read and update.
    runtime = config / "vibe-workflow" / "scripts" / "vibe.py"
    init = subprocess.run(
        [sys.executable, str(runtime), "--root", str(project), "init"],
        capture_output=True, text=True, check=False,
    )
    print(f"PROJECT_LOG init rc={init.returncode}", flush=True)
    ledger = project / ".project-log" / "ledger" / "v1" / "ledger.jsonl"

    provider, model = args.model.split("/", 1)
    model_spec = {"providerID": provider, "id": model}

    server, log = boot_server(project, environment, root)
    try:
        goal_state = root / "data" / "opencode-goal-plugin" / "goals.json"

        if "s1" in phases:
            print("PHASE S1 lifecycle read/write", flush=True)
            authoritative = json.loads(subprocess.run(
                [sys.executable, str(runtime), "--root", str(project), "status"],
                capture_output=True, text=True, check=True,
            ).stdout)
            real_project_id = authoritative["project_id"]
            before = ledger_lines(ledger)
            session = http("POST", "/session", {"agent": "vibe-main", "model": model_spec})
            sid = session["id"]
            http("POST", f"/session/{sid}/message", {
                "agent": "vibe-main", "model": {"providerID": provider, "modelID": model},
                "parts": [{"type": "text", "text": (
                    "Do two steps and report both verbatim.\n"
                    "Step 1: read the authoritative project state from .project-log and report the "
                    "exact project_id value you read.\n"
                    "Step 2: run exactly this shell command and report its JSON output:\n"
                    f'"{sys.executable}" "{runtime}" --root "{project}" record create '
                    '--kind business-atom --id BL-ACCEPT-001 '
                    '--title "Acceptance probe atom" --status active\n'
                )}],
            })
            wait_for_turns(sid, 2, args.seconds)
            after = wait_for_ledger_growth(ledger, before, args.seconds)
            joined = response_text(sid)
            check("s1.reads_authoritative_state", real_project_id in joined,
                  f"reported_project_id={real_project_id!r} present={real_project_id in joined}")
            check("s1.write_grows_ledger", after > before,
                  f"ledger lines {before} -> {after} record_id_present={after > before}")

        if "s2" in phases:
            print("PHASE S2 goal lifecycle", flush=True)
            session = http("POST", "/session", {"agent": "vibe-main", "model": model_spec})
            sid = session["id"]
            command(sid, "goal", args.model,
                    "Keep working until told otherwise: on each turn append one line "
                    "to journal.txt with an incrementing number. Never close the goal.")
            active = wait_for_turns(sid, 3, args.seconds)
            entry = goal_entry(goal_state, sid)
            check("s2.auto_continuation", active >= 2,
                  f"assistant turns={active} goal_status={entry.get('status')!r}")

            before_pause = census(sid)
            try:
                command(sid, "pause_goal", args.model)
            except RuntimeError as error:
                check("s2.pause_stops_continuation", False, f"pause_goal dispatch failed: {error}")
            else:
                # /pause_goal cannot cancel a continuation that is already in flight, so
                # wait for the session to go quiet before deciding, and report the
                # in-flight turns as an observation rather than as the pass condition.
                deadline = time.time() + 90
                settled = census(sid)[1]
                while time.time() < deadline:
                    time.sleep(10)
                    current = census(sid)[1]
                    if current == settled:
                        break
                    settled = current
                after_pause = census(sid)
                time.sleep(20)
                quiet = census(sid)
                paused_entry = goal_entry(goal_state, sid)
                check("s2.pause_stops_continuation",
                      quiet[1] == after_pause[1] and paused_entry.get("status") == "paused",
                      f"in_flight_turns_after_pause={after_pause[1] - before_pause[1]} "
                      f"stable_after={quiet[1] == after_pause[1]} "
                      f"status={paused_entry.get('status')!r}")

                try:
                    command(sid, "resume_goal", args.model)
                except RuntimeError as error:
                    check("s2.resume_restarts_continuation", False,
                          f"resume_goal dispatch failed: {error}")
                else:
                    resumed = wait_for_turns(sid, after_pause[1] + 1, args.seconds)
                    resumed_entry = goal_entry(goal_state, sid)
                    check("s2.resume_restarts_continuation",
                          resumed > after_pause[1] and resumed_entry.get("status") == "active",
                          f"assistant turns={resumed} status={resumed_entry.get('status')!r}")

        if "s3" in phases:
            print("PHASE S3 compaction survival", flush=True)
            session = http("POST", "/session", {"agent": "vibe-main", "model": model_spec})
            sid = session["id"]
            command(sid, "goal", args.model,
                    "Remember the codeword ORCHID and keep working: append one line to "
                    "note.txt each turn. Never close the goal.")
            wait_for_turns(sid, 2, args.seconds)
            before = goal_entry(goal_state, sid)
            compacted = None
            try:
                http("POST", f"/session/{sid}/summarize",
                     {"providerID": provider, "modelID": model}, timeout=150, tolerant=True)
                compacted = "summarize returned"
            except urllib.error.HTTPError as error:
                compacted = f"summarize HTTP {error.code}"
            except RuntimeError as error:
                compacted = f"summarize could not be confirmed: {error}"
            time.sleep(15)
            after = goal_entry(goal_state, sid)
            check("s3.compaction_keeps_goal",
                  bool(after) and after.get("objective") == before.get("objective"),
                  f"{compacted}; objective preserved={after.get('objective') == before.get('objective')} "
                  f"status={after.get('status')!r}")

        if "s4" in phases:
            print("PHASE S4 permission.task enforcement", flush=True)
            session = http("POST", "/session", {"agent": "vibe-main", "model": model_spec})
            sid = session["id"]
            http("POST", f"/session/{sid}/message", {
                "agent": "vibe-main", "model": {"providerID": provider, "modelID": model},
                "parts": [{"type": "text", "text": (
                    "Use the task tool to delegate to the subagent named 'build'. "
                    "Ask it to say hello. If the tool refuses, report the refusal verbatim."
                )}],
            })
            wait_for_turns(sid, 1, args.seconds)
            children = http("GET", f"/session/{sid}/children") or []
            texts = [p.get("text", "") for m in messages(sid)
                     for p in m.get("parts", []) if p.get("type") == "text"]
            joined = " ".join(texts).lower()
            refused = any(word in joined for word in
                          ("denied", "not allowed", "permission", "拒绝", "不允许"))
            check("s4.disallowed_role_blocked", len(children) == 0 or refused,
                  f"child_sessions={len(children)} refusal_language={refused}")

        if "s5" in phases:
            print("PHASE S5 reviewer read-only", flush=True)
            target = project / "reviewer-should-not-write.txt"
            try:
                parent = http("POST", "/session", {"agent": "vibe-main", "model": model_spec})
                child = http("POST", "/session", {
                    "parentID": parent["id"], "agent": "verification-reviewer",
                    "model": model_spec,
                })
                http("POST", f"/session/{child['id']}/message", {
                    "agent": "verification-reviewer",
                    "model": {"providerID": provider, "modelID": model},
                    "parts": [{"type": "text", "text": (
                        "Create a file named reviewer-should-not-write.txt containing the word ok."
                    )}],
                })
                wait_for_turns(child["id"], 1, args.seconds)
                texts = [p.get("text", "") for m in messages(child["id"])
                         for p in m.get("parts", []) if p.get("type") == "text"]
            except RuntimeError as error:
                check("s5.reviewer_cannot_edit", False, f"session setup failed: {error}")
            else:
                joined = " ".join(texts).lower()
                refused = any(word in joined for word in
                              ("denied", "not allowed", "permission", "read-only", "cannot edit",
                               "拒绝", "不允许", "只读"))
                check("s5.reviewer_cannot_edit", (not target.exists()) and refused,
                      f"file_created={target.exists()} refusal_language={refused}")

    except Exception as error:  # noqa: BLE001 - keep the summary even on a harness error
        check("phases.unhandled_error", False, f"{type(error).__name__}: {error}"[:400])
    finally:
        stop_server(server, log, args.keep, root)

    if "s6" in phases:
        print("PHASE S6 task-tool-unavailable degradation", flush=True)
        root2 = Path(tempfile.mkdtemp(prefix="oc-acceptance-s6-"))
        print(f"ISOLATED_ROOT {root2}", flush=True)
        project2, environment2 = prepare_root(root2, repo)
        config2 = root2 / "config" / "opencode"
        settings = json.loads((config2 / "opencode.json").read_text())
        # OpenCode keeps the `task` tool in the prompt as long as any subagent is
        # allowed, so disabling the tool alone is not enough: the per-role allowlist
        # copied into the agent frontmatter must be collapsed as well, which is what
        # makes delegation genuinely unavailable to the agent.
        settings["tools"] = {"task": False}
        settings.setdefault("permission", {})["task"] = {"*": "deny"}
        (config2 / "opencode.json").write_text(json.dumps(settings, indent=2) + "\n")
        collapse_task_permission(config2 / "agents" / "vibe-main.md")
        runtime2 = config2 / "vibe-workflow" / "scripts" / "vibe.py"
        subprocess.run([sys.executable, str(runtime2), "--root", str(project2), "init"],
                       capture_output=True, text=True, check=False)
        server2, log2 = boot_server(project2, environment2, root2)
        try:
            session = http("POST", "/session", {"agent": "vibe-main", "model": model_spec})
            sid = session["id"]
            http("POST", f"/session/{sid}/message", {
                "agent": "vibe-main", "model": {"providerID": provider, "modelID": model},
                "parts": [{"type": "text", "text": (
                    "Delegate to the subagent named 'codebase-onboarder': ask it to list the "
                    "top-level entries of this project directory. If the task tool is unavailable, "
                    "do that listing yourself in this session and include the exact marker "
                    "'serial-role-fallback' in your reply."
                )}],
            })
            wait_for_turns(sid, 2, args.seconds)
            children = http("GET", f"/session/{sid}/children") or []
            child_agents = [(child or {}).get("agent") for child in children]
            joined = response_text(sid)
            marker = "serial-role-fallback" in joined.lower()
            check("s6.no_subagent_when_task_disabled", len(children) == 0,
                  f"child_sessions={len(children)} child_agents={child_agents}")
            check("s6.serial_fallback_declared", marker,
                  f"marker_present={marker} reply_chars={len(joined)}")
        finally:
            stop_server(server2, log2, args.keep, root2)

    failed = [name for name, verdict, _ in CHECKS if verdict == "FAIL"]
    print(f"ACCEPTANCE_CHECKS {len(CHECKS)} failed={len(failed)}")
    for name in failed:
        print(f"   FAILED {name}")
    print(f"PROBE_STATUS {'ok' if not failed else 'failed'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
