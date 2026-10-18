import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / '.project-log/docs'
PY = (Path.home() / '.config/opencode/vibe-python').read_text().strip()
BASE = [PY, str(Path.home() / '.config/opencode/vibe-workflow/scripts/vibe.py'), '--root', str(ROOT)]

def cli(*args):
    result = subprocess.run(BASE + list(args), capture_output=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    print(result.stdout.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode()[-1400:])
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', errors='replace'))

def payload(name, data):
    path = DOCS / name
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding='ascii')
    return '@' + str(path)

if __name__ == '__main__':
    paper = ROOT / 'Transformer-Koopman/论文/新版本/Main.tex'
    shutil.copyfile(paper, DOCS / 'task062-before.tex')
    shutil.copyfile(Path.home() / 'Downloads/TASK061_TwoStage_LiftedLoss_Review_For_Agent_20261016.md', DOCS / 'task062-approved-review.md')
    ext = {
        'risk': 'high', 'risk_class': 'strict', 'implementer': 'implementation-builder', 'owner': 'vibe-main',
        'scope': 'Main.tex III-B losses, reference targets, Algorithm 1 only. No commit/push, code, figures, theory, or other chapter edits.',
        'done_when': [
            'Stage 0 and Stage 1 supervise x and complete z with positive lambda_0/lambda_R; existing labels and parameter sets retained',
            'Measured future references use existing z^{enc}; shared current encoder recomputes each update and references held fixed during that update; predictive branch remains trainable',
            'Prefix before III-B, suffix from its figure through III-C and remainder, rollout equations, all existing labels remain unchanged',
            'Two successful LaTeX compilations, no overfull or undefined refs, independent review go, diff and source-bound evidence',
            'No commit or push; limitations include unverified training-code alignment'
        ]
    }
    cli('task', 'create', '--id', 'TASK-062', '--title', 'Complete both training losses in III-B under approved fixed-reference update semantics', '--goal-id', 'GOAL-002', '--extensions', payload('task062-extensions.json', ext))
    cli('task', 'begin', '--task-id', 'TASK-062', '--run-id', 'RUN-062', '--next-action', 'Baseline build; minimally edit III-B and Algorithm 1 per approved review; compile twice; scope checks; independent review; no commit/push')
    decision = {
        'source': 'User starts writing with attached TASK061_TwoStage_LiftedLoss_Review_For_Agent_20261016.md',
        'decision': 'Shared encoder references recomputed at each update, held fixed during the update; prediction branch encoder remains trainable. Use z^{enc}, lambda_0>0 and lambda_R>0 with x coefficient 1.',
        'scope': ext['scope'],
        'boundary': 'Clarifies DEC-098: not permanent frozen targets, no teacher encoder. Keep A1-A3 and all theoretical results unchanged. No experiments or implementation edits.',
        'evidence': '.project-log/docs/task062-approved-review.md',
        'initial_source_sha256': hashlib.sha256(paper.read_bytes()).hexdigest(),
        'verification': 'pdflatex not available on PATH; use existing Tectonic for baseline and two final successful runs, plus independent static review.'
    }
    cli('record', 'create', '--kind', 'decision', '--id', 'DEC-100', '--title', 'Approve minimal III-B joint losses with per-update fixed and refreshed shared-encoder references', '--status', 'active', '--payload', payload('task062-decision.json', decision))
