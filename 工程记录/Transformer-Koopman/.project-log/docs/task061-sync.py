import json
import os
import pathlib
import subprocess

root = pathlib.Path(__file__).resolve().parents[2]
docs = root / '.project-log/docs'
py = (pathlib.Path.home() / '.config/opencode/vibe-python').read_text().strip()
base = [py, str(pathlib.Path.home() / '.config/opencode/vibe-workflow/scripts/vibe.py'), '--root', str(root)]
env = dict(os.environ, PYTHONIOENCODING='utf-8')

def run(args):
    result = subprocess.run(base + args, capture_output=True, env=env)
    print(result.stdout.decode('utf-8', errors='replace').encode('ascii', errors='replace').decode())
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', errors='replace'))

payload = {
    'approval': {'status': 'draft'},
    'source': 'User 2026-10-16 and active DEC-091',
    'confirmed': 'Both Stage 0 and Stage 1 must supervise x and z; current Main.tex supervises x only.',
    'scope': 'Clarification only; no manuscript, code, experiment or figure changes.',
    'pending': 'Whether z targets use encoded true future measured windows; gradient flow and weights remain unresolved.',
    'boundary': 'Empirical joint losses do not establish uniform residual assumption A3.',
    'evidence': '.project-log/docs/task061-clarification.md; Main.tex lines 335-442; business-analyst audit',
}
p = docs / 'task061-clarification-payload.json'
p.write_text(json.dumps(payload), encoding='ascii')
run(['record', 'create', '--kind', 'open-question', '--id', 'OQ-TASK061-001', '--title', 'Confirm true future history encoding as joint-loss latent target', '--status', 'open', '--payload', '@' + str(p)])

old = (root / '.project-log/current-session.md').read_text(encoding='utf-8')
start = old.index('\n## ') + 1
end = old.index('\n## ', start + 4)
snapshot = '''## 当前状态

- 当前阶段：业务逻辑澄清（TASK-061，strict）；当前目标 GOAL-002。
- 当前基线：用户优化全文已替换为 Main.tex，paper 提交 8d14a40 已推送；TASK-060 验证 passed、静态独立复核 go。最新编译 9 页、0 Overfull/未定义引用/字体警告，17 Underfull；未独立重编译。
- 当前任务：TASK-061；不改论文、代码、实验或图片，先确认双阶段联合 x+z 训练语义。
- 已确认：用户要求与 DEC-091 一致；当前 Stage 0/1 公式仅约束 x，正文与意图存在漂移。A3 基于真实历史编码的一步完整 z 残差。
- 待用户决定：两阶段 z 监督目标是否采用同一实测轨迹对应未来窗口的编码（推荐），而非自预测窗口编码。
- 边界：经验损失不能证明 A3 统一残差界；联合损失不新增稳定性、泛化或闭环保证。
- 下一步：先确认目标窗口来源，再确认梯度支路及权重；相关核查在 docs/task061-clarification.md。TASK-054 全量联网文献复核仍待定稿。
- 以下历史快照中的旧 HEAD、8 页与“未提交”已被 TASK-060 的 8d14a40/9 页替代，不代表当前状态。
'''
p = docs / 'task061-memory.json'
p.write_text(json.dumps({'current_session': old[:start] + snapshot + old[end:]}, ensure_ascii=True), encoding='ascii')
run(['memory', 'sync', '--file', '@' + str(p)])
