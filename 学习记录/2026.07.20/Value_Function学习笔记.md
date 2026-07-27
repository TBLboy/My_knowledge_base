# Value Function（价值函数）学习笔记

## 1. 为什么需要 Value Function

机器人做决策时，不仅要考虑**当前奖励（Reward）**，还要考虑**未来长期收益**。

例如：

```text
当前位置
├── 左边：立即获得 +5
└── 右边：经过一段路后获得 +100
```

如果只看当前奖励，会选择左边；如果考虑长期收益，则右边更优。

**Value Function** 用来回答：

> 当前状态对于未来到底有多“值钱”。

---

## 2. 什么是 Value Function

价值函数定义为：

V^π(s) = E[G_t | s_t=s]

含义：

> 在状态 s 下，如果之后一直按照策略 π 行动，最终能够获得的**期望累计回报**。

其中：

- State：当前状态
- Policy：策略
- Return：未来累计奖励

---

## 3. Reward、Return 与 Value

### Reward

即时奖励，只评价当前一步。

### Return

一次真实轨迹中未来所有奖励的累计。

Return = r_t + γr_(t+1) + γ²r_(t+2) + ...

### Value

Return 的期望值。

也就是：

> 从当前状态开始，多次重复实验后，平均能够获得多少累计奖励。

---

## 4. 为什么写成 V^π(s)

因为：

**同一个状态，在不同策略下，未来收益可能完全不同。**

所以 Value 永远依赖于策略。

---

## 5. Value 的直观理解

Value 可以理解为：

> 当前状态距离最终成功还有多大的潜力。

例如：

| 状态 | Value |
|------|------|
| 离目标很远 | 低 |
| 已接近目标 | 高 |
| 已完成任务 | 最高 |

---

## 6. Bellman Equation

Bellman Equation：

V(s) = E[r + γV(s')]

它表示：

> 当前价值 = 当前奖励 + 下一状态价值（折扣后）

这是强化学习最核心的递归公式。

---

## 7. Bellman Equation 为什么成立

因为：

Return 可以写成：

G_t = r_t + γG_(t+1)

而 Value 是 Return 的期望。

所以自然得到 Bellman Equation。

---

## 8. Value 与 World Model

```text
Observation
    ↓
Encoder
    ↓
Latent State
    ↓
World Model
    ↓
Future State
    ↓
Value Network
    ↓
Future Return
```

- World Model：预测未来
- Value Network：评价未来

---

## 9. Value 与 MPC

Value：

> 当前状态值多少钱？

MPC：

> 哪条未来轨迹最好？

Value 负责评价。

MPC 负责规划。

---

## 10. Value 与 Q Function

Value：

V(s)

回答：

> 当前状态好不好？

Q：

Q(s,a)

回答：

> 当前状态下，先执行动作 a，未来好不好？

Q 比 Value 多考虑了一个 Action。

---

## 11. 在学习路线中的位置

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
```

---

## 12. 常见误区

### Reward 就是 Value

错误。

Reward 是一步奖励。

Value 是未来长期价值。

### Value 与策略无关

错误。

不同策略对应不同 Value。

### Bellman Equation 需要死记

错误。

它来自 Return 的递归展开。

### Value 可以直接决定动作

错误。

Value 负责评价。

真正决定动作的是策略或 Q Function。

---

## 13. 核心总结

1. Value 描述的是长期价值，而不是即时奖励。
2. Value 是 Return 的期望。
3. Value 与策略有关，因此写成 V^π(s)。
4. Bellman Equation 是强化学习最重要的基础公式。
5. World Model 预测未来，Value Network 评价未来。

一句话总结：

> Value Function 衡量的是：从当前状态开始，按照某个策略继续行动，未来平均能够获得多少累计奖励。

---

## 14. 自检题

1. Reward、Return、Value 有什么区别？
2. 为什么 Value 要依赖策略？
3. Bellman Equation 为什么成立？
4. World Model 与 Value Network 分别负责什么？
5. Value 与 MPC 的区别是什么？
6. Value 与 Q Function 的区别是什么？
