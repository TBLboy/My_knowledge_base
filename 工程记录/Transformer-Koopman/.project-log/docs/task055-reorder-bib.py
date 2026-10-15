"""Reorder thebibliography entries by first citation order (IEEE numeric style).
Only moves whole \\bibitem blocks; text and cite keys are untouched."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAPER = next(p for p in (ROOT / 'Transformer-Koopman' / '\u8bba\u6587').iterdir()
             if p.is_dir() and p.name != '\u8001\u7248\u672c')
src = PAPER / 'Main.tex'
raw = src.read_bytes()
bom = raw.startswith(b'\xef\xbb\xbf')
text = raw.decode('utf-8-sig')

a = text.index(r'\begin{thebibliography}')
b = text.index(r'\end{thebibliography}')
head, bib, tail = text[:a], text[a:b], text[b:]

open_tag = re.match(r'\\begin\{thebibliography\}\{[^}]*\}\s*', bib)
prefix = open_tag.group(0)
body = bib[len(prefix):]
parts = re.split(r'(?=\\bibitem\{)', body)
parts = [p for p in parts if p.strip()]
items = {}
order_in_file = []
for p in parts:
    key = re.match(r'\\bibitem\{([^}]+)\}', p).group(1)
    items[key] = p.rstrip() + '\n\n'
    order_in_file.append(key)

# first-citation order in the body (everything before the bibliography)
cited = []
for m in re.finditer(r'\\cite\{([^}]+)\}', head):
    for k in (x.strip() for x in m.group(1).split(',')):
        if k not in cited:
            cited.append(k)

missing = [k for k in cited if k not in items]
uncited = [k for k in order_in_file if k not in cited]
DROP = '--drop-uncited' in sys.argv
new_order = [k for k in cited if k in items] + ([] if DROP else uncited)
assert DROP or sorted(new_order) == sorted(order_in_file), 'entry set changed'
new_bib = prefix + ''.join(items[k] for k in new_order)
new_text = head + new_bib + tail
out = ('\ufeff' if bom else '') + new_text
src.write_bytes(out.encode('utf-8'))
report = {'entries': len(order_in_file), 'cited_unique': len(cited),
          'missing_keys': missing, 'uncited_entries': uncited,
          'moved': sum(1 for i, k in enumerate(new_order) if order_in_file[i] != k)}
(ROOT / '.project-log/docs/task055-reorder-report.json').write_text(
    json.dumps({**report, 'new_order': new_order}, indent=1), encoding='ascii')
print(json.dumps(report))
