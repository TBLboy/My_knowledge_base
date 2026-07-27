# Edges

## Data Flow

```
User Input (ArmSidePanel)
    │
    ▼
ArmControlService(side)
    │
    ▼
ServiceRegistry.get_ros_bridge(side)
    │
    ├─ "left"  → RosServiceBridge(node_name="dexbot_gui_lclient", namespace="arm_l")
    │                   │
    │                   ▼
    │              ROS services (move_joints, get_state, enable_arm, etc.)
    │
    └─ "right" → RosServiceBridge(node_name="dexbot_gui_rclient", namespace="arm_r")
                    │
                    ▼
               ROS services (move_joints, get_state, enable_arm, etc.)
```

## Joint State Polling (500ms)

```
ArmSidePanel._poll_joints()
    │
    ├─ bridge = services.get_ros_bridge(self._side)
    │
    └─ bridge.get_latest_joint_deg()
            │
            ▼
        UI update: _joint_reading_vars[i] labels
```
