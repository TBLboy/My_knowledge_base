# 当前 Session

- 当前 Task：`data-collection-business-clarification`（balanced，active/prepare）：澄清数据采集链路业务逻辑，只产出基线文档，不改业务代码。
- 已批准并固化：
  - `hdf5-recording-format` v1.7：相机同步帧组驱动主时间轴、真实 60/30Hz；松 Grip 时 adapter 持续保持的 action 有效；action 可选 `eef_pose`/`joint_position`，按适配器声明落盘；观测字段白名单含 `eef_pose (T,7) xyzw`；manifest 删 success/discarded/n_discarded；`cam_dup` 废弃；`spec_version=inhouse-hdf5-v2`；`collect_mode=teleop`；`project` 只写 manifest；不记录相机内外参；`robot_id` 由机器人描述提供。
  - `unified-platform-integration-boundary` v1.5：采集中间层提供抽象基类 + 封闭字段白名单，适配器只能继承并声明子集，越界启动期失败；采集层不直连 adapter。
- 下一步（未定，需用户裁决）attrs 四处：
  1. `source` 同名不同义：`eef_pose` attrs 的 source 是数值来源（SDK/FK），`action/` 的 source 是控制来源（command/leader/policy）。
  2. `joint_velocity` / `joint_effort` 缺 attrs（建议补 `names` + `unit`）。
  3. action 的 `joint_position` 缺 attrs（建议补 `names` + `unit=rad`）。
  4. `base_extrinsics` 未列入 R8 根 attrs（建议补并注明仅双臂）。
- 已暂缓、不再追问：action 在 hold/暂停/失控的间歇缺失；不完整帧处理；采集端自检与「拒收」及 `_SUCCESS` 封口判据；音频/language；历史 HDF5 兼容。
- 约束：以元文档为基准，除 action `eef_pose`、四元数 attrs、观测 `eef_pose` 维度统一外不增删字段；新 HDF5 尚未实施到代码，现行代码仍是 Franka schema v3。
- 相关产物：`.vibe/docs/数据采集链路数据流拓扑.md`、`.vibe/docs/数据采集链路业务待澄清清单.md`。
