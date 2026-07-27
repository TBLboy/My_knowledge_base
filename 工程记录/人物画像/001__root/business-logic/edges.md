# Business Logic Edges

## E-P0-P1: Turn A Goal Into An Evidence Request

- From: P0
- To: P1
- Path: main
- Status: draft
- Method: 为当前目标确定需要的事实、约束、已有资产和未知项；优先读取已有记录，无法确定时再询问本人。
- Inputs: 目标描述、项目路径、时间/资源限制。
- Outputs: 事实清单、证据路径、开放问题。
- Error handling: 无法确认的内容标为 Unknown，不作为后续关键决策事实。
- Verification: 事实、推断、建议三类内容分离。

## E-P1-P2: Select The Smallest Effective Work Mode

- From: P1
- To: P2
- Path: main
- Status: draft
- Method: 根据目标类型选择直接工程、方案调研、深度研究、项目记录、知识蒸馏、交接或复盘；避免无差别加载全部 Skill。
- Inputs: 事实清单、约束、风险、预期产物。
- Outputs: 工作模式、Skill 组合、产物路径、验证门。
- Error handling: 若目标与约束冲突，回到 P0 重新定义优先级或请求本人决策。
- Verification: 每个 Skill 都能说明必要性和退出条件。

## E-P2-P3: Execute With Human-Owned Verification

- From: P2
- To: P3
- Path: main
- Status: draft
- Method: AI 协助执行，人在关键节点确认方向并对安全、职业和最终结果负责。
- Inputs: 执行方案、代码/资料/环境。
- Outputs: 可检查的工作产物和验证结果。
- Error handling: 出现未定义业务逻辑、环境不一致或风险边界时暂停，记录开放问题。
- Verification: 依据任务运行对应测试、检查或验收。

## E-P3-P4: Preserve Evidence Before Context Is Lost

- From: P3
- To: P4
- Path: main
- Status: draft
- Method: 在有意义的工作单元后记录目标、改变、决策理由、失败、证据、未验证项和下一步。
- Inputs: P3 结果。
- Outputs: 项目 `.project-log` 更新。
- Error handling: 不将临时猜测升级为主业务逻辑；不记录密钥和敏感数据。
- Verification: `current-session.md` 可在一分钟内恢复下一步，`progress.md` 保留可追溯时间线。

## E-P4-P5: Distill, Do Not Dump

- From: P4
- To: P5
- Path: main
- Status: draft
- Method: 从已验证记录中提炼跨项目可用的规则、架构模式、调试经验和 AI 协作改进；与已有知识库比较后再入库。
- Inputs: 项目记录、验证证据、已有知识库。
- Outputs: 带来源的知识候选项或 Skill 改进建议。
- Error handling: 一次性项目噪声、未经验证的解释和重复知识应丢弃或保留为候选。
- Verification: 每条正式知识具有来源、适用条件、置信度和反例边界。

## E-P5-P6: Convert Work Into Career Compounding

- From: P5
- To: P6
- Path: main
- Status: draft
- Method: 将成果和知识映射到能力资产、能力缺口、作品集证据、职业目标和下一个投入重点。
- Inputs: 可复用知识、项目结果、外部职业反馈。
- Outputs: 人物画像更新与下一周期优先级。
- Error handling: 不把阅读量、工具数量或他人成果误当成自身可证明能力。
- Verification: 下一周期目标能与具身智能算法主线和真实机会建立明确关联。
