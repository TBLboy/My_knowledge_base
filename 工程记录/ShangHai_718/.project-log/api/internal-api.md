# Internal API Reference

> **正式规范文档**: `/home/tbl/Project/ShangHai_718/robot_cooking_api_protocol.md` — 此文件为接口的权威定义，包含完整的请求/响应 JSON 示例、枚举值、错误码、轮询策略。本文件为工程摘要，以协议文档为准。

## Communication Protocol

- Protocol: HTTP/1.1, JSON
- Content-Type: application/json
- Unified Response: `{"code": 0, "message": "success", "data": {...}}`
- code=0: success; code!=0: error

## Endpoints

---

### GET /api/system/status

Get system status and robot state.

Response data:
```
softwareName: string
softwareVersion: string
robotStatus: string (idle/running/paused/error/emergency_stop)
workMode: string (developer/user)
dragMode: boolean
online: boolean
emergencyStopped: boolean
```

---

### GET /api/task/current

Get current task progress. Query: `?taskId=xxx`.

Response data:
```
taskId: string
recipeId: string
recipeName: string
status: string (waiting/running/finished/failed/paused/cancelled/skipped)
currentStepIndex: int
currentStepName: string
progress: int (0-100)
steps: [{stepIndex, stepName, status}]
```

---

### GET /api/logs

Get system logs. Query: `?level=all&limit=20` or `?taskId=xxx&limit=20`.

Response data:
```
[{logId, level(info/warning/error/debug), title, content, time}]
```

---

### POST /api/task/start

Start making a recipe.

Request body:
```
recipeId: string (required)
mode: string (auto/manual/debug, default auto)
operatorId: string (optional)
```

Response data:
```
taskId: string
recipeId: string
status: string
currentStepIndex: int
```

---

### POST /api/task/control

Task-level control (reusable).

Request body:
```
taskId: string (optional, not needed for system-level control)
command: string (required)
operatorId: string (optional)
reason: string (optional)
```

Command enum:
- call_staff: summon staff
- emergency_stop: emergency stop
- reset_pose: reset to initial pose
- drag_mode_on / drag_mode_off: toggle drag mode
- switch_developer_mode / switch_user_mode: mode switch
- pause / resume / cancel: task control

Response data:
```
taskId: string
command: string
result: string (accepted)
robotStatus: string
```

---

### POST /api/robot/action

Robot arm action control (reusable).

Request body:
```
taskId: string (optional)
arm: string (required: left/right/both)
action: string (required: grasp/release/reset_pose/move_to/stop/open_gripper/close_gripper)
target: string (optional: knife/cucumber/home/cutting_board)
operatorId: string (optional)
```

Button mapping:

| Button | arm | action | target |
|---|---|---|---|
| Left grasp knife | left | grasp | knife |
| Left release knife | left | release | knife |
| Left reset pose | left | reset_pose | home |
| Right grasp cucumber | right | grasp | cucumber |
| Right release cucumber | right | release | cucumber |
| Right reset pose | right | reset_pose | home |

Response data:
```
actionId: string
arm: string
action: string
target: string
status: string
```

---

## Optional: WebSocket

WS /ws/robot/status

Push types:
- task_progress: task progress update
- log: log message
- robot_status: robot status change
