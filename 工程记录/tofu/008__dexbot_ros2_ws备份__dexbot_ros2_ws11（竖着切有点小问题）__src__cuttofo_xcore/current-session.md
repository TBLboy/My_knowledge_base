# Current Session

## Last Updated

- 2026-05-17 (SAM3 point prompt research)
- 2026-05-16 19:55 CST

## Current Objective

- Implement user-drawn box for SAM3 manual tofu re-segmentation: draw box → BOX mode, delete box → TEXT mode.

## Completed This Session

### Phase7 Vertical Cut (done, awaiting test)
- Implemented `build_vertical_cut_waypoints()`: 4-step per cycle (press/cut/retract/return) + front_half push-pair + tail push + step.
- Replaced Phase7 placeholder with full action handler: `_tick_phase7_cut()`, goal/result callbacks, Phase7 → DONE.
- Added `phase7_third_cut` config with independent parameters.
- Integrated Phase7 into `knife_cut_action_server` via new `phase7_name` parameter.
- Verified 49 waypoints generated for 9 cycles, all positions correct (±1e-4m).
- Phase6 re-prepare now transitions to Phase7 vertical cut (was placeholder).
- Extended `MoveToPreparePose.action` goal with solver/execution override fields for Phase6 independent re-prepare params.
- Added `cutting.phase6_prepare` config, fixed prepare server to recompute TCP from corners using goal offset.
- Phase5 success now transitions to Phase6 instead of DONE.

### SAM3 Box Prompt — 调研完成, 规划最终定稿
- Researched SAM3 API: `Sam3Model` (文本/BBox) vs `Sam3TrackerModel` (点/Mask)
- **Decision**: 用户拖拽画框方案 — 拖拽画框进入 BOX MODE，框删除回退 TEXT MODE
- **确认点**: 1) 右键删框 2) 无超时 3) BOX 失败不自动删 4) 框=黄色，SAM3结果=绿色 5) RegionOfInterest 够用
- **架构**: 单一 auto_detect_callback，无推理锁，BOX/TEXT 条件分流
- **ROS Topic**: `/sam3/user_box` (RegionOfInterest)
- 完整实现计划: `.project-log/sam3-point-prompt-research.md` 章节 8 (含代码模板)
- 已确认: `Sam3TrackerModel` 不支持文本 prompt, 不能替换现有模型

## Current Business Logic Position

- Main path: Phase1 grab → Phase2 prepare → Phase3 cut → Phase4 return+wait+rotate+re-prepare → Phase5 cut → Phase6 return+wait+rotate+re-prepare → Phase7 vertical cut → DONE.
- **New branch**: 切割中途 SAM3 文本检测失败 → 用户在画面拖拽画框 → BOX MODE → 用户右键删框 → 回退 TEXT MODE。
- Active node: Phase7 vertical cut implemented; SAM3 user-drawn box prompt not yet implemented.
- Active edge: Phase7 = press/flange_Z → cut → retract/flange_-Z → return → [front_half push-pair] → [tail push] → DONE.
- Active branch: None.

## SAM3 Point Prompt Segmentation (Planned — 方案A定稿)

```
问题: 豆腐切割后形态改变，文本 "tofu" 可能检测失败
方案: 方案A - 点→小BBox (推荐)
  点击点 → 扩展为 40x40 px bbox → 复用 segment(image, [bbox])
  优点: 无需额外模型，参数 point_prompt_box_size 可调

并发设计 (方案A - 推理锁):
  self._inference_lock = threading.Lock()
  点提示 callback: with self._inference_lock (阻塞) → 立刻执行推理
  Auto-detect timer: if not acquire(blocking=False): return (非阻塞，跳过本周期)
  行为: 点提示抢占式优先，auto-detect 礼让；auto 丢一帧不影响
  auto 策略: 点提示成功后不永久停 auto，继续文本跑；再次失败再点

数据流:
  鼠标点击 (cv2.setMouseCallback)
    → /sam3/point_prompt (PointStamped)
    → sam3_detector_node: 推理锁保护
    → detector.segment(image, [bbox])
    → /detected_objects
    → pose_estimator_node → tofu_state_node → /tofu_state

改动:
  camera_viewer_node.py: cv2.setMouseCallback + 发布 /sam3/point_prompt
  sam3_detector_node.py: 推理锁 + 订阅 /sam3/point_prompt + segment([bbox])

文件: .project-log/business-logic/decision-records.md
     .project-log/sam3-point-prompt-research.md
```

## Phase7 Vertical Cut Flow (Active)

```
Phase6 re-prepare success
  → Phase7: read phase7_third_cut config
  → Phase7: for each cycle (9 total):
      press_normal along flange +Z (0.008m)
    → cut along base_y (0.05m)
    → retract along flange -Z (0.008m)
    → return to anchor
    → [cycle 4 only]: push_half_z → anchor → push_half_back_z → anchor
    → [cycle 8 last]: push_tail_z
    → step to next anchor (base Z -0.005m)
  → Phase7 complete → DONE
```

## Phase4 New Flow (Active)

```
Phase3 done
  → Phase4: return-to-prepare (RT Cartesian)
  → Phase4: move to wait_joint_positions
  → Phase4: BLOCK on terminal input() — "rotate tofu, press Enter"
  → Phase4: transitions to Phase2
  → Phase2: re-serve tofu (use_vision=True, edge_align=true)
  → Phase2: prepare success
  → Phase4 done → Phase5
```

## Phase6 New Flow (Active)

```
Phase5 done
  → Phase6: return-to-prepare (RT Cartesian)
  → Phase6: move to wait_joint_positions
  → Phase6: wait for /tmp/cuttofo_phase6_continue
  → Phase6: transitions to Phase2
  → Phase2: re-serve tofu (use_vision=True, edge_align=true)
  → Phase2: prepare success
  → Phase6 done → Phase7
```

## Problems Encountered

- Phase2 IK `valid=0`: all 263 seeds rejected by strict pos/rot error thresholds. Likely cause is `edge_align=true` + `offset_a=0` making target too constrained. Not yet resolved (separate from Phase4 work).

## Verification

- `python3 -m py_compile` passed for all modified Python and launch files.
- YAML validation passed for `phase7_third_cut`.
- `colcon build --packages-select cuttofo_xcore --cmake-args -DCMAKE_BUILD_TYPE=Release` succeeded (0.64s).
- Waypoint position verification: 49 waypoints for 9 cycles, all press/cut/retract/return/push positions correct (±1e-4m).
- Installed code and config verified in `install/cuttofo_xcore/`.
- `importlib.metadata` resolution succeeded for `cuttofo-xcore`.

## Next Steps

### Phase7 hardware test (immediate)
1. Relaunch and test full chain through Phase7 vertical cut.
2. Verify vertical cut waypoint structure in runtime logs.
3. Tune config values (press_normal, push distances, cycles) based on real tofu cutting results.

### SAM3 point prompt (planned, ready for implementation)
1. **camera_viewer_node.py**: `cv2.setMouseCallback` + 坐标映射 + 绿色十字 + 发布 `/sam3/point_prompt` (~55行)
2. **sam3_detector_node.py**: 推理锁 + 订阅 `/sam3/point_prompt` + bbox扩展 + `segment(image, [bbox])` + 橙色可视化 (~70行)
3. **sam3_detector.py**: 0改动, 复用 `segment()`
4. 验证: 点击豆腐 → 橙色 mask → 下游 tofu_state 更新
