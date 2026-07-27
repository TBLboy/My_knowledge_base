# tofu

Dexbot 双臂 ROS 2 工作空间，主线为结合视觉引导、灵巧手和双臂协同的切豆腐演示。这里保留去重后的唯一日志版本。

## 整理统计

- 原始日志副本：226 个
- 去重后唯一日志：35 个
- 删除完全重复副本：191 个

## 日志目录

以下日志目录均为同一级别；目录内部保留 `.project-log` 原有文件和结构：

- `001__dexbot_ros2_ws` ← `tofu/dexbot_ros2_ws/.project-log`；重复来源 4 个；SHA256 `7bf29dcca36ccf57`
- `002__dexbot_ros2_ws__src__cuttofo_calibration` ← `tofu/dexbot_ros2_ws/src/cuttofo_calibration/.project-log`；重复来源 3 个；SHA256 `a669ea88db660e1a`
- `003__dexbot_ros2_ws__src__cuttofo_lbot` ← `tofu/dexbot_ros2_ws/src/cuttofo_lbot/.project-log`；重复来源 2 个；SHA256 `5ca645ee08e1d6b0`
- `004__dexbot_ros2_ws__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws/src/cuttofo_xcore/.project-log`；重复来源 2 个；SHA256 `336c725628309e88`
- `005__dexbot_ros2_ws__src__gui` ← `tofu/dexbot_ros2_ws/src/gui/.project-log`；重复来源 12 个；SHA256 `56bc30b2c2eabd28`
- `006__dexbot_ros2_ws__src__gui_backup__gui` ← `tofu/dexbot_ros2_ws/src/gui_backup/gui/.project-log`；重复来源 2 个；SHA256 `02148a85b55f68b5`
- `007__dexbot_ros2_ws__src__gui_backup__gui2` ← `tofu/dexbot_ros2_ws/src/gui_backup/gui2/.project-log`；重复来源 2 个；SHA256 `976abbb3ceea161f`
- `008__dexbot_ros2_ws备份__dexbot_ros2_ws11（竖着切有点小问题）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws11（竖着切有点小问题）/src/cuttofo_xcore/.project-log`；重复来源 2 个；SHA256 `fa4924f9f8fb197d`
- `009__dexbot_ros2_ws备份__dexbot_ros2_ws11（竖着切有点小问题）__src__gui` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws11（竖着切有点小问题）/src/gui/.project-log`；重复来源 13 个；SHA256 `393fbc0de9c49328`
- `010__dexbot_ros2_ws备份__dexbot_ros2_ws（备份16-还没有集成抓刀逻辑，做了一下phase·跳转的优化）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（备份16-还没有集成抓刀逻辑，做了一下phase·跳转的优化）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `593760861dab846d`
- `011__dexbot_ros2_ws备份__dexbot_ros2_ws（复件12-切换右臂之后，还没调试好）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件12-切换右臂之后，还没调试好）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `1610d6538b6e342e`
- `012__dexbot_ros2_ws备份__dexbot_ros2_ws（复件14-目前暂时没问题的版本）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件14-目前暂时没问题的版本）/src/cuttofo_xcore/.project-log`；重复来源 2 个；SHA256 `9f75d460fa0e4aa0`
- `013__dexbot_ros2_ws备份__dexbot_ros2_ws（复件17-重新标定相机之后的版本）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件17-重新标定相机之后的版本）/src/cuttofo_xcore/.project-log`；重复来源 2 个；SHA256 `e9a3ba0acb401f90`
- `014__dexbot_ros2_ws备份__dexbot_ros2_ws（复件2）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件2）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `8ec28fe3fca8f053`
- `015__dexbot_ros2_ws备份__dexbot_ros2_ws（复件2）__src__gui` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件2）/src/gui/.project-log`；重复来源 1 个；SHA256 `20e12dfa0098d461`
- `016__dexbot_ros2_ws备份__dexbot_ros2_ws（复件3-15号初始）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件3-15号初始）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `ada7aacb1f82d7c0`
- `017__dexbot_ros2_ws备份__dexbot_ros2_ws（复件4）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件4）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `09cc143eebe33475`
- `018__dexbot_ros2_ws备份__dexbot_ros2_ws（复件5）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件5）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `cab5a41d48f5dd29`
- `019__dexbot_ros2_ws备份__dexbot_ros2_ws（复件6）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件6）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `4e53c74e24f6ea1f`
- `020__dexbot_ros2_ws备份__dexbot_ros2_ws（复件7）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件7）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `6f6ed7c999b19e85`
- `021__dexbot_ros2_ws备份__dexbot_ros2_ws（复件8中间，旋转不行）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件8中间，旋转不行）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `df6b09c0fe82c7c2`
- `022__dexbot_ros2_ws备份__dexbot_ros2_ws（复件9,phase1-5没问题）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（复件9,phase1-5没问题）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `91765090979ccc4b`
- `023__dexbot_ros2_ws备份__dexbot_ros2_ws（附件15-准备集成抓刀逻辑）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件15-准备集成抓刀逻辑）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `50bf8100a6912eaf`
- `024__dexbot_ros2_ws备份__dexbot_ros2_ws（附件17-开始集成抓刀的逻辑）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件17-开始集成抓刀的逻辑）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `a650b3ea36f7f443`
- `025__dexbot_ros2_ws备份__dexbot_ros2_ws（附件18-初步测试可以抓刀，需要修改一下抓刀参数然后测试能不能全流程）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件18-初步测试可以抓刀，需要修改一下抓刀参数然后测试能不能全流程）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `7148644abdd5fa34`
- `026__dexbot_ros2_ws备份__dexbot_ros2_ws（附件19-全流程能串但是拔刀之后切豆腐会抽搐）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件19-全流程能串但是拔刀之后切豆腐会抽搐）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `167ce22320f673a9`
- `027__dexbot_ros2_ws备份__dexbot_ros2_ws（附件20）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件20）/src/cuttofo_xcore/.project-log`；重复来源 3 个；SHA256 `7b7d5b2a1f15a2a6`
- `028__dexbot_ros2_ws备份__dexbot_ros2_ws（附件25-视觉优化第一版本）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件25-视觉优化第一版本）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `dd973d178f27c019`
- `029__dexbot_ros2_ws备份__dexbot_ros2_ws（附件26-继续优化）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件26-继续优化）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `d32ea31c67d77111`
- `030__dexbot_ros2_ws备份__dexbot_ros2_ws（附件27-视觉优化版本2）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件27-视觉优化版本2）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `1ceba3ff79ae03a8`
- `031__dexbot_ros2_ws备份__dexbot_ros2_ws（附件28-准备优化阶段7的切割逻辑）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件28-准备优化阶段7的切割逻辑）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `27ea46b9b71498b8`
- `032__dexbot_ros2_ws备份__dexbot_ros2_ws（附件29-23号最终版本）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件29-23号最终版本）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `a8069b412e469b7c`
- `033__dexbot_ros2_ws备份__dexbot_ros2_ws（附件33-垃圾版本）` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件33-垃圾版本）/.project-log`；重复来源 1 个；SHA256 `9456ba1f711d7ab6`
- `034__dexbot_ros2_ws备份__dexbot_ros2_ws（附件33-垃圾版本）__src__cuttofo_xcore` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件33-垃圾版本）/src/cuttofo_xcore/.project-log`；重复来源 1 个；SHA256 `79a74fa0938a71b5`
- `035__dexbot_ros2_ws备份__dexbot_ros2_ws（附件33-垃圾版本）__src__gui` ← `tofu/dexbot_ros2_ws备份/dexbot_ros2_ws（附件33-垃圾版本）/src/gui/.project-log`；重复来源 1 个；SHA256 `ee39d399d0359457`
