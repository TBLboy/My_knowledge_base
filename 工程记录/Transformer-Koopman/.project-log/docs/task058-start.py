# -*- coding: utf-8 -*-
import json
import pathlib
import shutil
import subprocess
import sys

root = pathlib.Path(r"D:/Project/Transformer-Koopman")
paper = root / "Transformer-Koopman" / "论文" / "新版本"
docs = root / ".project-log" / "docs"
shutil.copyfile(paper / "Main.tex", docs / "task058-before.tex")

base = [sys.executable if False else open(r"C:\Users\12187\.config\opencode\vibe-python").read().strip(),
        r"C:\Users\12187\.config\opencode\vibe-workflow\scripts\vibe.py", "--root", str(root)]


def run(args):
    r = subprocess.run(base + args, capture_output=True, text=True, encoding="utf-8")
    print(r.returncode, (r.stdout or r.stderr)[-300:].replace("\n", " "))
    if r.returncode != 0:
        sys.exit(1)


run(["task", "handoff", "--task-id", "TASK-054", "--next-action",
     "REV-TASK054-001=conditional (no web/PDF/shell in reviewer). Superseded by TASK-058 Introduction rewrite which changes Main.tex; "
     "re-run a network-capable reference pass and a go review on the final text. Artefacts: .project-log/docs/task057-reference-verification.md, task054-review-final.json."])
spec = {
    "risk": "high", "risk_class": "strict", "implementer": "vibe-main", "owner": "vibe-main",
    "scope": "Main.tex Introduction section only (prose, citations in the Introduction, bibliography order); abstract, other sections, experiments, figures untouched",
    "done_when": [
        "Introduction rewritten as one problem-driven storyline: MPC need, Koopman linearization via lifting, hand-picked then learned lifting, fixed-pair limitation, history in lifting vs history in transition, prediction and control consequences, this paper",
        "Every citation in the Introduction supports the sentence it is attached to, checked against the cited source; DeepKoopFormer not described as context-dependent transition; Wu 2026 not described as a learned neural predictor",
        "All 40 references remain cited and ordered by first citation; no undefined references",
        "No state-preserving modifier, no defensive filler, no experimental result or performance claim in the Introduction",
        "Recompiled with no overfull, no undefined references, no font warnings; independent review go",
    ],
}
run(["task", "create", "--id", "TASK-058", "--title",
     "Rewrite Introduction as a problem-driven storyline grounded in exemplar papers",
     "--goal-id", "GOAL-002", "--extensions", json.dumps(spec)])
run(["task", "begin", "--task-id", "TASK-058", "--run-id", "RUN-058", "--next-action",
     "Draft new Introduction, apply to Main.tex, reorder bibliography, recompile, validate, independent review"])
