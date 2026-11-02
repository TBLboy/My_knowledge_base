# HDF5 元数据收尾工程规格

范围：元文档 + 已批准业务基线的命名、sensors、TCP、双臂外参五项差异；不做历史迁移、控制算法变更或自检平台。

- `camera/core/identity.py`：开流前读设备身份。UVC sysfs 提供型号/USB serial；ZED SDK 可选提供 path→真实 serial/model，serial=0 无效。未取得用 unknown，绝不缓存路径为序列号。一次启动的缓存归 MultiCameraManager 所有，重启相机时重读；不做进程级陈旧缓存。- `MultiCameraManager.start` 在任何驱动 start 前查询全部设备；capture_service 按 role_map 映射身份，recorder 接收可选 camera_info，不重新枚举已占用设备。
- recorder 在开录时快照标准名 sensors：model/serial/width/height/mount。分辨率取编码器实际输出配置；mount 与标准槽位对应。机器人配置 kinematics.tcp/tcp_offset 按臂快照，base_extrinsics 为机型顶层配置。
- exporter 消费快照（不读实时配置），root sensors 规范化；图像 decoded_shape 继续留在 dataset attrs。观测/动作 EEF 均写 TCP attrs；双臂 root 写 base_extrinsics，缺失 unknown；单臂省略。旧快照缺字段 unknown，不伪造。
- sessions.episode_remote_name 六位补零；已有 remote_name 不改。
- Franka 最终方案（用户决定，取代早先的 flange 换算）：记录**不做任何坐标换算**，落盘的就是机器人自身 `O_T_EE`（该机为法兰前 0.16 m 的末端点）。配置声明 `tcp=fingertip_center`、`tcp_offset=[0,0,0.16]`，与实际数据一致。生产 controller 每帧用实时 `F_T_EE` 核对配置声明：声明 `flange` 而机器人有偏移、`tcp_offset` 与实时偏移差 >1 mm、或 tcp 未声明，都拒绝反馈（即拒绝录制），不写出与数据不符的声明。驱动只为该校验携带实时 F_T_EE，不改变控制目标。
- 验证：SDK 缺失/serial=0/路径匹配与角色交换、启动时序/重启、recorder 快照、单/双臂导出与未知值、命名；全量 pytest；工控机真实 UVC 预览→快照→临时导出验证，不下发机械臂命令、不写历史文件。
