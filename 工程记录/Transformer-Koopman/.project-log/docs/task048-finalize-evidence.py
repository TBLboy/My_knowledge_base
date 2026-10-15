"""Materialize bounded evidence for TASK-048 without changing product code."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
repo = root / 'Transformer-Koopman'
new = repo / '杂项' / '新版本'
theory = new / 'Theory_Package'
out = root / '.project-log' / 'docs'
index = theory / '00_Index.md'
before = json.loads((out / 'task048-before-reconciliation.json').read_text(encoding='utf-8'))
tests = json.loads((out / 'task048-reconciliation-tests.json').read_text(encoding='utf-8'))
qp = json.loads((out / 'task048-qp-outcomes.json').read_text(encoding='utf-8'))
assert tests['passed'] and len(tests['checks']) == 42
assert all(c['passed'] for c in tests['checks'])
assert {q['device'] for q in qp} == {'soft_platform', 'arm_3link'} and all(q['rc'] == 0 for q in qp)
checks = {'reconciliation_tests': '42/42', 'soft_platform_qp': '31/31', 'arm_3link_qp': '31/31'}

idx = index.read_text(encoding='utf-8')
mds = sorted(p for p in theory.glob('*.md') if p.name[:2] in [f'{i:02}' for i in range(1, 10)])
for p in mds:
    row = next(line for line in idx.splitlines() if line.startswith('| '+p.name[:2]+' |'))
    cells = [s.strip() for s in row.split('|')]
    assert int(cells[3]) == len(p.read_bytes()), p.name
    assert cells[4].strip('`') == hashlib.sha256(p.read_bytes()).hexdigest()[:16], p.name
    text = p.read_text(encoding='utf-8')
    assert text.count('$$') % 2 == 0, p.name
    assert not any((ord(ch)<32 and ch not in '\n\r\t') or ord(ch)==127 for ch in text)
    assert not any(s in text for s in [r'\begin{abstract}', r'\section{Introduction}', r'\maketitle', r'\title{'])
    # 09 is an unchanged bibliography note, not an edited mathematical proof.
    # Its inline `@type{key,` example is deliberately an incomplete BibTeX prefix
    # (line 127), so a whole-text grouping parser is not applicable there.
    if p.name.startswith('09_'):
        assert hashlib.sha256(p.read_bytes()).hexdigest() == before[p.relative_to(root).as_posix()]
        continue
    # LaTeX grouping braces, treating escaped braces as literal characters.
    stripped = re.sub(r'\\[{}]', '', text)
    depth = 0
    for char in stripped:
        depth += (char == '{') - (char == '}')
        assert depth >= 0, p.name
    assert depth == 0, p.name
checks['index_bytes_hash_prefix'] = '9/9 verified'
checks['targeted_math_grouping'] = '8/8 edited proofs grouping; 9/9 display delimiters/hard markers; unchanged bibliography hash verified'

protected = [k for k in before if 'Temporary_Experiments/' in k]
for rel in protected:
    assert hashlib.sha256((root/rel).read_bytes()).hexdigest() == before[rel], rel
assert not subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain', '--', '论文'], text=True).strip()
checks['protected_scope'] = 'control/model implementation hashes unchanged; paper git status empty'
paths = mds + [index, theory/'00_assembly_scan.py', theory/'00_assembly_scan.txt',
    new/'Theory_Package_Audit_and_Compact_Outline.md', new/'validation'/'validate_theory_reconciliation.py',
    new/'Temporary_Experiments'/'controllers'/'ltv_mpc.py',
    new/'Temporary_Experiments'/'models'/'library.py',
    new/'Temporary_Experiments'/'tests'/'test_ltv_qp.py',
    out/'task048-reconciliation-spec.md', out/'task048-reconciliation-tests.json',
    out/'task048-qp-baseline.txt', out/'task048-qp-outcomes.json', out/'task048-run-qp.py',
    out/'task048-before-reconciliation.json', Path(__file__).resolve()]
paths += [root/q['log'] for q in qp]
hashes = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
changed = [k for k,h in before.items() if hashlib.sha256((root/k).read_bytes()).hexdigest() != h]
validation = {'task': 'TASK-048', 'decision': 'DEC-093', 'checks': checks,
    'hashes': hashes, 'changed_since_baseline': changed,
    'limits': ['Synthetic bounds do not certify real-device constants', 'No continuous full-MPC global argmin computation or exact numerical-QP certificate',
               'No new training or physical experiment', 'Paper reference checked at structure/excerpt level, not complete PDF layout'],
    'retry': {'baseline': '27/28; missing lazy torch.backends.opt_einsum import',
              'hypothesis': 'explicit optional backend initialization resolves lazy import failure',
              'delta': 'wrapper preimports the installed backend; no package or product/test code changes',
              'result': '31/31 each device'},
    'role_fallback': 'implementation-builder model unavailable; serial-role-fallback; independent alignment review separate'}
validation['verification_harness_correction'] = 'Whole-text grouping on unchanged09 flagged its documented inline @type{key, syntax prefix. Scope corrected to mathematical01-08;09 still hash/inventory/display/hard-marker checked, not edited.'
val = out/'task048-final-validation.json'
val.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding='utf-8')
hashes[val.relative_to(root).as_posix()] = hashlib.sha256(val.read_bytes()).hexdigest()
binding = {'git_commit': subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(), 'file_hashes': hashes}
covers = {'tasks':['TASK-048'], 'files':list(hashes),
    'requirements':['Traceable recent paper structure reference','01-08 minimal-dependency audit independently reviewed',
                    'Compact six-chapter main/appendix outline','DEC-093 control-cost conflict reconciled with current measurement-space implementation']}
(out/'task048_final_covers.json').write_text(json.dumps(covers,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'task048_final_binding.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2),encoding='utf-8')
print('TASK048 final evidence: tests + index + targeted grouping + protected scope PASS')
print('Bound file count:', len(hashes))
