# Session: camera-capability-parity (balanced)

## 目标
三种相机能力对齐（曝光/增益/白平衡）+ SDK 资源可离线部署 + ZED 驱动。

## 已完成（全部已推送 `feat/franka`，HEAD `909db74`）
- 契约（Exposure/Gain/WhiteBalance 能力对象）、业务层与设置页按能力渲染。
- UVC 驱动（V4L2 ioctl）真机验证；Orbbec/RealSense 能力实现（假对象测试）。
- `camera/<type>/vendor/manifest.json` + udev 规则 + `tools/deploy/camera_deps.py`（离线优先、不提权）+ install.sh 接入。
- 依赖安装路径收敛：删除 `uv.lock`/`pyproject.toml`，`requirements.txt` 单一源，install.sh 优先 uv。
- ZED SDK 5.5.1 安装（只需 `cuda-cudart-12-9` + `--skip_cuda`）、pyzed 由公开源码 v5.4.0 编译、三台相机探测。
- `camera/zed/driver.py` + 13 个驱动测试 + 契约测试；真机经 `MultiCameraManager` 验证（三路 host 时钟、三控件读写、写控件期间不断流）。
- 本机 339 passed / 46 subtests。

## 待决 / 下一步
1. **是否把工位 `config/config.yaml` 的 `backend` 从 `uvc` 切到 `zed`**（需用户确认；切换要把三路绑定从 V4L2 路径改成 ZED 序列号：left/center/right = 13482374 / 39897211 / 12989796，注意站点实际左中右对应关系需在页面上核对画面）。
2. 站台 udev：`99-slabs.rules` 已由 SDK 安装器写入；orbbec/realsense 规则未装（本机无这两家相机）。
3. 可选清理：`/var/cache/apt/archives` 里 733MB 半途 CUDA deb、`/tmp/zed-installer`（2.6GB）。
4. 可选：把 pyzed wheel（9.4MB，`~/zed-python-api/src/dist/`）放进 `tools/deploy/downloads/` 作为离线缓存，下次装不必编译。

## 约束（不要违反）
- 不动工位 `config/config.yaml` 与 `config/robots/franka.yaml`（现场值/复位姿态）；不驱动机械臂。
- 相机业务层禁止型号字面量与 `if backend ==`（有测试守着）；ZED 不进 `_DETECT_ORDER`。
- 系统级文件由操作者 sudo 执行；脚本只打印命令。
- 测试命令在 `Dagger_web` 下：`env -u PYTHONPATH ../../.venv/bin/python -m pytest -q -c tools/tests/pytest.ini tools/tests`。
- 工控机 `embody` 已加入 `zed` 组；新登录会话才生效（当前验证用 `sg zed -c`）。
