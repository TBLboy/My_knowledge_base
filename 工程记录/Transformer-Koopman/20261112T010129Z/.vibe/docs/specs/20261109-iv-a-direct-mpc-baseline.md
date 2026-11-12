# IV-A direct-model MPC baseline and single-freeze transition

## Scope

仅修改 `论文/新版本/Main.tex` 第四章 IV-A 开头至冻结模型过渡处；不修改第三章、IV-B、附录、代码、实验和图片。

## Approved structure

1. 用一句话承接第三章 history-conditioned predictor 是滚动时域控制的自然预测模型。
2. 用一个不编号的紧凑优化问题给出“直接使用完整拟合预测器”的自然 MPC 基准图景；该问题不是新增实现，也不改变现有编号接口。
3. 用 `However` 说明候选输入会同时改变预测状态、历史 context 和后续调度矩阵，因此直接有限时域问题一般不是 QP，而是关于输入序列的非线性问题。
4. 用 `To retain...` 引出 single-freeze：一次完整标称 rollout，沿标称轨迹计算调度矩阵，优化候选输入时固定矩阵。
5. 再定义 `q_k^E`、可行标称序列 `\bar U_k` 和 `\bar q_{i|k}`，接入现有冻结模型公式。

## Mathematical constraints

- 直接 MPC 基准使用 `q_{i+1|k}=F(q_{i|k},\vu_{i|k})`、现有 `\ell_t`、`\beta`、`\Pi`、`\mathcal U` 和参考对象；仅用 `equation*`，不新增编号或标签。
- 直接 MPC 只作为未冻结基准图景；实际控制器仍是现有 single-freeze QP。
- 保留 `p`（冻结候选状态）与 `q`（完整预测器状态）的区分、nominal exact reproduction、所有现有公式标签和 IV-B 接口。
- 保持现有公式编号顺序；不加入 SQP、Jacobian 线性化、额外约束或新的理论结论。

## Presentation

- 本轮开始先将当前蓝色分组恢复为黑色，仅本轮新增/改写文字和直接 MPC 基准公式重新标蓝。
- 使用短段落和公式承载主要信息，避免在“问题→解决方案”之间堆砌解释。
