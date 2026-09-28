# Windows 平台测试失败报告核查（EV-WIN-AUDIT-001）

- 任务：TASK-098 / RUN-109
- 结论：**报告 5 类根因全部成立**；其中 1 类是**真实产品代码缺陷**，4 类是**测试未做平台适配**。
- 被审计版本：框架仓 `D:\Project\vibe-coding\vibe-coding`，工作树分支 `opencode-auto-research` @ `db7ed85260652292b6b46caade1197ab735b5ee3`（4 个被审文件在该工作树中均无本地修改）。
- 跨分支一致性：`git diff opencode opencode-auto-research -- scripts tests runtime` 为空，且 4 个被审文件的 blob 在两分支完全相同
  （`scripts/opencode_installer.py`=`f7a358831bb9`、`tests/test_opencode_installer.py`=`62284617d830`、
  `tests/test_opencode_plugin.py`=`250ef16d4b2f`、`tests/test_opencode_surface.py`=`79d5ad85a385`）
  → **本结论对两个分支同时成立**。

## 1. 复现结果

环境：Windows / PowerShell 5.1；解释器 `D:\conda\envs\vibe-coding\python.exe`（3.11）；命令在框架仓根目录执行：

```powershell
$env:PYTHONUTF8='1'
& "D:\conda\envs\vibe-coding\python.exe" -m unittest discover -s tests -p "test_*.py"
```

原始输出（日志留档 `C:\Users\12187\AppData\Local\Temp\opencode\fullsuite_audit.log`）：

```
Ran 246 tests in 172.483s
FAILED (failures=8, errors=13, skipped=3)
```

与报告声明 **逐项一致**：246 tests / 8 failures / 13 errors / 3 skipped。
失败分布也一致：3 + 12 + 1 + 4 + 1 = 21。

**计数环境依赖（独立复核后补正）**：测试总数恒为 246、failures 恒为 8；但 errors/skipped 的分配取决于
`bash` 在 `PATH` 上解析到哪一个可执行文件：

| `bash` 解析结果 | 结果 | 说明 |
|---|---|---|
| WSL 存根 `C:\Users\12187\AppData\Local\Microsoft\WindowsApps\bash.exe`（本机默认） | `8 failures / 13 errors / 3 skipped` | 即报告与本审计所用环境 |
| 真实 git-bash `C:\Program Files\Git\bin\bash.exe`（`PATH` 前置该目录，其内建无 `wslpath`） | `8 failures / 12 errors / 1 skipped` | 2 个 `test_cross_platform_surface.py` 守卫由 skip→执行，class 3 由 error→pass |

（第二行由主 Agent 于本机复跑确认：`Ran 246 tests in 159.460s` / `FAILED (failures=8, errors=12, skipped=1)`。）

因此“13 errors / 3 skipped”**不是平台固有值**，而是“WSL `bash` 存根在 `PATH` 上”时的取值。

## 2. 逐类判定

### 类别 1 —— 产品代码缺陷：安装状态文件写入反斜杠相对路径 ✅ 成立（3 failures）

判定：**真实产品缺陷，位于对外契约（安装状态文件）**，非测试问题。

证据链（代码 → 实盘 → 断言）：

| 环节 | 位置 | 事实 |
|---|---|---|
| 造键处 | `scripts/opencode_installer.py:104/107/110` | `assets[str(path.relative_to(surface))] = path` 等，用 `str()` 而非 `.as_posix()` |
| 造键处 | `scripts/opencode_installer.py:125` | `runtime_assets`：`assets[str(relative)] = path` |
| 落盘处 | `scripts/opencode_installer.py:360-382` | `plan_sync` 直接以 `sources` 原始键写 `managed[key]`；`preserved.append(key)`，无归一化 |
| 落盘处 | `scripts/opencode_installer.py:842` | `"managed_files": managed` 写入状态文件 |
| 提示处 | `scripts/opencode_installer.py:857` | `[!] PRESERVED local modification: {relative}` 打印原始键 |
| 实盘 | `C:\Users\12187\.config\opencode\.vibe-opencode-installation-state.json` | `managed_files` 共 103 键，**100 键含反斜杠**（污染率 97%）。精确分解：**37 键为混合分隔符**（如 `vibe-workflow/agents\alignment-reviewer.md`）+ **63 键纯反斜杠** + 2 键纯正斜杠（`vibe-workflow/vibe.ps1`、`vibe-workflow/vibe.sh`）+ 1 键无分隔符（`vibe-python`）= 103；归一化 `\`→`/` 后 103 个逻辑路径**无重复** |

对应失败断言（`tests/test_opencode_installer.py`），行号与报告完全一致：

- `:69` `assertIn("vibe-workflow/scripts/vibe.py", state["managed_files"])`
  → `AssertionError: 'vibe-workflow/scripts/vibe.py' not found in {'agents\\alignment-reviewer.md': '...'}`
- `:184` `assertIn("skills/a-loop-control/SKILL.md", state["preserved_local"])`
  → `AssertionError: 'skills/a-loop-control/SKILL.md' not found in ['skills\\a-loop-control\\SKILL.md']`
- `:392` `assertIn("vibe-workflow/scripts/vibe.py", update.stdout)`
  → 实际输出 `[!] PRESERVED local modification: vibe-workflow/scripts\vibe.py`，断言失败

**加重情节（报告未提及，本次核查新增）**：

1. **状态文件不可跨 OS 迁移。** `safe_relative()`（`:129-139`）在 Windows 上会把 `agents\x.md` 归一化为 `agents/x.md`，所以安装器能读回自己写出的畸形键、缺陷自洽隐藏；
   但在 Linux 上 `Path('agents\\x.md').parts` 是单个字面文件名 → 同一份状态文件会被解释为含反斜杠的**字面文件名**，`destination_for` 指向错误目标。
2. **同类模块做法不一致。** Codex 侧安装器（`scripts/global_installer.py`，包摘要处）使用 `relative.as_posix()`；
   OpenCode 侧却在造键时漏掉归一化 → 属实现漂移，而非设计取舍。
3. `validate_state_shape`（`:323-330`）只校验“安全”，不校验“分隔符规范”，因此该缺陷不会被自身校验拦下。

### 类别 2 —— 测试不兼容：`os.symlink` 需特权 ✅ 成立（12 errors）

- 全量日志中 `[WinError 1314] 客户端没有所需的特权。` 出现 **12 次**；探针确认文件/目录 symlink 均失败，且策略中不存在 `AllowDevelopmentWithoutDevLicense`。
- 调用点与报告一致：`tests/test_opencode_installer.py:868,891,907,937`、`tests/test_opencode_plugin.py:93,161`、`tests/test_opencode_surface.py:297`。
  - 补充：`tests/test_opencode_surface.py:300` 亦为 `os.symlink` 调用点，报告未列出。计数仍为 12 的原因是 **`:297` 的异常先中止了该方法，`:300` 根本不会执行**（而非“两者属于同一测试”）。
- 计数吻合：installer 侧 3 个方法 + `test_symlinked_special_files_are_refused` 的 6 个 subTest = 9，加 plugin 2、surface 1 = **12**。

### 类别 3 —— 测试不兼容：`bash` 解析到 WSL 存根且未指定编码 ✅ 成立（1 error）

判定：**测试不兼容，但根因需更正**（初版审计归因为“缺 `encoding=`”，经独立复核后修正为下述主次结构）。

- 代码位置：`tests/test_opencode_installer.py:502` 的 `subprocess.run([...])` **未传 `encoding=`**（同文件 `:497` 的 `read_text` 反而显式指定了 `encoding="utf-8"`）。
- **首要触发因素**：该用例直接调用 `bash`，未做可用性探测；本机 `bash`（`Get-Command bash`）解析到 WSL AppExecutionAlias
  `C:\Users\12187\AppData\Local\Microsoft\WindowsApps\bash.exe`。WSL 内的 bash **无法接收原生 Windows 路径**，且其输出不是可直接解码的本机字节流。
  仓库其实**已有**针对性守卫——`tests/test_cross_platform_surface.py:57-64` 的 `usable_posix_bash()`
  通过 `command -v wslpath` 探测并拒绝 WSL bash（注释原文：“A bash inside WSL exposes wslpath; it cannot take a native Windows path.”）——
  但本用例未复用该守卫。故这是**本用例缺少平台自适配**，而项目其它测试已有正确范式。
- **次要因素**：缺显式 `encoding=` 使报错形式随环境文本编码漂移（见下），但**单独补 `encoding=` 不能修复该用例**：
  只会把 `UnicodeDecodeError` 换成 `returncode != 0` 断言失败。
- 报告描述逐字复现：不设 `PYTHONUTF8` 单跑该用例得
  `UnicodeDecodeError: 'gbk' codec can't decode byte 0xff in position 47: illegal multibyte sequence`
  —— 与报告的 `gbk` / `0xff` / `position 47` **完全一致**。
- 编码签名漂移（次要因素的证据）：设 `PYTHONUTF8=1` 时同一测试报
  `'utf-8' codec can't decode byte 0xc0 in position 10`。**“gbk/0xff/47”只在默认（非 UTF-8 模式）环境下成立**；
  这解释了报告值与我首次带 `PYTHONUTF8=1` 的全量跑之间的表面差异，但两次都失败，失败本身与编码设置无关。

### 类别 4 —— 测试不兼容：假包管理器 shim 无扩展名 ✅ 成立（4 failures）

- 代码位置（与报告 cited 行基本一致，bun 段实际起于 `:474`）：
  - `tests/test_opencode_installer.py:216` `fake_npm = bin_dir / "npm"`（无扩展名）、`:229` `chmod(0o700)`
  - `tests/test_opencode_installer.py:444` 同类假 npm、`:454` `chmod`
  - `tests/test_opencode_installer.py:477` `fake_bun = bin_dir / "bun"`、`:478` 写入
- 失败断言实测：
  - `AssertionError: 2 != 0 : [X] npm or bun is required to install the OpenCode plugin dependency`（1 次）
  - `AssertionError: 0 == 0`（3 次）
- 报告的次要论点亦成立：3 次 `0 == 0` 出现在**成功路径**上，即“包管理器失败后的回滚”逻辑在 Windows 上**未被真正覆盖**，属静默的覆盖缺口。

### 类别 5 —— 测试不兼容：POSIX 可执行位断言 ✅ 成立（1 failure）

- 代码位置：`tests/test_opencode_surface.py:170`（与报告逐字一致）
  `self.assertTrue(wrapper.stat().st_mode & 0o111, "bin/vibe-python must be executable")`
- 实测：`AssertionError: 0 is not true : bin/vibe-python must be executable`（Windows 上 `st_mode` 恒无权限位）。

## 3. 报告准确性评估

| 维度 | 评价 |
|---|---|
| 失败总数与分类（21 项 / 5 类） | **准确**，逐项复现 |
| 5 类根因定性 | **全部准确** |
| 行号引用 | 准确（`test_opencode_installer.py:69/184/392/502/868/891/907/937`、`test_opencode_plugin.py:93/161`、`test_opencode_surface.py:170/297` 全部命中） |
| 偏差 | ① 漏列 `test_opencode_surface.py:300` 这一 symlink 调用点（不影响计数）；② 类别 3 的归因只讲到“缺 `encoding=`”，未指出首要触发因素是 `bash` 解析到 WSL 存根，也未说明“gbk/0xff/47”依赖非 `PYTHONUTF8` 环境；③ 未说明 13 errors / 3 skipped 依赖 WSL `bash` 存根在 `PATH` 上（否则为 12 / 1） |
| 遗漏的加重情节 | 类别 1 还导致状态文件**不可跨 OS 迁移**，且与 Codex 侧安装器 `as_posix()` 做法**实现漂移** |

## 4. 未验证项与后续建议

未验证（本任务范围外）：

- 未在其他 Windows 环境（无 `PYTHONUTF8` 以外的编码配置、非中文 locale）复跑，故“13 errors 的具体构成是否稳定”未做多环境交叉验证。
- 未验证 Linux/macOS 上同一套件的表现（本机无第二个平台）。
- 未评估修复类别 1 后**既有**状态文件（现网 100 个反斜杠键）需要迁移还是可自然收敛。
- 未检查仓库 CI 是否覆盖 Windows；若 CI 仅 Linux，则本报告暴露的 Windows 退化无人拦截。

建议后续动作（按优先级）：

1. **修类别 1（唯一产品缺陷）**：在 `surface_assets`/`runtime_assets` 造键处统一 `Path(...).as_posix()`，或在 `plan_sync` 入口单点归一化 `sources` 键；
   同时给 `validate_state_shape` 增加“键必须为 POSIX 形式”的校验，并断言修复后新状态文件 0 个反斜杠键。
2. **修类别 2-5**：按报告建议引入 `tests/_platform.py`（`can_symlink()` / `make_package_manager_shim()` / `posix_only` 装饰器），
   使 Windows 上要么跳过、要么按 `.cmd` shim 正确构造，且**不得**让“失败回滚”用例在 Windows 上静默走成功路径。
   类别 3 应直接复用仓库已有的 `usable_posix_bash()`（`tests/test_cross_platform_surface.py:57-64`）来探测 `bash`，
   并补 `encoding="utf-8"`；只补 `encoding=` 不足以修复。
3. 补 Windows CI（或至少在文档中声明支持的平台矩阵），防止同类退化再次漏网。

## 5. 证据绑定

- 全量套件日志：`C:\Users\12187\AppData\Local\Temp\opencode\fullsuite_audit.log`（`Ran 246 tests` / `failures=8, errors=13, skipped=3`；WSL `bash` 存根环境）
- 实盘状态文件：`C:\Users\12187\.config\opencode\.vibe-opencode-installation-state.json`（103 键 / 100 含反斜杠 / 37 混合）
- 被审代码：`vibe-coding/scripts/opencode_installer.py`、`vibe-coding/tests/test_opencode_installer.py`、
  `vibe-coding/tests/test_opencode_plugin.py`、`vibe-coding/tests/test_opencode_surface.py`

## 6. 复核与修订记录

- 独立复核：`verification-reviewer` 子 Agent（REVIEW-WIN-AUDIT-001），判定 `conditional`。
- 主 Agent 对复核意见**逐条独立复验**（不直接采信子 Agent 结论）：
  1. 混合分隔符计数：实跑确认 **37**（37 混合 + 63 纯反斜杠 + 2 纯正斜杠 + 1 无分隔符 = 103）；初版写的“39”实为**含正斜杠**的键数 → 已更正。
  2. `tests/test_cross_platform_surface.py:57-64` 的 `usable_posix_bash()` 守卫与 WSL 注释确实存在 → 已据此重写类别 3 的根因归属。
  3. `Get-Command bash` 确认本机解析到 `C:\Users\12187\AppData\Local\Microsoft\WindowsApps\bash.exe`（WSL AppExecutionAlias）→ 已补入计数环境依赖说明。
- 修订后类别 1 的“产品缺陷”定性、类别 2/4/5 的“测试不兼容”定性**均未改变**；受影响的只是类别 3 的根因表述与三处计数/推理精度。
