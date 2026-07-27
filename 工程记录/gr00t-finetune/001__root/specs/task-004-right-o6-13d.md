# Task-004 — 单右臂 O6 13D 数据与 Embodiment 配置

## 目标

将倒水任务转换为独立的 GR00T/LeRobot 训练数据集：三路 RGB 视觉观测、右臂 7 个关节位置、右 O6 手 6 个连续关节角度；状态与动作均为 13D。

## 已批准契约

- 图像：`cam_top`、`cam_left_wrist`、`cam_right_wrist`。
- state：`qpos[7:14]`（右臂关节，rad）+ `qpos[20:26] * 100 / 255`（O6 SDK 角度，0..100）。
- action：`actions[7:14]` + `actions[20:26] * 100 / 255`，使用相同顺序和尺度。
- O6 顺序：`thumb_flex`、`thumb_abd`、`index`、`middle`、`ring`、`pinky`。
- 不在 state/action 中放入左臂或左手；不把 O6 压缩为二值开合。

## 非目标

- 不删除或覆盖现有 `lerobot_dataset/` 双臂 ee_pose 14D 产物。
- 不包含深度、IMU、力传感器或语言标注。
- 不执行真实机器人控制；部署侧 CAN 编码仅记录契约。

## 实现

- 新转换器：`convert_to_lerobot_right_o6.py`。
- 输出目录：`lerobot_dataset_right_o6_13d/`。
- 输出保留 148 个有完整 telemetry 的 episode；源中缺 telemetry 的 episode 明确跳过。
- 所有视频复制到新输出，避免旧数据集和新数据集混用。
- `meta/info.json`、`meta/modality.json` 明确标记 13D 分段与命名。
- 新配置：`gr00t_n1/examples/linkerhand_right_o6_config.py`，使用 `NEW_EMBODIMENT`、两个 `NON_EEF` 动作分组（右臂、右 O6 手）。

## 验收与验证

1. 每个写入 parquet 的 state/action shape 均为 13，float32、有限值。
2. 右臂 7D 与源切片严格相等；O6 6D 与源切片乘 `100/255` 一致。
3. `modality.json` 分段为 `right_arm[0:7]`、`right_o6_hand[7:13]`。
4. 三路视频文件数均为 148，且每路 timestamps 与 telemetry 帧数匹配。
5. 运行时导入 embodiment 配置成功，注册键和 dataset modality 键一致。
6. 任意已存在输出目录必须显式 `--overwrite` 才可替换，防止静默覆盖。

## 风险与回滚

- 完整视频复制会耗时与占用空间；后台执行并保留日志。
- 失败时删除新输出目录即可回滚；旧 `lerobot_dataset/` 不受影响。
