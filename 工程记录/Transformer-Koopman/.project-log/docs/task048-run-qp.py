"""Re-run existing QP tests with explicit optional backend initialization.

Delta vs baseline: import torch.backends.opt_einsum before runpy, since the
baseline's lazy import failed, while an isolated explicit import succeeded.
No package installation or test/product-code modification.
"""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
test = root / 'Transformer-Koopman' / '杂项' / '新版本' / 'Temporary_Experiments' / 'tests' / 'test_ltv_qp.py'
code = "import torch.backends.opt_einsum; import sys,runpy; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='__main__')"
outcomes = []
for device in ['soft_platform', 'arm_3link']:
    res = subprocess.run([sys.executable, '-c', code, str(test), '--device', device], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
    log = root / '.project-log' / 'docs' / ('task048-qp-' + device + '.txt')
    log.write_text(res.stdout, encoding='utf-8')
    outcomes.append({'device': device, 'rc': res.returncode, 'log': log.relative_to(root).as_posix()})
    print(device, 'rc=', res.returncode, 'summary=', res.stdout.strip().splitlines()[-1])
(root / '.project-log' / 'docs' / 'task048-qp-outcomes.json').write_text(json.dumps(outcomes, indent=2), encoding='utf-8')
sys.exit(max(item['rc'] for item in outcomes))
