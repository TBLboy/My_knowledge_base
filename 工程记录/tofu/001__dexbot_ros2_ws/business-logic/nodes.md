# Nodes

## GUI Service Nodes

| Node | Description | Side | IP | CAN |
|------|-------------|------|----|-----|
| `arm_l` | Left arm ROS bridge | left | 192.168.2.160 | can1 |
| `arm_r` | Right arm ROS bridge | right | 192.168.2.161 | can0 |

## ROS Bridge Nodes (rclpy)

| Node Name | Namespace | Side |
|-----------|-----------|------|
| `dexbot_gui_lclient` | `arm_l` | left |
| `dexbot_gui_rclient` | `arm_r` | right |
