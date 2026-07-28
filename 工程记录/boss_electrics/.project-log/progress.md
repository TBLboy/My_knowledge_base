# Progress

倾倒入盘技术路线调研和 V1 业务澄清已完成，用户已确认 V1/V2 两版本方案；当前进入两个仓库的技术选型阶段。

- 推荐：示教轨迹基线 + 受限重量/力矩反馈局部修正。
- 回退：带安全限幅、超时、急停和人工确认的示教回放。
- V1：作为中间环节承接上游任务，订阅感知组锅把信息，沿锅把 PCA 主轴施加中心坐标系下的抓取偏置，使用参数化抓取 TCP 控制左臂；提锅后由底盘组协同移动，再以机器人中心坐标系下的餐盘中心点加 xyz 偏置计算倾倒点，通过参数化锅具 TCP 和其局部坐标系增量回放完成倾倒；放回/home、落料验收和异常处理后续补充，不考虑右手锅铲辅助。
- V2：V1 闭环稳定后，再评估右手锅铲抓取、放置、辅助动作和碰撞约束。
- 代码主链：`ScenePerception → TaskPlanner → ExecuteTask → MotionExecutor → RobotDriver`。
- 当前发现：代码具备通用 task/policy/skill/primitive 骨架，中心坐标系生成脚本和 `toolset.end/ref` 参数入口已存在，但尚未承载 V1 感知结果契约、锅具 TCP 转换、底盘保持姿态协同和锅具 TCP 增量倾倒回放。
- 下一步：执行 `TASK-008`，比较两仓库中感知消息、TaskTarget/ExecuteTask、Skill/Primitive、中心坐标转换、底盘协同和轨迹回放的承载方案；批准前不改产品代码。
- 旧版完整记录：`.project-log-legacy-20260728/`。
 旧版完整记录：`.project-log-legacy-20260728/`。

## 本轮会话（2026-07-28）更新

- 用户回顾今日任务记录，确认 V1/V2 两版本路线，完成新一轮业务逻辑澄清
- 用户详细描述了 V1 完整流程状态机（handoff → scene-check → perceive → calc-grasp → move-left → close-hand → grasp-check(预留) → lift → base-move → calc-pour → pan-tcp-translate → pour-replay → return(TBD) → open → home）
- 新增确认：
  - 倾倒点公式：`pour_point_C = plate_center_C + pour_offset_C`（中心坐标系 C 下 xyz 三向可调偏置）
  - 抓取偏置沿锅把 PCA 主轴方向，定义在中心坐标系 C 下
  - 抓取 TCP/锅具 TCP 位姿参数化，代码已有 `toolset.end/ref` 入口
  - 倾倒采用锅具 TCP 局部坐标系录制动回放
  - V1 不加落料验收、异常处理和抓取确认，只打通动作流程
  - 放回/张手/home 后续确定，具体参数不阻塞流程骨架
- 用户批量回答了全部开放问题，所有阻塞项均解除
- 用户确认进入技术选型阶段
- TASK-007：done ✅；TASK-008：in-progress
- DEC-008（类型化 PourTaskTarget 方案）proposed，待用户批准
- 产品代码仍未修改
- 当前阶段：solution-research（技术选型）
