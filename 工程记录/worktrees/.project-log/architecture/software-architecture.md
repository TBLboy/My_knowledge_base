# Software Architecture

## System Layers

```
[User/Operator]
      |
      v
[Upper APP] -- this project
      |
      v (HTTP)
[Middle NODE]
      |
      v (robot control interfaces)
[Robot ROS Program]
      |
      v
[Robot Hardware]
```

## Module Boundaries

### Upper APP (this project)
- UI Layer: page rendering, user interaction, event handling
- Service Layer: HTTP request construction, protocol serialization/deserialization
- Config Layer: middle NODE address, timeout, environment settings

### Middle NODE (not in scope)
- HTTP endpoint listener
- Request routing and unpacking
- Robot control interface adapter

### Robot ROS (not in scope)
- Cucumber cutting performance routines
- Motion control
- Sensor feedback

## Communication

- APP to Middle: HTTP (protocol details TBD)
- Middle to Robot: ROS interface (not in scope)

## Deployment

- APP: runs on Android PAD (user-facing device at exhibition)
- Middle NODE: runs on robot-side development board
- Robot: robot hardware with ROS
