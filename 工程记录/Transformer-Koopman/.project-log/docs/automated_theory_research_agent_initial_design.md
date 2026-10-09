# 自动理论科研 Agent：初步构想与参考材料

> **工作版本：v0.1**  
> **整理日期：2026-09-23**  
> **当前聚焦领域：Koopman / 非线性控制 / 数据驱动控制 / 理论型控制论文**  
> **目标定位：Theory-first Autonomous Research System，而不是单纯的论文生成器**

---

## 1. 项目起点

我们的目标不是简单做一个“自动写论文”的 Agent，而是构建一个能够较长时间自主推进研究任务的 **自动科研系统（Autonomous Research Agent / Automated Theory Research Lab）**。

用户可以给系统不同强度的起始信息：

- 一个已经有部分进展的 idea；
- 一篇或若干篇论文；
- 一个大致研究方向，例如 “Koopman control”；
- 一个研究约束，例如“偏理论、最终只做仿真实验”；
- 甚至只给出领域，而不给具体创新点。

系统需要完成从文献调研、gap 发现、idea 生成、可行性验证、理论推导、反例搜索、实验设计、仿真、数据整理到最终论文撰写的闭环。

核心目标不是“尽快生成一篇稿件”，而是尽可能满足：

\[
\text{Novel}+\text{Correct}+\text{Nontrivial}+\text{Supported}+\text{Reproducible}.
\]

---

## 2. 来自 CCK 论文的核心启发

我们目前讨论的 Control-Coherent Koopman（CCK）工作给了一个非常值得抽象的科研创新模式。

### 2.1 原始问题

原始 CCK 希望得到：

\[
z_{t+1}=Az_t+Bu_t,\qquad B=\text{constant}.
\]

为此，系统需要被组织为：

\[
\begin{aligned}
p_{t+1} &= \bar f_p(p_t,q_t)+B_pu_t,\\
q_{t+1} &= f_q(p_t,q_t),
\end{aligned}
\]

并且要求：

\[
B_p=\text{constant}.
\]

这是一项较强的结构性假设。

如果实际系统是

\[
p_{t+1}=\bar f_p(p,q)+B(p,q)u,
\]

则原始 CCK 的常数控制矩阵结构一般不能直接成立。

### 2.2 该论文的重要研究思路

它没有简单地“拟合一个近似常数 \(B\)”或直接放弃 CCK，而是引入类似 actuator prefilter 的 **virtual dynamics / dynamic extension**，人为构造一个增广系统，使新的外部输入满足原理论所要求的结构。

可以将这个创新模式抽象为：

\[
\boxed{
\text{Restrictive Assumption}
\rightarrow
\text{Structural Obstruction}
\rightarrow
\text{Problem Transformation}
\rightarrow
\text{Manufacture Desired Structure}
\rightarrow
\text{Reuse Existing Theory}
}
\]

更抽象地说：

> 当已有理论要求条件 \(C\)，而真实问题 \(P\) 不满足 \(C\) 时，不一定只考虑修改理论使其不再需要 \(C\)。另一条路线是寻找一个变换 \(T\)，使得增广或重构后的问题 \(T(P)\) 满足 \(C\)。

即：

\[
P\not\models C,\qquad T(P)\models C.
\]

可能采用的变换包括：

- state augmentation；
- dynamic extension；
- virtual dynamics；
- prefilter；
- coordinate transformation；
- latent-state introduction；
- input transformation；
- observer augmentation；
- decomposition。

这不是要照抄 CCK，而是要把它沉淀为一个可复用的 **Research Innovation Operator**。

---

## 3. 我们希望构建的科研闭环

系统不应采用单向流水线：

```text
Idea -> Theory -> Experiment -> Paper
```

而应该采用可以回退、分叉、证伪和重新搜索的研究图：

```text
Research Brief
      |
      v
Literature Mapping
      |
      v
Gap / Assumption Mining
      |
      v
Idea Population
   /  |  \
  I1  I2  I3 ...
   \  |  /
      v
Novelty / Feasibility / Falsification
      |
      v
Theory Construction
      |
      v
Proof Audit / Counterexample Search
      |
      +---- fail ----> idea refinement / branch switch
      |
      v
Claim-driven Experiment Design
      |
      v
Simulation / Data Analysis
      |
      +---- fail ----> experiment redesign / theory revision / branch kill
      |
      v
Evidence Ledger
      |
      v
Adversarial Review
      |
      +---- fail ----> previous stages
      |
      v
Paper Assembly
```

科研过程中的“失败”必须被当作合法结果，而不是异常。

---

## 4. 核心设计原则

### 4.1 Research Tree，而不是单一路线

一次产生多个 candidate ideas，而不是从一个 idea 一路硬做到底。

例如：

\[
I_1,I_2,\dots,I_{20}
\]

经过多个阶段逐渐剪枝：

\[
20\rightarrow 8\rightarrow 4\rightarrow 2\rightarrow 1.
\]

如果最终分支失败，系统可以回到此前仍然存活的分支，而不是整个项目重新开始。

### 4.2 Idea Tree 与 Theory Tree 分离

一个 idea 可以有多个理论实现；一个理论实现也可能产生多个 theorem 版本。

因此至少应区分：

- **Idea Tree**：研究方向层面的探索；
- **Theory Tree**：定义、假设、lemma、theorem、proof 的演化；
- **Experiment Tree**：不同实验方案和参数配置的探索。

### 4.3 Agent 之间应存在对抗关系

不能所有 Agent 都以“证明项目是对的”为目标。

需要人为制造角色冲突，例如：

- Theory Builder：尽量建立定理；
- Theory Skeptic：尽量找漏洞；
- Counterexample Hunter：寻找最小反例；
- Novelty Advocate：寻找与现有工作的差异；
- Prior-Art Hunter：尽量证明 idea 已经有人做过；
- Experiment Builder：设计能显示优势的实验；
- Adversarial Experimenter：寻找方法失效的场景。

只有经过对抗仍然保留下来的结论才进入最终材料。

### 4.4 Writer 不负责创造事实

Paper Writer 只能使用已经经过验证的内容。

最终论文中的每一个主要 claim 都应能回溯到：

- 文献证据；
- 数学证明；
- 形式验证；
- 数值验证；
- 仿真实验；
- 数据文件；
- 图表和日志。

---

## 5. 建议的 Agent 架构

### 5.1 Research Director / Orchestrator

职责：

- 维护整个研究项目状态；
- 分配资源和预算；
- 创建 / 删除 / 暂停研究分支；
- 决定下一步调用哪个子 Agent；
- 根据证据决定 `PROCEED / REFINE / PIVOT / KILL`。

它不应亲自完成所有数学和实验工作。

### 5.2 Problem Framer

将用户输入转换为结构化 Research Brief。

例如：

```yaml
domain:
  - nonlinear_control
  - koopman_operator

research_style:
  - theory_first

allowed_contributions:
  - new_formulation
  - relaxed_assumption
  - dynamic_augmentation
  - stability_result
  - error_bound

experiment_type:
  - simulation_only

seed_idea:
  optional

constraints:
  novelty_required: true
  theorem_required: true
  reproducibility_required: true
```

### 5.3 Literature Scout

负责：

- 搜索论文；
- 追踪引用链；
- 查找最新工作；
- 建立主题文献集合；
- 获取 PDF、metadata、DOI、年份、作者等；
- 保存引用证据。

重点不是生成总结，而是为后续研究建立可查询的证据库。

### 5.4 Literature Structure Extractor

把论文从“文本”变成结构化研究知识：

```text
Paper
├── Problem
├── Assumptions
├── Definitions
├── Main Theorems
├── Method
├── Claimed Advantages
├── Limitations
├── Experimental Setting
└── Future Work
```

例如 CCK 可以被抽取为：

```text
Method:
  Control-Coherent Koopman

Key assumptions:
  - actuator subsystem exists
  - p is an independent subsystem state
  - control acts directly on p
  - actuation is linear
  - Bp is constant
  - observables contain p
  - autonomous Koopman model is valid over the relevant domain

Structural limitation:
  many real physical actuators may not satisfy the required structure

Innovation pattern:
  virtual dynamics / prefilter
  -> dynamic extension
  -> manufacture desired input structure
```

### 5.5 Gap / Assumption Miner

其任务不是直接 brainstorm，而是系统提取：

- restrictive assumptions；
- known limitations；
- missing guarantees；
- contradictory results；
- weak evaluation conditions；
- strong prior knowledge requirements；
- observability / controllability assumptions；
- robustness gaps；
- computational bottlenecks；
- finite-data / finite-dimensional gaps；
- model mismatch gaps。

例如：

```text
Method M1 -> requires constant B
Method M2 -> requires full-state measurement
Method M3 -> requires invariant dictionary
Method M4 -> assumes noiseless data
Method M5 -> assumes known control-affine dynamics
Method M6 -> only gives local stability
```

形成 **Assumption / Gap Database**。

---

## 6. Innovation Operator Library

这是我们希望形成差异化的核心资产之一。

与其让模型直接回答“请给我 10 个创新点”，更可靠的方式是建立一个可扩展的创新算子库：

\[
O_i:(Problem,Gap,Assumption)\rightarrow CandidateIdea.
\]

初始算子可以包括：

1. **Relax Assumption**：放宽已有理论的强假设。
2. **Assumption Engineering / Structure Manufacturing**：通过重构问题使原假设成立。CCK virtual dynamics 属于这一类。
3. **State Augmentation**
4. **Dynamic Extension**
5. **Input / Coordinate Transformation**
6. **Observer Augmentation**
7. **Latent State Introduction**
8. **Robustification**：从 exact model 扩展到 model uncertainty / disturbance。
9. **Stochastic Extension**
10. **Local-to-Global / Global-to-Local Reformulation**
11. **Finite-data Extension**：从 ideal infinite-data result 变为 finite-sample result。
12. **Approximate Condition**：将 exact invariant / exact linearization 改为近似条件并给出误差界。
13. **Constraint Incorporation**
14. **Distributed / Decentralized Reformulation**
15. **Unknown-model Extension**
16. **Dual / Alternative Formulation**
17. **Decomposition**
18. **Regularization**
19. **Stability Guarantee Addition**
20. **Error-bound Addition**

系统可以通过：

\[
Gap\times InnovationOperator
\]

批量生成候选研究方向。

---

## 7. Idea Portfolio 与 Idea Falsification

每一个候选 Idea 应成为结构化节点：

```yaml
idea_id:
parent_id:

problem:
core_claim:

origin:
  source_papers:
  target_gap:
  innovation_operator:

required_assumptions:
expected_theorem:
expected_experiment:

novelty_evidence:
prior_art_risk:

status:
  proposed | screening | active | refined | killed | validated
```

Idea 必须经过至少几类独立检查：

### Novelty Check

- 是否已有同类论文？
- 是“真正新方法”，还是已有方法换符号？
- 是否只是已知理论的直接特例？

### Feasibility Check

- 是否存在明显数学矛盾？
- theorem 是否可能证明？
- 是否依赖无法满足或无法验证的假设？

### Significance Check

- 即使 theorem 成立，是否真的解决了一个有意义的问题？
- 是否仅仅引入额外复杂度而没有实际收益？

### Falsification Check

- 能否构造低维反例？
- 能否找到极端参数使 claim 失败？
- 是否存在简单 case 已经破坏理论？

---

## 8. Theory Engine

这是与大量现有“AI Scientist”项目最不同的部分。

建议至少包含：

```text
Theory Builder
      |
      v
Assumption Auditor
      |
      v
Proof Critic
      |
      v
Counterexample Hunter
      |
      v
Symbolic / Numerical Checker
      |
      v
Optional Formal Verifier
```

### 8.1 Theory Builder

负责：

- 定义系统；
- 明确 assumptions；
- 提出 lemma；
- 提出 theorem；
- 给出 proof；
- 标注 theorem 与既有结果的关系。

### 8.2 Assumption Auditor

检查：

- 是否遗漏隐含假设；
- domain 是否定义清楚；
- continuity / compactness / differentiability 等条件是否真的需要；
- theorem 结论是否超出 assumptions 能支持的范围。

### 8.3 Independent Proof Critic

最好不要直接读取 Theory Builder 的内部推理过程，而只看到：

- Definitions
- Assumptions
- Theorem
- Proof

独立重新审查。

### 8.4 Counterexample Hunter

专门寻找最简单的反例：

\[
n=1,\quad n=2,
\]

尝试：

\[
f(x)=x^2,\quad f(x)=\sin x,\quad f(x,u)=xu,
\]

以及退化矩阵、奇异情况、边界情况。

### 8.5 Symbolic / Numerical Checker

凡是可以交给 deterministic tool 的部分，尽量不要只依赖 LLM。

工具可包括：

- SymPy；
- NumPy / SciPy；
- CVXPY；
- python-control；
- numerical optimization；
- random / Monte-Carlo counterexample search。

### 8.6 Formal Verification

Lean / theorem prover 可作为高价值 theorem 的可选验证层，而不是 MVP 阶段强制要求。

---

## 9. Claim-driven Experiment

实验不能只是“随便选一个 pendulum 跑一下”。

每个实验应该明确绑定一个论文 claim。

例如，若 claim 为：

> Proposed method 对 state-dependent input matrix 的结构偏离更加鲁棒。

则可以设计：

\[
B_\alpha(x)=B_0+\alpha B_1(x)
\]

扫描：

\[
\alpha=0,0.1,\dots,1,
\]

并比较：

- DMDc；
- standard Koopman with control；
- bilinear Koopman；
- original CCK；
- proposed method。

指标例如：

- one-step prediction error；
- rollout prediction error；
- closed-loop tracking error；
- LQR/MPC cost；
- robustness；
- computation time。

产生：

\[
\text{error vs assumption violation}
\]

而不是只给一个孤立 demo。

---

## 10. Evidence Ledger

建议建立项目级 Claim Ledger：

| Claim | Type | Evidence | Verification | Status |
|---|---|---|---|---|
| Existing method requires constant \(B_p\) | literature | cited paper | citation checked | verified |
| Proposed augmentation yields constant \(B\) | theory | Theorem 1 | proof audit | verified / pending |
| Global stability holds | theory | Theorem 2 | counterexample search | rejected |
| Proposed method improves rollout prediction | experiment | Exp-04 | reproducible run | verified |
| Method always beats bilinear Koopman | experiment | Exp-07 | mixed results | unresolved |

最终 Writer 原则上只允许使用：

\[
\boxed{\text{verified claims}}
\]

`rejected` 与 `unresolved` 也必须保留，防止后续 Agent 再次无依据地提出相同结论。

---

## 11. Failure Memory / Idea Graveyard

失败研究应成为一等公民。

例如：

```yaml
idea:
  "lift state-dependent B(x)u into a constant-B linear Koopman model"

why_promising:
  "would retain LTI lifted control structure"

attempt:
  "include B(x) components in observable dictionary"

failure_reason:
  "input produces products between lifted states and u; generic result becomes bilinear rather than linear"

minimal_counterexample:
  "x_next = x + x*u"

salvage_paths:
  - bilinear Koopman
  - dynamic extension
  - virtual input
  - input transformation
```

以后系统再次生成相同想法时，应先检索 Failure Memory。

长期看，这个失败知识库可能比成功论文集合更有价值。

---

## 12. Research State

不要把“聊天记录”当作系统核心状态。

建议项目状态组织为：

```text
ResearchProject
├── ResearchBrief
├── LiteratureCorpus
├── PaperGraph
├── AssumptionGraph
├── GapGraph
├── InnovationOperatorLibrary
├── IdeaTree
├── TheoryTree
├── ExperimentTree
├── ClaimLedger
├── FailureMemory
├── CodeArtifacts
├── DataArtifacts
├── FigureArtifacts
└── ManuscriptArtifacts
```

所有对象应有 provenance：

- 谁生成；
- 基于哪些材料；
- 哪个模型；
- 哪次 run；
- 是否经过验证；
- 后续被哪些 claim 使用。

---

## 13. 初步状态机

```text
S0  Problem Initialization
 |
 v
S1  Literature Mapping
 |
 v
S2  Structured Knowledge Extraction
 |
 v
S3  Gap / Assumption Mining
 |
 v
S4  Idea Generation
 |
 v
S5  Novelty / Feasibility / Significance Screening
 |\
 | \------ failed -----> S4
 v
S6  Theory Construction
 |\
 | \------ proof issue -> S6 revision
 | \------ fatal issue -> S4 / branch switch
 v
S7  Theory Verification
 |
 v
S8  Experiment Design
 |\
 | \------ weak design -> S8 revision
 v
S9  Simulation
 |\
 | \------ implementation failure -> retry / debug
 | \------ negative evidence -> theory or idea revision
 v
S10 Claim Verification
 |\
 | \------ failed -----> previous stages
 v
S11 Adversarial Review
 |\
 | \------ failed -----> previous stages
 v
S12 Paper Assembly
```

---

## 14. 建议的 MVP 路线

### MVP-0：Research Idea Engine

目标：

> 输入一个控制 / Koopman 主题或一篇论文，自动产生有文献支撑、经过初步证伪的研究路线。

包含：

- literature mapping；
- assumption extraction；
- gap mining；
- innovation operators；
- idea portfolio；
- novelty check；
- preliminary falsification；
- 输出 2–3 个值得进一步推导的 branch。

这是最适合首先做好的部分。

### MVP-1：Theory Research Loop

目标：

- 自动形成 definitions；
- assumptions；
- lemmas；
- theorems；
- proofs；
- proof critique；
- counterexample search；
- theorem refinement。

最终产生经过多轮攻击的 Theory Tree。

### MVP-2：Simulation Research Loop

目标：

- theorem / claim -> experiment；
- 自动写仿真代码；
- 自动运行；
- 自动保存配置与随机种子；
- 自动绘图；
- 自动比较 baseline；
- 根据实验决定：

```text
PROCEED
REFINE
PIVOT
KILL
```

### MVP-3：Paper Compiler

只读取已经验证的材料：

- Claim Ledger；
- theorem；
- proof；
- literature evidence；
- experiment results；
- figures；
- tables。

自动形成：

- LaTeX；
- Introduction；
- Related Work；
- Method；
- Theory；
- Experiments；
- Limitations；
- Appendix。

最后由独立 Reviewer Agent 做 adversarial review。

---

## 15. 当前建议的技术方向

目前不急于实现，但候选技术栈可以先记录。

```text
Python
│
├── LangGraph / custom state machine
├── LLM abstraction layer
├── scientific literature RAG
├── OpenAlex / Crossref / arXiv / Semantic Scholar
├── SQLite / PostgreSQL
├── Git + filesystem artifact store
├── Docker sandbox
├── NumPy / SciPy
├── SymPy
├── CVXPY
├── python-control
├── Matplotlib
└── Lean / formal prover (optional)
```

关键原则：

> 不需要堆很多 Agent framework。比框架本身更重要的是 Research State、状态机、验证机制和 deterministic evaluation。

---

# 16. 现有相关工作与可借鉴项目

下面列出目前较值得研究的开源项目 / 系统。

## 16.1 The AI Scientist v2 — Sakana AI

**定位：** 端到端自动科学发现系统。

主要能力：

- autonomous hypothesis generation；
- experiments；
- data analysis；
- manuscript writing；
- progressive agentic tree search；
- experiment manager。

它和我们的想法非常接近的一点是：

> 不依赖单一路线，而是在开放式研究中进行 tree search。

官方也明确指出：相比有强模板约束的 v1，v2 更开放，但成功率并不一定更高。这说明 **开放探索能力与可靠性之间存在明显 trade-off**。

对我们的启发：

- research tree；
- branch search；
- experiment manager；
- sandbox 必不可少。

与我们目标的差异：

- 主要面向 ML empirical research；
- 理论推导、定理验证和数学反例不是核心。

**资料：**

- GitHub: https://github.com/SakanaAI/AI-Scientist-v2

## 16.2 Agent Laboratory

**定位：** LLM multi-agent autonomous research workflow。

其工作流大致覆盖：

- literature review；
- experimentation；
- report writing；
- specialized agents；
- checkpoint / project continuation。

对我们的启发：

- 研究过程可以分阶段交给不同专业 Agent；
- checkpoint 和持久状态很重要；
- human copilot 与 autonomous mode 可以共存。

与我们目标的差异：

- 原始设计仍然更偏实验和工程型研究；
- theory-first / theorem verification 不是主要核心。

**资料：**

- GitHub: https://github.com/SamuelSchmidgall/AgentLaboratory

## 16.3 AgentRxiv

**定位：** 让不同 autonomous research agents 上传、检索并继续彼此的研究，实现 cumulative research。

核心思想：

\[
\text{agent research}
\rightarrow
\text{shared persistent research artifacts}
\rightarrow
\text{later agents build on previous results}.
\]

对我们的启发：

- 长期研究系统不能每个项目都从零开始；
- 成功和失败材料都应进入可复用记忆；
- Research Memory 应跨项目积累。

**资料：**

- arXiv: https://arxiv.org/abs/2503.18102

## 16.4 Google AI Co-Scientist

**定位：** 多 Agent 科学假设生成与研究方案系统。

Google 公开介绍的 specialized agents 包括：

- Generation；
- Reflection；
- Ranking；
- Evolution；
- Proximity；
- Meta-review。

由 Supervisor 管理 worker queue 和资源。

其核心值得借鉴的是：

\[
\text{hypothesis population}
+
\text{reflection}
+
\text{ranking}
+
\text{evolution}
\]

而不是让单一模型一次性给出一个答案。

对我们的启发：

- idea population；
- tournament / ranking；
- hypothesis evolution；
- diversity / proximity control；
- meta-review。

与我们目标的差异：

- 重点更偏科学假设和生物医学；
- 不是一个面向控制理论证明和仿真的开源端到端系统。

**资料：**

- Google Research: https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/

## 16.5 Robin — FutureHouse

**定位：** multi-agent scientific discovery system。

公开仓库强调：

- hypothesis generation；
- experiment generation；
- data analysis；
- specialized agents；
- scientific discovery workflow。

对我们的启发：

- 专业化 Agent 分工；
- hypothesis 和 experiment 应形成闭环；
- literature / analysis 可以采用独立工具层。

与我们目标的差异：

- 更偏生物 / empirical scientific discovery；
- 控制理论 proof pipeline 需要我们自己构建。

**资料：**

- GitHub: https://github.com/Future-House/robin

## 16.6 PaperQA2 — FutureHouse

**定位：** 面向科学文献的高质量 agentic RAG。

公开功能包括：

- scientific literature RAG；
- metadata-aware retrieval；
- re-ranking；
- contextual summarization；
- agentic document retrieval；
- citations；
- contradiction detection；
- PDF / text / Office / source code support。

对我们的意义：

> 很适合作为 Literature Engine 的基础组件或设计参考。

我们的额外需求是在其上继续构建：

- Assumption extraction；
- theorem extraction；
- limitation extraction；
- paper-to-paper relation graph；
- evidence provenance。

**资料：**

- GitHub: https://github.com/Future-House/paper-qa

## 16.7 autoresearch — Andrej Karpathy

**定位：** 极简但很有启发性的 autonomous experiment loop。

其基本循环：

```text
modify code
-> run fixed-budget experiment
-> measure metric
-> keep / discard
-> repeat
```

公开仓库将研究目标约束为一个真实的小型 LLM training setup，并使用固定的实验时间预算和固定 metric。

对我们的最大启发不是“训练 LLM”，而是：

\[
\boxed{\text{LLM 负责提出修改，deterministic evaluation 负责裁决。}}
\]

这非常适合迁移到：

- theorem counterexample；
- numerical test；
- simulation；
- claim validation。

**资料：**

- GitHub: https://github.com/karpathy/autoresearch

## 16.8 Scholar Loop

**定位：** literature -> hypothesis -> experiment -> reflection -> writing 的 autonomous research loop。

公开架构中包含：

- Director；
- Literature Scout；
- Reasoner；
- Debate Panel；
- Funnel；
- Runner；
- Reflector；
- Advisor；
- Writer / Reviewer；
- Ledger / Skills。

尤其值得关注：

- frozen metric；
- deterministic guards；
- ledger；
- failure lessons；
- smoke -> verify -> full 的实验 funnel。

对我们的启发：

> 开放式 reasoning 和可确定的评价部分应该严格分开。

**资料：**

- GitHub: https://github.com/renee-jia/scholar-loop

## 16.9 LeanDojo / LeanDojo-v2

**定位：** Lean theorem proving 的程序化交互和机器学习基础设施。

可用于：

- theorem state extraction；
- tactic interaction；
- automated proof tooling。

注意原始 LeanDojo 仓库已提示新项目应关注 LeanDojo-v2。

对我们的作用：

- 未来可用于关键定理的 formal verification；
- 不建议 MVP 阶段要求所有控制理论都形式化。

**资料：**

- GitHub: https://github.com/lean-dojo/LeanDojo

## 16.10 DeepSeek-Prover-V2

**定位：** 面向 Lean 4 的 open-source formal theorem proving model。

其思路包括：

- complex problem decomposition；
- subgoal decomposition；
- recursive theorem proving；
- Lean verification。

对我们的启发：

> Theory Agent 的长期目标可以不是只产生自然语言 proof，而是将高价值 theorem 逐步转换为 formal verification task。

**资料：**

- GitHub: https://github.com/deepseek-ai/DeepSeek-Prover-V2

## 16.11 PaperBench — OpenAI

**定位：** 评估 Agent 从论文中复现 AI research 的能力。

PaperBench 将 20 篇 ICML 2024 Spotlight / Oral 论文的复现任务分解为大量可独立评分的子任务，并使用层级 rubric 评估。

对我们的重要启发：

> “自动科研”不能只看最终 PDF 是否像论文，而应该把研究能力拆成可检查的子能力。

例如我们未来也可以构造：

```text
Literature accuracy score
Assumption extraction score
Novelty detection score
Proof correctness score
Counterexample recall
Simulation reproducibility
Claim grounding score
```

**资料：**

- OpenAI: https://openai.com/index/paperbench/

## 16.12 ScienceAgentBench

**定位：** 对 data-driven scientific discovery agents 进行更严格的能力评估。

它提供：

- scientific agent benchmark；
- containerized evaluation harness；
- verified benchmark split。

对我们的启发：

- 必须建立自己的 benchmark；
- 最终不能仅靠“看起来能工作”的 demo 判断系统质量。

**资料：**

- GitHub: https://github.com/OSU-NLP-Group/ScienceAgentBench

## 16.13 LangGraph

**定位：** long-running、stateful agent workflow orchestration。

其公开特性包括：

- durable execution；
- state persistence；
- human-in-the-loop；
- long-running workflows；
- memory；
- tracing / debugging。

它与我们需要的 research state machine 很匹配。

但框架只是实现细节，不应让系统设计被框架本身绑死。

**资料：**

- GitHub: https://github.com/langchain-ai/langgraph

---

# 17. 与现有工作相比，我们可能的差异化方向

目前多数自动科研系统偏向：

\[
\text{Idea}
\rightarrow
\text{Code}
\rightarrow
\text{Experiment}
\rightarrow
\text{Metric}.
\]

我们希望聚焦：

\[
\boxed{
\text{Idea}
\rightarrow
\text{Mathematical Structure}
\rightarrow
\text{Theorem}
\rightarrow
\text{Proof}
\rightarrow
\text{Falsification}
\rightarrow
\text{Simulation}
\rightarrow
\text{Evidence}
}
\]

因此暂定定位可以是：

# Automated Theory Research Lab for Control Systems

初始垂直领域：

- Koopman operator；
- nonlinear systems；
- data-driven control；
- system identification；
- MPC / LQR with learned dynamics；
- stability / robustness；
- finite-dimensional lifting；
- bilinear / control-affine models。

先在一个小而结构明确的研究空间中跑通闭环，比一开始做“万能科学家”更实际。

---

# 18. 一个值得长期积累的资产：Research Pattern Cards

除了文献数据库之外，系统还应逐渐沉淀“优秀论文采用了什么创新推理模式”。

例如 CCK 论文可以形成：

```yaml
pattern_name:
  Structure Manufacturing / Assumption Engineering

trigger:
  Existing theory requires structural condition C,
  but real system does not satisfy C.

strategy:
  Construct augmented / transformed system T(P)
  such that T(P) satisfies C.

common_operators:
  - dynamic extension
  - state augmentation
  - virtual dynamics
  - prefilter
  - coordinate transformation

verification:
  - prove transformed system satisfies C
  - prove relation to original system
  - quantify added dynamics / approximation
  - simulation against original formulation
```

随着阅读越来越多的论文，可以形成几十到几百个 Research Pattern Cards。

这些卡片将成为：

\[
\boxed{\text{Innovation Operator Library 的经验来源}}
\]

而不是单纯依赖 LLM 的随机灵感。

---

# 19. 当前最重要的开放问题

后续设计时需要重点解决：

### 19.1 Novelty 如何可靠判断？

不能因为搜索不到就自动认为“没人做过”。

需要：

- 多数据库搜索；
- citation graph；
- synonym expansion；
- related-method search；
- adversarial prior-art agent；
- uncertainty label。

### 19.2 数学正确性如何验证？

可能采用：

\[
\text{Independent LLM Review}
+
\text{Counterexample Search}
+
\text{Symbolic Checking}
+
\text{Numerical Checking}
+
\text{Optional Formal Proof}.
\]

### 19.3 如何防止 Agent 不愿意放弃错误 idea？

必须定义 kill criteria，并由独立 Agent / deterministic check 执行。

### 19.4 如何评价“贡献是否足够”？

不仅要 novelty，还要判断：

- generality；
- practical relevance；
- theorem strength；
- experimental distinguishability；
- complexity cost；
- relation to strong baselines。

### 19.5 如何控制研究成本？

需要 budget-aware search：

- cheap literature screen；
- cheap counterexample；
- small simulation；
- full simulation；
- expensive formal / large experiment。

不要对大量低质量 idea 直接投入最高成本。

---

# 20. 当前阶段的暂定结论

我们要做的并不是：

> “让 AI 自动水论文”。

更合理的工程和研究目标是：

> **构建一个面向控制理论的、自带证伪机制和研究记忆的自动科研闭环。**

其核心特色可以总结为：

\[
\boxed{
\begin{aligned}
&\text{Literature-grounded gap discovery}\\
&+\text{Assumption / structure mining}\\
&+\text{Innovation operator library}\\
&+\text{Multi-branch idea search}\\
&+\text{Theory construction}\\
&+\text{Adversarial mathematical verification}\\
&+\text{Claim-driven simulation}\\
&+\text{Persistent failure memory}\\
&+\text{Evidence-grounded writing}.
\end{aligned}
}
\]

短期最值得先设计清楚的是：

1. Research State Schema；
2. Idea / Theory / Experiment Tree；
3. Innovation Operator Library；
4. Agent Contract；
5. Idea Kill Criteria；
6. Claim Ledger；
7. MVP-0 的完整状态机。

之后再进入代码实现。

---

# 21. 参考链接汇总

1. **The AI Scientist v2 — Sakana AI**  
   https://github.com/SakanaAI/AI-Scientist-v2

2. **Agent Laboratory**  
   https://github.com/SamuelSchmidgall/AgentLaboratory

3. **AgentRxiv: Towards Collaborative Autonomous Research**  
   https://arxiv.org/abs/2503.18102

4. **Google AI Co-Scientist**  
   https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/

5. **Robin — FutureHouse**  
   https://github.com/Future-House/robin

6. **PaperQA2 — FutureHouse**  
   https://github.com/Future-House/paper-qa

7. **autoresearch — Andrej Karpathy**  
   https://github.com/karpathy/autoresearch

8. **Scholar Loop**  
   https://github.com/renee-jia/scholar-loop

9. **LeanDojo**  
   https://github.com/lean-dojo/LeanDojo

10. **DeepSeek-Prover-V2**  
    https://github.com/deepseek-ai/DeepSeek-Prover-V2

11. **PaperBench — OpenAI**  
    https://openai.com/index/paperbench/

12. **ScienceAgentBench**  
    https://github.com/OSU-NLP-Group/ScienceAgentBench

13. **LangGraph**  
    https://github.com/langchain-ai/langgraph

---

## 22. 后续文档建议

后续可在本文件基础上继续拆成几个独立设计文档：

```text
00_vision.md
01_research_state_schema.md
02_agent_contracts.md
03_innovation_operator_library.md
04_idea_search_and_kill_criteria.md
05_theory_engine.md
06_experiment_engine.md
07_evidence_and_provenance.md
08_mvp0_specification.md
```

这样可以逐步从“研究构想”过渡到可实现的系统规格，而不是过早进入代码。
