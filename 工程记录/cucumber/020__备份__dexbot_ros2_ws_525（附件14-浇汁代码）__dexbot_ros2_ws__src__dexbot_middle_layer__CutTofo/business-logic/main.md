# Main Business Logic

## Status

- Current main path status: Stable

## Main Path

```text
A -> B -> C -> D -> E -> F -> G -> H -> I
```

主要切割流程（豆腐全流程）：
```text
A -> B -> C -> D -> E -> F -> G
```

黄瓜切割流程（简化版）：
```text
A -> H -> B -> C -> I
```

## Path Summary

| Node | Description | Package |
|------|-------------|---------|
| A | 双臂控制器就绪 | dexbot_bringup |
| B | 刀把抓取完成 | cuttofo_skill_handle_approach |
| C | 切刀预备位姿到达 | cuttofo_skill_tofu_prepare |
| D | 水平圆切第 1 轮完成 | cuttofo_skill_tofu_cut_round |
| E | 水平圆切第 2 轮完成 | cuttofo_skill_tofu_cut_round |
| F | 人工旋转豆腐完成 | cuttofo_orchestrator |
| G | 垂直切割完成 | cuttofo_skill_tofu_vertical_cut |
| H | 黄瓜夹持完成 | cuttofo_skill_cucumber_hold |
| I | 左臂归位 | cuttofo_skill_cucumber_hold |

## Implementation Priority

- Current target node: A (双臂控制 + 视觉就绪)
- Current target edge: A -> B (handle_approach 技能开发稳定)

## Stable Assumptions

- xCore SDK v0.5.1.ar_12 已安装于 dexbot_bottom_layer
- RealSense 相机已标定（手眼标定文件在校准结果中）
- O6 灵巧手通过 CAN0 控制
- 左臂无 TCP 工具偏移（URDF 全零），右臂有刀 TCP 偏移

## Verification Status

- Skills build successfully
- 完整运行验证：待下次实物测试
