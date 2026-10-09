# P2 PSR/预测状态路线数据审计 v0.1

## 结论

候选“action-conditioned predictive-state Koopman/PSR + 离散 pulse sequence planning”在现有离线数据上**不具备辨识支撑，暂时淘汰**。

## 审计事实

审计脚本：`C:\Users\12187\AppData\Local\Temp\opencode\audit_p2_psr.py`。

P2 处理数据：

- train：70 条轨迹 × 300 点 = 21000 行；
- val：20 条轨迹 × 300 点 = 6000 行；
- test：10 条轨迹 × 300 点 = 3000 行；
- `dt` 约 0.2 s，轨迹内稳定；
- `x` 为 2 维，`u` 为 2 维。

关键否证结果：

| 检查 | 结果 |
|---|---:|
| 全部 action 向量唯一数 | 30000 / 30000 |
| action 是否整数 | 0% 精确为整数；最大距最近整数约 0.5 |
| 重复长度 1 action prefix | 0 |
| 重复长度 2 action prefix | 0 |
| 重复长度 3 action prefix | 0 |
| 轨迹间 action-prefix 支持 | 未形成可重复条件分布 |

## 解释边界

- 外部 `软控逻辑.txt` 描述的是部署接口的脉冲语义；处理后的训练数组实际是连续浮点控制记录，二者不能静默视为同一 action space。
- 现有数据可以用于普通连续输入预测或局部动力学回归，但不能支撑“对相同/近似历史和未来 action string 估计条件未来测试分布”的 PSR/有限动作规划定理。
- 这不是模型优化失败，而是 action-support / identifiability 失败。

## 路线判定

暂时 kill：

```text
离线 action-conditioned PSR
+ 离散整数 pulse sequence planning
```

保留为未来数据重采集后的候选，不进入当前阶段③，也不作为当前论文路线。

## 搜索约束更新

下一轮候选必须适配：

1. 连续浮点控制记录，而非假设整数 pulse；
2. 单轨迹 action-prefix 基本不重复；
3. 现有 P2 只有 2D observation；
4. 不能依靠未观测张力/速度/mode；
5. 建模与控制器必须真正改变，不能退回常数 $(A,B)$+LQR。
