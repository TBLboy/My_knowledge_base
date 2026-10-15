# -*- coding: utf-8 -*-
import difflib
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(r"D:/Project/Transformer-Koopman")
DOCS = ROOT / ".project-log" / "docs"
PAPER = ROOT / "Transformer-Koopman" / "论文" / "新版本"
tex = (PAPER / "Main.tex").read_bytes().decode("utf-8-sig").replace("\r\n", "\n")
before = (DOCS / "task058-before.tex").read_bytes().decode("utf-8-sig").replace("\r\n", "\n")

a = tex.index("\\section{Introduction}")
b = tex.index("\\section{Preliminaries")
intro = tex[a:b]
(DOCS / "task058-intro.tex.txt").write_text(intro, encoding="utf-8")
diff = "".join(difflib.unified_diff(before.splitlines(True), tex.splitlines(True), "before", "after", n=1))
(DOCS / "task058-changes.diff").write_text(diff, encoding="utf-8")

body = tex[:tex.index("\\begin{thebibliography}")]
cited = []
for m in re.finditer(r"\\cite\{([^}]+)\}", body):
    for k in (x.strip() for x in m.group(1).split(",")):
        if k not in cited:
            cited.append(k)
bibkeys = re.findall(r"\\bibitem\{([^}]+)\}", tex)
log = (PAPER / "build_font" / "Main.log")
logt = log.read_text(encoding="utf-8", errors="ignore") if log.exists() else ""
intro_cites = []
for m in re.finditer(r"\\cite\{([^}]+)\}", intro):
    intro_cites += [x.strip() for x in m.group(1).split(",")]
words = len(re.sub(r"\\cite\{[^}]*\}|\$[^$]*\$|\\[a-zA-Z]+", " ", intro).split())
checks = {
    "bibitem_count": len(bibkeys), "distinct_cited": len(cited),
    "order_equals_first_citation": bibkeys == cited,
    "uncited": [k for k in bibkeys if k not in cited], "missing": [k for k in cited if k not in bibkeys],
    "state_preserving_in_intro": len(re.findall(r"state[- ]preserving", intro, re.I)),
    "defensive_in_intro": len(re.findall(r"we do not claim|not necessarily|does not imply|do not imply|by itself", intro, re.I)),
    "intro_words_approx": words, "intro_cite_keys": len(intro_cites),
    "log_overfull": len(re.findall(r"Overfull", logt)), "log_undefined": len(re.findall(r"undefined", logt, re.I)),
    "log_font_warning": len(re.findall(r"Font Warning", logt)),
    "intro_wu2026_cites": intro_cites.count("wu2026multistep"),
    "intro_deepkoopformer_cites": intro_cites.count("forootani2025deepkoopformer"),
}
(DOCS / "task058-validation.json").write_text(json.dumps(checks, indent=1), encoding="ascii")

arts = {
    "Transformer-Koopman/论文/新版本/Main.tex": PAPER / "Main.tex",
    "Transformer-Koopman/论文/新版本/build_font/Main.pdf": PAPER / "build_font" / "Main.pdf",
    ".project-log/docs/task058-changes.diff": DOCS / "task058-changes.diff",
    ".project-log/docs/task058-validation.json": DOCS / "task058-validation.json",
    ".project-log/docs/task058-intro.tex.txt": DOCS / "task058-intro.tex.txt",
}
hashes = {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in arts.items()}
(DOCS / "task058-covers.json").write_text(json.dumps({"files": sorted(arts), "tasks": ["TASK-058"]}, ensure_ascii=True), encoding="ascii")
(DOCS / "task058-binding.json").write_text(json.dumps({
    "git_commit": "none (paper directory untracked)", "diff_hash": hashes[".project-log/docs/task058-changes.diff"],
    "file_hashes": hashes}, indent=1, ensure_ascii=True), encoding="ascii")
print(json.dumps(checks, indent=1))
