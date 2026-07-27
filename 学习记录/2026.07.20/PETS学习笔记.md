# PETS（Probabilistic Ensembles with Trajectory Sampling）学习笔记

# 1. PETS 是什么？

PETS 全称：

> **Probabilistic Ensembles with Trajectory Sampling**

可以拆解为三个核心模块：

```text
PETS
│
├── Probabilistic（概率世界模型）
├── Ensembles（模型集）
└── Trajectory Sampling（轨迹采样规划）
```

一句话概括：

> **PETS = 概率世界模型 + 模型集 + MPC + CEM。**

它是现代 Model-Based Reinforcement Learning（MBRL）的经典算法之一。

---

# 2. 为什么需要 PETS？

传统 MBRL 流程：

```text
收集数据
    ↓
训练 World Model
    ↓
预测未来
    ↓
MPC 规划
```

问题：

> 单个 World Model 容易预测错误（Model Bias）。

如果模型预测错误，机器人就会规划错误。

因此 PETS 引入了：

- Ensemble（模型集）
- Probabilistic（概率建模）

用于表达模型的不确定性。

---

# 3. PETS 的整体框架

```text
真实环境
      │
      ▼
收集数据
      │
      ▼
训练 Ensemble World Models
      │
      ▼
当前状态
      │
      ▼
CEM 采样动作序列
      │
      ▼
World Model 预测未来
      │
      ▼
计算轨迹奖励
      │
      ▼
更新 CEM
      │
      ▼
最优动作序列
      │
      ▼
执行第一个动作
      │
      ▼
获得新状态
      │
      ▼
重新规划（MPC）
```

---

# 4. Ensemble（模型集）

PETS 不训练一个模型，而是训练多个模型：

```text
Model1
Model2
Model3
Model4
Model5
```

这些模型：

- 网络结构相同
- 参数初始化不同
- 使用同一数据集训练

目的：

> **利用多个模型之间预测结果的差异来估计模型认知的不确定性（Epistemic Uncertainty）。**

---

# 5. 为什么 Ensemble 有用？

如果只有一个模型：

```text
预测：
安全
```

机器人只能相信它。

如果五个模型：

```text
Model1：安全
Model2：安全
Model3：危险
Model4：安全
Model5：危险
```

说明：

> 当前区域模型并没有充分掌握。

因此机器人能够意识到：

> **这里存在较大的模型不确定性。**

---

# 6. Probabilistic World Model

普通神经网络：

输出一个确定值：

```text
x = 3.5
```

PETS：

输出概率分布：

\[
s_{t+1}
\sim
\mathcal N(\mu,\Sigma)
\]

例如：

```text
Mean = 3.5
Variance = 0.2
```

表示：

未来状态更可能位于某个范围，而不是唯一值。

---

# 7. 两种不确定性

## Aleatoric Uncertainty（随机性）

来源：

- 环境噪声
- 传感器误差
- 摩擦
- 风等随机因素

特点：

> 即使拥有无限数据，也无法完全消除。

---

## Epistemic Uncertainty（认知不确定性）

来源：

模型不了解某些状态。

例如：

机器人从未到过的新区域。

特点：

> 可以通过收集更多数据逐渐降低。

PETS 利用 Ensemble 来估计这种不确定性。

---

# 8. Trajectory Sampling

对于每条动作序列：

CEM：

```text
采样动作序列
```

World Model：

```text
预测未来状态
```

Trajectory Sampling：

```text
传播多个粒子
```

Reward：

```text
计算累计奖励
```

因此：

同一动作序列会产生多个可能未来，而不是唯一未来。

---

# 9. PETS 如何工作？

一次控制周期：

1. 当前状态 \(s_t\)
2. CEM 采样大量动作序列
3. Ensemble World Models 预测未来
4. 概率模型采样粒子传播
5. 计算累计奖励
6. CEM 更新采样分布
7. 得到最佳动作序列
8. 只执行第一个动作
9. 获得新状态
10. 再次规划

可以看出：

> PETS = MPC 外层循环 + CEM 内层循环 + 概率模型集预测。

---

# 10. PETS 中各模块分工

```text
World Model
负责预测未来状态

Probabilistic
表示环境随机性

Ensemble
表示模型认知不确定性

CEM
搜索最优动作序列

MPC
滚动规划与执行
```

---

# 11. PETS 的优点

- 数据利用效率高
- 能估计模型不确定性
- 在线规划能力强
- 规划更加稳健
- 适合机器人连续控制任务

---

# 12. PETS 的缺点

- 在线计算量大
- 每一步都要重新规划
- 每次规划需要多轮 CEM
- 多模型、多粒子预测开销高
- 依赖 World Model 的质量

---

# 13. PETS 与其他 MBRL 方法

| 方法 | World Model | 在线 MPC | CEM | 特点 |
|------|-------------|----------|-----|------|
| PETS | 概率模型集 | ✅ | ✅ | 在线规划 |
| MBPO | 世界模型 | ❌ | ❌ | 模型生成数据训练策略 |
| Dreamer | RSSM | ❌ | ❌ | 潜空间策略学习 |
| TD-MPC | 潜变量模型 | ✅ | 部分 | Actor + MPC |

---

# 14. 第一周知识链

```text
MDP
    ↓
POMDP
    ↓
Value
    ↓
Q
    ↓
Trajectory Optimization
    ↓
MPC
    ↓
CEM
    ↓
PETS
    ↓
MBPO
```

PETS 是前面所有知识点第一次真正融合在一起的算法。

---

# 15. 核心总结

请牢记：

1. **PETS = Probabilistic + Ensemble + MPC + CEM。**
2. **Ensemble 用于估计模型认知不确定性。**
3. **Probabilistic 用于表示环境随机性。**
4. **CEM 负责搜索动作序列。**
5. **MPC 负责滚动规划，只执行第一步动作。**
6. **World Model 负责预测未来状态。**
7. **PETS 是现代 MBRL 的经典起点，对 MBPO、Dreamer、TD-MPC 等方法影响深远。**

---

# 16. 自检题

1. PETS 为什么不用单个 World Model？
2. Ensemble 与 Probabilistic 分别解决什么问题？
3. PETS 为什么需要粒子传播？
4. CEM、MPC、World Model 在 PETS 中分别负责什么？
5. PETS 为什么只执行动作序列的第一步？
6. PETS 相比 MBPO、Dreamer 有什么特点？
