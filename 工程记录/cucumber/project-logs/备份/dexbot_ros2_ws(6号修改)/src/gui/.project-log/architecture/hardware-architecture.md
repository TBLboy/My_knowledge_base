# Hardware Architecture

## Robot Arm

| Property | Value |
|---|---|
| Model | xMateErProRobot / xMateRobot / xMateCr5Robot |
| DOF | 7 |
| Connection | TCP/IP (Ethernet) |
| Right Arm IP | 192.168.2.161 |
| Left Arm IP | 192.168.2.160 |
| SDK | xCore SDK v0.5.1 (via LbotRobot facade) |
| Control Mode | NRT (non-real-time) / RT (real-time) |
| Coordinate Frame | flangeInBase (default) |

## CAN Hand

| Property | Value |
|---|---|
| Models | O6 (6 DOF), L25 (16 DOF), L20lite (10 DOF) |
| Connection | CAN bus (can0) |
| Bitrate | 1000000 |
| SDK | linkerbot (O6/L25/L20lite classes) |
| Control | Angle set/get, torque preset, polling at 30Hz |

## Network Topology

```
┌─────────────┐     Ethernet      ┌──────────────┐
│  GUI Host   │ ◄────────────────► │  xMate Arm   │
│ (192.168.2.x)│                   │ (192.168.2.160/161)│
└──────┬──────┘                   └──────────────┘
       │
       │ CAN (can0)
       ▼
┌──────────────┐
│  CAN Hand    │
│  (O6/L25)    │
└──────────────┘
```

## Hardware Notes

- Arm and hand are on the same host machine
- CAN interface requires `pkexec` for setup (sudo privileges)
- Arm IPs are on the same subnet as GUI host
- Dual-arm setup: left and right arms share the same CAN bus (if both have hands)
