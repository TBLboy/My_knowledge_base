# 感知组需求：scene2 后处理输出 `plate_center`

状态：`pending`，尚未正式向感知组提出。
创建时间：2026-08-15

## 当前事实

- 当前模型 `kitchen_robot_home/local_models/yolo/yolo26l_obb.pt` 的类别包含 `plate`。
- 当前相机1感知配置 `task_name: boss_kitchen_scene2`。
- `boss_kitchen_scene2` 后处理的 `CENTER_CLASSES` 只包含 `seasoning_box`、`bowl_handle`、`bowl`、`pot_handle`，没有 `plate`。
- 因此当前 `/perception/scene` 不会发布 `plate` 或 `plate_center`，V1 的餐盘定位链路暂时没有感知输入。
- 记录时相机未连接，未做真实盘子识别验证。

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
