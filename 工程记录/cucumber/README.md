# cucumber

切黄瓜/切豆腐机器人 ROS2 工程记录。这里保留去重后的唯一日志版本，覆盖视觉、抓刀、机械臂控制、阶段流程和 GUI 等模块。

## 整理统计

- 原始日志副本：183 个
- 去重后唯一日志：34 个
- 删除完全重复副本：149 个

## 日志目录

以下日志目录均为同一级别；目录内部保留 `.project-log` 原有文件和结构：

- `001__dexbot_ros2_ws__src__cuttofo_xcore` ← `cucumber/dexbot_ros2_ws/src/cuttofo_xcore/.project-log`；重复来源 6 个；SHA256 `64d4054a500917fa`
- `002__dexbot_ros2_ws__src__dexbot_bottom_layer` ← `cucumber/dexbot_ros2_ws/src/dexbot_bottom_layer/.project-log`；重复来源 3 个；SHA256 `09bf036a8729f037`
- `003__dexbot_ros2_ws__src__dexbot_middle_layer__CutTofo` ← `cucumber/dexbot_ros2_ws/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `c437b544226cfecb`
- `004__dexbot_ros2_ws__src__dexbot_middle_layer__CutTofo__toolbox__cuttofo_calibration` ← `cucumber/dexbot_ros2_ws/src/dexbot_middle_layer/CutTofo/toolbox/cuttofo_calibration/.project-log`；重复来源 39 个；SHA256 `cd7b9f1775a8768d`
- `005__dexbot_ros2_ws__src__gui` ← `cucumber/dexbot_ros2_ws/src/gui/.project-log`；重复来源 3 个；SHA256 `dc64884d4ca627a2`
- `006__dexbot_ros2_ws__src__gui_backup__gui` ← `cucumber/dexbot_ros2_ws/src/gui_backup/gui/.project-log`；重复来源 64 个；SHA256 `15d453c71f64312b`
- `007__dexbot_ros2_ws__src__gui_backup__gui2` ← `cucumber/dexbot_ros2_ws/src/gui_backup/gui2/.project-log`；重复来源 64 个；SHA256 `edf90347b1d3d1a1`
- `008__dexbot_ros2_ws（另一个复件）__src__dexbot_middle_layer__CutTofo` ← `cucumber/dexbot_ros2_ws（另一个复件）/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `e756cb4e4553cd0a`
- `009__dexbot_ros2_ws（复件）__src__dexbot_middle_layer__CutTofo` ← `cucumber/dexbot_ros2_ws（复件）/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `4ff37c31bdbfa2ae`
- `010__dexbot_ros2_ws（第 3 个复件）__src__dexbot_middle_layer__CutTofo` ← `cucumber/dexbot_ros2_ws（第 3 个复件）/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `f6c1bd3d52795f3d`
- `011__备份__dexbot_ros2_ws(6号修改)__src__cuttofo_xcore` ← `cucumber/备份/dexbot_ros2_ws(6号修改)/src/cuttofo_xcore/.project-log`；重复来源 23 个；SHA256 `d2753aa330b46fb5`
- `012__备份__dexbot_ros2_ws(6号修改)__src__dexbot_middle_layer__CutTofo` ← `cucumber/备份/dexbot_ros2_ws(6号修改)/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `214ba5352c37acf7`
- `013__备份__dexbot_ros2_ws(附件16)__src__dexbot_middle_layer__CutTofo` ← `cucumber/备份/dexbot_ros2_ws(附件16)/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `3b27505e2ff4ff1b`
- `014__备份__dexbot_ros2_ws1（附件4）__src__cuttofo_xcore` ← `cucumber/备份/dexbot_ros2_ws1（附件4）/src/cuttofo_xcore/.project-log`；重复来源 4 个；SHA256 `a4a97e7a1d17b36c`
- `015__备份__dexbot_ros2_ws_525（复件）__dexbot_ros2_ws` ← `cucumber/备份/dexbot_ros2_ws_525（复件）/dexbot_ros2_ws/.project-log`；重复来源 1 个；SHA256 `48e80d5b2174acdd`
- `016__备份__dexbot_ros2_ws_525（附件-13）__dexbot_ros2_ws` ← `cucumber/备份/dexbot_ros2_ws_525（附件-13）/dexbot_ros2_ws/.project-log`；重复来源 1 个；SHA256 `fd2de7839befddc3`
- `017__备份__dexbot_ros2_ws_525（附件11-初步全流程）__dexbot_ros2_ws` ← `cucumber/备份/dexbot_ros2_ws_525（附件11-初步全流程）/dexbot_ros2_ws/.project-log`；重复来源 3 个；SHA256 `59fb7a260c04ceaa`
- `018__备份__dexbot_ros2_ws_525（附件14-saurce备份）__dexbot_ros2_ws__src__dexbot_middle_layer__CutTofo` ← `cucumber/备份/dexbot_ros2_ws_525（附件14-saurce备份）/dexbot_ros2_ws/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `efd601d3b5a10abb`
- `019__备份__dexbot_ros2_ws_525（附件14-浇汁代码）__dexbot_ros2_ws__src__cuttofo_xcore` ← `cucumber/备份/dexbot_ros2_ws_525（附件14-浇汁代码）/dexbot_ros2_ws/src/cuttofo_xcore/.project-log`；重复来源 2 个；SHA256 `992ee3a3f05e819b`
- `020__备份__dexbot_ros2_ws_525（附件14-浇汁代码）__dexbot_ros2_ws__src__dexbot_middle_layer__CutTofo` ← `cucumber/备份/dexbot_ros2_ws_525（附件14-浇汁代码）/dexbot_ros2_ws/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `ae17064e6a08d7bf`
- `021__备份__dexbot_ros2_ws_525（附件14-浇汁代码）__dexbot_ros2_ws__src__dexbot_middle_layer__CutTofo__toolbox__cuttofo_calibration` ← `cucumber/备份/dexbot_ros2_ws_525（附件14-浇汁代码）/dexbot_ros2_ws/src/dexbot_middle_layer/CutTofo/toolbox/cuttofo_calibration/.project-log`；重复来源 2 个；SHA256 `0e6fb07b46ce7673`
- `022__备份__dexbot_ros2_ws_525（附件14-浇汁代码）__dexbot_ros2_ws__src__gui_backup__gui` ← `cucumber/备份/dexbot_ros2_ws_525（附件14-浇汁代码）/dexbot_ros2_ws/src/gui_backup/gui/.project-log`；重复来源 2 个；SHA256 `33e02fa00ecd6bf8`
- `023__备份__dexbot_ros2_ws_525（附件14-浇汁代码）__dexbot_ros2_ws__src__gui_backup__gui2` ← `cucumber/备份/dexbot_ros2_ws_525（附件14-浇汁代码）/dexbot_ros2_ws/src/gui_backup/gui2/.project-log`；重复来源 2 个；SHA256 `eb51e88f94364413`
- `024__备份__dexbot_ros2_ws_525（附件2）__dexbot_ros2_ws` ← `cucumber/备份/dexbot_ros2_ws_525（附件2）/dexbot_ros2_ws/.project-log`；重复来源 3 个；SHA256 `8146b82a40e18bd8`
- `025__备份__dexbot_ros2_ws_525（附件7-框架优化）__dexbot_ros2_ws` ← `cucumber/备份/dexbot_ros2_ws_525（附件7-框架优化）/dexbot_ros2_ws/.project-log`；重复来源 1 个；SHA256 `6606e84d8653f113`
- `026__备份__dexbot_ros2_ws_525（附件8-开始解决豆腐问题）__dexbot_ros2_ws` ← `cucumber/备份/dexbot_ros2_ws_525（附件8-开始解决豆腐问题）/dexbot_ros2_ws/.project-log`；重复来源 2 个；SHA256 `175254c7d44b882e`
- `027__备份__dexbot_ros2_ws_525（黄瓜全流程）__dexbot_ros2_ws` ← `cucumber/备份/dexbot_ros2_ws_525（黄瓜全流程）/dexbot_ros2_ws/.project-log`；重复来源 2 个；SHA256 `687fcf22d46ed689`
- `028__备份__dexbot_ros2_ws_525（黄瓜全流程）__dexbot_ros2_ws__src__gui` ← `cucumber/备份/dexbot_ros2_ws_525（黄瓜全流程）/dexbot_ros2_ws/src/gui/.project-log`；重复来源 17 个；SHA256 `53b107176085b688`
- `029__备份__dexbot_ros2_ws（6月7日上午）__src__dexbot_middle_layer__CutTofo` ← `cucumber/备份/dexbot_ros2_ws（6月7日上午）/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `8259b73400766568`
- `030__备份__dexbot_ros2_ws（6月8日-上午）__src__dexbot_middle_layer__CutTofo` ← `cucumber/备份/dexbot_ros2_ws（6月8日-上午）/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `535089b325dbe57d`
- `031__备份__dexbot_ros2_ws（六月11日中午）__src__dexbot_middle_layer__CutTofo` ← `cucumber/备份/dexbot_ros2_ws（六月11日中午）/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `28a993f5466cd9eb`
- `032__备份__dexbot_ros2_ws（附件-14）__src__dexbot_middle_layer__CutTofo` ← `cucumber/备份/dexbot_ros2_ws（附件-14）/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `e5dc0ae5a1603e3a`
- `033__备份__dexbot_ros2_ws（附件-15）__src__dexbot_middle_layer__CutTofo` ← `cucumber/备份/dexbot_ros2_ws（附件-15）/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 1 个；SHA256 `b58258ae6fec1ef1`
- `034__备份__dexbot_ros2_ws（附件16）__src__dexbot_middle_layer__CutTofo` ← `cucumber/备份/dexbot_ros2_ws（附件16）/src/dexbot_middle_layer/CutTofo/.project-log`；重复来源 2 个；SHA256 `a18e93184a534538`
