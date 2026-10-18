# TASK-062 修改与验证记录

## 范围及差异

唯一产品改动：`Transformer-Koopman/论文/新版本/Main.tex`，III-B 第 335–403 行。

- 335 行：沿用 `z^{enc}`，按可用实测窗口定义参考；分别明确 Stage 0 的 I1 与 Stage 1 的 IR 索引，保留轨迹尾部有效一步样本。共享编码器每次更新重算参考，当前更新固定参考值，预测分支可训练。
- 337–347 行：定义名义一步预测；Stage 0 改为测量误差加完整提升误差，正权重 lambda_0，保留原损失名与标签 `eq:training_one_step_objects`，删除仅监督测量行的旧说明。
- 372–382 行：Stage 1 加完整提升空间项与正权重 lambda_R，保留 `eq:joint_training_loss`、原求和与 w_i=1/H_R；“起点编码一次”明确指预测支路。
- Algorithm 1 第 392 行：Stage 0 明确每次更新刷新并固定下一步实测编码参考。
- Algorithm 1 第 396 行：新增实测参考计算步骤（在预测起点初始化之前）。
- Algorithm 1 第 403 行：更新全文预测器时固定参考状态；循环、标题、标签及参数范围不变。

最终目标：

\[
\tilde z_{k+1}^0=A_0g_\theta(X_k)+B_0u_k,
\qquad
\mathcal L_{\mathrm{init}}=\sum_{k\in I_1}
\bigl[\|C_x\tilde z_{k+1}^0-x_{k+1}\|_2^2
+\lambda_0\|\tilde z_{k+1}^0-z_{k+1}^{\mathrm{enc}}\|_2^2\bigr].
\]

\[
\mathcal L_R=\sum_{k\in I_R}\sum_{i=1}^{H_R}w_i
\bigl[\|C_xz_{k+i|k}^P-x_{k+i}\|_2^2
+\lambda_R\|z_{k+i|k}^P-z_{k+i}^{\mathrm{enc}}\|_2^2\bigr],
\qquad \lambda_0,\lambda_R>0.
\]

## 验证

- 改前基线 Tectonic 编译成功。pdflatex 不在 PATH，使用工程既有 Tectonic。
- 最后修改后 Tectonic 独立执行两次均退出 0，PDF 9 页；0 Overfull、0 undefined、0 Font Warning、0 TeX errors。
- Underfull 17 → 19（最终含 2 个 vbox）；Fontconfig 环境提示仍存在，不声称投稿级视觉就绪。
- PDF 文本定位：Algorithm 1 在第 4 页、III-C 在第 5 页，方法顺序正确；未生成新图片。
- 前缀（III-B 之前）与后缀（其后图占位起至 EOF）逐字节相同；rollout/shift 方程不变；全部标签及顺序不变，无重复标签、悬空引用；算法循环结构不变。
- `git diff --check` 通过；仅 Main.tex，19 行增加 / 10 行删除。HEAD 仍 8d14a40；未执行 commit/push。
- 独立 verification-reviewer 首轮 conditional，指出参考定义可能限制 I1；修正并重编译/重新绑定后，次轮静态复核 go。复核方无 shell，未独立编译、重算哈希或确认 Git 状态；这些由主 Agent 执行。

## 稳定产物

- `task062-before.tex`、`task062-approved-review.md`、`task062-changes.diff`
- `task062-validation.json`、`task062-binding.json`、`task062-covers.json`
- `task062-build1.log`、`task062-build2.log`
- PDF：`Transformer-Koopman/论文/新版本/build_font/Main.pdf`

## 未验证 / 下一步

训练代码与逐次固定参考分支梯度策略尚未核验，也未修改；本次不跑实验、不改图、不新增理论保证。由用户审阅论文与 PDF；无自动提交或推送。
