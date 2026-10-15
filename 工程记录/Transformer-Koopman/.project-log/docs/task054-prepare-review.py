import hashlib
import json
import pathlib

ROOT = pathlib.Path(r"D:/Project/Transformer-Koopman")
DOCS = ROOT / ".project-log" / "docs"
PAPER = ROOT / "Transformer-Koopman" / "论文" / "新版本"

artifacts = {
    "Transformer-Koopman/论文/新版本/Main.tex": PAPER / "Main.tex",
    "Transformer-Koopman/论文/新版本/build_font/Main.pdf": PAPER / "build_font" / "Main.pdf",
    "Transformer-Koopman/论文/新版本/build_font/Main.log": PAPER / "build_font" / "Main.log",
    ".project-log/docs/task054-changes.diff": DOCS / "task054-changes.diff",
    ".project-log/docs/task054-validation.json": DOCS / "task054-validation.json",
    ".project-log/docs/task054-removed-material.json": DOCS / "task054-removed-material.json",
    ".project-log/docs/task057-reference-verification.md": DOCS / "task057-reference-verification.md",
    ".project-log/docs/task054-before.tex": DOCS / "task054-before.tex",
    ".project-log/docs/task054-font-note.md": DOCS / "task054-font-note.md",
    ".project-log/docs/task055-note.md": DOCS / "task055-note.md",
    ".project-log/docs/task056-note.md": DOCS / "task056-note.md",
}
hashes = {k: {"sha256": hashlib.sha256(v.read_bytes()).hexdigest(),
              "bytes": v.stat().st_size} for k, v in artifacts.items()}

validation = json.loads((DOCS / "task054-validation.json").read_text(encoding="utf-8"))
removed = json.loads((DOCS / "task054-removed-material.json").read_text(encoding="utf-8"))

scope = {
    "review_id": "REV-TASK054-001",
    "task": "TASK-054",
    "goal": "GOAL-002",
    "risk_class": "strict",
    "implementer": "vibe-main",
    "reviewer": "verification-reviewer",
    "verdict_semantics": (
        "go only if every claim below is confirmed by the listed artefact content the "
        "reviewer can read; conditional if a claim cannot be checked with the reviewer's "
        "available tools (state which); no-go if any artefact contradicts a claim."),
    "scope": ("Main.tex prose, bibliography and figure placeholders only; experiments and "
              "figures themselves untouched; no submission-ready claim."),
    "done_when": [
        "Abstract and 18 over-defensive sentences trimmed",
        "References ordered by first citation with 40 cited entries",
        "Every reference verified against authoritative metadata; clear typographic error corrected",
        "Three figure placeholders including one double-column figure",
        "Recompiled: no overfull, no undefined references, no font warnings",
    ],
    "artefacts": hashes,
    "claims": [
        {"id": "C1", "claim": "thebibliography has 40 \\bibitem entries; the set and order equal the "
                              "order of first \\cite in the body; no uncited entry and no cite without entry",
         "check": "task054-validation.json checks.bibitem_count/distinct_cited_keys/"
                  "bibitem_order_equals_first_citation_order/uncited_bibitems/cites_without_bibitem; "
                  "Main.tex can be re-read directly"},
        {"id": "C2", "claim": "no occurrence of 'state-preserving'/'state preserving' remains in the "
                              "source or in the rendered PDF",
         "check": "task054-validation.json checks.state_preserving_occurrences (0) and "
                  "checks.pdf_contains_state_preserving (false)"},
        {"id": "C3", "claim": "the over-defensive sentences were removed and replaced by direct "
                              "statements; no hedging pattern remains",
         "check": "task054-changes.diff (removals) and task054-removed-material.json "
                  "(flagged_removed_fragments); validation checks.residual_defensive_phrases all zero. "
                  "The count '18' is the implementer's tally of rewritten sentences, not an "
                  "independently derived number: judge whether the removed material supports it"},
        {"id": "C4", "claim": "three figure placeholders exist, one of them double-column, each with a "
                              "caption stating it is a placeholder, each referenced in the text",
         "check": "validation checks.figure_star_environments=1, placeholder_captions=3, "
                  "figure_labels=[fig:overview, fig:rollout, fig:freezing], figrefs same three; "
                  "the PDF text contains 'figure to be drawn' three times (one caption is "
                  "hyphenated across a line break as 'Place- holder; figure to be drawn.')"},
        {"id": "C5", "claim": "the 8-page build has 0 overfull boxes, 0 undefined references/"
                              "citations, 0 font warnings, 10 underfull boxes",
         "check": "validation checks.log_overfull/log_undefined/log_font_warning/log_underfull and "
                  "log_pages=8, pdf_pages=8; build_font/Main.log can be re-read directly"},
        {"id": "C6", "claim": "the bibliography typographic error 'data--driven' (en dash inside a "
                              "title) was corrected to 'data-driven' and the PDF shows a hyphen",
         "check": "validation checks.pdf_has_data_driven_hyphen=true, "
                  "checks.pdf_has_data_endash=false, plus the williams2015data entry in Main.tex"},
        {"id": "C7", "claim": "task057-reference-verification.md states one corrected and 39 verified "
                              "entries with per-entry sources and lists residual risks",
         "check": "read .project-log/docs/task057-reference-verification.md; confirm the table has 40 "
                  "rows numbered 1..40 and that the residual-risk section names the unverifiable items"},
    ],
    "known_limitations": [
        "Paywalled full texts were not read: venue/volume/page data come from publisher metadata, "
        "DBLP, arXiv, PubMed or official author publication lists, not from the PDFs.",
        "The 40 reference records were checked by the implementer through web lookups; if the "
        "reviewer has no web access it can only confirm internal consistency and its own knowledge.",
        "Two entries are arXiv preprints (wu2026multistep arXiv:2601.11901, forootani2026spectral "
        "arXiv:2602.02592) and may later acquire journal versions.",
        "vaswani2017attention page range 5998-6008 is the widely used proceedings numbering and is "
        "not shown on the NeurIPS site.",
        "The reference list carries no page numbers for ICLR/NeurIPS entries (liu2023koopa, "
        "li2025mamko, nie2023time), matching how those venues are cited.",
        "Experiments were not touched and no experimental claim is made; no submission-ready claim "
        "is made anywhere in this task.",
        "10 underfull boxes and the Tectonic 'Fontconfig error: Cannot load default config file' "
        "notice remain; both are cosmetic/environmental and were left unchanged.",
    ],
    "out_of_scope": [
        "experiments and experiment numbers",
        "actual figure artwork (placeholders only)",
        "submission-readiness judgement",
        "TASK-046/TASK-047 work",
    ],
    "reproduction_commands": [
        "D:\\conda\\envs\\edmddl2\\python.exe .project-log/docs/task054-validate.py",
        "D:\\conda\\envs\\edmddl2\\python.exe .project-log/docs/task054-removed-material.py",
        "tectonic --keep-logs --keep-intermediates --reruns 2 --outdir build_font Main.tex "
        "(run in Transformer-Koopman/论文/新版本)",
    ],
}
(DOCS / "task054-review-scope.json").write_text(
    json.dumps(scope, indent=1, ensure_ascii=False), encoding="utf-8")

covers = {"files": sorted(artifacts.keys()), "tasks": ["TASK-054"]}
(DOCS / "task054-covers.json").write_text(
    json.dumps(covers, indent=1, ensure_ascii=True), encoding="ascii")
binding = {
    "git_commit": "none (paper directory is untracked in the inner repository)",
    "diff_hash": hashes[".project-log/docs/task054-changes.diff"]["sha256"],
    "file_hashes": {k: v["sha256"] for k, v in hashes.items()},
}
(DOCS / "task054-binding.json").write_text(
    json.dumps(binding, indent=1, ensure_ascii=True), encoding="ascii")
print("ok")
print(json.dumps({k: v["sha256"][:12] for k, v in hashes.items()}, indent=1))
