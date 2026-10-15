"""Bounded algebra checks for audit remarks; not full theorem certification."""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

root = Path(__file__).resolve().parents[2]
repo = root / 'Transformer-Koopman'
new = repo / '杂项' / '新版本'
theory = new / 'Theory_Package'
out = root / '.project-log' / 'docs'
report = new / 'Theory_Package_Audit_and_Compact_Outline.md'
files = sorted(p for p in theory.glob('*.md') if p.name[:2] in [f'{i:02}' for i in range(1, 9)])
assert len(files) == 8
code = new / 'Temporary_Experiments' / 'controllers' / 'ltv_mpc.py'
checks = {}

g = 0.3
u = np.array([[1.0], [0.0]])
gamma = g * np.tanh(0.0)
correction_norm = float(np.linalg.norm(u @ np.diag([gamma]) @ u.T, 2))
assert correction_norm == 0.0 and g > 0.0
checks['fixed_network_supremum_counterexample'] = {'passed': True, 'zero_modulation_norm': correction_norm, 'g': g}

p = np.array([0.5, 0.5])
jac = np.diag(p) - np.outer(p, p)
spectral = float(np.linalg.norm(jac, 2))
assert abs(spectral - 0.5) < 1e-14
checks['softmax_optimal_constant_counterexample'] = {'passed': True, 'jacobian_spectral_norm': spectral}

# Jfr=(u-0.4)^2; Jfull=Jfr+0.1*u on [0,1].
# Ufr=0.4 and Ustar=0.35; compare any feasible reference, not a solver.
def full_cost(x):
    return (x - 0.4)**2 + 0.1*x

global_gap = full_cost(0.4) - full_cost(0.35)
eps = 0.1
ref_gaps = [full_cost(0.4) - full_cost(x) for x in np.linspace(0.0, 1.0, 1001)]
assert 0.0 <= global_gap <= 2*eps
assert max(ref_gaps) <= global_gap + 1e-14 and min(ref_gaps) < 0.0
checks['feasible_reference_cost_gap'] = {'passed': True, 'global_gap': global_gap, 'max_reference_gap': max(ref_gaps), 'min_reference_gap': min(ref_gaps), 'scope': 'any feasible reference, not an end-to-end optimizer test'}

text = report.read_text(encoding='utf-8')
assert not any((ord(ch) < 32 and ch not in '\n\r\t') or ord(ch) == 127 for ch in text)
assert text.count('```') % 2 == 0
assert all(f'| {i:02} ' in text for i in range(1, 9))
assert '不按定理个数拆章节' in text and '控制代价' in text
checks['report_targeted_readback'] = {'passed': True, 'theory_files_covered': 8}
paper_status = subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain', '--', '论文'], text=True).strip()
theory_diff = subprocess.check_output(['git', '-C', str(repo), 'diff', '--', '杂项/新版本/Theory_Package'], text=True).strip()
assert not paper_status and not theory_diff
checks['frozen_scope'] = {'passed': True, 'paper_status_empty': True, 'original_theory_diff_empty': True}

sources = files + [code, report, Path(__file__).resolve()]
hashes = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
lines = {p.relative_to(root).as_posix(): len(p.read_text(encoding='utf-8').splitlines()) for p in sources}
result = {'task': 'TASK-048', 'checks': checks, 'source_hashes': hashes, 'source_line_counts': lines,
          'limits': ['No training or new device experiment', 'No full theorem numerical certification', 'No uniform real-device constants or exact numerical argmin certificate', 'PDF full-layout unavailable']}
validation = out / 'task048-audit-validation.json'
validation.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
hashes[validation.relative_to(root).as_posix()] = hashlib.sha256(validation.read_bytes()).hexdigest()
commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
covers = {'tasks': ['TASK-048'], 'files': list(hashes), 'requirements': ['Traceable recent paper structure', 'Read-only theory audit 01-08', 'Compact six-section assembly', 'Control-cost conflict explicitly blocked for user decision']}
binding = {'git_commit': commit, 'file_hashes': hashes}
scope = {'role': 'alignment-reviewer', 'session': 'ses_ecf788fcdffeh6f6fkGsJU7lS1',
         'reviewed': [p.relative_to(root).as_posix() for p in files] + [code.relative_to(root).as_posix()],
         'finding': 'Core proof chain retained; costs and common-domain quantifiers require alignment, local-reference interpretation and several remarks require correction',
         'limits': 'Read-only source audit; reviewer ran no successful shell; primary added hashes and three bounded algebra checks. Not approval of future corrections or final paper.',
         'source_hashes': {p.relative_to(root).as_posix(): hashes[p.relative_to(root).as_posix()] for p in files + [code]}}
for name, obj in [('task048_covers.json', covers), ('task048_binding.json', binding), ('task048_review_scope.json', scope)]:
    (out / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
print('TASK048: 3 algebra checks + readback + frozen-scope checks PASS')
print('Sources: 8 theory files + control code + report; hashes bound in project-log')
print('Report SHA256:', hashes[report.relative_to(root).as_posix()])
