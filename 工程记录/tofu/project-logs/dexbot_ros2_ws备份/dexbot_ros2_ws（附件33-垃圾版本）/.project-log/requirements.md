# Requirements

## Project Summary

- **Goal**: 对 dexbot_ros2_ws 代码库进行系统重构，消除冗余、拆分大文件、提取共享抽象、补充测试，提升可维护性
- **Users / Operators**: 开发者（用户 tbl）
- **Current stage**: 重构规划与初始化阶段（Phase 0）

## Requirements

- 重构必须分阶段进行，不可一步到位
- 每个阶段完成后需确认代码仍可正常运行
- 不允许破坏现有的 ROS 2 节点通信、launch 文件、硬件驱动接口
- 不允许删除远程 git 历史（本地可自由清理）
- 不修改硬件/SDK/驱动层配置（不碰 xCore SDK、Lbot C API、Linker 灵巧手 SDK、RealSense 驱动）
- 重构前后的代码行为必须一致（纯重构，不修 bug、不加功能）

## Task Scope

- **In scope**:
  - 清理备份目录（`gui_backup/`）
  - 归档不再使用的遗留代码（`CutTofo/sdk/`、`dexbot_high_layer/` 中的陈旧脚本）
  - 统一配置文件散落问题
  - 提取共享抽象层（配置加载、切割轨迹规划等）
  - 拆分超过 1000 行的大文件
  - 补充关键路径的冒烟测试
  - 维护 `.project-log/` 工程记录

- **Out of scope**:
  - 修改硬件驱动或 SDK 封装层
  - 新增功能或修改业务逻辑
  - 升级 ROS 2 版本或依赖库版本
  - 重构期间修复已有 bug（除非影响重构验证）

## Constraints

- 硬件依赖无法在纯软件环境验证，需要真机或仿真测试
- 多个切豆腐实现并存（`cuttofo_xcore`、`cuttofo_lbot`、`CutTofo/`），需确认各自活跃状态后再清理
- 当前工作区 git 已重新初始化并连接到 `origin/cut_to_fo_featrue` 分支
- 现存代码约 540+ 文件、131,000+ 行 Python

## Acceptance Criteria

- Phase 1（清理）：`gui_backup/` 已删除，不再使用的 SDK 脚本已归档，配置目录已统一
- Phase 2（共享抽象）：配置加载、切割轨迹规划已有唯一实现，消除 3 份切豆腐逻辑的重复
- Phase 3（拆分大文件）：6000+ 行和 3000+ 行的单体文件已拆分到合理模块
- Phase 4（测试）：关键路径已有冒烟测试覆盖

## Decisions

- 采用 `project-log` 工程记录系统跟踪重构全过程
- 先清理、再提取共享、再拆分、最后加测试
- 已有 `.project-log/` 内容（GUI 双臂工作记录）保留不覆盖

## Open Questions

- `CutTofo/sdk/` 下的脚本是否仍在使用？需要确认后决定归档还是保留
- `dexbot_high_layer/` 的切黄瓜代码是否已完全废弃？
- `gui_backup/` 是否有未被迁移到当前 GUI 的代码？
