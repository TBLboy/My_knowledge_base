"""TASK-054 deterministic validation (paper edits after TASK-053).

ASCII-only stdout; full results are written to JSON files.
"""
import difflib
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(r"D:/Project/Transformer-Koopman")
PAPER = ROOT / "Transformer-Koopman" / "论文" / "新版本"
DOCS = ROOT / ".project-log" / "docs"
MAIN = PAPER / "Main.tex"
BEFORE = DOCS / "task054-before.tex"
PDF = PAPER / "build_font" / "Main.pdf"


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    src = MAIN.read_text(encoding="utf-8")
    before = BEFORE.read_text(encoding="utf-8")
    out = {"task": "TASK-054", "files": {}, "checks": {}}

    body, _, bib = src.partition("\\begin{thebibliography}")

    # --- bibliography ---
    bib_keys = re.findall(r"\\bibitem\{([^}]+)\}", bib)
    # --- citation order in body ---
    cite_order = []
    for m in re.finditer(r"\\cite\{([^}]+)\}", body):
        for k in m.group(1).split(","):
            k = k.strip()
            if k and k not in cite_order:
                cite_order.append(k)
    total_cites = len(re.findall(r"\\cite\{", body))

    out["checks"]["bibitem_count"] = len(bib_keys)
    out["checks"]["distinct_cited_keys"] = len(cite_order)
    out["checks"]["total_cite_commands"] = total_cites
    out["checks"]["bibitem_order_equals_first_citation_order"] = bib_keys == cite_order
    out["checks"]["uncited_bibitems"] = [k for k in bib_keys if k not in cite_order]
    out["checks"]["cites_without_bibitem"] = [k for k in cite_order if k not in bib_keys]
    if bib_keys != cite_order:
        out["checks"]["first_order_mismatch"] = [
            [i, bib_keys[i] if i < len(bib_keys) else None,
             cite_order[i] if i < len(cite_order) else None]
            for i in range(max(len(bib_keys), len(cite_order)))
            if i >= len(bib_keys) or i >= len(cite_order) or bib_keys[i] != cite_order[i]
        ]

    # --- banned modifier wording ---
    out["checks"]["state_preserving_occurrences"] = len(
        re.findall(r"state[- ]preserving", src, flags=re.IGNORECASE))

    # --- figure placeholders ---
    out["checks"]["figph_macros"] = len(re.findall(r"\\figph\{", src))
    out["checks"]["figure_environments"] = len(re.findall(r"\\begin\{figure\}", src))
    out["checks"]["figure_star_environments"] = len(re.findall(r"\\begin\{figure\*\}", src))
    out["checks"]["placeholder_captions"] = len(
        re.findall(r"Placeholder; figure to be drawn\.", src))
    out["checks"]["figure_labels"] = re.findall(r"\\label\{(fig:[^}]+)\}", src)
    out["checks"]["figrefs"] = re.findall(r"\\ref\{(fig:[^}]+)\}", body)

    # --- residual defensive-phrase scan (leftovers of the trimmed class) ---
    patterns = {
        "we_do_not_claim": r"we do not claim",
        "not_necessarily": r"not necessarily",
        "does_not_imply": r"does not imply",
        "it_is_not_our_intent": r"it is not our intent",
        "we_emphasize_that": r"we emphasize that",
        "no_claim_of": r"no claim of",
        "should_not_be_read": r"should not be read",
        "we_stress": r"we stress",
    }
    out["checks"]["residual_defensive_phrases"] = {
        name: len(re.findall(pat, src, flags=re.IGNORECASE))
        for name, pat in patterns.items()}

    # --- appendix / structure ---
    out["checks"]["appendix_sections"] = len(re.findall(r"\\section\*?\{", src.partition("\\appendix")[2])) \
        if "\\appendix" in src else 0
    out["checks"]["sections"] = re.findall(r"\\section\{([^}]*)\}", src)
    out["checks"]["appendix_labels"] = re.findall(r"\\label\{(app:[^}]+)\}", src)

    # --- diff ---
    diff = list(difflib.unified_diff(
        before.splitlines(keepends=True), src.splitlines(keepends=True),
        fromfile="task054-before.tex", tofile="Main.tex", n=2))
    (DOCS / "task054-changes.diff").write_text("".join(diff), encoding="utf-8")
    added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    out["checks"]["diff_lines_added"] = len(added)
    out["checks"]["diff_lines_removed"] = len(removed)
    out["checks"]["diff_hunks"] = sum(1 for l in diff if l.startswith("@@"))
    out["checks"]["diff_sha256"] = hashlib.sha256(
        "".join(diff).encode("utf-8")).hexdigest()

    # --- compiled artefacts ---
    log = (PAPER / "build_font" / "Main.log")
    logtext = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    out["checks"]["log_overfull"] = len(re.findall(r"Overfull", logtext))
    out["checks"]["log_underfull"] = len(re.findall(r"Underfull", logtext))
    out["checks"]["log_font_warning"] = len(re.findall(r"Font Warning", logtext))
    out["checks"]["log_undefined"] = len(re.findall(
        r"(?:Reference|Citation) `[^']*' on page \d+ undefined", logtext))
    m = re.search(r"Output written on Main\.xdv \((\d+) pages", logtext)
    out["checks"]["log_pages"] = int(m.group(1)) if m else None

    try:
        import fitz
        doc = fitz.open(str(PDF))
        out["checks"]["pdf_pages"] = doc.page_count
        text = "\n".join(p.get_text() for p in doc)
        out["checks"]["pdf_placeholder_captions"] = text.count(
            "Placeholder; figure to be drawn.")
        out["checks"]["pdf_contains_state_preserving"] = "state-preserving" in text
        out["checks"]["pdf_has_data_driven_hyphen"] = "data-driven" in text
        out["checks"]["pdf_has_data_endash"] = "data\u2013driven" in text
        out["checks"]["pdf_size_bytes"] = PDF.stat().st_size
        doc.close()
    except Exception as exc:  # pragma: no cover
        out["checks"]["pdf_error"] = repr(exc)

    out["files"] = {
        "Main.tex": {"sha256": sha(MAIN), "bytes": MAIN.stat().st_size},
        "build_font/Main.pdf": {"sha256": sha(PDF), "bytes": PDF.stat().st_size},
        "task054-before.tex": {"sha256": sha(BEFORE), "bytes": BEFORE.stat().st_size},
        "task054-changes.diff": {"sha256": sha(DOCS / "task054-changes.diff")},
    }
    (DOCS / "task054-validation.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=True), encoding="ascii")
    print("ok")


if __name__ == "__main__":
    sys.exit(main())
