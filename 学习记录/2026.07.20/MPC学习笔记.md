# MPC（Model Predictive Control，模型预测控制）学习笔记

# 1. 为什么需要 MPC

传统控制如果每次只考虑下一步动作，容易产生短视行为：

- 不能提前避障
- 容易陷入局部最优
- 无法充分考虑长期收益

MPC 的思想是：

> **机器人在每一个控制时刻，都先预测未来，再决定当前动作。**

---

# 2. MPC 的核心思想

一句话概括：

> **预测未来、优化未来、执行一步、重新规划。**

因此 MPC 又称：

**Rolling Horizon Control（滚动时域控制）**

完整循环：

```text
当前状态
    ↓
规划未来 H 步动作序列
    ↓
预测未来状态
    ↓
评价所有轨迹
    ↓
选择最佳动作序列
    ↓
只执行第一步
    ↓
获得新状态
    ↓
重新规划
```

---

# 3. MPC 的灵魂：滚动时域（Rolling Horizon）

MPC 最重要的特点不是预测，而是：

> **每次规划只执行第一步，然后重新规划。**

这样能够：

- 适应环境变化
- 修正模型误差
- 提高鲁棒性

因此：

> **MPC = Rolling Trajectory Optimization**

---

# 4. MPC 优化的对象

MPC 并不是直接优化一个动作。

真正优化的是：

\[
(a_t,a_{t+1},...,a_{t+H-1})
\]

即：

> **未来 H 步动作序列（Action Sequence）。**

---

# 5. 为什么优化动作序列？

机器人真正能够控制的是动作，而不是状态。

动力学满足：

\[
s_{t+1}=f(s_t,a_t)
\]

因此：

```text
动作序列
      ↓
系统动力学（World Model）
      ↓
状态序列
```

动作决定状态轨迹，因此 MPC 实际上通过优化动作序列来间接优化状态轨迹。

---

# 6. MPC 的优化目标

目标是寻找未来动作序列：

\[
\mathbf{a}^*
=
\arg\max_{\mathbf{a}}
\sum_{k=0}^{H-1}\gamma^k r_k
+\gamma^H V(s_{t+H})
\]

其中：

- 前半部分：规划窗口内累计奖励
- 后半部分：终端状态 Value

因此：

> **寻找一条动作序列，使其产生的状态轨迹具有最大的累计奖励（或最小总代价）。**

---

# 7. 为什么加入终端 Value？

MPC 只规划有限步。

真实任务可能持续很长时间。

因此通常使用：

\[
\sum r + V(s_H)
\]

来估计规划窗口之外的长期收益。

---

# 8. MPC 与 World Model

World Model 负责预测未来。

流程：

```text
Action Sequence
        ↓
World Model
        ↓
Future State Sequence
        ↓
Reward / Cost / Value
```

没有 World Model，MPC 无法预测未来。

---

# 9. MPC 的完整流程

```text
Current State
      ↓
Generate Candidate Action Sequences
      ↓
World Model Predicts Future
      ↓
Compute Reward / Cost
      ↓
Choose Best Trajectory
      ↓
Execute First Action
      ↓
Observe New State
      ↓
Repeat
```

---

# 10. MPC 与 Trajectory Optimization

Trajectory Optimization：

> 找到最优轨迹。

MPC：

> 每一步都重新寻找最优轨迹。

因此：

> **MPC = Rolling Trajectory Optimization**

---

# 11. MPC 与 Value、Q 的关系

Value：

评价状态。

Q：

评价状态-动作。

Trajectory Optimization：

评价动作序列。

MPC：

不断重复进行轨迹优化。

关系如下：

```text
Value
    ↓
Q
    ↓
Trajectory Optimization
    ↓
MPC
```

---

# 12. MPC 与 CEM

MPC 提出了规划问题：

> 怎样找到最优动作序列？

CEM 提供了一种经典搜索方法：

- 采样大量动作序列
- World Model 预测
- 保留优秀样本
- 重新采样优化

因此：

```text
World Model
      +
MPC
      +
CEM
      =
PETS
```

---

# 13. MPC 与 Dreamer、TD-MPC

Dreamer：

在潜在空间预测未来，再利用 Actor-Critic 更新策略。

TD-MPC：

结合：

- Latent World Model
- MPC Planning
- TD Learning

因此现代 MBRL 大多继承了 MPC 的规划思想。

---

# 14. MPC 的优点

- 能进行长期规划
- 能处理约束（避障、速度限制等）
- 能适应动态环境
- 能充分利用 World Model

---

# 15. MPC 的缺点

- 每一步都需要规划，计算量大
- 依赖 World Model 的预测精度
- 高维连续动作空间搜索困难

---

# 16. 常见误区

### 误区一：MPC 一次规划完整任务

错误。

MPC 每次只规划有限时域。

---

### 误区二：MPC 会执行完整轨迹

错误。

只执行第一步。

---

### 误区三：MPC 直接优化状态

错误。

优化变量始终是动作序列。

状态由动力学决定。

---

### 误区四：预测就是 MPC

错误。

预测只是手段。

真正核心是：

> 滚动优化控制。

---

# 17. 第一周知识体系中的位置

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

MPC 是连接强化学习基础理论与现代 Model-Based RL 的关键桥梁。

---

# 18. 核心总结

请牢记以下几点：

1. **MPC 的核心思想是：预测未来、优化未来、执行一步、重新规划。**
2. **MPC 的灵魂是滚动时域控制（Rolling Horizon）。**
3. **MPC 优化的是动作序列，而不是单个动作。**
4. **动作序列通过 World Model 产生未来状态序列，再根据奖励、代价或 Value 进行评价。**
5. **MPC 每次只执行第一个动作，因此能够适应动态环境。**
6. **Trajectory Optimization 是思想，MPC 是其经典实现方式。**
7. **CEM、PETS、Dreamer、TD-MPC 等方法都建立在 MPC 的思想基础之上。**

一句话总结：

> **MPC 是一种基于系统模型的滚动时域优化控制方法，它在每个控制时刻优化未来有限时域内的动作序列，通过预测其对应的状态轨迹并最大化累计回报（或最小化累计代价），只执行第一个动作，然后根据新的状态重新规划。**

---

# 19. 自检题

1. MPC 为什么叫滚动时域控制？
2. MPC 为什么只执行第一个动作？
3. MPC 为什么优化动作序列而不是状态？
4. 为什么需要 World Model？
5. 为什么规划目标中通常加入终端 Value？
6. MPC 与 Trajectory Optimization 的关系是什么？
7. MPC 与 CEM 分别负责什么？
8. MPC 与 Dreamer、TD-MPC 有什么联系？
