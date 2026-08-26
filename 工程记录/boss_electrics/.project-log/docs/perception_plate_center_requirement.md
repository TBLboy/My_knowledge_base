# 感知组需求：scene2 后处理输出 `plate_center`

状态：`perception-implemented-v1.0.19`，源码已确认输出 `plate_center`，真机相机未复测。
创建时间：2026-08-15
最近更新：2026-08-24

## 需求描述（可直接提给视觉组）

### 标题

在 `boss_kitchen_scene2` 后处理中新增“餐盘中心 `plate_center`”输出，用于倾倒任务的目标定位。

### 背景

- 当前相机1感知配置 `task_name: boss_kitchen_scene2`，模型 `yolo26l_obb` 的类别已包含 `plate`，`conf_threshold: 0.30`。
- 但 `boss_kitchen_scene2` 后处理的 `CENTER_CLASSES` 只有 `seasoning_box`、`bowl_handle`、`bowl`、`pot_handle`，没有 `plate`，所以当前 `/perception/scene` 不会发布 `plate` 或 `plate_center`。
- 消费方 `PanPourPolicy` 已预留 `update_plate_center(plate_center_in_center)`，倾倒点公式为 `pour_point_C = plate_center_C + pour_offset_C`，业务目标统一在机器人中心坐标系 C 下表达。

### 期望输出

1. 把 `plate` 加入 `boss_kitchen_scene2` 的深度后处理中心类，计算餐盘中心点并进行坐标转换。
2. 通过现有 `ScenePerception.objects` / `ObjectDetection` 发布；`class_name` 请使用稳定命名 `plate_center`。如果视觉组更倾向保留原始 `plate` 类供上层适配，请在确认时明确告知最终类名，我们按最终命名接入。
3. `pose.position` 为餐盘中心在机器人中心坐标系 C 下的 `xyz`（单位：米），`scene.header.frame_id` 请明确标记为 C。当前中心标定使用 `T_center_cam`，`calibration_path` 已指向中心标定结果。
4. 置信度按现有 `conf_threshold` 规则处理，与 `pot_handle_center` 等中心类保持一致；`scene_valid` 语义保持不变。
5. 无盘子、遮挡或有效深度不足时，不发布 `plate_center`，不要用 0 置信度占位。
6. 每帧更新 `header.stamp` 和 `scene_id`，供上层做新鲜度判断，避免旧餐盘观测驱动新的倾倒任务。
7. 本期只需要餐盘中心点位置；盘子的尺寸/朝向可作为附带信息输出，但不应阻塞本次需求。
8. 兼容性约束：不要破坏现有 `pot_handle_center`、`pot_inner_handle`、`bowl`、`bowl_handle` 等输出。

### 验收标准

- 视野内放置盘子时，`/perception/scene` 至少发布一个 `class_name=plate_center` 的 `ObjectDetection`，且 `pose.position` 在 C 下为有效的有限值。
- 移走盘子后，连续若干帧不再发布 `plate_center`。
- 同一帧锅把、碗、餐盘同时出现时，多类输出并存且各自坐标稳定、不互相覆盖。
- 提供一组现场样本（RGB + depth + 标定帧快照，或 rosbag/JSON 快照），便于我方离线验证 `plate_center` 与真实盘心的误差，再决定是否直接接真机链路。

### 依赖与后续

- 视觉组实现并给出最终类名后，我在主仓库补齐 `ScenePerception` 到 `PanPourPolicy.update_plate_center()` 的适配与单元测试，把餐盘中心真正接进 `/perception/scene`。
- 完成适配后，用真机验证倾倒点精度，再关闭本需求。

## 当前事实

- 2026-08-24 已安装新版 `ros-humble-dexbot-perception_1.0.19-0jammy_all.deb`。
- `scene_stir_frying/post_processor.py` 的 `CENTER_CLASSES` 已包含 `plate`，`_append_source_center` 会发布 `class_name=plate_center`。
- 静态断言通过；真机/离线相机帧尚未复测 `plate_center` 的实际坐标输出。

## 对感知组的建议需求

在 `boss_kitchen_scene2` 后处理中增加餐盘中心输出，建议明确以下契约：

- 输出类名稳定，例如 `plate_center`，或明确保留原始 `plate` 检测供上层适配。
- 坐标为机器人中心坐标系 C；当前 `calibration_path` 已指向 `center_calibration_result.yaml`。
- 明确置信度阈值、`scene_valid`、深度缺失时的行为。
- 明确时间戳、frame_id 和新鲜度语义，避免旧餐盘观测驱动新任务。

## 消费方

- `PanPourPolicy.WAITING_FOR_PLATE_DETECTION`
- `PanPourPolicy.update_plate_center(plate_center_in_center)`
- 倾倒点公式：`pour_point_C = plate_center_C + pour_offset_C`

## 后续动作

1. 与感知组正式沟通并确认 `plate_center` 输出契约。
2. 感知侧实现后，在主仓库接入 scene 到 Policy 的餐盘适配与测试。
3. 更新本记录状态，并补充真机验证证据。
