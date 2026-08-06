# Current Session

## 2026-08-06 GUI 工程归档

- 将当前 `gui/.project-log/` 归档至 `My_knowledge_base/工程记录/gui/.project-log`，共 24 个文件。
- 知识库远端已推送：`github.com/TBLboy/My_knowledge_base.git`，分支 `work_record`，commit `57812d8 archive: gui`。
- 归档脚本 `archive.py` 执行 `git add -A`，同次提交同时包含了知识库中已存在的未跟踪文件 `学习记录/2026.08.05/今日任务.md`；该文件不是本次 GUI 归档引入的新内容，未作回退。
- 下一步：如后续 GUI 工程记录有更新，再按 `a-project-log-archive` 流程重新归档。

## 2026-08-06 恢复旧版 delta 后处理（用户决定）

- 按用户要求放弃实验性平滑/重采样方案，将 `services/arm/flange_delta.py` 和 `tests/test_flange_delta.py` 恢复为基线 `bfb623a` 中已真机验证的旧版后处理。
- 验证：`git diff` 确认上述两个文件与基线完全一致，当前差异只剩 `.project-log/` 记录；`python3 -m unittest tests.test_flange_delta -v` 4/4 通过；`python3 -m compileall -q services/arm/flange_delta.py tests/test_flange_delta.py` 通过。
- 状态：代码已恢复，尚未提交；实验性 `smooth_v2` 派生资产未删除，后续不需要可自行清理。
- 下一步：如不再继续平滑实验，按需提交本次恢复结果或保持工作区现状。

## 2026-08-06 Delta 回放起点泛化边界诊断

- 用户第二轮真机日志显示：同一 delta 资产在不同当前起点下，失败点分别出现在 4、21、58、78 等位置，也有 61/89 点整段 IK 成功的记录；这些成功记录的 waypoint 数不同，说明测试中使用过不同处理资产或不同起点，不能把它们视为同一条件下的随机结果。
- 当前实现展开公式仍是 `T_replay_i = T_current @ Delta_i`。它保证相对法兰运动形式，不保证绝对工作空间、关节限位、奇异性或 7 轴 IK 分支在新起点下仍存在。
- 代码证据：`_solve_one_flange_pose()` 只尝试多个 elbow 初值，并以当前上一点关节解贪心选择最小步长候选；没有对 wrist/configuration 分支做全轨迹搜索。`_validate_ik_joint_point()` 按已记录的 J1-J7 限位和相邻步长做硬拒绝。
- 真机证据：日志中的 J7 结果 `0.8778` / `0.8850 rad` 超过当前 J7 上限 `0.8727 rad`（±50°），这是实际关节限位失败，不是浮点误差；多个 `getJointPos returned no solution` 的目标姿态在重复尝试中几乎不变，说明是确定性的可达性/分支问题。
- Conclusion: 当前 delta 回放语义实际是“从兼容起点重放相对法兰运动”，不是“任意当前起点都能泛化”。起点变化几毫米到几十毫米可能让某个中间目标进入不可达、越过 J7 限位或让贪心 IK 落入错误分支。
- Next technical direction: 若业务要求更强泛化，应实现多分支候选的全轨迹规划（至少增加 wrist/configuration 分支与关节限位余量评分，不能只按单点最小步长贪心），并在发送运动前给出起点兼容性预检；必要时保存录制时关节配置作为分支先验。当前未修改 IK 代码，未发送额外运动指令。

## 2026-08-06 Delta 平滑实验恢复，等待第二次真机测试

- 按用户要求恢复此前撤回的实验性后处理：7 点 Savitzky-Golay、首尾锁定、SO(3) 姿态差值、孤立跳点过滤、平移/旋转双约束重采样。
- 离线验证：`python3 -m unittest tests.test_flange_delta tests.test_xcore_pose_readout -v` 12/12 通过；同一原始文件重新生成 84 个 waypoint；delta 还原最大分量误差 `1.33e-15`。
- 待测文件：`trajectory/delta_motion_20260805_185408_823825_smooth_v2/segment_001_delta.json`。原始目录未修改。
- 测试约束：保持当前机械臂姿态不变，不先执行 jog；低速直接回放，用于排除起点变化对 IK 的干扰。
- Status: `implemented-unverified`，等待用户第二次真机测试。

## 2026-08-06 Delta 平滑实验真机 IK 回归（已撤回）

- 实验资产 `delta_motion_20260805_185408_823825_smooth_v2` 将原始 281 点改为 84 点；离线单测、编译和 delta 重建虽全部通过，但真机 `getJointPos` 在任何 `MoveAbsJ` 前即返回无解。
- 第一次报错发生时，展开起点相对下一次测试平移了 50 mm；第二次恢复起点后仍在新轨迹点 6 失败。该新目标与旧版同进度目标只差约 `0.765 mm / 0.001436 rad`，表明这台 7 轴 SDK 的 IK 分支对离线法兰轨迹的微小平滑扰动也可能失效。
- 已撤回实验性 7 点 Savitzky-Golay、首尾锁定和双约束重采样，恢复 Git 基线 `bfb623a` 中已真机验证的后处理；恢复后 `python3 -m unittest tests.test_flange_delta tests.test_xcore_pose_readout -v` 为 9/9 通过。
- 结论：不得直接离线改变可回放 delta 的法兰几何路径来追求平滑。后续如需优化，必须先在当前回放起点完成全轨迹 IK，再在关节空间处理，或先增加只求 IK 的预检。

## 2026-08-06 Delta 后处理平滑优化（等待真机对比）

- 变更范围仅限 `services/arm/flange_delta.py` 的离线后处理，JSON schema、delta 定义 `inverse(T0)@Ti`、GUI 回放入口及 xCore 回放路径均未改变。
- 优化内容：
  - 位置滤波由 5 点均值升级为 7 点二阶 Savitzky-Golay，首尾位置强制保留原始采样值。
  - 姿态平滑继续在旋转矩阵空间执行，但首尾姿态强制保留原始值。
  - 旋转去重改为 SO(3) 实际夹角，正确处理 Euler `±π` 绕回。
  - 离群判定改为仅删除“前后均大跳、两侧点连续”的孤立坏点，同时加入姿态跳变阈值，避免旧逻辑把坏点的相邻正常点一并删掉。
  - 空间重采样改为平移步长与姿态步长双约束；默认每段不超过约 10 mm 或 0.05 rad，而不是旧版的加权组合距离。
- 离线验证：`python3 -m unittest tests.test_flange_delta tests.test_xcore_pose_readout -v` 通过（12/12）；`python3 -m compileall -q services pages tests` 通过；未连接或移动机械臂。
- 对比资产：已从原始 281 点采样生成独立目录 `trajectory/delta_motion_20260805_185408_823825_smooth_v2/`；其 `segment_001_delta.json` 为待测文件，源目录 `trajectory/delta_motion_20260805_185408_823825/` 未修改。
  - 新处理结果：10 个重复点删除、0 个孤立离群点删除、84 个回放点；最大平移步长约 9.99 mm、最大姿态步长约 0.0492 rad。
  - `T_initial @ Delta_i` 离线还原 processed waypoint 的最大分量误差为 `1.34e-15`。
- 待验证：在空旷安全区域、低速条件下，从 Delta Trajectory Replay 选择 `trajectory/delta_motion_20260805_185408_823825_smooth_v2/segment_001_delta.json`，与原版 58 点轨迹对比平滑度、速度感和批次接缝卡顿。代码暂未提交，等待真机结论。

## 2026-08-06 Delta 后处理平滑性评估

- 当前后处理已包含：离群点剔除、重复点删除、5 点位置滑动平均、旋转矩阵 SVD 姿态平均、空间弧长重采样，以及最终 `inverse(T0)@Ti` delta 生成。
- 对真实样本 `delta_motion_20260805_185408_823825/segment_001` 的评估：281 raw 点→58 waypoint；无离群点、删除 8 个重复点；总路径长度变化约 0.6%，起终点误差约 0.064 mm / 0.000235 rad，当前滤波没有明显破坏轨迹几何形状。
- 主要不足：文件声明 80 Hz，但实际采样平均约 15.0 ms；后处理忽略 `time_sec`，空间重采样只保证路径点分布，不保证速度/加速度连续；位置滑动平均存在端点和急转弯被圆滑化风险；重复/姿态差值仍使用 Euler 分量阈值；当前 58 点的平均间隔约 14.4 mm，增加点数前必须先处理分批 `moveAppend` 接缝卡顿。
- Decision/assessment: 暂不修改代码。当前方案可作为“几何清洗”版本保留；若要进一步平滑，优先实施保端点的时间感知重采样、SO(3) 姿态差值/平滑、速度/加速度质量检查，再考虑自适应增加 waypoint。
- Status: `analysis-complete`，未发送任何机械臂运动指令。

## 2026-08-06 delta 法兰轨迹回放真机验证通过（关闭）

- 用户真机验证：重启 GUI 后选择 `delta_motion_20260805_185408_823825/segment_001_delta.json` 回放，完整执行成功，未再出现 `calcIk` 的 `-32 IK error`。
- 这确认了 2026-08-05 的根因修复（改用 `model.getJointPos` 带初值法兰空间逆解）在真实控制器上有效。
- 状态：`verified`（真机成功）。遗留的低优先级观察不变：分批次 `moveAppend` 回放中间会有一次卡顿，后续再优化。

### 精确下一步

- 可选：视反馈决定是否优化分批次 append 的衔接卡顿；当前功能已可用。

## 2026-08-05 delta 回放 IK 失败根因：SDK calcIk 求解器，而非 base 坐标系

### 用户线索与核查结论

- 用户提供线索：左/右臂 base 坐标系约定不同（一个 Y 轴朝上、一个 Y 轴朝下，X 均朝前），轨迹录制于左臂，怀疑 IK 用了右臂 base。
- 只读真机核查（全程无运动指令）：
  - 左臂 `baseFrame=[0,0,0,-1.5708,0,0]`，右臂 `baseFrame=[0,0,0,+1.5708,0,0]`，确实不同。
  - 但左臂路径的 `FlanInBaseToEndInRef(base_l, tool_l, flange)` 与控制器 `posture(endInRef)`、`model.calcFk(joints)` 三者数值一致（误差 <1e-3）。GUI 在左侧回放时使用的 base/toolset 与控制器一致，**base 坐标系并未用错**。
  - 若真的用右臂 base 解左臂轨迹，58 点全部 IK 失败（探针验证），与真实故障（前 17 点成功、第 6 点起失败）不符。

### 决定性证据

- `segment_001_delta.json` 在左臂当前位姿展开后，`calcIk` / `calcIk_SearchElbow` 只能解出 17/58 点，首个失败点就是真机报错的第 6 点。
- 同一组法兰位姿改用 `model.getJointPos(cartPos, elbow, jntInit, out)`（法兰空间逆解 + 以上一关节解为初值）后：**58/58 全部解出**，最大相邻关节步长 0.0962 rad，全部在关节限位内。
- 端到端复现新代码路径：57/57 个后续点全部解出（max step 0.0851 rad，399 次 SDK 调用），无失败。
- 因此轨迹文件本身可达（此前 MoveL 也成功执行过）；失败根因是 SDK `calcIk` 对 7 轴腕部姿态轨迹的求解能力不足，而不是录制、delta 展开或坐标系错误。

### 代码修复

- `services/arm/xcore.py::_solve_flange_trajectory_ik()` 不再使用 `FlanInBaseToEndInRef + CartesianPosition + calcIk`。
- 改为 `utility.postureToTransArray(flange_pose)` 生成 4x4 矩阵，调用 `model.getJointPos(matrix, elbow, jntInit, out)`，并以相邻关节解作为连续性初值；肘角按 `(0, ±0.5, ±1.0, ±2.0)` 回退尝试，取步长最小的解。
- 保留全轨迹 IK 全部成功、限位与连续性校验通过后才进入 `MoveAbsJ` 回放的安全设计。
- 副作用：该路径不再依赖 `baseFrame/toolset` 做法兰→末端转换，天然规避左右臂 base 约定差异在该环节的误用风险。

### 验证

- `python3 -m compileall -q services pages tests` 通过。
- `python3 -m unittest tests.test_xcore_pose_readout tests.test_flange_delta`：9/9 通过（含 IK 全解后才回放、IK 失败不回放两条回归）。
- 只读真机端到端验证通过（见上），未发送任何运动指令。
- 状态：`verified`（2026-08-06 真机 GUI 回放成功，见顶部会话条目）。

### 精确下一步

1. 重启 GUI，选择 `delta_motion_20260805_185408_823825/segment_001_delta.json`，速度设 `0.10-0.20` 真机回放。
2. 若仍有失败，记录失败点索引与 `flange_target`；预期不再出现 `calcIk` 的 `-32 IK error`。

## 2026-08-05 delta 回放首点 IK 失败修复

- 真机证据：回放 `trajectory/delta_motion_20260805_185408_823825/segment_001_delta.json` 时，控制器连续返回 `IK failed at flange trajectory point 0: 计算逆解错误`；尚未发送任何关节运动。
- 该文件的第 0 个 delta 是单位变换。因此展开后的第 0 点严格等于回放开始时读取的当前 `flangeInBase`，它不是录制轨迹错误的证据；对该点再次调用 IK 没有业务价值。
- 根因：旧实现错误地对单位首点再次执行 `calcIk`，并将本地 `calcFk` 推导出的肘角/构型强加到目标。控制器已经拥有当前真实构型；这个额外约束会把本应等价于当前姿态的请求变成无解。
- 修复：`_solve_flange_trajectory_ik()` 现在直接将实时 `jointPos` 作为第 0 个关节轨迹点，不对单位首点调用 IK。第 1 点及后续点才求 IK，首次约束来自控制器实时 `cartPosture(endInRef)` 的肘角和构型；每次成功解后用该解的 FK 更新下一点构型。全轨仍然在开始 `MoveAbsJ` 前完成 IK、限位与连续性验证。
- 验证：`python3 -m py_compile services/arm/xcore.py tests/test_xcore_pose_readout.py pages/arm_hand.py` 通过；`python3 -m unittest discover -s tests -v` 通过，9 项测试。测试明确覆盖首点不调用 IK、后续点才调用 IK、IK 失败仍不触发关节回放。
- 状态：`implemented-unverified`。需要复测同一文件；无需重新录制。

### 精确下一步

1. 完全退出并重启 GUI，以加载新的 `services/arm/xcore.py`。
2. 在相同安全条件下选择同一 `segment_001_delta.json`，速度先设为 `0.10` 至 `0.20`。
3. 若仍失败，提供首条错误及其点索引；预期首个可能的 IK 点现在是 `1`，不应再是 `0`。

### 后续证据修正（19:28）

- 重启后的真机日志确认首点修复已生效：错误从点 `0` 移至点 `1`。这证明第 0 点已不再触发 IK，但尚未证明第 1 点 IK 路径正确。
- 离线可证伪检查：以该文件的 `initial_flange` 展开全部 58 个 delta 后，逐点还原 `segment_001_processed.json` 的 58 个原始法兰位姿，最大单分量误差为 `2.22e-15`。因此录制、平滑、`inverse(T0) @ Ti`、delta 文件和展开矩阵均正常；不能将本错误归因于轨迹录制。
- 第 1 点相对于轨迹起点仅约 `5.7 mm, -10.2 mm, -4.5 mm` 和小姿态变化；失败发生在 GUI 至 SDK 的 IK 调用层。
- 对照官方 SDK 示例与 Boss xCore 封装后，发现 GUI 曾额外写入 `hasElbow`、`elbow` 和 `confData`；官方/封装 IK 路径只做 `FlanInBaseToEndInRef → CartesianPosition → calcIk`。这些额外构型写入已删除，避免将不受证据支持的构型约束施加到目标。
- 新失败日志包含 `flange_target` 与转换后的 `end_target`，用于区分工具/基座坐标语义和控制器 IK 本身的拒绝。验证：Python 编译及 9 项单元测试通过。

## 2026-08-05 delta 法兰轨迹回放改为 IK 后复用普通关节回放

- 用户明确确认：delta 轨迹继续录制为法兰坐标系增量；不切换到关节增量录制，不使用 RT 控制，也不使用 xCore 非实时 `MoveL` 队列。
- 真机错误 `xCore motion did not enter a moving state after moveStart` 的根因是 delta 回放错误走了笛卡尔 `MoveL`，而已验证可用的普通轨迹回放走的是关节 `MoveAbsJ` 批量 append，两者不是同一条执行路径。
- 当前回放契约：读取当前 `flangeInBase` → 用 `T_current @ Delta_i` 展开完整法兰轨迹 → 使用 SDK `FlanInBaseToEndInRef(baseFrame, toolset, flange_pose)` 转换 IK 输入 → 对全部点完成 `calcIk`、关节范围和相邻解连续性校验 → 仅在全部通过后调用既有 `replay_joint_trajectory()` 的 `MoveAbsJ` 分批 append 回放。
- IK 前置验证：7 个关节范围分别是 J1/J3/J5 `[-178°, 178°]`、J2 `[-120°, 120°]`、J4 `[-60°, 145°]`、J6/J7 `[-50°, 50°]`；相邻 IK 点最大关节跳变上限为 `1.0 rad`，防止分支跳变。任一 IK、范围或连续性失败时，绝不向机械臂发送运动命令。
- 旧记录中“delta 回放使用批量 `MoveL`、最终法兰终点校验”的方案已废弃，仅保留为问题定位历史，不再是当前实现或建议。
- 验证：`python3 -m py_compile services/arm/xcore.py pages/arm_hand.py tests/test_xcore_pose_readout.py` 通过；`python3 -m unittest discover -s tests -v` 通过，9 项测试覆盖 delta 展开、IK 全量预求解、IK 失败不触发关节回放、法兰读数和历史笛卡尔批处理回归。
- 状态：`implemented-unverified`。尚未获得本次 IK → `MoveAbsJ` 路径的真机证据。

### 精确下一步

1. 重启 GUI，在空载、急停可达、无其他控制器占用的条件下，选择一个短 delta 文件进行首测。
2. 首次速度设为 `0.10` 至 `0.20`，确认日志出现 IK 完成后的普通 joint replay，而不是 `Cartesian trajectory` / `MoveL`。
3. 若失败，保留首个明确错误：`toolset/baseFrame`、法兰转换、IK 点索引、限位、分支跳变或 `MoveAbsJ` 执行错误；不要回退到 `MoveL` 或 RT。

## 2026-08-05 delta 回放显示成功但机械臂未动

- 用户录制的 `trajectory/delta_motion_20260805_185408_823825/` 有效：281 raw、58 delta、约 286 mm 空间范围，不是零轨迹。
- 根因在旧回放执行层：每个 `MoveL` 启动后立刻把控制器短暂的 `idle` 接受窗口误判为完成；下一点的 `moveReset` 清除了尚未实际执行的指令，所以日志会虚报“58 点成功”。
- 已改为整段轨迹批量 append、一次 `moveStart`、确认进入 `moving` 后等待结束，并以 `flangeInBase` 终点回读作为成功条件；未实际位移将直接报错。
- 另增加 SDK 回归测试，验证 MoveL 目标显式写入 `CartesianPosition.trans/rpy`、只调用一次 `moveStart`。
- Python 编译和 7 个单元测试通过；未执行真机回放。下一步是在空载、急停可达条件下重启 GUI 后重放该目录的 `segment_001_delta.json`。

## 2026-08-05 普通倾倒轨迹离线转换为 delta

- 用户要求将 `trajectory/倾倒轨迹/` 转为独立的 delta 轨迹目录，源文件不允许变更。
- 已生成 `trajectory/delta_倾倒轨迹_20260805_184910/`：包含 437 个 FK raw flange 样本、91 个 processed waypoints 和 91 个可回放 delta；`manifest.json` 标记为 `flange_delta` 并记录来源与 SHA256。
- 通过 xCore `model.calcFk(joints, Toolset(), ec)` 将 7 轴绝对关节录制离线转为 `flangeInBase` pose6，再生成 `inverse(T0) @ Ti`。
- 新增可复用工具 `scripts/convert_joint_trajectory_to_delta.py`。其运行路径严格只读：不调用 SDK 的 motion prepare/enable/stop/disconnect 接口。
- 源文件哈希在转换后不变；delta schema/臂别校验通过；Python 编译和 6 个现有单元测试通过。
- 未做真机回放；选择 `segment_001_delta.json` 后仍需在安全空载条件下验证实际执行。

## 2026-08-05 增量法兰轨迹录制与回放

### 2026-08-05 实机录制只生成 raw 的修复

- 用户实际录制目录 `trajectory/delta_motion_20260805_183859_911423/` 包含两段 raw（661、504 个样本），但每个 `pose6` 都是 `[0, 0, 0, 0, 0, 0]`。
- `manifest.json` 的失败原因是：去重后只剩一个点，故按规则不生成 processed/delta；这不是用户未移动或采样数量不足。
- 根因：GUI `XCoreArmSession.state()` 从 `cartPosture(...).pos` 读取位姿。该 SDK 对象的 `pos` 字段是默认零值；官方 SDK 示例与参考录制代码使用 `posture(CoordinateType.flangeInBase)` 返回的 6 元 `[x,y,z,rx,ry,rz]`。
- 修复：`services/arm/xcore.py` 改为 `posture(flangeInBase)`，并验证返回长度为 6。增量采集和增量回放锚点均经 `session.state()` 自动使用修复后的真实法兰位姿。
- 历史全零 raw 无法可靠恢复为 delta，必须重新录制。
- 验证：新增 `tests/test_xcore_pose_readout.py`；`python3 -m unittest discover -s tests -v` 共 6 项通过。离线非零样本可构建并验证 replayable delta；原全零 raw 仍按预期拒绝。

### 已实现

- `Arm + Hand` 的 `Drag (xCoreSDK)` 区新增“开始增量录制 / 停止增量录制”；与普通关节轨迹录制互斥。
- 增量录制复用物理按键按下/松开和连续 3 次松开去抖语义，按 80 Hz 采集 `flangeInBase` 的 `pose6`（m/rad，XYZ RPY）。
- 录制名称由 GUI `name` 输入给出；普通会话存入 `trajectory/<动作名>_<timestamp>/`，增量会话存入 `trajectory/delta_<动作名>_<timestamp>/`。每段保留 `raw`、`processed`、`delta` JSON 和 `manifest.json`；处理失败仍保留 raw 与失败原因。
- 离线处理按参考流程生成 `inverse(T0) @ Ti` delta，保存 `initial_flange`，并包含异常点处理、平滑、去重和空间重采样。
- 普通关节轨迹新文件标记 `trajectory_type: joint_absolute`；历史无标签文件仍按普通轨迹兼容。普通回放拒绝显式 delta 文件。
- 普通回放下方新增独立 `Delta Trajectory Replay` 区：校验文件类型、schema、臂别、坐标系、单位、姿态顺序和机器人型号；以当前法兰位姿展开 `T_current @ Delta_i` 后执行。

### 当前技术边界

- 直接 xCore SDK 尚未确认可用的笛卡尔 RT/批量路径接口。delta 回放当前使用受支持的同步 `MoveL` 单点序列，因此能执行展开路径但相邻点可能停顿。
- 尚未接入 IK、关节限位、碰撞检查或 RT 连续控制；delta 文件与当前法兰位姿检查通过不等同于真机安全可达。

### 验证

- `python3 -m unittest discover -s tests -v`：4 个 delta 离线处理/校验/展开测试通过，覆盖 identity delta、`initial_flange`、schema、臂别与无效样本。
- `python3 -m py_compile pages/arm_hand.py services/arm/xcore.py services/arm/flange_delta.py services/arm/control.py main.py`：通过。
- `timeout 8s xvfb-run -a python3 main.py`：GUI 正常进入 Tkinter mainloop；未连接机械臂，未执行真机动作。
- `xvfb-run` 控件实例化检查：动作名规范化及开始/停止增量录制控件存在，通过。
- 状态：`implemented-unverified`；需要在急停可达、控制器未被其他程序占用的真机条件下低速验证录制与回放。

### 精确下一步

1. 真机低速录制一个短 delta 段，确认目录命名、raw/processed/delta/manifest 和物理按键采样语义。
2. 在安全空载位置选择该 `_delta.json`，确认以当前法兰为起点展开并执行。
3. 若 MoveL 单点序列的停顿不可接受，基于 SDK 文档或官方例程验证笛卡尔 RT/批量 append 接口后替换执行层；不得猜测 SDK 调用约定。

## Last Updated

- 2026-08-05 18:10 CST

## Current Objective

- 机械臂连接失败时 GUI 保持可响应 — **已解决**

## Current Business Logic Position

- Main path: A -> B -> C -> D -> E (stable)
- Dual-arm path: A -> DA -> DB -> DC -> DD -> E (stable)
- Active branch: None

## Completed This Session

- **机械臂连接失败不再冻结 Tkinter 主线程**：关节轮询改为后台线程执行，连接失败只清空读数并保持 GUI 可操作。

## 2026-08-04 机械臂离线时 GUI 不冻结

### 问题

- 机械臂不可达时，`_poll_joints()` 在 Tkinter 主线程直接调用 xCore SDK `state()`。
- SDK 网络连接失败或阻塞时，主线程无法处理窗口事件，表现为 GUI 启动即卡死。

### 修改

- `pages/arm_hand.py`、`pages/dual_arm.py`：
  - 关节轮询改到 daemon 后台线程执行。
  - 后台线程只读取状态，UI 更新通过 `after(0, ...)` 回到主线程。
  - 使用轮询锁防止 SDK 阻塞时堆积重复轮询线程。
  - 连接失败不再打印完整 traceback，改为受限日志并显示 `offline` / `joints: -`。
  - “Fill From Live” 改为 `_run_async()`，避免按钮点击时主线程阻塞。
- `pages/arm_hand.py`、`pages/advanced_arm.py`、`pages/tasks.py`：
  - Stop 类按钮的 `stop_motion()` 调用改为后台线程执行，SDK 阻塞时 GUI 仍可响应。
- `services/arm/xcore.py`：
  - `close()` 增加 1 秒锁超时；后台轮询线程被网络调用阻塞时，关闭窗口不会被 session 清理锁卡住。

### 验证

- `python3 -m py_compile pages/dual_arm.py pages/arm_hand.py pages/tasks.py pages/advanced_arm.py main.py` 通过。
- `timeout 8s xvfb-run -a python3 main.py` 在无机械臂环境下成功进入 Tkinter mainloop；日志仅显示网络连接失败，窗口未卡死。
- 阻塞场景 smoke test：人为持有 `XCoreArmSession._lock` 后调用 `close(timeout_s=0.2)`，约 0.2s 返回，关闭窗口不会无限等待。
- 状态：implemented-unverified；尚未在真实机械臂连接/断连场景下验证自动恢复，也未做完整界面人工检查。

## 2026-08-04 GUI 按钮反馈迟缓

### 根因

- 仅把轮询放到后台线程仍不够：xCore SDK 的机器人构造/网络调用可能持有 Python GIL。
- `Arm + Hand` 和 `Dual Arm` 页面在启动时都自动启动关节轮询，导致离线时同时触发 SDK 网络连接，Tk 事件循环出现延迟。

### 修改

- 启动时不再自动连接机械臂；只有用户点击 `Refresh` 成功后才开启对应页面的 live readback。
- 背景轮询间隔调整为 1000ms。
- 轮询改为只读取 `jointPos`，不再每次同时查询笛卡尔位姿。
- 增加 `try_joint_positions()`：无法立即取得 session 锁时直接跳过本次轮询，不阻塞机械臂操作。

### 验证

- `python3 -m py_compile pages/arm_hand.py pages/dual_arm.py services/arm/xcore.py` 通过。
- `timeout 10s xvfb-run -a python3 main.py` 在机械臂不连接时进入 mainloop，未触发网络连接失败日志。
- 状态：implemented-unverified；需用户在实际 GUI 中确认按钮反馈延迟已消失。

## 2026-08-04 轨迹回放 `moveAppend` 参数错误

### 根因

- 回放轨迹文件有效：`segment_001.json` 包含 320 个点，每个点 7 个浮点关节值。
- `replay_joint_trajectory()` 将全部 320 个 `MoveAbsJCommand` 一次性传给 `moveAppend`，超出控制器/SDK 绑定对命令列表的实际限制。
- 回放构造 `MoveAbsJCommand` 时使用 `-1` 作为速度参数，与 SDK 官方示例的有效速度参数用法不一致。

### 修改

- `MoveAbsJCommand` 的速度参数改为 `1000`，实际关节速度继续由 `command.jointSpeed` 控制。
- 轨迹命令按每批 50 个拆分后调用 `moveAppend`，避免单次参数列表过大。
- 普通 `move_joints()` 同步改为使用 `1000` 速度参数，保持调用方式一致。

### 验证

- `python3 -m py_compile services/arm/xcore.py pages/arm_hand.py pages/dual_arm.py` 通过。
- 实际轨迹文件结构校验通过：320 点，7 点/批，全部为数值关节数组。
- 状态：implemented-unverified；需要在真机上用该轨迹执行低速回放验证。

- **左臂关节读数根因确认**：问题在 xcore 控制器 `get_joint_readout_rad()` 走 UDP 缓存，非 GUI 订阅/轮询。
- **控制器修复**：`query_joint_positions_for_readout()` + `get_joint_readout_rad()` 优先同步 `jointPos(ec)`；`dexbot_bottom_layer` 已 build。
- **GUI 防御性修正**（保留）：左右 bridge 分离、side 切换重建 service、`rclpy.shutdown` 生命周期、namespace 属性名修复。
- **用户验证通过**：重启控制器后 Dual Arm 左臂读数随真机更新。

## Problems And Resolutions

| 问题 | 结论 |
|------|------|
| 左臂 GUI J1–J7 冻结 ~19.7° | 根因在 `/arm_l/joint_states` 数据源 stale；控制器读数路径已修复 |
| 初期怀疑 GUI bridge 混用 | 已做防御性修正，但不是本次冻结的主因 |

## Verification

- 用户真机：左臂移动 → GUI 关节角正常更新 ✓
- 需重启 xcore 控制器后修复才生效（非仅重启 GUI）

## Files Changed

- `src/dexbot_bottom_layer/.../lbot_robot_xcore.py`
- `src/dexbot_bottom_layer/.../robot_controller_state.py`
- `src/gui/pages/arm_hand.py`, `src/gui/pages/dual_arm.py`, `src/gui/services/registry.py`
- `src/dexbot_toolbox/dexbot_toolbox/gui/arm_hand_gui.py`
- `src/gui/BUG_FIX_LOG_2026-06-12.md`（早期记录，最终以控制器修复为准）

## Current State

- 左臂关节 live readback 正常。CutTofo 左臂 handoff per-candidate offset 重构见 CutTofo `.project-log`。

## Next Steps

- 按 CutTofo 计划继续：`_DEBUG_STOP_AFTER_TRANSFER` 关闭后排完整 workflow 联调（若尚未做）。

## 2026-08-03 GUI 直连 xCore SDK 迁移进度

### 当前目标

- 以 `/home/tbl/Project/gui` 为主，机械臂主要功能统一使用 xCore SDK 直连。
- Web GUI 不在本次范围内。

### 已完成

- 新增共享 SDK 会话层：`services/arm/xcore.py`。
- `ServiceRegistry` 统一管理左右机械臂 SDK session。
- 左臂映射：`192.168.2.159`。
- 右臂映射：`192.168.2.160`。
- 状态读取、关节运动、笛卡尔运动、World Jog、停止、使能、急停恢复、清错、碰撞检测改为 SDK 调用。
- 拖动示教、轨迹录制、停止录制、保存轨迹、取消录制改为 SDK 调用。
- `pages/tasks.py` 的切片锚点位姿改为从 SDK 查询，不再依赖 ROS bridge。
- `arm_hand`、`dual_arm`、`advanced_arm` 删除重复的页面级 SDK 连接，统一复用共享 session。
- `get_ros_bridge()` 保留为主动报错保护，防止主路径误走 ROS。

### 验证结果

- 相关 Python 文件 `py_compile` 通过。
- 离线检查确认工作区路径有效。
- 离线检查确认左右臂 IP 映射正确。
- 源码扫描确认页面运行路径没有残留 ROS bridge 调用。

### 当前限制

- `rt_follow_start()` 暂无 xCore SDK 等价高层接口，当前明确报错，不回退到 ROS。
- `optimize_joint_comfort()` 暂无 xCore SDK 等价接口，当前明确报错。
- `servo_move_path()` 当前以多个 SDK 笛卡尔点顺序执行，不等价于原 ROS 实时轨迹模式，需真机验证运动连续性。
- 本次尚未启动 GUI，未执行真实机械臂动作验证。

### 启动方式

```bash
cd ~/Project/gui
python3 main.py
```

可选环境启动：

```bash
cd ~/Project/gui
source ~/miniconda3/etc/profile.d/conda.sh
conda activate vibe-coding
python3 main.py
```

### 下一步

1. 启动 GUI，先验证页面加载和状态读取。
2. 单独验证左右臂状态读取、World Jog、拖动示教。
3. 真机验证轨迹录制与回放。
4. 单独评估 `servo_move_path()` 是否满足当前业务运动要求。

## 2026-08-03 删除 GUI Comfort 功能

- 需求：删除 Tkinter GUI 中不再需要的 Comfort/Joint Optimization 功能；Web GUI 不在本次范围内。
- 修改：
  - `pages/arm_hand.py` 删除 Comfort 面板、参数窗口、状态变量、参数变量和回调。
  - `pages/advanced_arm.py` 删除 Comfort 面板、参数窗口、状态变量、参数变量和回调。
  - 保留 `services/arm/control.py` 中的 `ComfortParams` 和 `optimize_joint_comfort()` 兼容定义，避免影响 Web GUI 或其他未纳入本次范围的调用；该接口仍明确报告 xCore SDK 不支持。
- 验证：
  - `python3 -m py_compile pages/arm_hand.py pages/advanced_arm.py services/arm/control.py main.py` 通过。
  - `pages` 和 `services` 中不再存在 Comfort 页面引用，仅服务层兼容定义保留。
- 状态：implemented-unverified；尚未启动 GUI 做视觉确认。

## 2026-08-03 修复拖动按钮触发语义

- 用户反馈：GUI 点击“Drag ON”后机械臂可能直接进入可移动状态；期望为按住机械臂物理拖动按钮才允许运动，松开即停止。
- 根因：`services/arm/xcore.py` 的 `XCoreArmSession.drag(True)` 原先尝试组合中优先使用 `enableDrag(..., enable_drag_button=True)`，该参数可能绕过机械臂物理按钮，导致 GUI 点击后直接进入拖动状态。
- 修复：
  - 仅尝试笛卡尔自由拖动和关节自由拖动两种组合。
  - 两种组合都固定传入 `enable_drag_button=False`，要求控制器使用机械臂上的物理按钮触发拖动。
  - 删除自动拖动模式回退，避免失败后意外切换到无需物理按钮的模式。
  - 成功提示明确为 `drag enabled; hold the arm button to move`。
- 验证：
  - `python3 -m py_compile services/arm/xcore.py pages/arm_hand.py pages/advanced_arm.py pages/dual_arm.py` 通过。
  - 源码扫描确认 GUI 主路径只有 `enableDrag(..., False)`，没有自动按钮模式调用。
- 真机验证步骤：重启 GUI，点击 `Drag ON` 后不要触碰机械臂，确认机械臂不动；按住机械按钮确认可拖动；松开按钮确认停止；最后点击 `Drag OFF`。
- 状态：implemented-unverified，尚未执行真机验证。

## 2026-08-03 ArmHand 页面增加左右臂独立 IP 输入

- 需求：顶部控制栏不能只显示一个 `arm_ip`，需要左臂、右臂分别配置 IP。
- 修改：
  - `pages/arm_hand.py` 增加 `L arm_ip` 和 `R arm_ip` 两个输入框，默认分别为 `192.168.2.159`、`192.168.2.160`。
  - 侧别切换时，当前 `ArmControlService` 使用对应输入框的 IP。
  - 当前选中侧的 IP 输入框失焦或执行动作前，会重新同步 SDK session；修改 IP 后会关闭旧 session 并按新 IP 建立连接。
  - 删除原来单一 `_robot_ip_var` 的主页面依赖。
  - 修复侧别切换时 CAN 接口被重复赋值的问题：左侧使用 `can0`，右侧使用 `can1`。
  - `ServiceRegistry.get_arm_session()` 支持按 side + ip 缓存/重建 SDK session。
  - `ArmControlService` 支持传入可选 IP。
- 验证：`python3 -m py_compile pages/arm_hand.py services/arm/control.py services/registry.py` 通过。
- 状态：implemented-unverified；尚未启动 GUI 进行界面视觉确认或连接真机。

## 2026-08-03 机械臂与灵巧手记录支持自定义名称和自动编号

### 需求

- 机械臂位置记录不再要求用户输入数字 ID，用户输入自定义名称。
- 灵巧手姿态记录增加自定义名称输入。
- 两类记录保存时自动分配编号，并继续默认保存到工作区本地文件。
- 启动或切换侧别/型号时自动扫描本地记录，避免记录只存在于运行内存中。

### 实现

- `pages/arm_hand.py`：机械臂预设输入改为 `name`，自动编号显示为只读 `auto id`；列表显示 `编号 | 名称`。
- `pages/dual_arm.py`：双臂子页面采用同样的机械臂和灵巧手命名交互。
- `services/arm/control.py`：机械臂记录增加 `preset_id` 和 `name` 字段；内部 JSON key 继续使用数字字符串，保持 Move-To、Run、Delete 和数字序列兼容。
- `services/hand/control.py`：灵巧手姿态继续使用 `pose_001.json` 等自动编号文件名，同时写入 `pose_id` 和 `name` 字段；增加元数据读取接口供列表显示。
- 机械臂记录仍保存到 `arm_preset/arm_poses_{side}.json`；灵巧手姿态仍保存到 `poses/poses_{model}_{side}/pose_*.json`。

### 兼容性

- 旧机械臂 JSON 没有 `name` 时列表显示 `(unnamed)`，不影响按数字 ID 执行。
- 旧灵巧手 JSON 没有 `name` 或 `pose_id` 时回退使用文件名 stem。
- 不删除、不覆盖已有本地记录；新记录从现有最大编号继续递增。

### 验证

- `python3 -m py_compile pages/arm_hand.py pages/dual_arm.py services/arm/control.py services/hand/control.py main.py` 通过。
- 临时目录离线测试通过：机械臂编号从 1、2 递增并保存名称；灵巧手生成 `pose_001.json` 并保存 `pose_id`、`name`。
- 状态：implemented-unverified；尚未启动 GUI 做视觉确认，尚未连接真机验证记录/执行流程。

## 2026-08-03 删除机械臂预设 Prev/Next 按钮

- 删除 `pages/arm_hand.py` 中 Arm Presets 区域的 `Prev`、`Next` 按钮。
- 删除对应的 `_arm_prev()`、`_arm_next()` 回调，避免保留无用交互代码。
- 保留列表直接选择、`Move-To`、`Run`、`Delete` 等有效操作。
- `python3 -m py_compile pages/arm_hand.py pages/dual_arm.py services/arm/control.py services/hand/control.py` 通过。

## 2026-08-03 增加可选择并记忆机器人工作区

### 需求

- 在 Arm + Hand 顶部工具条增加工作区选择按钮。
- 用户可以手动选择机器人工作区，后续启动自动使用上次选择的工作区。

### 实现

- `pages/arm_hand.py` 增加 `Workspace` 按钮和目录选择对话框。
- 工作区必须同时包含：
  - `src/sdk/xcoresdk_python-v0.5.1.ar_12`
  - `src/sdk/linkerbot-python-sdk`
- 选择结果保存到：`~/.config/dexbot_gui/config.json`。
- `main.py` 和 `services/registry.py` 启动时优先读取已保存工作区，再尝试自动发现和默认工作区。
- 保存工作区后提示重启 GUI，避免运行中的 Python SDK 模块和动态库继续使用旧工作区。

### 验证

- `python3 -m py_compile main.py app/shell.py pages/arm_hand.py services/registry.py services/arm/xcore.py services/hand/control.py` 通过。
- 临时目录工作区结构校验通过；不完整目录不会被视为有效工作区。
- 状态：implemented-unverified；尚未启动 GUI 做按钮视觉确认和实际切换验证。

## 2026-08-03 轨迹录制文件与 Skill 的业务逻辑

### 已确认的业务约束

- GUI 负责拖动示教过程中的轨迹采集，并生成轨迹文件。
- 用户手动把生成的轨迹文件放入指定 Skill 的轨迹目录。
- 一个 Skill 可以包含一条或多条轨迹文件，不要求“一条轨迹对应一个 Skill”。
- Skill 是轨迹回放能力的执行载体；轨迹文件是该 Skill 管理的具体数据资源。
- Planner 下发任务时只需要指定 Skill 和轨迹文件/轨迹名称，Skill 负责读取并回放对应轨迹。
- 轨迹录制阶段希望依据机械臂物理拖动按钮的按下/松开状态，切分连续或多段轨迹。

### 待确认技术问题

- 当前 xCore SDK 或控制器接口是否能直接读取机械臂物理拖动按钮的按下/松开状态。
- 如果 SDK 不暴露该状态，需要继续复用控制器的 `startRecordPath`/`stopRecordPath` 机制，或采用其他可观测信号实现轨迹分段。

### 已澄清技术事实

- 当前 xCore SDK 提供 `robot.getKeypadState(ec)`，可以读取末端物理按键 `key1_state` 至 `key7_state`。
- SDK 示例位于 `src/sdk/xcoresdk_python-v0.5.1.ar_12/example/get_keypad_state_example.py`。
- 现有 `robot_motion_executor` 已有按键轮询实现：`read_keypad_states()`、`wait_for_drag_key_press()`、`wait_for_drag_key_release()` 和 `record_path_on_robot()`。
- 因此，GUI 不需要通过关节角度变化推断物理按钮状态，可以直接使用 xCore 的按键状态接口。

### 录制与回放路径约束

- GUI 自定义录制方案可以轮询 `robot.jointPos(ec)`，将关节角度和时间信息保存为 JSON/YAML 轨迹文件。
- 每次物理按钮按下到松开对应一个轨迹片段；用户再次按下按钮可以继续采集下一段。
- 用户点击 GUI 的“停止录制”后，系统结束采集、关闭拖动模式，并保存本次轨迹结果。
- xCore 原生 `startRecordPath()` 的数据保存在机器人控制器内部，不等同于 JSON/YAML 文件；如果要求文件化、可复制、可放入代码仓库，需要采用 GUI 自定义采集逻辑。
- 用户手动将 GUI 生成的轨迹文件放入指定 Skill 的轨迹目录。
- 一个 Skill 可以包含一条或多条轨迹文件；轨迹文件是 Skill 管理的数据资源，不要求一条轨迹对应一个 Skill。
- Planner 只需要指定 Skill 及轨迹名称，Skill 负责加载对应文件并执行回放。

## 2026-08-03 GUI 自定义拖动轨迹录制

### 需求与界面调整

- Drag 区删除 `Rec Start`、`Rec Stop`、`Save`、`Cancel` 四个基于控制器原生路径的按钮。
- 新增 `开始录制` 和 `停止录制` 两个按钮。
- 点击 `开始录制` 后自动进入物理按钮拖动模式；不点击 GUI 的 Drag ON。
- 物理按钮按下开始采集关节轨迹，松开结束当前片段；可以再次按下继续采集下一片段。
- 点击 `停止录制` 后停止采集并关闭拖动模式。

### 当前实现

- `services/arm/xcore.py` 增加 `joint_positions()` 和 `keypad_states()`，分别读取 7 个关节角度和 `key1_state` 至 `key7_state`。
- `pages/arm_hand.py` 在后台线程中轮询物理按键和关节角度，采样周期当前为 `0.02s`。
- 每次录制创建一个时间戳目录：`/home/tbl/Project/gui/trajectory/YYYYMMDD_HHMMSS_microseconds/`。
- 每个按钮按下/松开片段保存为 `segment_001.json`、`segment_002.json` 等。
- 同目录写入 `manifest.json`，记录机械臂侧别、IP、片段数量和文件列表。
- 轨迹点当前保存关节弧度和相对片段起始时间，不调用 xCore 原生 `startRecordPath()`。

### 验证与边界

- `python3 -m py_compile pages/arm_hand.py services/arm/xcore.py` 通过。
- 临时轨迹 JSON 格式检查通过。
- 尚未进行真机验证；需要确认真实设备上 `getKeypadState()` 的按下值变化、采样频率和录制期间 xCore 连接稳定性。

### UI 修正

- `Drag ON` 和 `Drag OFF` 按钮保留，用于单独手动开启/关闭拖动模式。
- `开始录制` 和 `停止录制` 按钮仅负责自定义轨迹采集及其生命周期，不替代上述拖动控制按钮。

## 2026-08-03 增加 GUI 自定义轨迹文件回放

### 功能

- 在 Drag 区下方新增独立的 `Trajectory Replay` 区域。
- `选择轨迹` 打开文件浏览器，选择一个 JSON 轨迹片段文件。
- `开始回放` 读取所选文件并执行回放。

### 回放逻辑

- 读取轨迹文件中的 `points[*].joint_positions_rad`。
- 读取当前机械臂 7 个关节角度，与轨迹第一个点比较。
- 默认起点容差为 `0.05 rad`；超出容差时先自动 MoveJ 到轨迹起点。
- 到达起点后，将轨迹关节点按顺序提交给 xCore SDK 执行。
- 回放速度复用 Arm Presets 的 `speed` 参数。
- 当前回放针对单个 `segment_*.json` 文件；多段轨迹需要由上层按顺序调用或后续增加 manifest 回放入口。

### 验证

- `python3 -m py_compile pages/arm_hand.py services/arm/xcore.py` 通过。
- 临时 JSON 轨迹格式检查通过。
- 尚未进行真机验证；需要确认真实控制器对批量 `MoveAbsJCommand` 的执行连续性和安全速度。

## 2026-08-03 改善轨迹回放连续性

- 根因：旧实现将每个采样点创建为 `MoveAbsJCommand(..., zone=0)`，控制器会把每个点当作必须停稳的终点，因此回放出现明显卡顿。
- 修改：`replay_joint_trajectory()` 对中间点使用默认 `blend_zone_mm=10.0` 的转弯区，允许轨迹融合；最后一个点仍使用 `zone=0` 精确停稳。
- 轨迹起点对齐、关节速度和文件格式保持不变。
- 当前仅完成静态修改，仍需真机确认 `10 mm` 转弯区对实际运动平滑度和安全性的影响。

## 2026-08-03 轨迹臂侧校验与独立回放速度

- 录制的 `segment_*.json` 已写入 `arm_side`，取值为 `left` 或 `right`；会话 `manifest.json` 同样记录臂侧。
- 回放读取轨迹后，先校验 `arm_side` 是否有效，并要求它与 GUI 当前选中的机械臂一致；缺失、非法或不一致时拒绝回放，不连接、不移动机械臂。
- `Trajectory Replay` 新增独立 `speed` 输入，范围限制为 `0.01 - 1.0`，回放不再复用 Arm Presets 的速度参数。
- 代码已完成静态修改，仍需进行 GUI 启动和真机回放验证。
