# Branch: sam3-point-prompt (SAM3 User-Drawn Box for Manual Re-Segmentation)

## Status: idea (structured but not confirmed for implementation)

## Purpose
When SAM3 text prompt ("tofu") fails after tofu rotation/cutting, the user can draw a box on the camera feed to manually guide SAM3 re-segmentation. Box exists = BOX mode (use RegionOfInterest), box deleted = TEXT mode (auto-detection resumes).

## Start Node
- PHASE_2 / PHASE_6 re-prepare (when /tofu_state invalid or detection fails)

## Target Node
- PHASE_2 / PHASE_6 re-prepare (with valid /tofu_state from manual re-segmentation)

## Logic Path
Auto-detect fail → user draws box → SAM3 uses RegionOfInterest → /detected_objects → /tofu_state valid → prepare proceeds

## Execution Chain (planned)
1. camera_viewer_node: cv2.setMouseCallback → detects drag-box → publishes /sam3/user_box (RegionOfInterest)
2. sam3_detector_node: checks /sam3/user_box → if present, uses box for segment(image, [bbox]); if absent, uses text prompt
3. User right-clicks to delete box → resumes auto text detection
4. Visualization: user box = yellow, SAM3 result = green

## Assumptions
- RegionOfInterest message format is sufficient for SAM3 API
- No inference lock needed (single callback handles BOX/TEXT switching)
- camera_viewer_node has access to image coordinate ↔ pixel mapping

## Risks
- SAM3 may still fail even with box prompt
- User workflow: drawing box adds manual step to autonomous pipeline
- Potential race conditions between auto-detection timer and manual box callback

## Open Questions
- What to do if SAM3 fails with box prompt (retry? fallback?)
- Should box persist across detection failures?
- Thread safety of concurrent auto-detect + manual box in ROS2 node

## Verification Plan
1. Test with real tofu: start auto-detection, intentionally obscure tofu, draw box
2. Verify /detected_objects publishes correct mask for box region
3. Verify /tofu_state updates and Phase2/6 re-prepare proceeds
4. Verify deletion of box resumes auto-detection

## Merge Condition
- Hardware verified: user draws box → SAM3 detects → prepare pipeline proceeds
- No regression in existing auto-detection flow
- User workflow is natural and does not break the cutting sequence

## Research Notes (from original document)
---
# SAM3 点提示分割调研笔记

**日期**: 2026-05-17
**状态**: 已调研，待实现

---

## 1. 背景问题

豆腐切割后形态改变，SAM3 文本提示 (`"tofu"`) 可能检测失败。
用户希望在摄像头画面里点击豆腐来重新提示 SAM3 进行分割。

---

## 2. 现有 Pipeline

```
RealSense Camera
      │
      ├── /camera/color/image_raw (RGB 1280x720)
      │
      ▼
sam3_detector_node          ← /sam3/text_prompt (String, for prompt changes)
      │                        auto_detect timer @ 5 Hz
      │                        Calls SAM3Detector.segment_with_text()
      │
      ├──► /detected_objects  (ObjectStateArray)  — mask + bbox per object
      ├──► /sam3/segmentation_result (Image)      — visualization overlay
      │
      ▼
pose_estimator_node         ← /detected_objects (time-synced with depth)
      │                      ← /camera/aligned_depth_to_color/image_raw (848x480 16UC1)
      │                        Calls vision_utils.get_pose_from_mask()
      │
      └──► /objects_with_pose (ObjectStateArray) — with 6D pose + corners + extents
      │
      ▼
tofu_state_node             ← /objects_with_pose
      │                        Filters by class_id == "tofu"
      │                        Sliding-window buffer (N frames)
      │
      └──► /tofu_state (TofuState) — top_corners, edge_dir, tcp_target, top_y
      │
      ▼
camera_viewer_node          ← /camera/color/image_raw
      │                      ← /sam3/segmentation_result (priority 1)
      │                      ← /objects_with_pose (for 6D pose overlay)
      │
      └── OpenCV window with overlays
```

---

## 3. SAM3 API 研究

### 3.1 现有代码使用的模型

```python
# sam3_detector.py line 46-60
from transformers import Sam3Model, Sam3Processor

self.processor = Sam3Processor.from_pretrained(model_path, local_files_only=True)
self.model = Sam3Model.from_pretrained(model_path, local_files_only=True).to(self.device)
```

### 3.2 Point Prompt 支持

SAM3 官方支持两种 prompt 模式：

| 模式 | 模型类 | Processor 类 | 支持 prompt |
|------|--------|-------------|------------|
| Concept Segmentation | `Sam3Model` | `Sam3Processor` | 文本 + BBox |
| Promptable Visual Segmentation (PVS) | `Sam3TrackerModel` | `Sam3TrackerProcessor` | 点 + BBox + Mask |

### 3.3 Point Prompt API (Sam3TrackerModel)

```python
from transformers import Sam3TrackerModel, Sam3TrackerProcessor

model = Sam3TrackerModel.from_pretrained("facebook/sam3").to(device)
processor = Sam3TrackerProcessor.from_pretrained("facebook/sam3")

# 点坐标: [batch, object, points, xy]
input_points = [[[x1, y1], [x2, y2]]]
input_labels = [[1, 0]]  # 1=前景, 0=背景

inputs = processor(
    images=image,
    input_points=input_points,
    input_labels=input_labels,
    return_tensors="pt"
).to(device)

with torch.no_grad():
    outputs = model(**inputs)

masks = processor.post_process_masks(
    outputs.pred_masks.cpu(),
    inputs["original_sizes"]
)[0]
# masks.shape: [num_masks, H, W]，quality-ranked，index 0 = 最好
```

参考: PyImageSearch 2026-02-02 "Advanced SAM 3: Multi-Modal Prompting and Interactive Segmentation"

### 3.4 现有 BBox Prompt API (已实现)

```python
# sam3_detector.py line 222-291
def segment(self, image, boxes):
    inputs = self.processor(
        images=pil_image,
        input_boxes=[boxes],
        return_tensors="pt"
    ).to(self.device)
    outputs = self.model(**inputs)
    pred_masks = self.processor.post_process_masks(...)
```

---

## 4. 方案对比

| 方案 | 实现方式 | 优点 | 缺点 | 风险 |
|------|---------|------|------|------|
| **A: 点→小BBox** | 点击点扩展为 40x40 px bbox，复用 `segment(boxes)` | 零额外依赖，复用现有 Sam3Model | bbox 大小启发式 | **推荐** |
| **B: Sam3TrackerModel 真点提示** | 加载 `Sam3TrackerModel`，使用 `input_points` | 原生点提示，精度最高 | 需下载额外模型，需切换模型类 | 备选 |
| **C: cv2.selectROI** | 用户手动拉框 | OpenCV 内置 | 交互复杂，不适合切割中间使用 | 不推荐 |

**推荐方案 A**，因为：
1. 无需下载/切换模型
2. `segment(image, boxes)` 已存在
3. 40px box 可通过参数调节
4. 如果效果不佳可升级到方案 B

---

## 5. 实现方案 A 架构

### 5.1 并发设计 (方案A - 推理锁)

SAM3 模型在 GPU 上推理不是线程安全的，auto-detect timer 和点提示 callback 可能同时触发推理。

```
auto_detect timer (5Hz)              点提示 callback
      │                                     │
      ├─ try acquire lock (非阻塞)          ├─ acquire lock (阻塞)
      │  └─ 抢不到 → skip 本周期           │  └─ 抢到 → 立刻跑推理
      │                                     │     → publish result
      │                                     │  └─ release lock
      └─ 下一周期重试
```

```python
# sam3_detector_node.py
self._inference_lock = threading.Lock()

# 点提示: 阻塞等锁，保证执行
def point_prompt_callback(self, msg):
    with self._inference_lock:  # 阻塞
        image = self._get_latest_image()
        bbox = self._point_to_bbox(msg.point.x, msg.point.y)
        masks = self.detector.segment(image, [bbox])
        self._publish_result(masks)

# Auto-detect: 非阻塞，抢不到锁就跳过
def auto_detect_callback(self):
    if not self._inference_lock.acquire(blocking=False):
        return  # 点提示正在跑，跳过本周期
    try:
        image = self._get_latest_image()
        masks = self.detector.segment_with_text(image, self.text_prompt, ...)
        self._publish_result(masks)
    finally:
        self._inference_lock.release()
```

**行为总结**：
| 场景 | 结果 |
|------|------|
| 点提示触发，auto 未在跑 | 点提示立刻执行 |
| 点提示触发，auto 正在跑 | 点提示等锁 (最多 500ms SAM3 单次推理) |
| auto timer 到，点提示在跑 | auto skip 本周期，下周期重试 |
| 用户连续快速点击 | 第二次等第一次完成 |

**Auto-detect 策略**：点提示成功后不永久停 auto。auto 继续用文本提示跑。如果文本又失败，用户再点。

### 5.2 数据流

```
鼠标点击 (OpenCV window)
  → camera_viewer_node: cv2.setMouseCallback
  → 发布 /sam3/point_prompt (geometry_msgs/PointStamped, pixel x,y)
  → sam3_detector_node: 推理锁保护
  → 点 → bbox 扩展: [x-20, y-20, x+20, y+20]
  → detector.segment(image, [bbox])
  → 发布 /detected_objects + /sam3/segmentation_result
  → pose_estimator_node → tofu_state_node → /tofu_state
```

### 5.3 改动文件

#### `dexbot_toolbox/dexbot_toolbox/visualization/camera_viewer_node.py`

新增:
- `cv2.setMouseCallback(window_name, self._on_mouse_click, window_name)`
- `self._click_point` 存储点击坐标 (threading.Lock)
- 发布 `/sam3/point_prompt` (PointStamped)
- `_on_mouse_click`: 左键点击时画绿色十字 (50px) + 坐标文字

#### `dexbot_middle_layer/dexbot_middle_layer/sam3_detector_node.py`

新增:
- `self._inference_lock = threading.Lock()` (在 `__init__` 中)
- 参数 `point_prompt_box_size` (默认 40)
- 订阅 `/sam3/point_prompt` (PointStamped)
- `_point_to_bbox(x, y)`: 点 → bbox 扩展
- `_run_point_detection(x, y)`: 点提示推理路径
- `_publish_result(masks, label="point")`: 统一发布结果

### 5.4 ROS Topic 定义

新 Topic: `/sam3/point_prompt`
- 类型: `geometry_msgs/PointStamped`
- 字段: `point.x` = 像素 x, `point.y` = 像素 y
- frame_id: `camera_color_optical_frame`

### 5.5 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `point_prompt_box_size` | 40 | 点击点扩展的 bbox 尺寸 (像素) |

---

## 6. 已知限制与风险

1. **BBox 大小**: 40px 对不同距离的豆腐可能不适用，需通过参数 `point_prompt_box_size` 调优
2. **多实例**: 点提示可能返回多个分割实例，需 `only_max_mask=True` 取最大
3. **线程安全**: 推理锁 (`_inference_lock`) 已解决 auto-detect 与点提示的并发问题
4. **窗口焦点**: `cv2.imshow` 窗口必须在前台才能接收鼠标事件
5. **图像分辨率**: 点击坐标是显示缩放后的像素坐标，需映射回原图坐标再送入 SAM3

---

## 7. 参考资料

1. PyImageSearch: "Advanced SAM 3: Multi-Modal Prompting and Interactive Segmentation" (2026-02-02)
   - Section: "Interactive Segmentation Using Point-Based Refinement (Click to Guide the Model)"
   - 详细代码示例展示 `Sam3TrackerModel` + `Sam3TrackerProcessor` 点提示用法
2. HuggingFace: https://huggingface.co/docs/transformers/main/en/model_doc/sam3
3. GitHub: https://github.com/facebookresearch/sam3
4. SAM3 AI: https://sam3.ai (Visual Prompts 文档)

---

## 8. 实现计划 (用户画框方案 — 最终)

### 8.0 方案对比 (已废弃旧方案)

| | 旧方案 (点→小BBox) | 新方案 (用户画框) |
|---|---|---|
| 用户操作 | 单击一个点 | **拖拽画框** |
| 框大小 | 固定 40px | **用户自定义** |
| 推理入口 | 两个 callback (timer + 点提示) | **单一 callback** |
| 并发 | 需要推理锁 | **不需要锁** |
| 模式切换 | 点提示抢占式 | **框存在=BOX, 框删除=TEXT** |

### 8.1 核心架构

```
camera_viewer_node                    sam3_detector_node
      │                                       │
      ├─ 左键拖拽画框                           │
      ├─ 坐标映射 display→orig                  │
      ├─ 发布 /sam3/user_box ────────────────►├─ 存 self._user_box
      │                                       │
      │                                       ├─ auto_detect_callback (唯一):
      │                                       │     if user_box:
      │                                       │       segment(image, [bbox])
      │                                       │     else:
      │                                       │       segment_with_text("tofu")
      │                                       │
      │  ◄── /sam3/segmentation_result ────────┤
      │  ◄── /objects_with_pose ───────────────┤
      │                                       │
      ├─ 黄色矩形框 (BOX MODE 指示)             │
      ├─ 绿色 SAM3 结果 (不变)                  │
      │                                       │
      ├─ 右键 → 删框                           │
      └─ 发布 /sam3/user_box (w=0,h=0) ──────►├─ user_box=None → 回退 TEXT MODE
```

### 8.2 交互定义

| 操作 | viewer 行为 | 发布 |
|------|-----------|------|
| **左键按下** | 记录起点 p1，开始拖拽 | 无 |
| **鼠标移动** | 画黄色虚线橡皮筋 (p1→当前) | 无 |
| **左键释放** | 框定稿 → 黄色实线矩形，进入 BOX MODE | `/sam3/user_box` |
| **右键按下** | 删除框，回退 TEXT MODE | `/sam3/user_box` (w=0, h=0) |
| **新拖拽** | 覆盖旧框 | 同上 |
| **BOX 检测失败** | 框保持，下周期重试 | 日志 warn，不删框 |

### 8.3 文件改动汇总

| 文件 | 改动量 | 改动内容 |
|------|--------|----------|
| `camera_viewer_node.py` | ~70行新增 | 鼠标拖拽状态机 + 橡皮筋绘制 + 发布 `/sam3/user_box` |
| `sam3_detector_node.py` | ~25行新增 | 订阅 `/sam3/user_box` + auto_detect 分流逻辑 |
| `sam3_detector.py` | **0改动** | 复用现有 `segment()` |

---

### 8.4 camera_viewer_node.py 改动

#### 8.4.1 `__init__` 新增 (约10行)

```python
from sensor_msgs.msg import RegionOfInterest

# 用户框状态
self._user_box = None           # (x, y, w, h) in orig coords, None=无框
self._box_start = None           # (x, y) display coords of mousedown
self._drawing = False           # 是否正在拖拽
self._box_pub = self.create_publisher(
    RegionOfInterest, '/sam3/user_box', 10)
```

#### 8.4.2 `_display_callback` 改动 (2处)

**位置1: 存 display 尺寸 (resize 前)**
```python
with self._lock:
    self._display_orig_w = display.shape[1]
    self._display_orig_h = display.shape[0]
```

**位置2: imshow 前 (注册回调 + 画框)**
```python
if not self._cb_registered:
    cv2.setMouseCallback(self.window_name, self._on_mouse)
    self._cb_registered = True

# 画用户框 (黄色)
display = self._draw_user_box(display)
```

#### 8.4.3 新增 `_on_mouse` (约30行)

```python
def _on_mouse(self, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        self._drawing = True
        self._box_start = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE and self._drawing:
        pass  # 橡皮筋在 _draw_user_box 里画

    elif event == cv2.EVENT_LBUTTONUP and self._drawing:
        self._drawing = False
        x1, y1 = self._box_start
        x2, y2 = x, y
        # 转换为 orig 坐标
        scale = self._display_orig_w / self.window_width
        ox1 = int(min(x1, x2) * scale)
        oy1 = int(min(y1, y2) * scale)
        ow = int(abs(x2 - x1) * scale)
        oh = int(abs(y2 - y1) * scale)
        if ow < 5 or oh < 5:
            return  # 太小，忽略
        self._user_box = (ox1, oy1, ow, oh)
        self._publish_user_box()

    elif event == cv2.EVENT_RBUTTONDOWN:
        self._user_box = None
        self._publish_user_box()

def _publish_user_box(self):
    msg = RegionOfInterest()
    if self._user_box is not None:
        x, y, w, h = self._user_box
        msg.x_offset = x
        msg.y_offset = y
        msg.width = w
        msg.height = h
    else:
        msg.width = 0
        msg.height = 0
    msg.do_rectify = False
    self._box_pub.publish(msg)
```

#### 8.4.4 新增 `_draw_user_box` (约25行)

```python
def _draw_user_box(self, img):
    if self._user_box is None and not self._drawing:
        return img
    if self._display_orig_w <= 0:
        return img

    scale = self.window_width / self._display_orig_w
    result = img.copy()
    color = (0, 255, 255)  # 黄色

    if self._drawing and self._box_start:
        # 橡皮筋：虚线矩形
        sx, sy = self._box_start
        cv2.rectangle(result, (sx, sy), (self._drag_cur if hasattr(self, '_drag_cur') else (sx, sy)),
                      color, 2, lineType=cv2.LINE_8)

    if self._user_box is not None:
        # 定稿框：实线黄色
        x, y, w, h = self._user_box
        dx = int(x * scale)
        dy = int(y * scale)
        dw = int(w * scale)
        dh = int(h * scale)
        cv2.rectangle(result, (dx, dy), (dx + dw, dy + dh), color, 2)
        cv2.putText(result, 'BOX MODE', (dx + 5, dy + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)
    return result
```

#### 8.4.5 线程安全

鼠标回调在 `cv2.waitKey` 内同步执行，与 `_display_callback` 同线程。`_user_box` 的读写均在同一线程，无需加锁。

---

### 8.5 sam3_detector_node.py 改动

#### 8.5.1 `__init__` 新增 (约8行)

```python
from sensor_msgs.msg import RegionOfInterest

self._user_box = None
self._user_box_sub = self.create_subscription(
    RegionOfInterest, '/sam3/user_box',
    self._user_box_callback, 10)

def _user_box_callback(self, msg):
    if msg.width > 0 and msg.height > 0:
        self._user_box = [msg.x_offset, msg.y_offset,
                          msg.x_offset + msg.width,
                          msg.y_offset + msg.height]
    else:
        self._user_box = None
```

#### 8.5.2 `auto_detect_callback` 改动 (单一路径, 无锁)

```python
def auto_detect_callback(self):
    with self._image_lock:
        if self.latest_image is None:
            return
        image = self.latest_image.copy()
        stamp = self.latest_image_stamp

    if self._user_box is not None:
        # BOX MODE
        try:
            masks = self.detector.segment(image, [self._user_box])
        except Exception as e:
            self.get_logger().error(f'Box segment failed: {e}')
            return
        if not masks:
            self.get_logger().warn('Box mode: no masks, retry')
            return
        self._publish_box_result(masks, image, stamp)
    else:
        # TEXT MODE (default)
        self.perform_detection(image, stamp, 'tofu')
```

#### 8.5.3 新增 `_publish_box_result` (约40行)

```python
def _publish_box_result(self, masks, image, stamp):
    import numpy as np
    objects_msg = ObjectStateArray()
    objects_msg.header.stamp = stamp if stamp else \
        self.get_clock().now().to_msg()
    objects_msg.header.frame_id = 'camera_color_optical_frame'

    mask = masks[0]
    mask_bin = (mask > 0.5).astype(np.uint8) * 255

    obj_state = ObjectState()
    obj_state.header = objects_msg.header
    obj_state.id = 0
    obj_state.class_id = 'tofu'
    obj_state.confidence = 1.0

    mask_msg = self.bridge.cv2_to_imgmsg(mask_bin, encoding='mono8')
    mask_msg.header = objects_msg.header
    obj_state.mask_image = mask_msg

    ys, xs = np.where(mask_bin > 0)
    if len(xs) > 0:
        bbox = [int(xs.min()), int(ys.min()),
                int(xs.max()), int(ys.max())]
        area = float(np.count_nonzero(mask_bin))
    else:
        bbox = self._user_box
        area = 0.0
    obj_state.geometric_features = [
        float(bbox[0]), float(bbox[1]),
        float(bbox[2] - bbox[0]),
        float(bbox[3] - bbox[1]),
        area,
    ]
    objects_msg.objects.append(obj_state)

    # 绿色可视化 (与 TEXT MODE 一致)
    if self.publish_viz:
        viz = image.copy()
        cm = np.zeros_like(viz)
        cm[mask_bin > 0] = (0, 255, 0)
        viz = cv2.addWeighted(viz, 0.7, cm, 0.3, 0)
        cv2.rectangle(viz, (bbox[0], bbox[1]),
                      (bbox[2], bbox[3]), (0, 255, 0), 2)
        cv2.putText(viz, 'tofu: box',
                    (bbox[0], bbox[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        viz_msg = self.bridge.cv2_to_imgmsg(viz, encoding='bgr8')
        viz_msg.header = objects_msg.header
        self.viz_pub.publish(viz_msg)

    self.objects_pub.publish(objects_msg)
```

---

### 8.6 ROS Topic

| Topic | 类型 | 说明 |
|-------|------|------|
| `/sam3/user_box` (新) | `sensor_msgs/RegionOfInterest` | x_offset, y_offset, width, height (orig 像素)；w=h=0 清除 |

---

### 8.7 可视化规则

| 元素 | 颜色 | 说明 |
|------|------|------|
| 用户定稿框 | `(0, 255, 255)` 黄色 | BOX MODE 指示 |
| 橡皮筋拖拽 | `(0, 255, 255)` 黄色虚线 | 临时 |
| SAM3 检测 mask | `(0, 255, 0)` 绿色 | 不变，与 TEXT MODE 一致 |
| SAM3 检测 bbox | `(0, 255, 0)` 绿色 | 不变 |
| FPS/模式文字 | `TEXT` / `BOX` | 左上角 |

---

### 8.8 边界处理

| 场景 | 处理 |
|------|------|
| 框超出图像 | clip 到 `[0, w] × [0, h]` |
| 拖拽太小 (< 5px) | 忽略，不进入 BOX MODE |
| 框尺寸 w=0/h=0 | viewer 不发布，sam3 收到后清空 user_box |
| 窗口 resize 时拖拽 | 坐标基于当前 display，最后统一映射到 orig |
| SAM3 segment 崩溃 | try/except，warn + 保持框，下周期重试 |
| 无图像时画框 | cb 跳过，不发布 |

---

### 8.9 相对于旧方案的删除内容

- `_inference_lock` → **删除**（不需要）
- `point_prompt_box_size` 参数 → **删除**（不需要）
- 点→BBox 扩展逻辑 → **删除**（用户直接画框）
- 点击十字标记 (`_draw_click_markers`) → **删除**（替换为橡皮筋）
- `/sam3/point_prompt` topic → **删除**（改用 `/sam3/user_box`）

---

## 9. 关键文件索引

| 文件 | 行数 | 用途 |
|------|------|------|
| `dexbot_toolbox/.../camera_viewer_node.py` | 398 | OpenCV 摄像头窗口，无鼠标 |
| `dexbot_middle_layer/.../sam3_detector_node.py` | 318 | SAM3 ROS2 封装，auto-detect timer |
| `dexbot_middle_layer/.../sam3_detector.py` | 343 | SAM3 模型封装，`segment()` 已支持 bbox |
| `dexbot_middle_layer/.../vision_utils.py` | 369 | `get_pose_from_mask()` PCA 6D pose |
| `cuttofo_xcore/.../tofu_state_node.py` | 321 | 豆腐状态节点 |
| `.project-log/business-logic/decision-records.md` | - | 决策记录 |
| `.project-log/sam3-point-prompt-research.md` | - | 本文件 |
