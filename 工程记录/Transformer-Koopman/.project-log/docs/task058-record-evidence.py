# -*- coding: utf-8 -*-
import pathlib
import subprocess
import sys

root = pathlib.Path(r"D:/Project/Transformer-Koopman")
docs = root / ".project-log" / "docs"
py = open(r"C:\Users\12187\.config\opencode\vibe-python").read().strip()
base = [py, r"C:\Users\12187\.config\opencode\vibe-workflow\scripts\vibe.py", "--root", str(root)]
args = ["evidence", "record", "--id", "EV-TASK058-INTRO-002", "--kind", "verification",
        "--subject", "Introduction rewrite: 39 refs ordered (diehl2005rtistability dropped as uncited after removing off-topic stability sentence) by first citation, no defensive/state-preserving wording, compile clean (0 overfull/undefined/font warning), claim-source check",
        "--status", "valid", "--task-id", "TASK-058",
        "--covers", "@" + str(docs / "task058-covers.json"),
        "--version-binding", "@" + str(docs / "task058-binding.json")]
r = subprocess.run(base + args, capture_output=True, text=True, encoding="utf-8")
print(r.returncode, (r.stdout or r.stderr)[-400:].replace("\n", " "))
