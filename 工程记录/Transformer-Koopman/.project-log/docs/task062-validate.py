import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import fitz

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / '.project-log/docs'
REPO = ROOT / 'Transformer-Koopman'
PAPER = REPO / '论文/新版本'
before_bytes = (DOCS / 'task062-before.tex').read_bytes()
after_bytes = (PAPER / 'Main.tex').read_bytes()
before = before_bytes.decode('utf-8-sig')
after = after_bytes.decode('utf-8-sig')
start = r'\subsection{Two-Stage Training and Recursive Prediction}'
figure = r'\begin{figure}[H]'
old_a, new_a = before.index(start), after.index(start)
old_b, new_b = before.index(figure, old_a), after.index(figure, new_a)
old_section, section = before[old_a:old_b], after[new_a:new_b]

def equation(text, label):
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', text, re.S):
        if r'\label{' + label + '}' in match.group():
            return match.group()
    raise ValueError(label)

labels_before = re.findall(r'\\label\{([^}]+)\}', before)
labels_after = re.findall(r'\\label\{([^}]+)\}', after)
checks = {
    'prefix_unchanged_bytes': before_bytes[:before_bytes.index(start.encode())] == after_bytes[:after_bytes.index(start.encode())],
    'suffix_from_training_figure_unchanged_bytes': before_bytes[before_bytes.index(figure.encode(), before_bytes.index(start.encode())):] == after_bytes[after_bytes.index(figure.encode(), after_bytes.index(start.encode())):],
    'all_labels_order_unchanged': labels_before == labels_after,
    'duplicate_labels': sorted({x for x in labels_after if labels_after.count(x) > 1}),
    'unresolved_source_refs': sorted(set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', after)) - set(labels_after)),
    'rollout_equations_unchanged': all(equation(before, label) == equation(after, label) for label in ['eq:training_context_update', 'eq:recursive_prediction', 'eq:training_rollout_update', 'eq:rollout_shift', 'eq:rollout_input_shift']),
    'stage0_x_and_complete_z': all(s in equation(after, 'eq:training_one_step_objects') for s in [r'C_x\tilde\vz', r'\lambda_0\norm{\tilde\vz', r'\vz_{k+1}^{\mathrm{enc}}']),
    'stage1_x_and_complete_z': all(s in equation(after, 'eq:joint_training_loss') for s in [r'C_x\vz_{k+i|k}^{P}', r'\lambda_R\norm{\vz_{k+i|k}^{P}', r'\vz_{k+i}^{\mathrm{enc}}']),
    'positive_weights': r'\lambda_0>0' in section and r'\lambda_R>0' in section,
    'uniform_weights_retained': '$w_i=1/H_R$' in section,
    'algorithm_loop_structure_unchanged': re.findall(r'\\(?:FOR\{[^\n]*|ENDFOR)', old_section) == re.findall(r'\\(?:FOR\{[^\n]*|ENDFOR)', section),
    'obsolete_output_rows_claim_removed': 'the remaining rows are updated' not in section,
    'forbidden_implementation_words': re.findall(r'\b(?:teacher|detach|stop.gradient|autograd|EMA)\b', section, re.I),
}
logs = {}
for name in ['baseline', 'build1', 'build2']:
    text = (DOCS / f'task062-{name}.log').read_text(encoding='utf-8', errors='replace')
    logs[name] = {key: len(re.findall(pattern, text, re.I)) for key, pattern in {
        'overfull': r'Overfull', 'underfull': r'Underfull', 'undefined': r'undefined', 'font_warning': r'Font Warning', 'tex_errors': r'^!'
    }.items()}
    logs[name]['pages'] = re.findall(r'Output written on .*?\((\d+) pages', text)
pdf = fitz.open(PAPER / 'build_font/Main.pdf')
pdf_locations = []
for i, page in enumerate(pdf):
    text = page.get_text()
    if 'Two-Stage Training' in text or 'Algorithm 1' in text or 'Finite-Horizon Prediction Analysis' in text:
        pdf_locations.append({'page': i + 1, 'algorithm': 'Algorithm 1' in text, 'training_heading': 'Two-Stage Training' in text, 'theory_heading': 'Finite-Horizon Prediction Analysis' in text})
diff = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), 'task062-before.tex', 'Main.tex'))
(DOCS / 'task062-changes.diff').write_text(diff, encoding='utf-8')
result = {
    'checks': checks, 'logs': logs, 'pdf_pages': len(pdf), 'pdf_heading_locations': pdf_locations,
    'git_diff_stat': subprocess.check_output(['git', 'diff', '--stat'], cwd=REPO).decode('utf-8'),
    'limitations': ['No independent compiler execution by reviewer', 'No training-code alignment or gradient behavior tests', 'Tectonic used because pdflatex unavailable; Fontconfig environmental notice remains', 'Underfull boxes remain; no claim of visual submission readiness'],
}
(DOCS / 'task062-validation.json').write_text(json.dumps(result, indent=2, ensure_ascii=True), encoding='ascii')
assert all(v is True or v == [] for v in checks.values()), checks
assert all(logs[n][key] == 0 for n in ['build1', 'build2'] for key in ['overfull', 'undefined', 'font_warning', 'tex_errors'])
paths = [PAPER / 'Main.tex', PAPER / 'build_font/Main.pdf', DOCS / 'task062-before.tex', DOCS / 'task062-approved-review.md', DOCS / 'task062-changes.diff', DOCS / 'task062-validation.json', DOCS / 'task062-build1.log', DOCS / 'task062-build2.log']
hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(DOCS / 'task062-covers.json').write_text(json.dumps({'tasks': ['TASK-062'], 'files': list(hashes)}), encoding='ascii')
(DOCS / 'task062-binding.json').write_text(json.dumps({'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO).decode().strip(), 'diff_hash': hashes['.project-log/docs/task062-changes.diff'], 'file_hashes': hashes}, indent=2), encoding='ascii')
print(json.dumps(result, ensure_ascii=True, indent=2))
