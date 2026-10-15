"""Reflow/renumber verification: compile twice, compare content, render all pages."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import fitz

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / '.project-log/docs'
PAPER = ROOT / 'Transformer-Koopman' / '\u8bba\u6587' / '\u65b0\u7248\u672c'
OUT = PAPER / 'build_equations'
EXE = Path(r'C:\Users\12187\AppData\Local\Temp\opencode\tectonic\tectonic.exe')
OUT.mkdir(exist_ok=True)
before = (DOCS / 'task053-before.tex').read_text(encoding='utf-8')
source = PAPER / 'Main.tex'
after = source.read_text(encoding='utf-8')
REFERENCE_COMPLEMENTS = {
    r'\eqref{eq:Lipschitz_constants}': r'\eqref{eq:transition_Lipschitz_constant} and \eqref{eq:Lipschitz_constants}',
    r'\eqref{eq:QP_coefficients}': r'\eqref{eq:QP_Hessian} and \eqref{eq:QP_coefficients}',
}
# Exact reviewer-approved delta, not a general allowance for prose/ref changes.
expected_before = before
for original, complemented in REFERENCE_COMPLEMENTS.items():
    expected_before = expected_before.replace(original, complemented)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unbox(text):
    # Remove only boxed wrapper, retaining its exact balanced-brace argument.
    while r'\boxed{' in text:
        start = text.index(r'\boxed{')
        inner = start + len(r'\boxed{')
        depth, end = 1, inner
        while depth:
            if text[end] == '{':
                depth += 1
            elif text[end] == '}':
                depth -= 1
            end += 1
        text = text[:start] + text[inner:end-1] + text[end:]
    return text


def canonical(text):
    matrices = []
    def protect(match):
        matrices.append(re.sub(r'\s+', '', match.group(0)))
        return f'MATRIXTOKEN{len(matrices)-1}ENDTOKEN'
    text = re.sub(r'\\begin\{(bmatrix|pmatrix|matrix|cases|array)\}.*?\\end\{\1\}', protect, text, flags=re.S)
    text = unbox(text)
    text = re.sub(r'\\(?:begin|end)\{(?:equation\*?|align\*?|gather\*?|gathered|aligned|split|alignedat)\}', '', text)
    text = re.sub(r'\\label\{[^}]+\}', '', text)
    text = re.sub(r'\\(?:qquad|quad|nonumber|notag)\b', '', text)
    text = text.replace('{}', '').replace(r'\\', '').replace('&', '')
    text = re.sub(r'\s+', '', text)
    for i, matrix in enumerate(matrices):
        text = text.replace(f'MATRIXTOKEN{i}ENDTOKEN', matrix)
    return text


BLOCK = re.compile(r'\\begin\{(equation\*?|align\*?|gather\*?)\}(.*?)\\end\{\1\}', re.S)


def prose(text):
    return re.sub(r'\s+', ' ', BLOCK.sub('', text)).strip()


def inventory(text):
    result = []
    for match in BLOCK.finditer(text):
        kind, body = match.groups()
        result.append({'line': text.count('\n', 0, match.start())+1,
                       'environment': kind, 'labels': re.findall(r'\\label\{([^}]+)\}', body),
                       'tex': body.strip()})
    return result


commands = []
source_hash = sha(source)
for number in (1, 2):
    command = [str(EXE), '--only-cached', '--keep-logs', '--keep-intermediates',
               '--reruns', '2', '--outdir', str(OUT), 'Main.tex']
    p = subprocess.run(command, cwd=PAPER, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (DOCS / f'task053-compile-{number}.txt').write_bytes(p.stdout)
    if (OUT / 'Main.log').exists():
        (DOCS / f'task053-pass-{number}.log').write_bytes((OUT / 'Main.log').read_bytes())
    commands.append({'command': command, 'returncode': p.returncode})
    if p.returncode:
        raise RuntimeError(p.stdout.decode(errors='replace'))
log = (OUT / 'Main.log').read_text(encoding='utf-8', errors='replace')
warnings = {
    'overfull': re.findall(r'[^\n]*Overfull[^\n]*', log),
    'underfull': re.findall(r'[^\n]*Underfull[^\n]*', log),
    'references': re.findall(r'[^\n]*(?:(?:Reference|Citation)[^\n]*undefined|There were undefined (?:references|citations)|Label[^\n]*multiply defined|Rerun to get|Label\(s\) may have changed)[^\n]*', log),
    'errors': re.findall(r'(?m)^![^\n]*', log),
    'font': re.findall(r'[^\n]*(?:Font Warning|font shape|inputenc Warning)[^\n]*', log),
}


def labels(path):
    return dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', path.read_text(encoding='utf-8')))


old_labels = labels(PAPER / 'build_layout/Main.aux')
new_labels = labels(OUT / 'Main.aux')
label_keys = re.findall(r'\\label\{([^}]+)\}', after)
old_source_labels = set(re.findall(r'\\label\{([^}]+)\}', before))
diff = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                  fromfile='before/Main.tex', tofile='after/Main.tex'))
(DOCS / 'task053-equations.diff').write_text(diff, encoding='utf-8')
pdf = fitz.open(OUT / 'Main.pdf')
renders = OUT / 'rendered'
renders.mkdir(exist_ok=True)
boundary_issues, tags = [], []
for index, page in enumerate(pdf):
    page.get_pixmap(matrix=fitz.Matrix(1.8, 1.8), alpha=False).save(renders / f'page-{index+1:02d}.png')
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                x0, y0, x1, y1 = span['bbox']
                text = span['text']
                if y0 < 55 or y1 > 755 or not text.strip() or (index == 0 and y0 < 180):
                    continue
                if x0 < 46.964 or x1 > 565.037 or (x0 < 300.023 and x1 > 302.023):
                    boundary_issues.append({'page': index+1, 'bbox': span['bbox'], 'text': text})
                if re.fullmatch(r'\(\d+\)', text.strip()) and (abs(x1-300.023)<2 or abs(x1-563.037)<2):
                    tags.append({'page': index+1, 'bbox': span['bbox'], 'text': text})
tag_numbers = [int(t['text'][1:-1]) for t in tags]
refs_before = re.findall(r'\\(?:eqref|ref|cite)\{[^}]+\}', expected_before)
refs_after = re.findall(r'\\(?:eqref|ref|cite)\{[^}]+\}', after)
report = {
    'commands': commands, 'layout_only_canonical_match': canonical(expected_before) == canonical(after),
    'prose_unchanged': prose(expected_before) == prose(after),
    'reference_and_citation_keys_unchanged': refs_before == refs_after,
    'allowed_reference_complements': REFERENCE_COMPLEMENTS,
    'existing_label_keys_preserved': old_source_labels.issubset(new_labels),
    'source_label_keys_unique': len(label_keys) == len(set(label_keys)),
    'label_number_map': {k:{'before':old_labels.get(k),'after':v} for k,v in new_labels.items() if k.startswith('eq:')},
    'boxed_removed': r'\boxed' not in after,
    'source_sha256': source_hash, 'source_unchanged_during_compile': source_hash == sha(source),
    'warnings': warnings, 'pdf_pages': len(pdf), 'boundary_issues': boundary_issues,
    'boundary_tolerance_bp': 2, 'equation_tag_positions': tags,
    'visible_tags_contiguous_and_unique': bool(tags) and tag_numbers == list(range(1, len(tags)+1)),
    'visible_tag_count': len(tags), 'display_inventory': inventory(after),
    'limitations': ['Font substitution and underfull warnings remain; not submission-ready.',
                    'Layout/no-renumber errors are checked; no mathematical theory recertification.',
                    'Geometry is only supplementary to visual review.']
}
def expected_tag_count(text):
    count = 0
    for match in BLOCK.finditer(text):
        kind, body = match.groups()
        if '*' in kind:
            continue
        if kind == 'equation':
            count += 1
            continue
        stack, row = [], ''
        for token in re.split(r'(\\begin\{[^}]+\}|\\end\{[^}]+\}|\\\\)', body):
            if token.startswith(r'\begin{'):
                stack.append(token)
            elif token.startswith(r'\end{'):
                stack.pop()
            elif token == r'\\' and not stack:
                count += int(bool(row.strip()) and r'\nonumber' not in row and r'\notag' not in row)
                row = ''
                continue
            row += token
        count += int(bool(row.strip()) and r'\nonumber' not in row and r'\notag' not in row)
    return count
report['expected_tag_count_from_source'] = expected_tag_count(after)
report['visible_tag_count_matches_source'] = len(tags) == report['expected_tag_count_from_source']
eq_numbers = [int(v) for k,v in new_labels.items() if k.startswith('eq:') and v.isdigit()]
report['aux_equation_numbers_within_visible_tags'] = bool(eq_numbers) and set(eq_numbers).issubset(tag_numbers)
checks = ['layout_only_canonical_match', 'prose_unchanged', 'reference_and_citation_keys_unchanged',
          'existing_label_keys_preserved', 'source_label_keys_unique', 'boxed_removed',
          'source_unchanged_during_compile', 'visible_tags_contiguous_and_unique',
          'visible_tag_count_matches_source', 'aux_equation_numbers_within_visible_tags']
report['failed_automated_checks'] = [k for k in checks if not report[k]]
report['failed_automated_checks'] += [f'warnings.{k}' for k in ('overfull','references','errors') if warnings[k]]
if boundary_issues:
    report['failed_automated_checks'].append('boundary_issues')
report['visual_review'] = 'pending; tag ownership and grouping require independent artifact inspection'
if not report['layout_only_canonical_match']:
    a, b = canonical(expected_before), canonical(after)
    mismatch = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    report['canonical_mismatch_context'] = {'index': mismatch,
        'before': a[max(0,mismatch-100):mismatch+150],
        'after': b[max(0,mismatch-100):mismatch+150]}
(DOCS / 'task053-validation.json').write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding='utf-8')
files = [source, PAPER/'IEEEtran.cls', OUT/'Main.pdf', OUT/'Main.log', OUT/'Main.aux',
         Path(__file__), DOCS/'task053-validation.json', DOCS/'task053-equations.diff',
         DOCS/'task053-before.tex', DOCS/'task053-spec.json']
files += list(renders.glob('*.png')) + list(DOCS.glob('task053-compile-*.txt')) + list(DOCS.glob('task053-pass-*.log'))
file_names = [str(p.relative_to(ROOT)).replace('\\','/') for p in files]
(DOCS/'task053-binding.json').write_text(json.dumps({'file_hashes':dict(zip(file_names,map(sha,files)))},indent=2),encoding='utf-8')
(DOCS/'task053-covers.json').write_text(json.dumps({'files':file_names,'tasks':['TASK-053'],'requirements':[]},indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('equation_tag_positions','display_inventory')}, indent=2))
if report['failed_automated_checks']:
    raise SystemExit(1)
