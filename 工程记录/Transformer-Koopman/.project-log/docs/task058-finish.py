# -*- coding: utf-8 -*-
import pathlib
import subprocess
import json

root = pathlib.Path(r"D:/Project/Transformer-Koopman")
docs = root / ".project-log" / "docs"
py = open(r"C:\Users\12187\.config\opencode\vibe-python").read().strip()
base = [py, r"C:\Users\12187\.config\opencode\vibe-workflow\scripts\vibe.py", "--root", str(root)]


def run(args):
    r = subprocess.run(base + args, capture_output=True, text=True, encoding="utf-8")
    print(r.returncode, (r.stdout or r.stderr)[-500:].replace("\n", " "))
    return r.returncode


scope = {
    "task": "TASK-058", "risk_class": "strict",
    "scope": "Introduction rewrite of Main.tex (v2 after conditional review 1); judged from files only, reviewer had no shell/web",
    "deliberate_deviation": "references 40->39: diehl2005rtistability removed with the off-topic stability sentence; no uncited entry remains",
    "not_independently_verified": [
        "compile counts (main-agent self-report: 0 overfull, 0 undefined, 0 font warnings)",
        "external reference metadata",
        "exact gain-scheduling/QLPV titles"],
    "known_gap": "no general MPC textbook reference",
}
p = docs / "task058-review-scope.json"
p.write_text(json.dumps(scope, ensure_ascii=True, indent=1), encoding="ascii")
run(["review", "record", "--id", "REV-TASK058-001", "--task-id", "TASK-058", "--reviewer", "verification-reviewer",
     "--verdict", "go", "--scope", "@" + str(p), "--evidence-ref", "EV-TASK058-INTRO-002"])
run(["gate", "--task", "TASK-058"])
