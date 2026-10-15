"""Extract the removed material of TASK-054 from the diff for reviewer inspection."""
import json
import pathlib
import re

DOCS = pathlib.Path(r"D:/Project/Transformer-Koopman/.project-log/docs")
diff = (DOCS / "task054-changes.diff").read_text(encoding="utf-8").splitlines()
removed = [l[1:] for l in diff if l.startswith("-") and not l.startswith("---")]
added = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]


def sentences(lines):
    text = " ".join(lines)
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p for p in parts if len(p) > 12]


rem_s = sentences(removed)
add_s = sentences(added)
markers = [
    "do not claim", "not necessarily", "does not imply", "cannot be", "we note that",
    "it should be noted", "not intended", "no guarantee", "we caution", "only a",
    "does not establish", "should not", "is not a", "cannot guarantee",
]
flagged = [s for s in rem_s if any(m in s.lower() for m in markers)]

out = {
    "diff_sha256": __import__("hashlib").sha256(
        (DOCS / "task054-changes.diff").read_bytes()).hexdigest(),
    "removed_lines": len(removed),
    "added_lines": len(added),
    "removed_sentence_fragments": len(rem_s),
    "added_sentence_fragments": len(add_s),
    "removed_fragments_with_hedging_markers": len(flagged),
    "flagged_removed_fragments": flagged,
    "removed_lines_all": removed,
}
(DOCS / "task054-removed-material.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=True), encoding="ascii")
print("ok", len(rem_s), len(flagged))
