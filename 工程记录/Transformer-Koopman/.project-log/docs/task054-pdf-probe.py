import fitz, re, json, pathlib

p = r"D:/Project/Transformer-Koopman/Transformer-Koopman/论文/新版本/build_font/Main.pdf"
d = fitz.open(p)
norm = re.sub(r"\s+", " ", "\n".join(pg.get_text() for pg in d))
ctx = []
for m in re.finditer(r"Placeholder", norm):
    ctx.append(norm[max(0, m.start() - 70): m.start() + 70])
drawn = [norm[max(0, m.start() - 90): m.start() + 40]
         for m in re.finditer(r"figure to be drawn", norm)]
pathlib.Path("task054-pdf-captions.json").write_text(
    json.dumps({"placeholder_contexts": ctx, "drawn_contexts": drawn},
               indent=1, ensure_ascii=False), encoding="utf-8")
print("ok", len(ctx), len(drawn))
