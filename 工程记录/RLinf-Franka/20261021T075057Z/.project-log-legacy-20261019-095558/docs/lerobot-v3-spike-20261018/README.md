# LeRobot v3 synthetic spike（2026-10-18）

## 目的

在不修改 RLinf 运行环境、不操作真机的前提下，验证候选 LeRobot v3 API、semantic feature、视频写入、episode metadata 和本地 reload。

## 环境

- 当前项目 `RLinf/.venv`：`lerobot==0.1.0`，旧 `lerobot.common.datasets` API，属于 v2.1 路径；未修改。
- 隔离环境 `/tmp/opencode/lerobot-spike-044`：`lerobot==0.4.4`，Python 3.11.14。
- `lerobot==0.6.1` 要求 Python >=3.12；已建立 Python 3.12 隔离环境并安装包本体，但完整 dataset 依赖安装在当前网络/超时条件下未完成。因此 0.6.1 目前只有静态 API 证据，未进行运行时 spike。

## 运行命令

```bash
PYTHONPATH=/tmp/opencode/lerobot-spike-044/lib/python3.11/site-packages:RLinf/.venv/lib/python3.11/site-packages \
  /tmp/opencode/lerobot-spike-044/bin/python \
  .project-log/docs/lerobot-v3-spike-20261018/run_spike.py
```

脚本只生成 3 帧合成 episode，包含：

- `observation.state.joint_position[7]`
- `observation.state.eef_pose[7]`
- `observation.state.gripper[1]`
- `action.eef_pose[7]`
- `action.gripper[1]`
- `observation.images.cam_ext_0`
- `observation.images.cam_wrist_right`
- 一个 task

视频 feature 使用 `dtype=video`，编码器使用 `vcodec=h264`，实际编码器输出为 H.264/YUV420P。

## 0.4.4 结果

成功生成并 reload：

```text
data/chunk-000/file-000.parquet
meta/episodes/chunk-000/file-000.parquet
meta/info.json
meta/stats.json
meta/tasks.parquet
videos/observation.images.cam_ext_0/chunk-000/file-000.mp4
videos/observation.images.cam_wrist_right/chunk-000/file-000.mp4
```

reload 结果：`3` frames，`codebase_version=v3.0`，`fps=30`。

episode metadata 包含：

- `dataset_from_index` / `dataset_to_index`
- 每路视频的 chunk/file/from_timestamp/to_timestamp
- `meta/episodes/chunk_index` / `file_index`

实际视频检查：

- 每路 3 帧；
- container FPS `30.0`；
- time base `1/15360`；
- duration `1536` ticks；
- codec `h264`；
- pixel format `yuv420p`；
- 两路视频均独立文件；
- `gop=2` 通过 LeRobot 0.4.4 的 encoder 默认路径传入，仍需在正式 QC 中解析实际 keyframe 间隔。

## 发现与限制

1. 0.4.4 的官方 writer 可以直接承载项目语义 feature 和 v3 文件布局，但不能把 `timestamp` 作为普通 frame extra key；它由 writer 自动生成。因此项目原始/对齐时间戳必须通过对齐 manifest 和 v3 timestamp 生成边界处理，不能假设任意 raw 字段都能直接塞入 frame。
2. `dtype=video` 是触发 MP4 写入的必要条件；`dtype=image` 会得到 parquet 图像列而不生成 `videos/`。
3. 0.4.4 的 `LeRobotDataset.finalize()` 是必要生命周期步骤；当前 RLinf 0.1.0 writer 没有同名 finalize，不能复用当前 writer 作为 v3 writer。
4. 当前合成 spike 没有覆盖项目自定义 `custom.action_space`、camera map、outcome 和 raw alignment manifest；这些仍必须由项目 wrapper/QC 写入并验证。
5. 0.6.1 的包元数据显示其 API 仍是 v3 方向，但其 Python >=3.12 且完整依赖未安装，不能把它标记为运行时兼容。

## 当前决策

保留 `RS-022` 的推荐：先采用固定版本 wrapper-adapter。下一步优先以 0.4.4 作为可运行候选，补做：

- 完整 project raw → virtual-30Hz → semantic v3 source provenance；
- outcome、episode terminal provenance 与 strict QC；
- 正式 h264/GOP/PTS/loader QC 和完整 v3 文件限制；
- 与 0.6.x 的兼容性重新验证。

当前临时决策记录为 `D-039-lerobot-044-spike-candidate`：先以 0.4.4 作为 wrapper-adapter 候选，但不是最终锁定版本；正式实现前必须记录版本 pin、依赖锁和失效条件。

## T-025 isolated writer/QC fixture

`writer_qc_fixture.py` is an isolated synthetic wrapper. It writes semantic
state/action/gripper features, the fixed/wrist camera map, v3 metadata, tasks,
episodes, stats and MP4 references, then validates them fail-closed. It records
the raw batch SHA-256 when supplied and rejects mutation. Only `success` and
`failure` are publishable; `timeout` and `abort` remain raw-only.

Run from the pinned environment (never `RLinf/.venv`):

```bash
PYTHONPATH=/tmp/opencode/lerobot-spike-044/lib/python3.11/site-packages:/tmp/opencode/lerobot-spike-044/lib/python3.11/site-packages:.project-log/docs/lerobot-v3-spike-20261018 \
  /tmp/opencode/lerobot-spike-044/bin/python .project-log/docs/lerobot-v3-spike-20261018/run_t025.py
```

The strict loader boundary is the pinned `LeRobotDataset` reload: only v3
metadata with semantic features, tasks/episodes and validated video references
is accepted. Project-labelled fields (`custom`, outcome and manifest) are
project provenance and are not interpreted by an unmodified generic loader;
call project QC before strict publication.

## T-028 future raw recorder boundary

`RLinf-Franks/rlinf_ext/future_raw_writer.py` provides an explicit, offline-capable
boundary for normalized records. `write_raw_batch()` validates measured q/TCP/
gripper state, per-step action samples, terminal outcome, monotonic timestamps,
camera media references, and completion state before atomically publishing a
read-only sealed `future-raw-v1` JSON artifact with a SHA-256 digest. Existing
artifacts cannot be overwritten; `dry_run=True` performs the same validation
without writing.

This is not live hardware integration. The remaining gap is wiring normalized
records from the live Worker and camera capture (including durable media frame
references) into this boundary under the collection lifecycle. No automatic
registration or control behavior was changed.
