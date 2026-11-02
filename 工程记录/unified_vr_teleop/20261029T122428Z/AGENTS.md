<!-- VIBE-PROJECT-GENERAL:BEGIN -->
<!-- 通用开发规则（由 a-project-init 维护，勿手动删除；修改规则请改本模板后重新初始化） -->
1. 动手前先读取相关代码、配置、测试和 `.vibe/progress.md`（若存在），再判断和修改。
2. 遵循项目现有代码架构与约定，不引入与现有风格冲突的并行结构。
3. 新增功能优先不修改公共资源；若必须修改公共资源，先向用户说明并取得许可。
4. 最小改动，不做与当前任务无关的重构。
5. 修改前检查 Git 状态，保留用户与其他任务已有的未提交改动，不回滚无关文件。
6. 没有验证证据不声称完成；明确区分已实现、已验证、环境阻塞与未验证。
7. 若当前仓库为团队协作仓库，新增与主业务流程无关的文件（如测试文件、个人功能性脚本、文档等）时，先询问用户是否将这些文件加入 `.git/info/exclude` 不纳入跟踪，避免污染公共仓库提交。
8. 在项目过程中发现 Vibe Coding 框架自身的缺陷、bug 或文档漂移时，及时向用户报告，并记录到本项目 `.vibe/progress.md` 的「已知限制」（现象、复现步骤、期望与实际、涉及文件），供后续集中修复框架；不要因为"不属于本项目范围"而略过。
9. 一个项目只能存在一个 `.vibe/` 工程日志与项目记忆文件夹，统一位于项目根目录；即使项目包含多个子仓库或 worktree，所有子目录也必须共用根目录的 `.vibe/`，不得在子目录、子仓库或 worktree 中另建 `.vibe/`。切换工作目录不改变项目记忆根目录；所有 Task、进度与 Session 恢复文件均写入该唯一目录。

### 八荣八耻

1. 以暗猜接口为耻，以认真查阅为荣
2. 以模糊执行为耻，以寻求确认为荣
3. 以盲想业务为耻，以人类确认为荣
4. 以创造接口为耻，以复用现有为荣
5. 以跳过验证为耻，以主动测试为荣
6. 以破坏架构为耻，以遵循规范为荣
7. 以假装理解为耻，以诚实无知为荣
8. 以盲目修改为耻，以谨慎重构为荣
<!-- VIBE-PROJECT-GENERAL:END -->

## 项目级规则

仓库类型：根目录为多仓库工作区（非 Git 仓库）；`unified_vr_teleop/` 与 `unified_vr_teleop_franka/` 为同一团队协作仓库（华为云 CodeHub `embody/robopipe/unified_vr_teleop`）的两个检出，`robot_capture_franka/` 为个人仓库（GitHub `TBLboy/robot_capture_franka`）。团队仓库内按通用规则第 7 条处理非业务文件。

- 不在根目录执行 `git init`；提交、分支、推送只在对应子目录仓库内进行，不跨仓库混合改动。
- `robot_capture_franka/AGENTS.md` 为该子项目的更高优先级规则（只改控制链路以适配 Pico 遥操作 Franka，不改数据采集/上传链路）；根目录不重复、不覆盖它。
- `unified_vr_teleop*/`：DAgger 项目。`Dagger_web/` 是 Linux 工控机上位机；`PICO_XR_Link_PowerSave/` 是 PICO 头显省电版 Unity 应用（Unity 6000.3.24f1，包名 `com.modelbest.xrlink.powersave`，版本 0.1.0）。Quest3 应用不在此目录。
- `robot_capture_franka/`：NiceGUI 采集台（Robot Capture v3），Franka 驱动与 Pico 发布器内置。Franka 控制 worker 默认禁用；联调先走无控制相机检查（`docs/franka-no-control-start.md`），再按 `docs/franka-staged-startup.md` 分阶段启用。
- `robot_capture_franka/` 运行约束：不要同时运行 systemd 服务 `robot-capture` 与前台实例；调试前 `sudo systemctl stop robot-capture`。环境检查 `bash scripts/run.sh doctor`，真机冒烟 `bash scripts/run.sh smoke`（需三路相机）。
- 任何会让机械臂真实运动的操作，先向用户说明并获得确认。
