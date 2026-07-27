# Hardware List

| Component | Model | Role | Side | Connection | IP/Interface | Notes |
|-----------|-------|------|------|------------|-------------|-------|
| 机械臂 | xCore AR5-5 07L-W4C1C1 | 夹持 / 切割 | Left | TCP/IP | 192.168.2.160 | 7-DOF, SDK v0.5.1.ar_12 |
| 机械臂 | xCore AR5-5 07R-W4C1C1 | 刀把抓取 + 切割 | Right | TCP/IP | 192.168.2.161 | 7-DOF, SDK v0.5.1.ar_12 |
| 灵巧手 | LinkerHand O6 | 抓取 | Left | CAN | can1 | 6 轴, bitrate 1M |
| 灵巧手 | LinkerHand O6 | 抓取 | Right | CAN | can0 | 6 轴, bitrate 1M |
| 深度相机 | Intel RealSense D4xx | 视觉感知 | — | USB3 | — | 对齐深度到彩色 |
