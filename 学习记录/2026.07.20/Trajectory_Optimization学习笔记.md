# Trajectory Optimization（轨迹优化）学习笔记

## 1. 为什么需要 Trajectory Optimization

机器人执行任务时，如果每次只考虑**下一步动作**，容易出现短视行为：

- 来回调整
- 容易碰撞
- 效率低
- 难以完成长时序任务

人类通常会先在脑海中规划未来几步，再开始行动。

Trajectory Optimization 的思想就是：

> **一次性规划未来一整段动作序列，而不是只优化当前一步。**

---

## 2. 什么是 Trajectory（轨迹）

Trajectory（轨迹）表示机器人从起点到终点的一整段执行过程。

数学表示：

\[
\tau=(s_0,a_0,s_1,a_1,\cdots,s_T)
\]

其中：

- \(s_t\)：状态（State）
- \(a_t\)：动作（Action）

轨迹由状态和动作交替组成。

例如抓取杯子：

```text
机械臂初始位置
    ↓
向前移动
    ↓
靠近杯子
    ↓
下降
    ↓
到达杯子
    ↓
闭合夹爪
    ↓
抓住杯子
```

---

## 3. 什么是 Trajectory Optimization

Trajectory Optimization（轨迹优化）回答的问题是：

> **在所有可能的轨迹中，哪一条最好？**

这里优化的是：

- 动作序列（Action Sequence）
- 而不是单个动作

目标通常是：

- 最大化累计奖励
- 或最小化总代价

---

## 4. 为什么不能只优化当前动作

假设：

动作 A：

- 当前奖励：+5
- 未来撞墙：-100

动作 B：

- 当前奖励：0
- 最终完成任务：+100

如果只关注当前奖励，会错误选择 A。

Trajectory Optimization 会比较整条轨迹，因此选择长期收益更高的 B。

因此：

> **Trajectory Optimization 是长期规划，而不是贪心决策。**

---

## 5. Trajectory Optimization 的优化目标

假设规划未来 \(H\) 步：

\[
a_{0:H-1}^{*}
=
\arg\max
\sum_{t=0}^{H-1}\gamma^t r_t
\]

即寻找未来一段动作序列，使累计奖励最大。

这里优化对象是：

```text
a0 → a1 → a2 → ... → aH
```

而不是某一个动作。

---

## 6. 为什么需要 World Model

机器人不能把所有候选轨迹都在真实世界尝试一遍。

原因包括：

- 成本高
- 太慢
- 可能损坏机器人
- 不安全

因此需要：

> **World Model（世界模型）**

流程：

```text
Candidate Action Sequence
          ↓
      World Model
          ↓
Predict Future States
          ↓
Evaluate Reward / Cost
```

机器人先在模型中“想象未来”，再决定真正执行什么。

---

## 7. Trajectory Optimization 的基本流程

```text
Current State
      ↓
生成候选动作序列
      ↓
World Model 预测未来
      ↓
计算累计奖励或总代价
      ↓
选择最佳轨迹
      ↓
执行第一步动作
```

注意：

最终通常只执行第一步。

下一时刻重新规划，这就是 MPC 的思想。

---

## 8. 与 Value Function 的关系

规划时，经常采用：

\[
\sum r + V(s_H)
\]

其中：

- 前半部分：规划时域内累计奖励
- 后半部分：终点状态的 Value

原因：

规划通常只覆盖有限步，而任务可能持续更长时间。

Value 可以估计规划范围之外的长期收益。

---

## 9. 与 Q Function 的关系

Q Function：

评价：

> 当前状态下执行某个动作是否值得。

Trajectory Optimization：

评价：

> 整个动作序列是否值得。

可以理解为：

```text
Q
↓

单个动作评分

Trajectory Optimization
↓

整条动作序列评分
```

---

## 10. 三种主流轨迹优化方法

### （1）梯度优化

代表：

- iLQR
- DDP

特点：

- 利用梯度优化动作序列
- 收敛速度快
- 容易陷入局部最优

---

### （2）采样优化

代表：

- CEM
- MPPI
- PETS

特点：

- 随机采样大量轨迹
- World Model 预测结果
- 保留优秀轨迹继续优化

无需梯度。

---

### （3）学习优化

代表：

- Dreamer
- Actor 网络

特点：

- 学习直接输出高质量动作
- 推理速度快
- 训练成本较高

---

## 11. 为什么 PETS 使用 CEM

机器人动作通常是连续空间。

无法枚举所有动作。

因此：

1. 采样很多动作序列
2. World Model 预测未来
3. 计算累计奖励
4. 保留优秀样本
5. 继续采样优化

最终得到优秀轨迹。

---

## 12. Trajectory Optimization 与 MPC

Trajectory Optimization：

回答：

> 哪条轨迹最好？

MPC：

回答：

> 每执行一步，都重新进行轨迹优化。

因此：

> **MPC = Rolling Trajectory Optimization（滚动轨迹优化）**

---

## 13. Trajectory Optimization 与 Dreamer

Dreamer 不直接搜索真实环境中的轨迹。

而是在：

```text
Latent State
      ↓
Imagine Future
      ↓
Evaluate
      ↓
Update Policy
```

也就是说：

Dreamer 在潜在空间完成轨迹优化。

---

## 14. 在第一周知识体系中的位置

```text
MDP
    ↓
POMDP
    ↓
Value Function
    ↓
Q Function
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

Trajectory Optimization 是连接强化学习理论和模型预测控制的重要桥梁。

---

## 15. 常见误区

### 误区一：Trajectory 就是一条机器人运动路径

不完整。

Trajectory 同时包含：

- State
- Action

而不仅仅是空间路径。

---

### 误区二：Trajectory Optimization 等于 MPC

错误。

Trajectory Optimization 是思想。

MPC 是一种经典实现方式。

---

### 误区三：Trajectory Optimization 必须依赖梯度

错误。

采样优化（如 CEM）完全不需要梯度。

---

### 误区四：机器人真的执行完整轨迹

错误。

现代 MPC 通常只执行第一步，然后重新规划。

---

## 16. 核心总结

请牢记以下几点：

1. **Trajectory 是状态和动作组成的一整段执行过程。**
2. **Trajectory Optimization 优化的是整条动作序列，而不是单个动作。**
3. **World Model 用于预测不同轨迹的未来结果。**
4. **轨迹通常通过累计奖励和终点 Value 共同评价。**
5. **Trajectory Optimization 是 MPC、CEM、PETS、Dreamer 等现代模型的共同基础。**

一句话总结：

> **Trajectory Optimization 的目标是在所有可能的未来动作序列中，找到长期收益最高（或总代价最低）的那一条轨迹。**

---

## 17. 自检题

1. Trajectory 与单个 Action 有什么区别？
2. 为什么机器人不能只优化当前动作？
3. Trajectory Optimization 的优化对象是什么？
4. 为什么需要 World Model？
5. 为什么规划时经常加入终点 Value？
6. Trajectory Optimization 与 Q Function 的区别是什么？
7. 三种轨迹优化方法分别是什么？
8. 为什么 PETS 使用 CEM？
9. 为什么 MPC 只执行第一步动作？
10. Dreamer 是如何在潜在空间进行轨迹优化的？
