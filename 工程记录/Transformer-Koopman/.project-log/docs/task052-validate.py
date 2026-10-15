"""Compile, compare mathematical content/numbering and render layout evidence."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import difflib
import fitz

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / '.project-log/docs'
PAPER = ROOT / 'Transformer-Koopman' / '\u8bba\u6587' / '\u65b0\u7248\u672c'
OUT = PAPER / 'build_layout'
EXE = r'C:\Users\12187\AppData\Local\Temp\opencode\tectonic\tectonic.exe'
OUT.mkdir(exist_ok=True)
before = (DOCS / 'task052-before.tex').read_text(encoding='utf-8')
after = (PAPER / 'Main.tex').read_text(encoding='utf-8')


def canonical(text):
    # Layout-only whitelist. Exact textual math/prose otherwise retained.
    text = re.sub(r'\\(?:begin|end)\{(?:gathered|aligned|split)\}', '', text)
    text = text.replace(r'\le{}', r'\le').replace(r'={}', '=')
    text = re.sub(r'\\(?:qquad|quad)\b', '', text)
    return re.sub(r'\s+', '', text.replace(r'\\', '').replace('&', ''))


commands = []
source_before = hashlib.sha256((PAPER / 'Main.tex').read_bytes()).hexdigest()
for number in (1, 2):
    command = [EXE, '--only-cached', '--keep-logs', '--keep-intermediates',
               '--reruns', '2', '--outdir', str(OUT), 'Main.tex']
    proc = subprocess.run(command, cwd=PAPER, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (DOCS / f'task052-compile-{number}.txt').write_bytes(proc.stdout)
    commands.append({'command': command, 'returncode': proc.returncode})
    if proc.returncode:
        raise RuntimeError(proc.stdout.decode(errors='replace'))
log = (OUT / 'Main.log').read_text(encoding='utf-8', errors='replace')
warnings = {
    'overfull': re.findall(r'[^\n]*Overfull[^\n]*', log),
    'underfull': re.findall(r'[^\n]*Underfull[^\n]*', log),
    'references': re.findall(r'[^\n]*(?:(?:Reference|Citation)[^\n]*undefined|There were undefined (?:references|citations)|Label[^\n]*multiply defined|Rerun to get|Label\(s\) may have changed)[^\n]*', log),
    'errors': re.findall(r'(?m)^![^\n]*', log),
    'font': re.findall(r'[^\n]*(?:Font Warning|font shape|inputenc Warning)[^\n]*', log),
}


def labels(path):
    return re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', path.read_text(encoding='utf-8'))


old_labels = labels(PAPER / 'build_current/Main.aux')
new_labels = labels(OUT / 'Main.aux')
diff = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                  fromfile='before/Main.tex', tofile='after/Main.tex'))
(DOCS / 'task052-layout.diff').write_text(diff, encoding='utf-8')
pdf = fitz.open(OUT / 'Main.pdf')
renders = OUT / 'rendered'
renders.mkdir(exist_ok=True)
boundary_issues = []
number_positions = []
for index, page in enumerate(pdf):
    page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(renders / f'page-{index+1:02d}.png')
    # IEEEtran journal letter: textwidth=43pc, columnsep=1pc.
    # TeX pt -> PDF bp; each column is 21pc. Allow <=2bp microtype protrusion.
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                x0, y0, x1, y1 = span['bbox']
                text = span['text']
                if y0 < 60 or y1 > 742 or not text.strip():
                    continue  # running header and footer
                if index == 0 and y0 < 180:
                    continue  # full-width title/author block
                if x0 < 46.964 or x1 > 565.037 or (x0 < 300.023 and x1 > 302.023):
                    boundary_issues.append({'page': index+1, 'bbox': span['bbox'], 'text': text})
                if re.fullmatch(r'\(\d+\)', text.strip()):
                    number_positions.append({'page': index+1, 'bbox': span['bbox'], 'text': text})
old_pdf = fitz.open(PAPER / 'build_current/Main.pdf')
def equation_numbers(document):
    return [s['text'].strip() for page in document
            for b in page.get_text('dict')['blocks'] for line in b.get('lines', [])
            for s in line.get('spans', []) if re.fullmatch(r'\(\d+\)', s['text'].strip())]
report = {
    'commands': commands,
    'layout_only_canonical_match': canonical(before) == canonical(after),
    'numbered_labels_unchanged': old_labels == new_labels,
    'label_count': len(new_labels),
    'rendered_equation_number_sequence_unchanged': equation_numbers(old_pdf) == equation_numbers(pdf),
    'rendered_equation_numbers': equation_numbers(pdf),
    'source_sha256': source_before,
    'source_unchanged_during_compile': source_before == hashlib.sha256((PAPER/'Main.tex').read_bytes()).hexdigest(),
    'warnings': warnings,
    'pdf_pages': len(pdf),
    'boundary_issues': boundary_issues,
    'boundary_tolerance_bp': 2,
    'equation_number_positions': number_positions,
    'limitations': ['Font substitution warnings inherited from compiler remain.',
                    'Geometry checks support but do not replace visual review.',
                    'No experiments or figures added/edited. No mathematical theory re-certification.'],
}
(DOCS / 'task052-validation.json').write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k != 'equation_number_positions'}, indent=2))
