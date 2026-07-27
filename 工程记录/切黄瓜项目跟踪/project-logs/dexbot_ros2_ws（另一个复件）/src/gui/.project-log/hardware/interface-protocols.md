# Interface Protocols

## ROS2 Services

All services use `dexbot_interfaces_low` message types.

### Service Call Pattern

```python
bridge = self._services.get_ros_bridge()
bridge.wait_clients([bridge.cli_X], timeout_s=3.0)
request = bridge.ServiceType.Request()
request.field = value
response = bridge.call(bridge.cli_X, request, timeout_s=5.0)
if not response.success:
    raise RuntimeError(response.message)
```

### Namespace Mapping

- Right arm: `arm_r` → services at `/robot/*`
- Left arm: `arm_l` → services at `/robot/*`
- Namespace set in `RosServiceBridge(node_name=..., namespace="arm_r"/"arm_l")`

## xCore SDK Protocol

- Transport: TCP/IP
- Default port: SDK-managed (no manual port config)
- Connection: `robot = RobotClass(ip_address)`
- Error handling: `ec = {}; robot.method(ec); if ec.get("ec") != 0: raise`

## CAN Hand Protocol

- Interface: Linux CAN (`can0`)
- Bitrate: 1000000
- Setup: `ip link set can0 down → set bitrate → set txqueuelen → up`
- Requires: `pkexec` for privilege escalation (single password prompt)
- Polling: `hand.start_polling({SensorSource.ANGLE: 1/30})` at 30Hz

## Web GUI Protocol

- HTTP: FastAPI endpoints (`/login`, `/register`, `/api/*`)
- WebSocket: `/ws?token=<session_token>`
- Message format: JSON via stdin/stdout
  - Client → Worker: `{"cmd": "arm.call", "params": {"method": "...", "args": [], "kwargs": {}}}`
  - Worker → Client: `{"type": "response", "id": ..., "result": ...}` or `{"type": "error", "id": ..., "error": "..."}`

## Logging Protocol

- Format: `[LEVEL|YYYY-MM-DD HH:MM:SS.mmm] [module] message`
- Tkinter: `logs/tkinter_YYYY-MM-DD.log`
- Web server: `logs/web_YYYY-MM-DD.log`
- Worker: stderr with `[WORKER|LEVEL|HH:MM:SS.mmm] message`
- Rotation: midnight, 30-day retention (Tkinter), single file (Web)
