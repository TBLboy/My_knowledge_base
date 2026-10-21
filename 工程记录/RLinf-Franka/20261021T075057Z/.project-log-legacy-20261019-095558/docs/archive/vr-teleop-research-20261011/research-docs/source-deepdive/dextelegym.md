# 源码深挖 · `zhourui9813/DexTeleGym`

> **证据级**：**L2（源码可证）**，来源为独立只读子 Agent 报告 **+ 主 Agent 抽查**（§6，含体积构成的实测复核）。
> **规模**：812 文件 / **817 MB**。**体积构成已实测**：`issac_gym_python` 436.4 + `.git` 189 + `assets` 134.3 + `repo_assets` 57 + `teleop` 0.1 ≈ 816.8 MB。
> **前情**：报告记为「仅仿真（非真机）」——**本轮确认该判断成立，但发现了更严重的问题。**

---

## 1. 一句话

**它不是「无许可证」那么简单，而是「无授权 + 内嵌禁止再分发的 NVIDIA 专有 Isaac Gym + 派生自 Apache-2.0 上游却抹掉声明」——代码不可采用；正当来源是上游 `OpenTeleVision/TeleVision`（Apache-2.0）。**

---

## 2. ⚠️ 许可证：三重问题（**比"无许可证文件"严重得多**）

### 2.1 本仓库本体：**既无许可证文件，也无授权**（主 Agent 实测确认）

| 检查项 | 结果 |
| --- | --- |
| 根 `LICENSE` / `LICENSE.txt` / `LICENSE.md` / `COPYING` / `NOTICE` | **全部不存在** ✅实测 |
| 根 `pyproject.toml` / `setup.py` | **不存在** ✅实测 |
| README 授权段落 | **无**（全文 313 行，止于致谢） |
| 源文件版权头 | 项目自身代码**无任何**版权/许可声明 |
| GitHub 元数据 | `license: null` |

→ **默认适用「保留一切权利」。不是开源项目。**

### 2.2 内嵌 **NVIDIA 专有 Isaac Gym**（**禁止再分发**）

```
issac_gym_python/LICENSE.txt:1-3
    Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
    NVIDIA CORPORATION and its licensors retain all intellectual property
    and proprietary rights in and to this software, related documentation
```
- `issac_gym_python/setup.py:37` `license='Copyright (c) 2020-2022, NVIDIA CORPORATION. All rights reserved.'`
- Isaac Gym Preview 需注册下载且**禁止再分发** → **本仓库把它打包进公开 repo，本身即构成许可违规**
- → **我方绝不能沿用该目录**，必须自行向 NVIDIA 获取

### 2.3 上游许可被抹除

- `README.md:313` 自述基于 **OpenTeleVision/TeleVision**
- 上游 `LICENSE` = **Apache-2.0**（含署名要求与衍生清单）
- 本仓库**未保留任何 Apache 声明** → **衍生代码的许可合规性存疑**

### 2.4 资产来源不明

`franka_description`（Franka 官方，上游 Apache-2.0）、`inspire_hand`（未声明）、混入的 **Unitree H1 人形部件**（`left_hip_*` / `left_ankle_*` / `torso_link` / `pelvis`）——均**无许可文件或署名**。

---

## 3. ★ 确认：**仅仿真**

| 证据 | 内容 |
| --- | --- |
| `simulation.py:7-9` | `from isaacgym import gymapi/gymutil/gymtorch` |
| `simulation.py:97, 120, 375` | `gymapi.acquire_gym()` / `create_sim(..., gymapi.SIM_PHYSX, ...)` / `self.gym.simulate(...)` |
| 全仓 `grep realsense\|rospy\|dynamixel\|libfranka\|UR5\|ur10\|Piper\|Shadow\|Allegro\|LEAP` | **项目自身代码零命中** |

**疑似真机代码均为死代码/未接线**：
- `teleop/webrtc/webcam.py:11, 66-70` `from pyzed import sl` 打开真实 ZED —— **但全仓无任何文件 import `webcam`**
- `TeleVision.py:8` 只 import `teleop.webrtc.zed_server`，而 `zed_server.py:26-56` 取的是**共享内存里的仿真帧队列**，**不是**真实 ZED
- `requirements.txt:6` `dynamixel_sdk==3.7.31`（真实舵机 SDK）**全仓零 import** → 遗留意图，非真机路径

> **判定**：既有审计「仅仿真（非真机）」**正确**（L2 确认）。

---

## 4. ★ 数据记录：**连仿真数采闭环也不完整**

- 录制实现：`teleop_run.py:71-104` `cv2.VideoWriter(..., 'mp4v', 30.0, (1280,720))` → **6 路 MP4**：`left/right_rgb.mp4`、`left/right_depth.mp4`、`left/right_segment.mp4`
- 目录：`output/<YYYYmmdd_HHMMSS>/episodeN/{RGB,Depth,Segment}/`

**⚠️ 关键数据质量事实**：

| # | 问题 | 证据 |
| --- | --- | --- |
| 1 | **深度是有损彩化图** —— 先 `get_camera_image(IMAGE_DEPTH)` 再 `depth_img_to_color`（`COLORMAP_JET` + uint8 归一化），**原始公制深度被丢弃** | `simulation.py:399-402, 292-302` |
| 2 | **分割是有损彩化图** —— 原始 seg ID 被丢弃 | `simulation.py:404-407`；`teleop_run.py:114-130, 214-215` |
| 3 | **无任何动作/状态/关节角/时间戳落盘** —— `grep h5py\|zarr\|wandb\|tensorboard\|\.h5` 项目代码**零命中**（尽管 `requirements.txt:8, 27, 32, 33` 列了这些依赖） | — |
| 4 | **帧率不可信** —— `VideoWriter` 声明 30 FPS，但主循环 `while True` 无固定步频/无节流 → 实际帧率随仿真性能浮动 | `teleop_run.py:201`；`simulation.py:411` |
| 5 | 相机同步 | 左右相机在同一仿真步内渲染 → **仿真内天然同步**，但**无显式时间戳**，且深度/分割均为可视化后产物 |

> → **不构成可训练的 (observation, action) 数据集**，与「面向模型训练的数采闭环」**不匹配**。

---

## 5. XR 输入 / 机器人 / 手部重定向

### 5.1 XR：vuer WebXR，**代码层无设备分支**

- 依赖 `vuer==0.0.32rc7`（**RC 版本**，`requirements.txt:26`）
- 事件源：`TeleVision.py:23-24` `add_handler("HAND_MOVE")` / `add_handler("CAMERA_MOVE")`
- 手部：**25 点 WebXR 关键点**（`TeleVision.py:37-38` `Array('d', 75)` → `(25,3)`）
- 指尖索引：`constants_vuer.py:3` `tip_indices = [4, 9, 14, 19, 24]`
- **全仓 `grep Quest|PICO|OpenXR|Oculus` 于 Python → 零命中**
- ⚠️ 硬编码网络参数：`TeleVision.py:121` `src="https://192.168.8.102:8080/offer"`
- 文档**仅声明 Quest 3**（`README.md:7, 22, 119`）

> **对本项目硬约束**：代码层**没有把任一设备写死**（正面）；但**没有任何 PICO 适配或验证**，且依赖 WebXR 手部追踪（PICO 浏览器支持度未知）。

### 5.2 机器人：**仅 Franka Panda + Inspire Hand**

- 仿真资产：`simulation.py:176-177` `franka_inspire_hand/franka_description/robots/franka_panda_{right,left}.urdf`
- IK 资产：`teleop_run.py:135` `assets/franka_pinocchio/robots/franka_panda.urdf`
- 关节：`simulation.py:204-207` 初始化 **19 DOF**（7 臂 + 12 手）
- **无 UR / Piper / Allegro / Shadow / LEAP**

> ⚠️ **注意**：这是本轮**唯一**一个用 **Franka** 的仿真数采项目 —— 但它是**仿真**，且**无许可**。

### 5.3 手部重定向：**用 `dex-retargeting` 0.4.6**

- `vuer_teleop.py:29-35` `RetargetingConfig.set_default_urdf_dir(...)` → `from_dict(cfg['left'|'right'])` → `.build()`
- **输入输出**：`vuer_teleop.py:49-50` `retarget(left_hand_mat[tip_indices])[[0..11]]` → **输入 = 5 指尖位置**，**输出 = 12 手部关节角**
- 实际配置：`config/inspire_hand_0_4_6.yml`（`type: vector`、`scaling_factor: 1.15`、`low_pass_alpha: 0.2`）
- ⚠️ **疑似索引错配**：实际使用的配置 `:14` 用 `[4,8,12,16,20]`（**MediaPipe 21 点**惯例），而代码喂入的是 **WebXR 25 点**指尖 `[4,9,14,19,24]`；**未被使用**的 `inspire_hand.yml:14` 反而与代码一致 → 若 `type: vector` 仍按该字段索引，存在**越界风险**（未运行验证）

---

## 6. 主 Agent 抽查记录

| # | 断言 | 抽查结果 |
| --- | --- | --- |
| 1 | 根目录无任何 LICENSE/COPYING/NOTICE | ✅ 确认（7 个候选名全部缺失） |
| 2 | 内嵌 Isaac Gym 为专有 | ✅ 确认（`issac_gym_python/LICENSE.txt` 头 3 行 = NVIDIA "All rights reserved"） |
| 3 | 体积 817 MB 的构成 | ✅ **实测解开了与 GitHub 263 MB 的矛盾**：`issac_gym_python` 436.4 + `.git` 189 + `assets` 134.3 + `repo_assets` 57 ≈ 817。**GitHub 报的是 packfile，本机含 `.git` 与 LFS 资产** |
| 4 | 仅仿真 | 采信子 Agent（`grep` 全仓 + `simulation.py` 证据链） |

---

## 7. 成熟度

| 维度 | 事实 |
| --- | --- |
| 测试 | **无**（无 `tests/`、无 `pytest` 引用） |
| CI | **无**（`glob .github/**` → 无） |
| 文档 | 仅 `README.md`（较详细）；无 API 文档、无架构图、无 changelog |
| 仿真后端抽象 | **不存在**（无 `fake`/`sim`/`real` 切换；Isaac Gym 硬性内嵌） |
| 代码卫生 | 注释混用中英；`teleop_utils.py:360-377` **重复定义 `normalize`**；`vuer_teleop.py:40` 注释掉的 `pdb`；`teleop_run.py:9` 无用导入 |
| 依赖 | `isaacgym`（**专有预览版**，`python_requires='>=3.6,<3.9'`）、`dex_retargeting==0.4.6`（上游 MIT）、`pin==3.3.1`/`pin-pink==3.1.0`（MIT）、`vuer==0.0.32rc7`、`torch==2.4.1`；`dynamixel_sdk`/`h5py`/`zarr`/`wandb`/`tensorboard` **均未被代码使用** |

---

## 8. 复用强度判定

### 整体：**不可采用**（`not-usable`，强于 `reference-only`）

扣分项：**无授权**（法律阻断）+ **内嵌禁止再分发的专有 Isaac Gym**（法律阻断）+ **仿真-only 且无数采闭环**（与目标不匹配）+ 无测试/无 CI + 依赖 RC 版本。

### 分子模块

| 子模块 | 判定 | 理由 |
| --- | --- | --- |
| **手部重定向部分** | **范式参考**（代码不可复制） | 自有代码仅 `vuer_teleop.py:29-35, 49-50`（**约 10 行**）+ 2 个 yml + Inspire URDF。**真正可复用的是外部 `dexsuite/dex-retargeting`（MIT）**。可借鉴：① 5 指尖 → 关节角的 vector 接线；② `low_pass_alpha` 低通滤波；③ 给 URDF 追加 `*_tip` link 作为 task link |
| **仿真环境部分** | **基本不可复用** | 深度绑定 Isaac Gym（`simulation.py` 全篇 `gymapi.*`）。唯一可提炼的通用件是 `simulation.py:34-81` 的 `pink_solve_ik`（**Pink/Pinocchio QP IK，约 50 行**）—— 但底层 Pink 本身即开源 |
| XR / 流传输 | 弱参考 | `TeleVision.py` + `webrtc/zed_server.py` 展示「共享内存双色图 → vuer ImageBackground / WebRTC H.264」低延迟回传模式；但**上游 OpenTeleVision（Apache-2.0）才是正当来源** |

---

## 9. 对本项目的直接输入

1. **建议将 `DexTeleGym` 从「候选采用名单」降级为「仅作范式参考」**，并**移除其作为可复用代码/资产来源的资格**。
2. **建议把该调研条目的「真身」改为上游 `OpenTeleVision/TeleVision`（Apache-2.0）**，并显式标注 `DexTeleGym` 是其**未合规的衍生 fork**。
   > ⚠️ **注意**：上游 `TeleVision` **也已被本轮判定为 `reference-only`**（见 [`isaac_ros_teleop-television.md`](isaac_ros_teleop-television.md)）→ **这条线整体不进入候选采用名单。**
3. **报告既有结论「仅仿真（非真机）」保留**，并补充「**并无数采闭环 / 无授权**」两条限定。
4. **若引用过其代码或 mesh，需移除**并改为引用上游（保留 Apache-2.0 署名要求）；Isaac Gym 相关内容只保留「需自行注册获取」的说明。
5. **可借鉴的只有 3 个模式**：`dex-retargeting` 的 vector 接线、`low_pass_alpha` 滤波、URDF 追加 `tip` link。

---

## 10. 未验证项

| # | 未验证项 | 原因 |
| --- | --- | --- |
| 1 | PICO 浏览器对 vuer/WebXR 手部追踪的支持与精度 | 无 L3/L4 |
| 2 | `retarget()` 在 0.4.6 下是否真会索引越界 | 未运行 |
| 3 | 上游 `OpenTeleVision` 的完整审计 | 本轮未单独做（子 Agent 只核了 LICENSE） |
| 4 | 提交日期 / 星数 / 文件数 | 子 Agent 无 shell；主 Agent 未逐项核 |
| 5 | `repo_assets` 57 MB 的具体内容（LFS demo 文件？） | 未展开 |
