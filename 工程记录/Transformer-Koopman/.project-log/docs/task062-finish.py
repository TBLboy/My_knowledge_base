import hashlib
import json
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / '.project-log/docs'
PY = (Path.home() / '.config/opencode/vibe-python').read_text().strip()
BASE = [PY, str(Path.home() / '.config/opencode/vibe-workflow/scripts/vibe.py'), '--root', str(ROOT)]

def cli(*args):
    r = subprocess.run(BASE + list(args), capture_output=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    print(r.stdout.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode()[-1100:])
    if r.returncode:
        raise RuntimeError(r.stderr.decode('utf-8', errors='replace'))
    return json.loads(r.stdout) if r.stdout.strip() else None

def save(name, data):
    p = DOCS / name
    p.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding='ascii')
    return '@' + str(p)

if __name__ == '__main__':
    binding = json.loads((DOCS / 'task062-binding.json').read_text())
    for name, digest in binding['file_hashes'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    cli('evidence', 'record', '--id', 'EV-TASK062-001', '--kind', 'verification', '--subject', 'III-B both complete x+z losses; refreshed fixed references; two Tectonic runs exit0 9pages 0overfull/undefined/font warnings; immutable prefix/suffix/rollout/labels; no commit/push', '--status', 'valid', '--task-id', 'TASK-062', '--covers', '@' + str(DOCS / 'task062-covers.json'), '--version-binding', json.dumps(binding))
    scope = {
        'scope': 'Independent static acceptance of III-B losses, reference update rule and Algorithm1 against task062-approved-review.md; final source after I1 domain clarification',
        'implementer': 'implementation-builder; main-agent fixed reference domain wording',
        'reviewer_session': 'ses_ebb00c7bfffe6SZD0Npph5wR1D',
        'verdict': 'go',
        'initial_verdict': 'conditional: reference definition might restrict tail I1 samples to complete H_R segments',
        'resolution': 'Define enc references for all available measured windows; Stage0 t=k+1 k in I1, Stage1 t=k+i k in IR; independently reread and accepted',
        'evidence': ['task062-changes.diff', 'task062-validation.json', 'task062-binding.json', 'task062-build1.log', 'task062-build2.log', 'Main.tex:328-408'],
        'limitations': ['Reviewer has no shell: did not independently compile, hash or query Git', 'Main-agent two final builds and byte checks used for runtime evidence', 'Training-code alignment and gradient execution unverified', 'Underfull 19 and Fontconfig environmental notice remain; no submission visual certification']
    }
    cli('review', 'record', '--id', 'REV-TASK062-001', '--task-id', 'TASK-062', '--reviewer', 'verification-reviewer', '--verdict', 'go', '--scope', save('task062-review.json', scope), '--evidence-ref', 'EV-TASK062-001')
    gate = cli('gate', '--task', 'TASK-062')
    assert gate['decision'] == 'allowed', gate
    cli('task', 'finish', '--task-id', 'TASK-062', '--summary', 'III-B Stage0/1 now supervise x and complete z with lambda0/lambdaR>0, shared measured references refreshed per update and fixed therein; parameters/rollout/labels/prefix/suffix unchanged. Two Tectonic builds exit0,9pages,0overfull/undefined/font warnings,19underfull. Independent static review go. No code/experiment/figure edits, commit or push; code-gradient alignment unverified. User to review PDF.')
    snapshots = {
        'current_session': '''## 当前状态

- 当前阶段：论文最小修改 TASK-062 已完成本次范围；GOAL-002 整体仍未完成。
- 基线：paper / 8d14a40；工作区仅 Main.tex 有本次未提交修改，未 commit/push。
- 完成：III-B Stage 0/1 同时监督 x 与完整 z，正权重 lambda_0/lambda_R；沿用 z^{enc}，同轨迹实测参考由共享编码器逐次更新前重算、更新时固定，预测支路保持训练；Algorithm 1 同步。
- 边界验证：III-B 前缀、图占位起后缀至全文末尾、递归方程、全部标签逐字节/序列保持；III-C、第四章、实验、图片、附录不变。
- 最近验证：EV-TASK062-001 valid；REV-TASK062-001 静态独立复核 go；最终两轮 Tectonic exit0、9 页、0 Overfull/未定义引用/字体警告，19 Underfull（原17，含2个vbox）；Fontconfig 环境提示仍在。pdflatex 不可用。
- 未验证：Reviewer 未独立运行编译/哈希；训练代码与参考分支梯度规则未核验，本次不做实验或代码修改。
- 产物：论文/新版本/build_font/Main.pdf；docs/task062-change-report.md、task062-changes.diff、task062-validation.json、task062-binding.json。
- 下一步：用户审阅改稿/PDF；仅另获授权后提交或推送。TASK-054 全量联网文献复核继续留待定稿。
''',
        'progress': '''## 当前状态

- 当前阶段：阶段③论文撰写，GOAL-002 整体进行中；本次 TASK-062 范围已完成。
- 最新成果：III-B 双阶段 x+完整z 监督及 Algorithm 1 补齐；共享编码参考逐次重算/单次固定；其余章节、理论、图和实验保持不变。
- 验证：两轮 Tectonic 9页、0 Overfull/未定义引用/字体警告；19 Underfull；REV-TASK062-001 静态 go，EV-TASK062-001 valid。
- 版本：HEAD 8d14a40，仅 Main.tex 未提交修改，本轮未提交/推送。
- 限制：训练代码/梯度行为未核验，Reviewer 未独立编译或算哈希；不声称 A3 由损失证明或新增稳定性结论。
- 下一步：用户审阅 PDF 与 docs/task062-change-report.md；定稿后另处理 TASK-054 联网参考文献复核，实验与图片继续暂缓。
'''
    }
    memory = {}
    for key, snap in snapshots.items():
        path = ROOT / '.project-log' / ('current-session.md' if key == 'current_session' else 'progress.md')
        old = path.read_text(encoding='utf-8')
        a = old.index('\n## ') + 1
        b = old.index('\n## ', a + 4)
        memory[key] = old[:a] + snap + old[b:]
    cli('memory', 'sync', '--file', save('task062-memory.json', memory))
